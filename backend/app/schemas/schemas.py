from pydantic import BaseModel, EmailStr, Field, HttpUrl
from datetime import datetime
from typing import Optional
from decimal import Decimal

# ==================== Developer ====================

class DeveloperRegister(BaseModel):
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, max_length=128, description="密码")


class DeveloperLogin(BaseModel):
    email: EmailStr = Field(..., description="邮箱")
    password: str = Field(..., min_length=6, description="密码")


class DeveloperResponse(BaseModel):
    id: int
    email: str
    pay_key: str
    status: int
    created_at: datetime

    class Config:
        from_attributes = True


class DeveloperWithSecret(BaseModel):
    id: int
    email: str
    pay_key: str
    pay_secret: str
    status: int
    created_at: datetime

    class Config:
        from_attributes = True


# ==================== Wallet ====================

class WalletResponse(BaseModel):
    balance: Decimal
    frozen_balance: Decimal
    total_income: Decimal
    total_withdraw: Decimal

    class Config:
        from_attributes = True


# ==================== Order ====================

class OrderCreate(BaseModel):
    developer_order_no: str = Field(..., max_length=64, description="开发者订单号")
    amount: Decimal = Field(..., ge=0.01, description="订单金额")
    notify_url: HttpUrl = Field(..., description="回调URL")


class OrderResponse(BaseModel):
    platform_order_no: str
    developer_order_no: str
    amount: Decimal
    platform_fee: Decimal
    developer_income: Decimal
    status: int
    created_at: datetime

    class Config:
        from_attributes = True


class OrderDetail(BaseModel):
    id: int
    platform_order_no: str
    developer_order_no: str
    amount: Decimal
    platform_fee: Decimal
    developer_income: Decimal
    status: int
    notify_url: str
    pay_time: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class OrderQuery(BaseModel):
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    status: Optional[int] = None


# ==================== Withdraw ====================

class WithdrawApply(BaseModel):
    amount: Optional[Decimal] = Field(None, ge=0.01, description="提现金额")
    withdraw_all: bool = Field(False, description="是否全额提现")


class WithdrawResponse(BaseModel):
    id: int
    amount: Decimal
    status: int
    created_at: datetime
    finished_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==================== Token ====================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    developer_id: Optional[int] = None


class ApiKeyRotateRequest(BaseModel):
    password: str = Field(..., min_length=6, max_length=128, description="当前登录密码")


class BindWechatRequest(BaseModel):
    wechat_openid: str = Field(..., min_length=10, max_length=128, description="微信OpenID")
