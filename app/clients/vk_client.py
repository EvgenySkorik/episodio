from typing import Any

import httpx

from app.core.config import AppSettings
from app.core.exceptions.exceptions import NotificationError
from app.core.logging import get_logger
from app.infrastructure.http_client import HTTPClient

logger = get_logger(__name__)


class VkClient:
    """Клиент для работы с VK API."""
    def __init__(self, http_client: HTTPClient, settings: AppSettings) -> None:
        self._settings = settings
        self._http = http_client
        self._token = self._settings.vk.token
        self._api_url = self._settings.vk.api_url
        self._api_version = self._settings.vk.api_version

    async def _call(self, method: str, params: dict | None = None) -> dict[str, Any]:
        """Выполняет запрос к VK API."""
        if params is None:
            params = {}
        params["access_token"] = self._token
        params["v"] = self._api_version

        try:
            response = await self._http.request(
                "GET",
                f"{self._api_url}{method}",
                params=params
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()

            if "error" in data:
                error_msg = data["error"].get("error_msg", "Unknown VK error")
                logger.error(f"VK API error: {error_msg}")
                raise NotificationError(f"VK API error: {error_msg}")
            return data

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error from VK: {e.response.status_code}")
            raise NotificationError(f"VK API unavailable: {e.response.status_code}") from e
        except Exception as e:
            logger.error(f"Unexpected error calling VK API: {e}")
            raise NotificationError("Failed to call VK API") from e

    async def get_long_poll_server(self, group_id: int) -> dict:
        """Получает данные Long Poll сервера для группы."""
        return await self._call("groups.getLongPollServer", {"group_id": group_id})

    async def send_message(self, user_id: int, message: str) -> dict:
        """Отправляет сообщение пользователю через VK API."""
        return await self._call(
            "messages.send",
            {
                "user_id": user_id,
                "message": message,
                "random_id": 0,
            }
        )
