import base64
import hashlib
import hmac
import os
from typing import Any

import aiofiles
from collections import OrderedDict
from datetime import datetime, timezone, timedelta
from urllib.parse import urlencode

import jwt

from app.core.config import settings
from app.core.exceptions.exceptions import TokenExpiredError, InvalidTokenError, SecurityError, LogFileNotFoundError, \
    LogFileReadError
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

    sorted_params = OrderedDict(sorted(vk_params.items()))

    query_string = urlencode(sorted_params, doseq=True)

    hmac_hash = hmac.new(
        secret.encode(),
        query_string.encode(),
        hashlib.sha256
    ).digest()

    expected_sign = base64.urlsafe_b64encode(hmac_hash).decode().rstrip('=')

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
    payload: dict[str, Any] = jwt.decode(
        token,
        settings.secret_jwt_key,
        algorithms=["HS256"],
    )
    vk_id = payload.get("vk_id")
    if vk_id is None:
        raise InvalidTokenError("Missing vk_id in token")
    return int(vk_id)

def get_current_user_impl(token: str) -> int:
    """Проверяет JWT и возвращает vk_id."""
    try:
        return decode_jwt(token)
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()

def verify_admin_password(password: str) -> bool:
    """Проверка админского пароля"""
    return password == settings.logs_password


async def read_log_file() -> str:
    """Асинхронно читает файл логов"""
    log_path = settings.log_file_path

    if not log_path.exists():
        raise LogFileNotFoundError(f"Файл логов не найден: {log_path}")

    try:
        async with aiofiles.open(log_path, 'r', encoding='utf-8') as f:
            return await f.read()

    except PermissionError as e:
        logger.error(f"Нет прав на чтение логов: {e}")
        raise LogFileReadError(f"Нет прав на чтение файла логов: {log_path}")
    except Exception as e:
        logger.error(f"Ошибка чтения логов: {e}")
        raise LogFileReadError(f"Ошибка чтения файла логов: {str(e)}")


async def read_log_lines(n: int = 50) -> str:
    """Читает последние N строк логов"""
    try:
        logs = await read_log_file()
        lines = logs.split('\n')
        return '\n'.join(lines[-n:])
    except LogFileNotFoundError:
        raise
    except Exception as e:
        logger.error(f"Ошибка чтения логов: {e}")
        raise LogFileReadError(f"Ошибка при чтении последних {n} строк: {str(e)}")
