from contextlib import asynccontextmanager
from dataclasses import dataclass
from typing import AsyncIterator

from app.clients.kp_client import KinopoiskClient
from app.clients.vk_client import VkClient
from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import AsyncSessionLocal
from app.infrastructure.http_client import HTTPClient
from app.repositories.movie_rep import MovieRepository
from app.repositories.user_rep import UserRepository
from app.services.movie import MovieService
from app.services.notification import NotificationService
from app.services.user import UserService


logger = get_logger(__name__)


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
        Автоматически закрывает ресурсы.
        """
    session = AsyncSessionLocal()
    http_client = HTTPClient()

    try:
        movie_repository = MovieRepository(session=session)
        user_repository = UserRepository(session=session)

        kino_client = KinopoiskClient(settings=settings, http_client=http_client)
        vk_client = VkClient(http_client=http_client, settings=settings)

        notification_service = NotificationService(
            movie_repository=movie_repository,
            user_repository=user_repository,
            vk_client=vk_client,
        )

        movie_service = MovieService(
            repository=movie_repository,
            kinopoisk_client=kino_client,
            notification_service=notification_service,
        )
        user_service = UserService(
            user_repo=user_repository,
            movie_repo=movie_repository,
        )

        logger.info("Создали контейнер для работы с сервисами")
        yield Container(
            movie_service=movie_service,
            user_service=user_service,
            notification_service=notification_service,
        )

    finally:
        await session.close()
        await http_client.close()