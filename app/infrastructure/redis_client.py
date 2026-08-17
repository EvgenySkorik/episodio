import json
from functools import wraps
from typing import Callable

from redis.asyncio import Redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff


from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisCacheClient:
    """Клиент для работы с Redis."""
    def __init__(self):
        retry = Retry(ExponentialBackoff(), 3)
        self._redis = Redis.from_url(
            f"redis://:{settings.redis_password}@redis:6379/1",
            decode_responses=True,
            retry=retry,
            retry_on_error=[ConnectionError, TimeoutError],
        )
        logger.info("Redis кеш-клиент инициализирован")

    @property
    def client(self) -> Redis:
        """Возвращает инстанс Redis."""
        return self._redis

    async def get(self, key: str):
        """Получить значение из кеша."""
        return await self._redis.get(key)

    async def setex(self, key: str, ttl: int, value: str):
        """Сохранить значение с TTL."""
        await self._redis.setex(key, ttl, value)

    async def close(self) -> None:
        if hasattr(self, "_redis"):
            await self._redis.close()
            del self._redis
            logger.info("Redis кеш-клиент закрыт")





