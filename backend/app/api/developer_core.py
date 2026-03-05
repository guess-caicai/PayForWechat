import secrets
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import case, func
from sqlalchemy.orm import Session

from ..api.deps import get_current_developer
from ..core.database import get_db
from ..models.models import Developer, Order, Wallet
from ..schemas.schemas import (
    ApiKeyRotateRequest,
    BindWechatRequest,
    DeveloperLogin,
    DeveloperRegister,
    DeveloperResponse,
    Token,
)
from ..utils.auth import create_access_token, get_password_hash, verify_password

router = APIRouter()


@router.post("/register", response_model=DeveloperResponse)
async def register_developer(developer: DeveloperRegister, db: Session = Depends(get_db)):
    existing = db.query(Developer).filter(Developer.email == developer.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="email already registered")

    new_dev = Developer(
        email=developer.email,
        password_hash=get_password_hash(developer.password),
        pay_key=f"KEY_{uuid4().hex[:16].upper()}",
        pay_secret=f"SECRET_{secrets.token_hex(32)}",
        status=1,
    )
    db.add(new_dev)
    db.flush()
    db.add(Wallet(developer_id=new_dev.id, balance=0, frozen_balance=0, total_income=0, total_withdraw=0))
    db.commit()
    db.refresh(new_dev)
    return new_dev


@router.post("/login", response_model=Token)
async def login_developer(developer: DeveloperLogin, db: Session = Depends(get_db)):
    db_developer = db.query(Developer).filter(Developer.email == developer.email).first()
    if not db_developer or not verify_password(developer.password, db_developer.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid email or password")
    if db_developer.status == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="account disabled")
    token = create_access_token(data={"sub": db_developer.email, "developer_id": db_developer.id})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/profile", response_model=dict)
async def get_profile(current_developer: Developer = Depends(get_current_developer), db: Session = Depends(get_db)):
    wallet = db.query(Wallet).filter(Wallet.developer_id == current_developer.id).first()
    order_total, paid_count, paid_amount = (
        db.query(
            func.count(Order.id),
            func.sum(case((Order.status == 1, 1), else_=0)),
            func.sum(case((Order.status == 1, Order.amount), else_=0)),
        )
        .filter(Order.developer_id == current_developer.id)
        .first()
    )
    return {
        "id": current_developer.id,
        "email": current_developer.email,
        "status": current_developer.status,
        "created_at": current_developer.created_at,
        "pay_key": current_developer.pay_key,
        "wechat_openid": current_developer.wechat_openid,
        "wallet": {
            "balance": float(wallet.balance) if wallet else 0.0,
            "frozen_balance": float(wallet.frozen_balance) if wallet else 0.0,
            "total_income": float(wallet.total_income) if wallet else 0.0,
            "total_withdraw": float(wallet.total_withdraw) if wallet else 0.0,
        },
        "stats": {
            "order_total": int(order_total or 0),
            "paid_count": int(paid_count or 0),
            "paid_amount": float(paid_amount or 0),
        },
    }


@router.get("/api-keys", response_model=dict)
async def get_api_keys(current_developer: Developer = Depends(get_current_developer)):
    return {"pay_key": current_developer.pay_key, "pay_secret": current_developer.pay_secret}


@router.post("/wechat/bind", response_model=dict)
async def bind_wechat_openid(
    payload: BindWechatRequest,
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db),
):
    current_developer.wechat_openid = payload.wechat_openid.strip()
    db.commit()
    return {"wechat_openid": current_developer.wechat_openid}


@router.post("/api-keys/rotate", response_model=dict)
async def rotate_api_keys(
    payload: ApiKeyRotateRequest,
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db),
):
    if not verify_password(payload.password, current_developer.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="password incorrect")
    current_developer.pay_key = f"KEY_{uuid4().hex[:16].upper()}"
    current_developer.pay_secret = f"SECRET_{secrets.token_hex(32)}"
    db.commit()
    db.refresh(current_developer)
    return {"pay_key": current_developer.pay_key, "pay_secret": current_developer.pay_secret}
