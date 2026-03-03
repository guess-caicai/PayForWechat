from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from ..core.database import get_db
from ..models.models import Developer, Withdraw
from ..schemas.schemas import WithdrawApply, WithdrawResponse
from ..api.deps import get_current_developer
from ..services.payment_service import freeze_withdraw_amount, unfreeze_withdraw_amount, complete_withdraw
from typing import Optional

router = APIRouter()


@router.post("/apply", response_model=WithdrawResponse, summary="申请提现")
async def apply_withdraw(
    withdraw: WithdrawApply,
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db)
):
    """申请提现"""
    # 检查提现金额
    if withdraw.amount <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="提现金额必须大于0"
        )

    # 冻结金额
    success = freeze_withdraw_amount(db, current_developer.id, withdraw.amount)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="余额不足"
        )

    # 创建提现记录
    new_withdraw = Withdraw(
        developer_id=current_developer.id,
        amount=withdraw.amount,
        status=0  # 待审核
    )

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
    db: Session = Depends(get_db)
):
    """查询提现记录"""
    query = db.query(Withdraw).filter(Withdraw.developer_id == current_developer.id)

    if status is not None:
        query = query.filter(Withdraw.status == status)

    total = query.count()
    withdraws = query.order_by(Withdraw.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [{
            "id": w.id,
            "amount": float(w.amount),
            "status": w.status,
            "created_at": w.created_at.isoformat(),
            "finished_at": w.finished_at.isoformat() if w.finished_at else None
        } for w in withdraws]
    }


# 管理员接口
@router.post("/approve", response_model=WithdrawResponse, summary="管理员审核通过")
async def approve_withdraw(
    withdraw_id: int,
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db)
):
    """
    管理员审核通过提现（这里简化为开发者自己审核，实际应有管理员权限控制）
    """
    withdraw = db.query(Withdraw).filter(Withdraw.id == withdraw_id).first()
    if not withdraw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提现记录不存在"
        )

    if withdraw.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="提现状态不是待审核"
        )

    # 更新状态为已通过
    withdraw.status = 1
    withdraw.finished_at = db.execute("SELECT NOW()").scalar()

    # 完成提现（从冻结余额中扣除）
    complete_withdraw(db, withdraw.developer_id, withdraw.amount)

    db.commit()
    db.refresh(withdraw)

    return withdraw


@router.post("/reject", response_model=WithdrawResponse, summary="管理员拒绝提现")
async def reject_withdraw(
    withdraw_id: int,
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db)
):
    """
    管理员拒绝提现（这里简化为开发者自己审核，实际应有管理员权限控制）
    """
    withdraw = db.query(Withdraw).filter(Withdraw.id == withdraw_id).first()
    if not withdraw:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="提现记录不存在"
        )

    if withdraw.status != 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="提现状态不是待审核"
        )

    # 更新状态为已拒绝
    withdraw.status = 2
    withdraw.finished_at = db.execute("SELECT NOW()").scalar()

    # 解冻金额
    unfreeze_withdraw_amount(db, withdraw.developer_id, withdraw.amount)

    db.commit()
    db.refresh(withdraw)

    return withdraw
