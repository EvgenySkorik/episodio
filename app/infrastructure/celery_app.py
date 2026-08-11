from celery import Celery
from celery.schedules import crontab

from app.core.config import settings
import app.tasks.movie_tasks
import app.tasks.notification_tasks

celery_app = Celery(
    "kino_movie_api",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
)

celery_app.autodiscover_tasks(['app.tasks.movie_tasks', 'app.tasks.notification_tasks'])

celery_app.conf.update(
    task_serializer=settings.celery.task_serializer,
    result_serializer=settings.celery.result_serializer,
    accept_content=settings.celery.accept_content,
    timezone=settings.celery.timezone,
    enable_utc=settings.celery.enable_utc,
)


celery_app.conf.beat_schedule = {
    'check-new-series': {
        'task': 'app.tasks.movie_tasks.check_series_updates',
        'schedule': crontab(
            hour=settings.celery.check_series_hour,
            minute=settings.celery.check_series_minute,
            day_of_week=f'*/{settings.celery.check_series_day}'),
    },

    # 'send-test-notification': {
    #     'task': 'send_notification_series',
    #     'schedule': 60.0,  # Каждые 60 секунд!
    #     'args': (733882553,),      # Твой тестовый user_id = 10
    # },
}

