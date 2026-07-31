import hashlib
import hmac
from datetime import datetime, timezone, timedelta

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
    sign = params.get("sign")
    if not sign:
        logger.warning("Ошибка получения 'sign' от VK Mini App.")
        raise SecurityError("Invalid VK sign")

    params.pop("sign")

    sorted_params = sorted(params.items())
    check_string = "&".join(f"{k}={v}" for k, v in sorted_params)

    expected = hmac.new(
        secret.encode(),
        check_string.encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(sign, expected):
        raise SecurityError("secrets not valid")

    vk_user_id = params.get("vk_user_id")
    if not vk_user_id:
        raise SecurityError("Missing vk_user_id")

    return int(vk_user_id)


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


