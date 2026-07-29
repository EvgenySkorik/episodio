import hashlib
import hmac
from typing import Annotated, TypeAlias

from fastapi import Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.clients.kp_client import KinopoiskClient
from app.clients.vk_client import VkClient
from app.core.config import settings
from app.db.database import get_db
from app.infrastructure.http_client import HTTPClient
from app.repositories.movie_rep import MovieRepository
from app.repositories.user_rep import UserRepository

from app.services.movie import MovieService
from app.services.notification import NotificationService

from app.services.user import UserService


# ---------------------------------------------------------------------------
# --------------------------VK MiniApp проверка------------------------------
# ---------------------------------------------------------------------------

async def get_vk_user_id(request: Request) -> int:
    vk_id_query = request.query_params.get("vk_id")
    if vk_id_query:
        return int(vk_id_query)

    params = dict(request.query_params)
    sign = params.pop("sign", None)

    if sign:
        secret = settings.vk.token
        sorted_params = sorted(params.items())
        check_string = "&".join(f"{k}={v}" for k, v in sorted_params)
        expected = hmac.new(secret.encode(), check_string.encode(), hashlib.sha256).hexdigest()

        if not hmac.compare_digest(sign, expected):
            raise HTTPException(status_code=403, detail="Invalid VK sign")

        vk_user_id = params.get("vk_user_id")
        if vk_user_id:
            return int(vk_user_id)

    raise HTTPException(status_code=401, detail="Missing vk_user_id")

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

async def get_http_client(request: Request) -> HTTPClient:
    """Возвращает HTTPClient из состояния приложения (синглтон).

    HTTPClient создаётся ОДИН раз при старте приложения и живёт
    до его остановки. Переиспользует connection pool.
    """
    return request.app.state.http_client


async def get_kinopoisk_client(
        http_client: Annotated[HTTPClient, Depends(get_http_client)]
) -> KinopoiskClient:
    return KinopoiskClient(settings=settings, http_client=http_client)


# ---------------------------------------------------------------------------
# -----------------------------Сервисы---------------------------------------
# ---------------------------------------------------------------------------

async def get_notification_service(
        movie_repo: Annotated[MovieRepository, Depends(get_movie_repository)],
        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
        http_client: Annotated[HTTPClient, Depends(get_http_client)],
) -> NotificationService:
    vk_client = VkClient(http_client, settings=settings)
    return NotificationService(
        movie_repository=movie_repo,
        user_repository=user_repo,
        vk_client=vk_client,
    )


async def get_movie_service(
        movie_repo: Annotated[MovieRepository, Depends(get_movie_repository)],
        kino_client: Annotated[KinopoiskClient, Depends(get_kinopoisk_client)],
        notify_service: Annotated[NotificationService, Depends(get_notification_service)]
) -> MovieService:
    return MovieService(repository=movie_repo, kinopoisk_client=kino_client, notification_service=notify_service)


async def get_user_service(
        user_repo: Annotated[UserRepository, Depends(get_user_repository)],
        movie_repo: Annotated[MovieRepository, Depends(get_movie_repository)],
) -> UserService:
    return UserService(user_repo=user_repo, movie_repo=movie_repo)


# ----------------------------------------------------------------------------
# -------------------Типизированные аннотации для роутеров--------------------
# ----------------------------------------------------------------------------

ServiceMovieDep: TypeAlias = Annotated[MovieService, Depends(get_movie_service)]
ServiceUserDep: TypeAlias = Annotated[UserService, Depends(get_user_service)]
VkUserIdDep: TypeAlias = Annotated[int, Depends(get_vk_user_id)]
