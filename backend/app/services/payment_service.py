import uuid
import qrcode
import io
import base64
from decimal import Decimal
from typing import Optional
from sqlalchemy.orm import Session
from ..models.models import Order, Wallet, WalletLog
from ..utils.signature import generate_sign


def generate_platform_order_no() -> str:
    """生成平台订单号"""
    return f"PF{int(uuid.uuid1().time)}{uuid.uuid4().hex[:8].upper()}"


def generate_qr_code(data: str) -> str:
    """
    生成二维码

    :param data: 二维码内容
    :return: base64编码的二维码图片
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # 转换为base64
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


def calculate_platform_fee(amount: Decimal) -> Decimal:
    """
    计算平台手续费（假设费率5%）

    :param amount: 订单金额
    :return: 手续费
    """
    fee_rate = Decimal('0.05')  # 5%手续费
    return (amount * fee_rate).quantize(Decimal('0.01'))


def calculate_developer_income(amount: Decimal, platform_fee: Decimal) -> Decimal:
    """
    计算开发者收入

    :param amount: 订单金额
    :param platform_fee: 平台手续费
    :return: 开发者收入
    """
    return (amount - platform_fee).quantize(Decimal('0.01'))


def process_payment_success(db: Session, order: Order) -> bool:
    """
    处理支付成功

    :param db: 数据库会话
    :param order: 订单对象
    :return: 是否成功
    """
    try:
        # 检查订单状态，防止重复处理
        if order.status == 1:
            return False

        # 计算手续费和开发者收入
        platform_fee = calculate_platform_fee(order.amount)
        developer_income = calculate_developer_income(order.amount, platform_fee)

        # 更新订单
        order.status = 1
        order.platform_fee = platform_fee
        order.developer_income = developer_income
        order.pay_time = db.execute("SELECT NOW()").scalar()

        # 更新钱包
        wallet = db.query(Wallet).filter(Wallet.developer_id == order.developer_id).first()
        if wallet:
            old_balance = wallet.balance
            wallet.balance += developer_income
            wallet.total_income += developer_income

            # 记录钱包流水
            wallet_log = WalletLog(
                developer_id=order.developer_id,
                wallet_id=wallet.id,
                amount=developer_income,
                balance=wallet.balance,
                change_type=1,  # 1-收入
                order_id=order.id,
                description=f"订单{order.platform_order_no}收入"
            )
            db.add(wallet_log)

        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise e


def freeze_withdraw_amount(db: Session, developer_id: int, amount: Decimal) -> bool:
    """
    冻结提现金额

    :param db: 数据库会话
    :param developer_id: 开发者ID
    :param amount: 金额
    :return: 是否成功
    """
    try:
        wallet = db.query(Wallet).filter(Wallet.developer_id == developer_id).first()
        if not wallet:
            return False

        # 检查余额是否充足
        if wallet.balance < amount:
            return False

        # 冻结金额
        wallet.balance -= amount
        wallet.frozen_balance += amount

        # 记录流水
        wallet_log = WalletLog(
            developer_id=developer_id,
            wallet_id=wallet.id,
            amount=amount,
            balance=wallet.balance,
            change_type=3,  # 3-冻结
            description=f"提现冻结{amount}"
        )
        db.add(wallet_log)

        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise e


def unfreeze_withdraw_amount(db: Session, developer_id: int, amount: Decimal) -> bool:
    """
    解冻提现金额（提现失败时）

    :param db: 数据库会话
    :param developer_id: 开发者ID
    :param amount: 金额
    :return: 是否成功
    """
    try:
        wallet = db.query(Wallet).filter(Wallet.developer_id == developer_id).first()
        if not wallet:
            return False

        # 解冻金额
        wallet.balance += amount
        wallet.frozen_balance -= amount

        # 记录流水
        wallet_log = WalletLog(
            developer_id=developer_id,
            wallet_id=wallet.id,
            amount=amount,
            balance=wallet.balance,
            change_type=4,  # 4-解冻
            description=f"提现解冻{amount}"
        )
        db.add(wallet_log)

        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise e


def complete_withdraw(db: Session, developer_id: int, amount: Decimal) -> bool:
    """
    完成提现（提现成功，从冻结余额中扣除）

    :param db: 数据库会话
    :param developer_id: 开发者ID
    :param amount: 金额
    :return: 是否成功
    """
    try:
        wallet = db.query(Wallet).filter(Wallet.developer_id == developer_id).first()
        if not wallet:
            return False

        # 从冻结余额中扣除
        wallet.frozen_balance -= amount
        wallet.total_withdraw += amount

        # 记录流水
        wallet_log = WalletLog(
            developer_id=developer_id,
            wallet_id=wallet.id,
            amount=amount,
            balance=wallet.balance,
            change_type=2,  # 2-提现
            description=f"提现{amount}"
        )
        db.add(wallet_log)

        db.commit()
        return True

    except Exception as e:
        db.rollback()
        raise e
