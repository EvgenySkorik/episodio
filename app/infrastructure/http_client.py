import httpx

from app.core.logging import get_logger

logger = get_logger(__name__)


class HTTPClient:
    """Асинхронный HTTP-клиент с переиспользованием соединений."""
    def __init__(self, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
        )

    async def request(
            self,
            method: str,
            url: str,
            headers: dict | None = None,
            params: dict | None = None,
            json: dict | None = None,
    ) -> httpx.Response:
        """Выполняет HTTP-запрос."""
        response = await self._client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
        )
        logger.debug(f"Запрос к API: {method} {url} — статус {response.status_code}")
        return response

    async def close(self) -> None:
        """Закрывает HTTP-клиент и освобождает ресурсы."""
        await self._client.aclose()
        logger.debug("HTTP-клиент закрыт")
