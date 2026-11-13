import json

from redis.asyncio import Redis
from redis.asyncio.retry import Retry
from redis.backoff import ExponentialBackoff

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class RedisCacheClient:
    """Клиент для работы с Redis."""

    def __init__(self) -> None:
        retry = Retry(ExponentialBackoff(), 3)
        self._redis: Redis = Redis.from_url(
            f"redis://:{settings.redis.password}@{settings.redis.host}:{settings.redis.port}/{settings.redis.cache_db}",
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


class RedisChatClient:
    """Клиент для работы с историей чата в Redis."""

    def __init__(self) -> None:
        self._redis: Redis = Redis.from_url(
            f"redis://:{settings.redis.password}@{settings.redis.host}:{settings.redis.port}/{settings.redis.chat_db}",
            decode_responses=True,
        )
        logger.info("Redis чат-клиент инициализирован")

    async def add_message(self, payload: dict, max_history: int = 50) -> None:
        """Добавить сообщение в историю (последние max_history)."""
        await self._redis.lpush("chat:history", json.dumps(payload))
        await self._redis.ltrim("chat:history", 0, max_history - 1)

    async def get_history(self, max_history: int = 50) -> list[dict]:
        """Получить историю сообщений."""
        raw = await self._redis.lrange("chat:history", 0, max_history - 1)
        return [json.loads(item) for item in reversed(raw)]

    async def close(self) -> None:
        await self._redis.close()
