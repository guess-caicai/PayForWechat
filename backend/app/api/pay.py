from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from decimal import Decimal
from datetime import datetime
from typing import Optional
from ..core.database import get_db
from ..models.models import Developer, Order
from ..schemas.schemas import OrderCreate, OrderResponse, OrderDetail, OrderQuery
from ..services.payment_service import (
    generate_platform_order_no,
    generate_qr_code,
    calculate_platform_fee,
    calculate_developer_income
)
from ..utils.signature import verify_sign
from ..api.deps import get_current_developer

router = APIRouter()


@router.get("/profile", response_model=dict, summary="获取开发者信息")
async def get_profile(
    current_developer: Developer = Depends(get_current_developer)
):
    """获取当前开发者信息（含密钥）"""
    return {
        "id": current_developer.id,
        "email": current_developer.email,
        "pay_key": current_developer.pay_key,
        "pay_secret": current_developer.pay_secret,
        "status": current_developer.status,
        "created_at": current_developer.created_at
    }


@router.post("/create", response_model=dict, summary="创建支付订单")
async def create_order(
    order: OrderCreate,
    pay_key: str = Query(..., description="支付密钥"),
    sign: str = Query(..., description="签名"),
    db: Session = Depends(get_db)
):
    """
    创建支付订单（对外接口）

    :param order: 订单信息
    :param pay_key: 支付密钥
    :param sign: 签名
    :param db: 数据库会话
    :return: 订单信息和支付二维码
    """
    # 验证开发者
    developer = db.query(Developer).filter(Developer.pay_key == pay_key).first()
    if not developer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的pay_key"
        )

    if developer.status == 0:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="开发者账号已被禁用"
        )

    # 验证签名
    sign_params = {
        "developer_order_no": order.developer_order_no,
        "amount": str(order.amount),
        "notify_url": order.notify_url,
        "pay_key": pay_key
    }

    if not verify_sign(sign_params, developer.pay_secret, sign):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="签名验证失败"
        )

    # 检查订单是否已存在
    existing_order = db.query(Order).filter(
        Order.developer_id == developer.id,
        Order.developer_order_no == order.developer_order_no
    ).first()

    if existing_order:
        # 如果订单已存在且已支付，直接返回
        if existing_order.status == 1:
            qr_code = generate_qr_code(f"mockpay://{existing_order.platform_order_no}")
            return {
                "platform_order_no": existing_order.platform_order_no,
                "pay_url": f"http://localhost:8000/pay/mock/{existing_order.platform_order_no}",
                "qr_code": qr_code,
                "amount": float(existing_order.amount),
                "status": existing_order.status
            }
        # 如果订单存在但未支付，更新订单
        existing_order.amount = order.amount
        existing_order.notify_url = order.notify_url
        db.commit()
        db.refresh(existing_order)
        platform_order_no = existing_order.platform_order_no
    else:
        # 生成平台订单号
        platform_order_no = generate_platform_order_no()

        # 计算手续费和开发者收入
        platform_fee = calculate_platform_fee(order.amount)
        developer_income = calculate_developer_income(order.amount, platform_fee)

        # 创建订单
        new_order = Order(
            platform_order_no=platform_order_no,
            developer_order_no=order.developer_order_no,
            developer_id=developer.id,
            amount=order.amount,
            platform_fee=platform_fee,
            developer_income=developer_income,
            status=0,  # 待支付
            notify_url=order.notify_url
        )

        db.add(new_order)
        db.commit()
        db.refresh(new_order)

    # 生成支付二维码（模拟）
    qr_code = generate_qr_code(f"mockpay://{platform_order_no}")

    return {
        "platform_order_no": platform_order_no,
        "pay_url": f"http://localhost:8000/pay/mock/{platform_order_no}",
        "qr_code": qr_code,
        "amount": float(order.amount),
        "status": 0
    }


@router.post("/notify", summary="支付回调（模拟）")
async def payment_notify(
    platform_order_no: str = Query(..., description="平台订单号"),
    db: Session = Depends(get_db)
):
    """
    模拟支付回调

    :param platform_order_no: 平台订单号
    :param db: 数据库会话
    :return: 处理结果
    """
    # 查询订单
    order = db.query(Order).filter(Order.platform_order_no == platform_order_no).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="订单不存在"
        )

    # 幂等处理：如果已支付，直接返回成功
    if order.status == 1:
        return {"status": "success", "message": "订单已支付"}

    # 处理支付成功
    from ..services.payment_service import process_payment_success
    success = process_payment_success(db, order)

    if success:
        # 异步发送回调通知
        from ..workers.callback_worker import process_order_callback
        import asyncio
        asyncio.create_task(process_order_callback(db, order))

        return {"status": "success", "message": "支付处理成功"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="支付处理失败"
        )


@router.get("/mock/{platform_order_no}", summary="模拟支付页面")
async def mock_pay_page(
    platform_order_no: str,
    db: Session = Depends(get_db)
):
    """
    模拟支付页面（用于测试）

    :param platform_order_no: 平台订单号
    :param db: 数据库会话
    :return: HTML页面
    """
    order = db.query(Order).filter(Order.platform_order_no == platform_order_no).first()
    if not order:
        return {"error": "订单不存在"}

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>模拟支付</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 600px;
                margin: 50px auto;
                padding: 20px;
                border: 1px solid #ddd;
                border-radius: 10px;
            }}
            h1 {{ color: #333; }}
            .info {{ margin: 20px 0; }}
            .info label {{ font-weight: bold; display: inline-block; width: 120px; }}
            .btn {{
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
                font-size: 16px;
            }}
            .btn:hover {{ background-color: #45a049; }}
        </style>
    </head>
    <body>
        <h1>💰 模拟支付</h1>
        <div class="info">
            <div><label>订单号:</label> {order.platform_order_no}</div>
            <div><label>金额:</label> ¥{order.amount}</div>
            <div><label>状态:</label> {'✅ 已支付' if order.status == 1 else '⏳ 待支付'}</div>
        </div>
        <form action="/api/pay/notify?platform_order_no={platform_order_no}" method="post">
            <button type="submit" class="btn" {'disabled' if order.status == 1 else ''}>
                {'✅ 订单已完成' if order.status == 1 else '💳 立即支付（模拟）'}
            </button>
        </form>
    </body>
    </html>
    """
    return html


@router.get("/", response_model=dict, summary="查询订单列表")
async def get_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[int] = Query(None),
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db)
):
    """查询当前开发者的订单列表"""
    query = db.query(Order).filter(Order.developer_id == current_developer.id)

    if status is not None:
        query = query.filter(Order.status == status)

    total = query.count()
    orders = query.order_by(Order.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [{
            "platform_order_no": order.platform_order_no,
            "developer_order_no": order.developer_order_no,
            "amount": float(order.amount),
            "platform_fee": float(order.platform_fee),
            "developer_income": float(order.developer_income),
            "status": order.status,
            "pay_time": order.pay_time.isoformat() if order.pay_time else None,
            "created_at": order.created_at.isoformat()
        } for order in orders]
    }


@router.get("/success", response_model=dict, summary="查询成功订单")
async def get_success_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_developer: Developer = Depends(get_current_developer),
    db: Session = Depends(get_db)
):
    """查询当前开发者的成功订单"""
    query = db.query(Order).filter(
        Order.developer_id == current_developer.id,
        Order.status == 1
    )

    total = query.count()
    orders = query.order_by(Order.pay_time.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "data": [{
            "platform_order_no": order.platform_order_no,
            "developer_order_no": order.developer_order_no,
            "amount": float(order.amount),
            "platform_fee": float(order.platform_fee),
            "developer_income": float(order.developer_income),
            "pay_time": order.pay_time.isoformat(),
            "created_at": order.created_at.isoformat()
        } for order in orders]
    }
