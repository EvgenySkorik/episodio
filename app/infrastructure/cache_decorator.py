import json
from collections.abc import Callable
from functools import wraps

from redis.exceptions import ConnectionError, TimeoutError

from app.core.logging import get_logger

logger = get_logger(__name__)


def cached(ttl: int = 60, key_prefix: str = ""):
    """Декоратор для кеширования результата async-функции."""

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            cached_client = self._redis

            key_parts = [key_prefix or func.__name__]
            key_parts.extend(str(a).lower() for a in args[1:])
            key_parts.extend(f"{k}={str(v).lower()}" for k, v in sorted(kwargs.items()))
            cache_key = ":".join(key_parts)

            try:
                cached_value = await cached_client.get(cache_key)
                if cached_value:
                    logger.debug(f"Кеш-хит: {cache_key}")
                    return json.loads(cached_value)
            except (ConnectionError, TimeoutError, json.JSONDecodeError) as e:
                logger.warning(f"Ошибка чтения из кеша: {e}")

            result = await func(self, *args, **kwargs)

            if result is None or result == []:
                return result

            try:
                if isinstance(result, list):
                    json_result = [r.model_dump() for r in result]
                elif hasattr(result, "model_dump"):
                    json_result = result.model_dump()
                else:
                    json_result = result
                await cached_client.setex(cache_key, ttl, json.dumps(json_result, default=str))
                logger.debug(f"Кеш сохранён: {cache_key} (TTL={ttl}с)")
            except (ConnectionError, TimeoutError) as e:
                logger.warning(f"Ошибка записи в кеш: {e}")

            return result

        return wrapper

    return decorator
