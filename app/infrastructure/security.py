import base64
import hashlib
import hmac
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import jwt

from app.core.config import settings
from app.core.exceptions.exceptions import TokenExpiredError, InvalidTokenError, SecurityError
from app.core.logging import get_logger

logger = get_logger(__name__)


def verify_vk_sign(params: dict, secret: str) -> int:
    """
    Проверяет подпись VK Mini App.
    Args:
        params: все query-параметры от VK.
        secret: секретный ключ приложения VK.

    Returns:
        vk_user_id: int - если подпись верна
    """
    vk_params = {k: v for k, v in params.items() if k.startswith("vk_")}

    # Сортируем по ключам
    sorted_params = OrderedDict(sorted(vk_params.items()))

    # Формируем строку запроса
    query_string = urlencode(sorted_params, doseq=True)

    # Вычисляем HMAC-SHA256
    hmac_hash = hmac.new(
        secret.encode(),
        query_string.encode(),
        hashlib.sha256
    ).digest()

    # Base64 URL-safe без padding
    expected_sign = base64.urlsafe_b64encode(hmac_hash).decode().rstrip('=')

    # Сравниваем
    sign = params.get("sign")
    if not sign:
        raise SecurityError("Missing sign")

    if not hmac.compare_digest(sign, expected_sign):
        raise SecurityError("Invalid VK sign")

    return int(params["vk_user_id"])


def create_jwt(vk_id: int) -> str:
    """Создаёт JWT токен для пользователя VK."""
    payload = {
        "vk_id": vk_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.secret_jwt_key, algorithm="HS256")


def decode_jwt(token: str) -> int:
    """Проверяет JWT и возвращает vk_id."""
    payload = jwt.decode(
        token,
        settings.secret_jwt_key,
        algorithms=["HS256"],
    )
    return payload["vk_id"]

def get_current_user_impl(token: str) -> int:
    """Проверяет JWT и возвращает vk_id."""
    try:
        return decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()


