import asyncio

import httpx
from hawk_python_sdk import Hawk

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class HawkEvent(Exception):
    """Event для Hawk"""


class HawkClient:
    """Клиент для работы с Hawk."""
    def __init__(self, token: str | None = None) -> None:
        self._token = token or settings.hawk_secret_token
        self._hawk = Hawk(self._token)
        logger.info("HawkClient инициализирован")

    async def send_event(self, message: str, level: str = "info", extra: dict | None = None) -> None:
        """Отправляет событие в Hawk."""
        try:
            event = HawkEvent(message)
            context = {"level": level, "extra": extra or {}}
            await asyncio.to_thread(self._hawk.send, event, context)
            logger.debug(f"Событие отправлено в Hawk: {message}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при отправке в Hawk: {e.response.status_code}")
        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при отправке в Hawk: {e}")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Ошибка отправки в Hawk: {e}")

    async def send_error(self, error: Exception, context: dict | None = None) -> None:
        """Отправляет ошибку в Hawk."""
        try:
            await asyncio.to_thread(self._hawk.send, error, context or {})
            logger.debug(f"Ошибка отправлена в Hawk: {error}")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP ошибка при отправке в Hawk: {e.response.status_code}")
        except httpx.TimeoutException as e:
            logger.error(f"Таймаут при отправке в Hawk: {e}")
        except Exception as e:  # noqa: BLE001
            logger.error(f"Ошибка отправки в Hawk: {e}")