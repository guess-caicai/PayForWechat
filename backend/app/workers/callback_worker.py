import httpx
import asyncio
from typing import Dict, Any
from sqlalchemy.orm import Session
from ..models.models import Order
import logging

logger = logging.getLogger(__name__)


async def send_callback_async(notify_url: str, data: Dict[str, Any], max_retries: int = 5) -> bool:
    """
    异步发送回调通知

    :param notify_url: 回调URL
    :param data: 回调数据
    :param max_retries: 最大重试次数
    :return: 是否成功
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        for attempt in range(max_retries):
            try:
                response = await client.post(notify_url, json=data)
                if response.status_code == 200:
                    logger.info(f"Callback success: {notify_url}")
                    return True
                else:
                    logger.warning(f"Callback failed (attempt {attempt + 1}/{max_retries}): status={response.status_code}")
            except Exception as e:
                logger.error(f"Callback error (attempt {attempt + 1}/{max_retries}): {e}")

            # 指数退避重试
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)

    logger.error(f"Callback failed after {max_retries} attempts: {notify_url}")
    return False


def send_callback_sync(notify_url: str, data: Dict[str, Any], max_retries: int = 5) -> bool:
    """
    同步发送回调通知

    :param notify_url: 回调URL
    :param data: 回调数据
    :param max_retries: 最大重试次数
    :return: 是否成功
    """
    for attempt in range(max_retries):
        try:
            response = httpx.post(notify_url, json=data, timeout=10.0)
            if response.status_code == 200:
                logger.info(f"Callback success: {notify_url}")
                return True
            else:
                logger.warning(f"Callback failed (attempt {attempt + 1}/{max_retries}): status={response.status_code}")
        except Exception as e:
            logger.error(f"Callback error (attempt {attempt + 1}/{max_retries}): {e}")

        # 指数退避重试
        if attempt < max_retries - 1:
            import time
            time.sleep(2 ** attempt)

    logger.error(f"Callback failed after {max_retries} attempts: {notify_url}")
    return False


async def process_order_callback(db: Session, order: Order) -> bool:
    """
    处理订单回调

    :param db: 数据库会话
    :param order: 订单对象
    :return: 是否成功
    """
    callback_data = {
        "platform_order_no": order.platform_order_no,
        "developer_order_no": order.developer_order_no,
        "amount": float(order.amount),
        "platform_fee": float(order.platform_fee),
        "developer_income": float(order.developer_income),
        "status": order.status,
        "pay_time": order.pay_time.isoformat() if order.pay_time else None
    }

    # 异步发送回调
    success = await send_callback_async(order.notify_url, callback_data)

    return success
