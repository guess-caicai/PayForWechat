from typing import Any, Dict

from .callback_worker import send_callback_async


async def process_order_callback(notify_url: str, callback_data: Dict[str, Any]) -> bool:
    return await send_callback_async(notify_url, callback_data)
