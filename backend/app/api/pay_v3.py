import ipaddress
import json
import socket
from decimal import Decimal
from typing import Optional
from urllib.parse import urlparse

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.responses import HTMLResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..api.deps import get_current_developer
from ..core.database import get_db
from ..core.settings import settings
from ..models.models import Developer, Order, ProviderEvent
from ..schemas.schemas import OrderCreate
from ..services.payment_ops import (
    calculate_developer_income,
    calculate_platform_fee,
    generate_platform_order_no,
    generate_qr_code,
    process_payment_success,
)
from ..services.wechat_pay_service import wechat_pay_service
from ..utils.signature import generate_sign, verify_sign
from ..workers.callback_worker import send_callback_sync

router = APIRouter()


def _is_private_host(hostname: str) -> bool:
    try:
        for addr in socket.getaddrinfo(hostname, None):
            ip = ipaddress.ip_address(addr[4][0])
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return True
    except socket.gaierror:
        return True
    return False


def _validate_notify_url(notify_url: str) -> str:
    parsed = urlparse(notify_url)
    if parsed.scheme not in {"http", "https"}:
        raise HTTPException(status_code=400, detail="notify_url 仅支持 http/https")
    if not parsed.hostname:
        raise HTTPException(status_code=400, detail="notify_url 不合法")
    if not settings.ALLOW_LOCAL_NOTIFY and _is_private_host(parsed.hostname):
        raise HTTPException(status_code=400, detail="notify_url 不能是内网地址")
    return notify_url


def _create_or_update_order(db: Session, developer: Developer, order_in: OrderCreate) -> Order:
    notify_url = _validate_notify_url(str(order_in.notify_url))
    existing = db.query(Order).filter(
        Order.developer_id == developer.id,
        Order.developer_order_no == order_in.developer_order_no,
    ).first()

    fee = calculate_platform_fee(order_in.amount)
    income = calculate_developer_income(order_in.amount, fee)

    if existing:
        if existing.status == 1:
            return existing
        existing.amount = order_in.amount
        existing.notify_url = notify_url
        existing.platform_fee = fee
        existing.developer_income = income
        db.commit()
        db.refresh(existing)
        return existing

    new_order = Order(
        platform_order_no=generate_platform_order_no(),
        developer_order_no=order_in.developer_order_no,
        developer_id=developer.id,
        amount=order_in.amount,
        platform_fee=fee,
        developer_income=income,
        status=0,
        notify_url=notify_url,
        payment_channel="wechat",
    )
    db.add(new_order)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        conflict = db.query(Order).filter(
            Order.developer_id == developer.id,
            Order.developer_order_no == order_in.developer_order_no,
        ).first()
        if not conflict:
            raise HTTPException(status_code=500, detail="订单创建失败")
        return conflict
    db.refresh(new_order)
    return new_order


def _build_callback_payload(order: Order, pay_secret: str) -> dict:
    payload = {
        "platform_order_no": order.platform_order_no,
        "developer_order_no": order.developer_order_no,
        "amount": str(order.amount),
        "platform_fee": str(order.platform_fee),
        "developer_income": str(order.developer_income),
        "status": order.status,
        "pay_time": order.pay_time.isoformat() if order.pay_time else None,
    }
    payload["sign"] = generate_sign(payload, pay_secret)
    return payload


def _sync_create_wechat_native(order: Order) -> tuple[str, str]:
    if settings.WECHAT_ENABLED:
        description = f"开发者订单-{order.developer_order_no}"
        notify_url = settings.WECHAT_PAY_NOTIFY_URL or "http://localhost:8000/api/pay/notify/wechat"
        result = wechat_pay_service.create_native_order(
            out_trade_no=order.platform_order_no,
            amount_fen=int(order.amount * 100),
            description=description,
            notify_url=notify_url,
        )
        return result.code_url, result.prepay_id or ""

    code_url = f"mockpay://{order.platform_order_no}"
    return code_url, ""


def _build_create_response(order: Order, code_url: str) -> dict:
    return {
        "platform_order_no": order.platform_order_no,
        "pay_url": f"http://localhost:8000/api/pay/mock/{order.platform_order_no}",
        "code_url": code_url,
        "qr_code": generate_qr_code(code_url),
        "amount": float(order.amount),
        "status": order.status,
    }


def _notify_developer(db: Session, order: Order):
    developer = db.query(Developer).filter(Developer.id == order.developer_id).first()
    if not developer:
        return
    payload = _build_callback_payload(order, developer.pay_secret)
    send_callback_sync(order.notify_url, payload)


@router.post("/create", response_model=dict, summary="创建支付订单(开发者后台)")
async def create_order(
    order: OrderCreate,
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db),
):
    order_obj = _create_or_update_order(db, current_developer, order)
    code_url, prepay_id = _sync_create_wechat_native(order_obj)
    order_obj.code_url = code_url
    if prepay_id:
        order_obj.provider_trade_no = prepay_id
    db.commit()
    return _build_create_response(order_obj, code_url)


@router.post("/gateway/create", response_model=dict, summary="创建支付订单(开放网关)")
async def gateway_create_order(
    order: OrderCreate,
    pay_key: str = Query(..., description="支付密钥"),
    sign: str = Query(..., description="签名"),
    db: Session = Depends(get_db),
):
    developer = db.query(Developer).filter(Developer.pay_key == pay_key).first()
    if not developer:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="无效的 pay_key")
    if developer.status == 0:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="开发者账号已被禁用")

    sign_params = {
        "developer_order_no": order.developer_order_no,
        "amount": str(order.amount),
        "notify_url": str(order.notify_url),
        "pay_key": pay_key,
    }
    if not verify_sign(sign_params, developer.pay_secret, sign):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="签名验证失败")

    order_obj = _create_or_update_order(db, developer, order)
    code_url, prepay_id = _sync_create_wechat_native(order_obj)
    order_obj.code_url = code_url
    if prepay_id:
        order_obj.provider_trade_no = prepay_id
    db.commit()
    return _build_create_response(order_obj, code_url)


@router.post("/notify", summary="支付回调(模拟)")
async def payment_notify_mock(
    platform_order_no: str = Query(..., description="平台订单号"),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.platform_order_no == platform_order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")
    if order.status == 1:
        return {"status": "success", "message": "订单已支付"}
    if not process_payment_success(db, order):
        raise HTTPException(status_code=500, detail="支付处理失败")
    order.provider_state = "SUCCESS"
    db.commit()
    _notify_developer(db, order)
    return {"status": "success", "message": "支付处理成功"}


@router.post("/notify/wechat", summary="微信支付回调")
async def payment_notify_wechat(request: Request, db: Session = Depends(get_db)):
    raw_body = (await request.body()).decode("utf-8")
    headers = dict(request.headers)
    if not wechat_pay_service.verify_callback_signature(headers, raw_body):
        raise HTTPException(status_code=401, detail="微信回调验签失败")

    body_json = json.loads(raw_body)
    resource_data = wechat_pay_service.decrypt_callback_resource(body_json)

    out_trade_no = resource_data.get("out_trade_no")
    trade_state = resource_data.get("trade_state")
    transaction_id = resource_data.get("transaction_id")

    db.add(
        ProviderEvent(
            event_type="wechat.pay.callback",
            ref_no=out_trade_no,
            payload=raw_body,
            processed=0,
        )
    )

    order = db.query(Order).filter(Order.platform_order_no == out_trade_no).first()
    if not order:
        db.commit()
        return {"code": "SUCCESS", "message": "ok"}

    order.callback_payload = raw_body
    order.provider_trade_no = transaction_id
    order.provider_state = trade_state

    if trade_state == "SUCCESS" and order.status != 1:
        process_payment_success(db, order)
        db.commit()
        _notify_developer(db, order)
    else:
        db.commit()

    return {"code": "SUCCESS", "message": "ok"}


@router.get("/mock/{platform_order_no}", summary="模拟支付页面")
async def mock_pay_page(platform_order_no: str, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.platform_order_no == platform_order_no).first()
    if not order:
        raise HTTPException(status_code=404, detail="订单不存在")

    html = f"""
    <!DOCTYPE html>
    <html>
    <head><meta charset="UTF-8"><title>模拟支付</title></head>
    <body style="font-family: Arial, sans-serif; max-width: 640px; margin: 40px auto; padding: 16px; border: 1px solid #ddd; border-radius: 10px;">
      <h2>模拟支付</h2>
      <p><strong>订单号:</strong> {order.platform_order_no}</p>
      <p><strong>金额:</strong> ¥{order.amount}</p>
      <p><strong>状态:</strong> {'已支付' if order.status == 1 else '待支付'}</p>
      <form action="/api/pay/notify?platform_order_no={platform_order_no}" method="post">
        <button type="submit" {'disabled' if order.status == 1 else ''}>确认支付</button>
      </form>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@router.get("/", response_model=dict, summary="查询订单列表")
async def get_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None),
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db),
):
    query = db.query(Order).filter(Order.developer_id == current_developer.id)
    if status is not None:
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [
            {
                "platform_order_no": o.platform_order_no,
                "developer_order_no": o.developer_order_no,
                "amount": float(o.amount),
                "platform_fee": float(o.platform_fee),
                "developer_income": float(o.developer_income),
                "status": o.status,
                "provider_state": o.provider_state,
                "pay_time": o.pay_time.isoformat() if o.pay_time else None,
                "created_at": o.created_at.isoformat(),
            }
            for o in orders
        ],
    }


@router.get("/success", response_model=dict, summary="查询成功订单")
async def get_success_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db),
):
    query = db.query(Order).filter(Order.developer_id == current_developer.id, Order.status == 1)
    total = query.count()
    orders = query.order_by(Order.pay_time.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [
            {
                "platform_order_no": o.platform_order_no,
                "developer_order_no": o.developer_order_no,
                "amount": float(o.amount),
                "platform_fee": float(o.platform_fee),
                "developer_income": float(o.developer_income),
                "provider_state": o.provider_state,
                "pay_time": o.pay_time.isoformat() if o.pay_time else None,
                "created_at": o.created_at.isoformat(),
            }
            for o in orders
        ],
    }
