from datetime import UTC, datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from ..api.deps import get_current_developer, verify_admin_access
from ..core.database import get_db
from ..models.models import Developer, Withdraw
from ..schemas.schemas import WithdrawApply, WithdrawResponse
from ..services.payment_ops import complete_withdraw, freeze_withdraw_amount, unfreeze_withdraw_amount

router = APIRouter()
admin_router = APIRouter(dependencies=[Depends(verify_admin_access)])


@router.post("/apply", response_model=WithdrawResponse, summary="申请提现")
async def apply_withdraw(
    withdraw: WithdrawApply,
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db),
):
    if withdraw.amount <= 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="提现金额必须大于0")

    if not freeze_withdraw_amount(db, current_developer.id, withdraw.amount):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="余额不足")

    new_withdraw = Withdraw(developer_id=current_developer.id, amount=withdraw.amount, status=0)
    db.add(new_withdraw)
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
                "status": w.status,
                "created_at": w.created_at.isoformat(),
                "finished_at": w.finished_at.isoformat() if w.finished_at else None,
            }
            for w in rows
        ],
    }


@admin_router.post("/approve", response_model=WithdrawResponse, summary="管理员通过提现")
async def approve_withdraw(withdraw_id: int, db: Session = Depends(get_db)):
    withdraw = db.query(Withdraw).filter(Withdraw.id == withdraw_id).first()
    if not withdraw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提现记录不存在")
    if withdraw.status != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="提现状态不是待审核")

    if not complete_withdraw(db, withdraw.developer_id, withdraw.amount):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="冻结余额不足")

    withdraw.status = 3
    withdraw.finished_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(withdraw)
    return withdraw


@admin_router.post("/reject", response_model=WithdrawResponse, summary="管理员拒绝提现")
async def reject_withdraw(withdraw_id: int, db: Session = Depends(get_db)):
    withdraw = db.query(Withdraw).filter(Withdraw.id == withdraw_id).first()
    if not withdraw:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="提现记录不存在")
    if withdraw.status != 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="提现状态不是待审核")

    if not unfreeze_withdraw_amount(db, withdraw.developer_id, withdraw.amount):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="冻结余额不足")

    withdraw.status = 2
    withdraw.finished_at = datetime.now(UTC).replace(tzinfo=None)
    db.commit()
    db.refresh(withdraw)
    return withdraw
