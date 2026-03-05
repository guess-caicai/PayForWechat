from datetime import UTC, datetime
from decimal import Decimal
import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from ..api.deps import get_current_developer, verify_admin_access
from ..core.database import get_db
from ..core.settings import settings
from ..models.models import Developer, ProviderEvent, Wallet, Withdraw
from ..schemas.schemas import WithdrawApply, WithdrawResponse
from ..services.payment_ops import complete_withdraw, freeze_withdraw_amount, unfreeze_withdraw_amount
from ..services.wechat_pay_service import wechat_pay_service

router = APIRouter()
admin_router = APIRouter(dependencies=[Depends(verify_admin_access)])


def _build_transfer_no(withdraw_id: int) -> str:
    return f"WD{withdraw_id:012d}"


def _trigger_transfer(db: Session, withdraw: Withdraw, developer: Developer) -> None:
    if not developer.wechat_openid:
        raise HTTPException(status_code=400, detail="开发者未绑定微信OpenID")

    if not settings.WECHAT_ENABLED:
        withdraw.status = 3
        withdraw.provider_status = "MOCK_SUCCESS"
        withdraw.provider_transfer_no = _build_transfer_no(withdraw.id)
        withdraw.finished_at = datetime.now(UTC).replace(tzinfo=None)
        if not complete_withdraw(db, developer.id, withdraw.amount):
            raise HTTPException(status_code=400, detail="冻结余额不足")
        return

    out_bill_no = _build_transfer_no(withdraw.id)
    notify_url = settings.WECHAT_TRANSFER_NOTIFY_URL or "http://localhost:8000/api/withdraw/notify/wechat"
    result = wechat_pay_service.create_transfer_bill(
        out_bill_no=out_bill_no,
        openid=developer.wechat_openid,
        amount_fen=int(withdraw.amount * 100),
        remark=f"开发者提现{withdraw.id}",
        notify_url=notify_url,
    )
    withdraw.provider_transfer_no = result.transfer_no or out_bill_no
    withdraw.provider_status = result.status or "ACCEPTED"
    withdraw.provider_package_info = result.package_info
    withdraw.status = 1


@router.post("/apply", response_model=WithdrawResponse, summary="申请提现")
async def apply_withdraw(
    payload: WithdrawApply,
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db),
):
    wallet = db.query(Wallet).filter(Wallet.developer_id == current_developer.id).first()
    if not wallet:
        raise HTTPException(status_code=404, detail="钱包不存在")

    amount = wallet.balance if payload.withdraw_all else payload.amount
    if amount is None:
        raise HTTPException(status_code=400, detail="请提供提现金额或选择全额提现")
    amount = Decimal(amount).quantize(Decimal("0.01"))
    if amount <= 0:
        raise HTTPException(status_code=400, detail="提现金额必须大于0")

    if not freeze_withdraw_amount(db, current_developer.id, amount):
        raise HTTPException(status_code=400, detail="余额不足")

    new_withdraw = Withdraw(
        developer_id=current_developer.id,
        amount=amount,
        mode="all" if payload.withdraw_all else "partial",
        status=0,
    )
    db.add(new_withdraw)
    db.commit()
    db.refresh(new_withdraw)

    if settings.WECHAT_TRANSFER_AUTO_APPROVE:
        _trigger_transfer(db, new_withdraw, current_developer)
        if new_withdraw.status == 3:
            new_withdraw.finished_at = datetime.now(UTC).replace(tzinfo=None)
        db.commit()
        db.refresh(new_withdraw)
    return new_withdraw


@router.get("/", response_model=dict, summary="查询提现记录")
async def get_withdraws(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None),
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db),
):
    query = db.query(Withdraw).filter(Withdraw.developer_id == current_developer.id)
    if status is not None:
        query = query.filter(Withdraw.status == status)
    total = query.count()
    rows = query.order_by(Withdraw.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [
            {
                "id": w.id,
                "amount": float(w.amount),
                "mode": w.mode,
                "status": w.status,
                "provider_status": w.provider_status,
                "created_at": w.created_at.isoformat(),
                "finished_at": w.finished_at.isoformat() if w.finished_at else None,
            }
            for w in rows
        ],
    }


@router.post("/notify/wechat", summary="微信提现回调")
async def transfer_notify_wechat(request: Request, db: Session = Depends(get_db)):
    raw_body = (await request.body()).decode("utf-8")
    headers = dict(request.headers)
    if not wechat_pay_service.verify_callback_signature(headers, raw_body):
        raise HTTPException(status_code=401, detail="微信提现回调验签失败")
    body = json.loads(raw_body)
    resource = wechat_pay_service.decrypt_callback_resource(body)

    out_bill_no = resource.get("out_bill_no")
    state = resource.get("state")
    fail_reason = resource.get("fail_reason")

    db.add(
        ProviderEvent(
            event_type="wechat.transfer.callback",
            ref_no=out_bill_no,
            payload=raw_body,
            processed=0,
        )
    )
    withdraw = db.query(Withdraw).filter(Withdraw.provider_transfer_no == out_bill_no).first()
    if not withdraw:
        db.commit()
        return {"code": "SUCCESS", "message": "ok"}

    withdraw.provider_status = state
    if state == "SUCCESS":
        withdraw.status = 3
        withdraw.finished_at = datetime.now(UTC).replace(tzinfo=None)
        complete_withdraw(db, withdraw.developer_id, withdraw.amount)
    elif state in {"FAIL", "CLOSED"}:
        withdraw.status = 2
        withdraw.failure_reason = fail_reason
        withdraw.finished_at = datetime.now(UTC).replace(tzinfo=None)
        unfreeze_withdraw_amount(db, withdraw.developer_id, withdraw.amount)
    db.commit()
    return {"code": "SUCCESS", "message": "ok"}


@admin_router.post("/approve", response_model=WithdrawResponse, summary="管理员通过提现")
async def approve_withdraw(withdraw_id: int, db: Session = Depends(get_db)):
    withdraw = db.query(Withdraw).filter(Withdraw.id == withdraw_id).first()
    if not withdraw:
        raise HTTPException(status_code=404, detail="提现记录不存在")
    if withdraw.status != 0:
        raise HTTPException(status_code=400, detail="提现状态不是待审核")
    developer = db.query(Developer).filter(Developer.id == withdraw.developer_id).first()
    _trigger_transfer(db, withdraw, developer)
    db.commit()
    db.refresh(withdraw)
    return withdraw


@admin_router.post("/reject", response_model=WithdrawResponse, summary="管理员拒绝提现")
async def reject_withdraw(withdraw_id: int, db: Session = Depends(get_db)):
    withdraw = db.query(Withdraw).filter(Withdraw.id == withdraw_id).first()
    if not withdraw:
        raise HTTPException(status_code=404, detail="提现记录不存在")
    if withdraw.status != 0:
        raise HTTPException(status_code=400, detail="提现状态不是待审核")

    if not unfreeze_withdraw_amount(db, withdraw.developer_id, withdraw.amount):
        raise HTTPException(status_code=400, detail="冻结余额不足")

    withdraw.status = 2
    withdraw.finished_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(withdraw)
    return withdraw
