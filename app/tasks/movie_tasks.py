import asyncio
from typing import Any

from app.core.logging import get_logger
from app.factories import create_container
from app.infrastructure.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="check_series_updates",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def check_series_updates(self: Any) -> None:
    """Celery задача для проверки обновлений эпизодов сериалов."""
    logger.info("Запуск задачи check_series_updates")

    async def _run():
        async with create_container() as c:
            await c.movie_service.check_series_updates()

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_run())
        logger.info("Задача check_series_updates завершена успешно")
    except Exception as exc: # noqa: BLE001
        logger.error(f"Ошибка в задаче check_series_updates: {exc}")
        raise self.retry(exc=exc)