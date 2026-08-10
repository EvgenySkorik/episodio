import asyncio
import atexit
import signal
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from app.clients.kp_client import KinopoiskClient
from app.clients.vk_client import VkClient
from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import AsyncSessionLocal
from app.infrastructure.hawk_client import HawkClient
from app.infrastructure.http_client import HTTPClient
from app.repositories.movie_rep import MovieRepository
from app.repositories.user_rep import UserRepository
from app.services.movie import MovieService
from app.services.notification import NotificationService
from app.services.user import UserService

logger = get_logger(__name__)


_http_client: HTTPClient | None = None
_hawk_client: HawkClient | None = None

def get_http_client() -> HTTPClient:
    global _http_client
    if _http_client is None:
        _http_client = HTTPClient()
    return _http_client

def get_hawk_client() -> HawkClient:
    global _hawk_client
    if _hawk_client is None:
        _hawk_client = HawkClient()
    return _hawk_client

def _cleanup():
    """Закрываем ресурсы при остановке процесса."""
    loop = asyncio.new_event_loop()
    try:
        if _http_client is not None:
            loop.run_until_complete(_http_client.close())
    finally:
        loop.close()

atexit.register(_cleanup)
signal.signal(signal.SIGTERM, lambda *args: _cleanup())


@dataclass(slots=True)
class Container:
    """Контейнер всех сервисов приложения."""
    movie_service: MovieService
    user_service: UserService
    notification_service: NotificationService


@asynccontextmanager
async def create_container() -> AsyncIterator[Container]:
    """Создаёт контейнер со всеми сервисами.
        Одна сессия и один HTTPClient на все сервисы.
        """
    session = AsyncSessionLocal()
    http_client = get_http_client()
    hawk_client = get_hawk_client()

    try:
        movie_repository = MovieRepository(session=session)
        user_repository = UserRepository(session=session)

        kino_client = KinopoiskClient(settings=settings, http_client=http_client)
        vk_client = VkClient(http_client=http_client, settings=settings)

        notification_service = NotificationService(
            movie_repository=movie_repository,
            user_repository=user_repository,
            vk_client=vk_client,
            hawk=hawk_client,
        )

        movie_service = MovieService(
            repository=movie_repository,
            kinopoisk_client=kino_client,
            notification_service=notification_service,
            hawk=hawk_client,
        )
        user_service = UserService(
            user_repo=user_repository,
            movie_repo=movie_repository,
            hawk=hawk_client,
        )

        logger.info("Создан контейнер для работы с сервисами")
        yield Container(
            movie_service=movie_service,
            user_service=user_service,
            notification_service=notification_service,
        )

    finally:
        await session.close()