from typing import Annotated

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.paginations import PaginationParams
from app.clients.kp_client import KinopoiskClient
from app.clients.vk_client import VkClient
from app.core.config import settings
from app.core.exceptions.exceptions import SecurityError
from app.db.database import get_db
from app.infrastructure.hawk_client import HawkClient
from app.infrastructure.http_client import HTTPClient
from app.infrastructure.redis_client import RedisCacheClient
from app.infrastructure.security import get_current_user_impl, verify_vk_sign
from app.repositories.movie_rep import MovieRepository
from app.repositories.user_rep import UserRepository
from app.services.movie import MovieService
from app.services.notification import NotificationService
from app.services.user import UserService

# ---------------------------------------------------------------------------
# --------------------------VK MiniApp проверка------------------------------
# ---------------------------------------------------------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/vk")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> int:
    return get_current_user_impl(token)



async def get_vk_user_id(request: Request) -> int:
    try:
        return verify_vk_sign(dict(request.query_params), settings.vk.secret_key)
    except SecurityError as e:
        raise HTTPException(status_code=403, detail=str(e))

# ---------------------------------------------------------------------------
# -----------------------------Репозитории-----------------------------------
# ---------------------------------------------------------------------------

async def get_movie_repository(
        session: Annotated[AsyncSession, Depends(get_db)]
) -> MovieRepository:
    return MovieRepository(session=session)


async def get_user_repository(
        session: Annotated[AsyncSession, Depends(get_db)]
) -> UserRepository:
    return UserRepository(session=session)


# ---------------------------------------------------------------------------
# -----------------------------Клиенты---------------------------------------
# ---------------------------------------------------------------------------
async def get_hawk_client(request: Request) -> HawkClient:
    """Возвращает HawkClient из состояния приложения (синглтон)."""
    return request.app.state.hawk_client  # type: ignore[no-any-return]


async def get_http_client(request: Request) -> HTTPClient:
    """Возвращает HTTPClient из состояния приложения (синглтон).

    HTTPClient создаётся ОДИН раз при старте приложения и живёт
    до его остановки. Переиспользует connection pool.
    """
    return request.app.state.http_client # type: ignore[no-any-return]


async def get_kinopoisk_client(
        http_client: Annotated[HTTPClient, Depends(get_http_client)]
) -> KinopoiskClient:
    return KinopoiskClient(settings=settings, http_client=http_client)

async def get_redis_client(request: Request) -> RedisCacheClient:
    """Возвращает Redis-клиент из состояния приложения (синглтон)."""
    return request.app.state.redis_client # type: ignore[no-any-return]


# ---------------------------------------------------------------------------
# -----------------------------Сервисы---------------------------------------
# ---------------------------------------------------------------------------

async def get_notification_service(
        movie_repo: Annotated[MovieRepository, Depends(get_movie_repository)],
        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
        http_client: Annotated[HTTPClient, Depends(get_http_client)],
        hawk_client: Annotated[HawkClient, Depends(get_hawk_client)],
) -> NotificationService:
    vk_client = VkClient(http_client, settings=settings)
    return NotificationService(
        movie_repository=movie_repo,
        user_repository=user_repo,
        vk_client=vk_client,
        hawk=hawk_client,
    )


async def get_movie_service(
        movie_repo: Annotated[MovieRepository, Depends(get_movie_repository)],
        kino_client: Annotated[KinopoiskClient, Depends(get_kinopoisk_client)],
        notify_service: Annotated[NotificationService, Depends(get_notification_service)],
        hawk_client: Annotated[HawkClient, Depends(get_hawk_client)],
        redis_client: Annotated[RedisCacheClient, Depends(get_redis_client)],
) -> MovieService:
    return MovieService(
        repository=movie_repo,
        kinopoisk_client=kino_client,
        notification_service=notify_service,
        hawk=hawk_client,
        cached_client=redis_client,
    )


async def get_user_service(
        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
        movie_repo: Annotated[MovieRepository, Depends(get_movie_repository)],
        hawk_client: Annotated[HawkClient, Depends(get_hawk_client)],
) -> UserService:
    return UserService(user_repo=user_repo, movie_repo=movie_repo, hawk=hawk_client,)


# ----------------------------------------------------------------------------
# -------------------Типизированные аннотации для роутеров--------------------
# ----------------------------------------------------------------------------

type ServiceMovieDep = Annotated[MovieService, Depends(get_movie_service)]
type ServiceUserDep = Annotated[UserService, Depends(get_user_service)]
type VkUserIdDep = Annotated[int, Depends(get_vk_user_id)]
type CurrentUserVkIdDep = Annotated[int, Depends(get_current_user)]

type PaginationDep = Annotated[PaginationParams, Depends()]

