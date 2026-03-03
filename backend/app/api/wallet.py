from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.models import Developer, Wallet, WalletLog
from ..schemas.schemas import WalletResponse
from ..api.deps import get_current_developer
from typing import Optional

router = APIRouter()


@router.get("/", response_model=WalletResponse, summary="查询钱包余额")
async def get_wallet(
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db)
):
    """查询当前开发者的钱包"""
    wallet = db.query(Wallet).filter(Wallet.developer_id == current_developer.id).first()
    if not wallet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="钱包不存在"
        )
    return wallet


@router.get("/logs", response_model=dict, summary="查询钱包流水")
async def get_wallet_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db)
):
    """查询钱包流水记录"""
    total = db.query(WalletLog).filter(WalletLog.developer_id == current_developer.id).count()
    logs = db.query(WalletLog).filter(
        WalletLog.developer_id == current_developer.id
    ).order_by(
        WalletLog.created_at.desc()
    ).offset((page - 1) * page_size).limit(page_size).all()

    change_type_map = {
        1: "收入",
        2: "提现",
        3: "冻结",
        4: "解冻"
    }

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [{
            "id": log.id,
            "amount": float(log.amount),
            "balance": float(log.balance),
            "change_type": change_type_map.get(log.change_type, "未知"),
            "description": log.description,
            "created_at": log.created_at.isoformat()
        } for log in logs]
    }
