import base64
import json
import os
import secrets
import time
from dataclasses import dataclass
from typing import Any

import httpx
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography import x509

from ..core.settings import settings


@dataclass
class WechatNativeResult:
    code_url: str
    prepay_id: str | None = None
    raw: dict[str, Any] | None = None


@dataclass
class WechatTransferResult:
    transfer_no: str | None
    status: str | None
    package_info: str | None
    raw: dict[str, Any] | None = None


class WechatPayService:
    def __init__(self):
        self.enabled = settings.WECHAT_ENABLED
        self.base_url = settings.WECHAT_BASE_URL.rstrip("/")
        self.mch_id = settings.WECHAT_MCH_ID
        self.app_id = settings.WECHAT_APP_ID
        self.serial_no = settings.WECHAT_MCH_SERIAL_NO
        self.api_v3_key = settings.WECHAT_API_V3_KEY
        self._private_key = self._load_private_key()
        self._platform_public_key = self._load_platform_public_key()

    def _load_private_key(self):
        pem = settings.WECHAT_PRIVATE_KEY_PEM
        if not pem and settings.WECHAT_PRIVATE_KEY_PATH:
            if os.path.exists(settings.WECHAT_PRIVATE_KEY_PATH):
                with open(settings.WECHAT_PRIVATE_KEY_PATH, "rb") as f:
                    pem = f.read().decode("utf-8")
        if not pem:
            return None
        return serialization.load_pem_private_key(pem.encode("utf-8"), password=None)

    def _load_platform_public_key(self):
        if not settings.WECHAT_PLATFORM_CERT_PATH or not os.path.exists(settings.WECHAT_PLATFORM_CERT_PATH):
            return None
        with open(settings.WECHAT_PLATFORM_CERT_PATH, "rb") as f:
            cert_data = f.read()
        if b"BEGIN CERTIFICATE" in cert_data:
            cert = x509.load_pem_x509_certificate(cert_data)
            return cert.public_key()
        return serialization.load_pem_public_key(cert_data)

    def _build_authorization(self, method: str, path: str, body: str) -> str:
        if not self._private_key:
            raise ValueError("微信商户私钥未配置")
        timestamp = str(int(time.time()))
        nonce = secrets.token_hex(16)
        message = f"{method}\n{path}\n{timestamp}\n{nonce}\n{body}\n"
        signature = self._private_key.sign(
            message.encode("utf-8"),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        sign_b64 = base64.b64encode(signature).decode("utf-8")
        return (
            f'WECHATPAY2-SHA256-RSA2048 mchid="{self.mch_id}",'
            f'nonce_str="{nonce}",timestamp="{timestamp}",serial_no="{self.serial_no}",'
            f'signature="{sign_b64}"'
        )

    def _request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.enabled:
            raise ValueError("微信真实支付未启用")
        if not self.mch_id or not self.app_id or not self.serial_no or not self.api_v3_key:
            raise ValueError("微信商户关键配置缺失")

        body = json.dumps(payload or {}, ensure_ascii=False) if payload is not None else ""
        auth = self._build_authorization(method, path, body)
        headers = {
            "Authorization": auth,
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "PayForWechat/1.0",
        }
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=15.0) as client:
            response = client.request(method, url, headers=headers, content=body if body else None)
        if response.status_code >= 400:
            raise ValueError(f"微信接口错误 {response.status_code}: {response.text}")
        if not response.text:
            return {}
        return response.json()

    def create_native_order(self, out_trade_no: str, amount_fen: int, description: str, notify_url: str) -> WechatNativeResult:
        payload = {
            "mchid": self.mch_id,
            "appid": self.app_id,
            "description": description,
            "out_trade_no": out_trade_no,
            "notify_url": notify_url,
            "amount": {
                "total": amount_fen,
                "currency": "CNY",
            },
        }
        data = self._request("POST", "/v3/pay/transactions/native", payload)
        return WechatNativeResult(code_url=data.get("code_url", ""), prepay_id=data.get("prepay_id"), raw=data)

    def create_transfer_bill(self, out_bill_no: str, openid: str, amount_fen: int, remark: str, notify_url: str) -> WechatTransferResult:
        payload = {
            "appid": self.app_id,
            "out_bill_no": out_bill_no,
            "transfer_scene_id": "1000",
            "openid": openid,
            "transfer_amount": amount_fen,
            "transfer_remark": remark[:32],
            "notify_url": notify_url,
            "user_recv_perception": "开发者提现到账",
        }
        data = self._request("POST", "/v3/fund-app/mch-transfer/transfer-bills", payload)
        return WechatTransferResult(
            transfer_no=data.get("transfer_bill_no") or data.get("out_bill_no"),
            status=data.get("state"),
            package_info=data.get("package_info"),
            raw=data,
        )

    def decrypt_callback_resource(self, body: dict[str, Any]) -> dict[str, Any]:
        resource = body.get("resource", {})
        nonce = resource.get("nonce")
        associated_data = resource.get("associated_data", "")
        ciphertext = resource.get("ciphertext")
        if not nonce or not ciphertext:
            raise ValueError("回调报文缺少加密资源")
        aesgcm = AESGCM(self.api_v3_key.encode("utf-8"))
        plain = aesgcm.decrypt(
            nonce.encode("utf-8"),
            base64.b64decode(ciphertext),
            associated_data.encode("utf-8"),
        )
        return json.loads(plain.decode("utf-8"))

    def verify_callback_signature(self, headers: dict[str, str], raw_body: str) -> bool:
        if not settings.WECHAT_CALLBACK_STRICT:
            return True
        if not self._platform_public_key:
            raise ValueError("未配置微信平台公钥")
        timestamp = headers.get("Wechatpay-Timestamp") or headers.get("wechatpay-timestamp")
        nonce = headers.get("Wechatpay-Nonce") or headers.get("wechatpay-nonce")
        signature = headers.get("Wechatpay-Signature") or headers.get("wechatpay-signature")
        if not timestamp or not nonce or not signature:
            return False
        message = f"{timestamp}\n{nonce}\n{raw_body}\n".encode("utf-8")
        try:
            self._platform_public_key.verify(
                base64.b64decode(signature),
                message,
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False


wechat_pay_service = WechatPayService()
