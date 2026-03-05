import base64
import io
import uuid
from datetime import UTC, datetime
from decimal import Decimal

import qrcode
from sqlalchemy.orm import Session

from ..core.settings import settings
from ..models.models import Order, Wallet, WalletLog


def generate_platform_order_no() -> str:
    return f"PF{int(uuid.uuid1().time)}{uuid.uuid4().hex[:8].upper()}"


def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


def calculate_platform_fee(amount: Decimal) -> Decimal:
    fee_rate = Decimal(str(settings.PLATFORM_FEE_RATE))
    return (amount * fee_rate).quantize(Decimal("0.01"))


def calculate_developer_income(amount: Decimal, platform_fee: Decimal) -> Decimal:
    return (amount - platform_fee).quantize(Decimal("0.01"))


def process_payment_success(db: Session, order: Order) -> bool:
    if order.status == 1:
        return True

    platform_fee = calculate_platform_fee(order.amount)
    developer_income = calculate_developer_income(order.amount, platform_fee)

    order.status = 1
    order.platform_fee = platform_fee
    order.developer_income = developer_income
    order.pay_time = datetime.now(UTC).replace(tzinfo=None)

    wallet = db.query(Wallet).filter(Wallet.developer_id == order.developer_id).first()
    if not wallet:
        return False

    wallet.balance += developer_income
    wallet.total_income += developer_income

    db.add(
        WalletLog(
            developer_id=order.developer_id,
            wallet_id=wallet.id,
            amount=developer_income,
            balance=wallet.balance,
            change_type=1,
            order_id=order.id,
            description=f"订单{order.platform_order_no}收入",
        )
    )
    return True


def freeze_withdraw_amount(db: Session, developer_id: int, amount: Decimal) -> bool:
    wallet = db.query(Wallet).filter(Wallet.developer_id == developer_id).first()
    if not wallet or wallet.balance < amount:
        return False

    wallet.balance -= amount
    wallet.frozen_balance += amount
    db.add(
        WalletLog(
            developer_id=developer_id,
            wallet_id=wallet.id,
            amount=amount,
            balance=wallet.balance,
            change_type=3,
            description=f"提现冻结{amount}",
        )
    )
    return True


def unfreeze_withdraw_amount(db: Session, developer_id: int, amount: Decimal) -> bool:
    wallet = db.query(Wallet).filter(Wallet.developer_id == developer_id).first()
    if not wallet or wallet.frozen_balance < amount:
        return False

    wallet.balance += amount
    wallet.frozen_balance -= amount
    db.add(
        WalletLog(
            developer_id=developer_id,
            wallet_id=wallet.id,
            amount=amount,
            balance=wallet.balance,
            change_type=4,
            description=f"提现解冻{amount}",
        )
    )
    return True


def complete_withdraw(db: Session, developer_id: int, amount: Decimal) -> bool:
    wallet = db.query(Wallet).filter(Wallet.developer_id == developer_id).first()
    if not wallet or wallet.frozen_balance < amount:
        return False

    wallet.frozen_balance -= amount
    wallet.total_withdraw += amount
    db.add(
        WalletLog(
            developer_id=developer_id,
            wallet_id=wallet.id,
            amount=amount,
            balance=wallet.balance,
            change_type=2,
            description=f"提现{amount}",
        )
    )
    return True
