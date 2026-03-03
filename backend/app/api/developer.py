from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..models.models import Developer, Wallet
from ..schemas.schemas import DeveloperRegister, DeveloperLogin, DeveloperResponse, Token
from ..utils.auth import get_password_hash, verify_password, create_access_token

router = APIRouter()


@router.post("/register", response_model=DeveloperResponse, summary="开发者注册")
async def register_developer(
    developer: DeveloperRegister,
    db: Session = Depends(get_db)
):
    """注册新开发者"""
    # 检查邮箱是否已存在
    existing_developer = db.query(Developer).filter(Developer.email == developer.email).first()
    if existing_developer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已注册"
        )

    # 创建开发者
    from uuid import uuid4
    import secrets

    new_developer = Developer(
        email=developer.email,
        password_hash=get_password_hash(developer.password),
        pay_key=f"KEY_{uuid4().hex[:16].upper()}",
        pay_secret=f"SECRET_{secrets.token_hex(32)}",
        status=1
    )

    db.add(new_developer)
    db.flush()  # 获取ID

    # 创建钱包
    wallet = Wallet(
        developer_id=new_developer.id,
        balance=0,
        frozen_balance=0,
        total_income=0,
        total_withdraw=0
    )
    db.add(wallet)

    db.commit()
    db.refresh(new_developer)

    return new_developer


@router.post("/login", response_model=Token, summary="开发者登录")
async def login_developer(
    developer: DeveloperLogin,
    db: Session = Depends(get_db)
):
    """开发者登录"""
    # 查询开发者
    db_developer = db.query(Developer).filter(Developer.email == developer.email).first()
    if not db_developer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 验证密码
    if not verify_password(developer.password, db_developer.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误"
        )

    # 检查状态
    if db_developer.status == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="账号已被禁用"
        )

    # 创建token
    access_token = create_access_token(data={"sub": db_developer.email, "developer_id": db_developer.id})
    return {"access_token": access_token, "token_type": "bearer"}
