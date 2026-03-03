import hashlib
import hmac
from typing import Dict, Optional
import json


def generate_sign(params: Dict, secret_key: str) -> str:
    """
    生成签名

    算法:
    1. 过滤掉 sign 和空值
    2. 按key字典序排序
    3. 拼接成 key1=value1&key2=value2 格式
    4. 末尾追加 &key=secret_key
    5. MD5加密

    :param params: 待签名参数
    :param secret_key: 密钥
    :return: 签名字符串
    """
    # 过滤掉 sign 和空值
    filtered_params = {
        k: v for k, v in params.items()
        if k != 'sign' and v is not None and v != ''
    }

    # 按key字典序排序
    sorted_params = sorted(filtered_params.items())

    # 拼接
    param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])

    # 追加密钥
    string_to_sign = f"{param_str}&key={secret_key}"

    # MD5签名
    sign = hashlib.md5(string_to_sign.encode('utf-8')).hexdigest().upper()

    return sign


def verify_sign(params: Dict, secret_key: str, expected_sign: str) -> bool:
    """
    验证签名

    :param params: 参数字典
    :param secret_key: 密钥
    :param expected_sign: 期望的签名
    :return: 验证是否通过
    """
    actual_sign = generate_sign(params, secret_key)
    return actual_sign == expected_sign.upper()


def generate_hmac_sign(params: Dict, secret_key: str) -> str:
    """
    使用HMAC-SHA256生成签名（更安全）

    :param params: 待签名参数
    :param secret_key: 密钥
    :return: 签名字符串
    """
    # 过滤和排序
    filtered_params = {
        k: v for k, v in params.items()
        if k != 'sign' and v is not None and v != ''
    }

    sorted_params = sorted(filtered_params.items())
    param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])

    # HMAC-SHA256签名
    signature = hmac.new(
        secret_key.encode('utf-8'),
        param_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest().upper()

    return signature


def verify_hmac_sign(params: Dict, secret_key: str, expected_sign: str) -> bool:
    """
    验证HMAC签名

    :param params: 参数字典
    :param secret_key: 密钥
    :param expected_sign: 期望的签名
    :return: 验证是否通过
    """
    actual_sign = generate_hmac_sign(params, secret_key)
    return actual_sign == expected_sign.upper()
