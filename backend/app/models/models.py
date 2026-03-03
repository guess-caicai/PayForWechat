from sqlalchemy import Column, BigInteger, String, Integer, DateTime, Numeric, ForeignKey, Index
from sqlalchemy.sql import func
from backend.app.core.database import Base
import uuid

class Developer(Base):
    """开发者表"""
    __tablename__ = "developers"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="开发者ID")
    email = Column(String(128), unique=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希")
    pay_key = Column(String(64), unique=True, nullable=False, comment="支付密钥")
    pay_secret = Column(String(128), nullable=False, comment="支付密钥")
    status = Column(Integer, default=1, comment="状态: 1-正常, 0-禁用")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    __table_args__ = (
        Index('idx_pay_key', 'pay_key'),
        Index('idx_email', 'email'),
    )


class Wallet(Base):
    """钱包表"""
    __tablename__ = "wallets"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="钱包ID")
    developer_id = Column(BigInteger, ForeignKey('developers.id', ondelete='CASCADE'), unique=True, nullable=False, comment="开发者ID")
    balance = Column(Numeric(15, 2), default=0, comment="可用余额")
    frozen_balance = Column(Numeric(15, 2), default=0, comment="冻结余额")
    total_income = Column(Numeric(15, 2), default=0, comment="总收入")
    total_withdraw = Column(Numeric(15, 2), default=0, comment="总提现")

    __table_args__ = (
        Index('idx_developer_id', 'developer_id'),
    )


class Order(Base):
    """订单表"""
    __tablename__ = "orders"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="订单ID")
    platform_order_no = Column(String(64), unique=True, nullable=False, comment="平台订单号")
    developer_order_no = Column(String(64), nullable=False, comment="开发者订单号")
    developer_id = Column(BigInteger, ForeignKey('developers.id', ondelete='CASCADE'), nullable=False, comment="开发者ID")
    amount = Column(Numeric(15, 2), nullable=False, comment="订单金额")
    platform_fee = Column(Numeric(15, 2), default=0, comment="平台手续费")
    developer_income = Column(Numeric(15, 2), default=0, comment="开发者收入")
    status = Column(Integer, default=0, comment="状态: 0-待支付, 1-已支付, 2-已取消")
    notify_url = Column(String(255), nullable=False, comment="回调URL")
    pay_time = Column(DateTime, nullable=True, comment="支付时间")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    __table_args__ = (
        Index('idx_platform_order_no', 'platform_order_no'),
        Index('idx_developer_order_no', 'developer_order_no'),
        Index('idx_developer_id', 'developer_id'),
        Index('idx_status', 'status'),
    )


class Withdraw(Base):
    """提现表"""
    __tablename__ = "withdraws"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="提现ID")
    developer_id = Column(BigInteger, ForeignKey('developers.id', ondelete='CASCADE'), nullable=False, comment="开发者ID")
    amount = Column(Numeric(15, 2), nullable=False, comment="提现金额")
    status = Column(Integer, default=0, comment="状态: 0-待审核, 1-已通过, 2-已拒绝, 3-已完成")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
    finished_at = Column(DateTime, nullable=True, comment="完成时间")

    __table_args__ = (
        Index('idx_developer_id', 'developer_id'),
        Index('idx_status', 'status'),
    )


class WalletLog(Base):
    """钱包流水表"""
    __tablename__ = "wallet_logs"

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="流水ID")
    developer_id = Column(BigInteger, ForeignKey('developers.id', ondelete='CASCADE'), nullable=False, comment="开发者ID")
    wallet_id = Column(BigInteger, ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False, comment="钱包ID")
    amount = Column(Numeric(15, 2), nullable=False, comment="变动金额")
    balance = Column(Numeric(15, 2), nullable=False, comment="变动后余额")
    change_type = Column(Integer, nullable=False, comment="变动类型: 1-收入, 2-提现, 3-冻结, 4-解冻")
    order_id = Column(BigInteger, nullable=True, comment="关联订单ID")
    withdraw_id = Column(BigInteger, nullable=True, comment="关联提现ID")
    description = Column(String(255), nullable=True, comment="描述")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")

    __table_args__ = (
        Index('idx_developer_id', 'developer_id'),
        Index('idx_order_id', 'order_id'),
        Index('idx_withdraw_id', 'withdraw_id'),
    )
