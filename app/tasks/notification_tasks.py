import asyncio
from typing import Any

from app.core.logging import get_logger
from app.factories import create_container
from app.infrastructure.celery_app import celery_app

logger = get_logger(__name__)


@celery_app.task(
    name="send_notification_series",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
)
def send_notification_series(self: Any, user_id: int) -> None:
    """Celery задача для отправки уведомлений о новых сериях."""
    logger.info("Запуск задачи send_notification_series")
    async def _run():
        async with create_container() as c:
            await c.notification_service.send_notification(
                user_id=user_id,
                name="Тестовое уведомление",
                new_episodes=1,
            )

    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(_run())
        logger.info("Задача send_notification_series завершена успешно")
    except Exception as exc:
        logger.error(f"Ошибка: {exc}", exc_info=True)
        raise self.retry(exc=exc)