import asyncio
from collections.abc import Sequence

from app.clients.kp_client import KinopoiskClient
from app.core.config import settings
from app.core.exceptions.exceptions import MovieNotFoundError
from app.core.logging import get_logger
from app.infrastructure.hawk_client import HawkClient
from app.repositories.bases.base_movie import BaseMovieRepository
from app.schemas.kinopoisk_schemas import KinopoiskMovieResponse
from app.schemas.movie_schemas import MovieCreate, MovieResponse, MovieUpdate
from app.services.notification import NotificationService

logger = get_logger(__name__)


class MovieService:
    """Сервис для работы с Movie"""

    def __init__(
            self,
            repository: BaseMovieRepository,
            kinopoisk_client: KinopoiskClient,
            notification_service: NotificationService,
            hawk: HawkClient,
    ):
        self._repo = repository
        self._kino_client = kinopoisk_client
        self._notify_service = notification_service
        self._hawk = hawk

    async def get_all_movies(self) -> list[MovieResponse]:
        """Получить все фильмы, отдает схему"""
        movies_orm = await self._repo.get_all()
        logger.info(f"Получен список всех фильмов, количество: {len(movies_orm)}")
        return [MovieResponse.model_validate(m, from_attributes=True) for m in movies_orm]

    async def get_movie_by_id(self, movie_id: int) -> MovieResponse:
        """Получить фильм по ID, отдает схему"""
        movie_orm = await self._repo.get_by_id(movie_id)
        if not movie_orm:
            logger.warning(f"Фильм с ID {movie_id} не найден")
            raise MovieNotFoundError("Фильм не найден")
        logger.info(f"Получен фильм: id={movie_orm.id}, name='{movie_orm.name}'")
        return MovieResponse.model_validate(movie_orm, from_attributes=True)

    async def get_movie_by_name(self, movie_name: str) -> list[MovieResponse]:
        """
        Получить фильм(ы) по названию (регистронезависимый поиск).
        Передаёт в репозиторий лимит **limit=10** — достаточно для подсказок
            в поисковой строке. Если совпадений нет, возвращается пустой список.
        Args:
            movie_name: Поисковый запрос (часть названия).

        Returns:
            list[MovieResponse]: Список схем фильмов (от 0 до 10 элементов).
        """
        movies_orm = await self._repo.search_by_query(movie_name, limit=10)
        if movies_orm:
            logger.info(f"Фильм '{movie_name}' найден в БД")
            return [MovieResponse.model_validate(m, from_attributes=True) for m in movies_orm]

        logger.info(f"Фильм '{movie_name}' не найден в БД, запрос к Кинопоиску")
        kinopoisk_movies = await self._kino_client.search_by_name(movie_name, limit=5)
        if not kinopoisk_movies:
            logger.warning(f"Фильм '{movie_name}' не найден нигде")
            return []

        saved = []
        for movie in kinopoisk_movies:
            saved.append(await self._repo.create(movie.model_dump()))
        logger.info(f"Получены совпадения по '{movie_name}' из Кинопоиска")
        return [MovieResponse.model_validate(m, from_attributes=True) for m in saved]

    async def get_series_detail_information(self, kp_id: int):
        """Получает детальную информацию о Movie из АПИ, отдает словарь"""
        return await self._kino_client.get_series_details(kp_id=kp_id)

    async def get_token_balance(self):
        """Получает количество оставшихся токенов API Кинопоиска"""
        return await self._kino_client.get_token_balance()

    async def create_movie(self, movie: KinopoiskMovieResponse | MovieCreate) -> MovieResponse:
        """Создает фильм по схеме от АПИ или Create, отдает схему"""
        movie_orm = await self._repo.create(movie.model_dump())
        logger.info(f"Фильм '{movie_orm.name}' создан, id={movie_orm.id}")
        await self._hawk.send_event(
            message="Фильм создан",
            extra={"name": movie_orm.name, "id": movie_orm.id},
        )
        return MovieResponse.model_validate(movie_orm, from_attributes=True)

    async def update_movie(self, movie_id: int, movie: MovieUpdate) -> MovieResponse:
        """Обновляет фильм по схеме от АПИ, принимает id, схему с данными, отдает схему фильма"""
        movie_data = movie.model_dump(exclude_unset=True)
        movie_orm = await self._repo.update(movie_id, movie_data)
        if not movie_orm:
            logger.warning(f"Фильм с ID {movie_id} не найден при обновлении")
            raise MovieNotFoundError(f"Фильм с ID {movie_id} не найден")
        logger.info(f"Фильм '{movie_orm.name}' обновлён, id={movie_orm.id}")
        return MovieResponse.model_validate(movie_orm, from_attributes=True)

    async def delete_movie(self, movie_id: int) -> None:
        """Удаляет фильм по ID"""
        movie_orm = await self._repo.delete(movie_id)
        if not movie_orm:
            logger.warning(f"Фильм с ID {movie_id} не найден при удалении")
            raise MovieNotFoundError(f"Фильм с ID {movie_id} не найден")
        logger.info(f'Удален из БД фильм с id={movie_id}')
        await self._hawk.send_event(
            message="Удален из БД фильм",
            extra={"id": movie_id},
        )

    async def check_series_updates(self) -> None:
        """
        Основной метод для проверки обновлений сериалов.

        Получает список отслеживаемых сериалов, запускает проверку каждого
        и отправляет уведомления пользователям при обнаружении новых серий.
        """
        logger.info("Запуск проверки обновлений сериалов")
        tracked = await self._repo.get_tracked_series()
        if not tracked:
            logger.info("Нет отслеживаемых сериалов")
            return

        logger.info(f"Найдено отслеживаемых сериалов: {len(tracked)}, ")
        await self._check_notify_all(tracked)
        await self._hawk.send_event(
            message="Проверка обновления сериалов",
            extra={
                "total_series": len(tracked),
                "status": "success"
            }
        )

    async def _check_update_one(
            self,
            mov_id: int,
            kp_id: int,
            current_episodes: int,
            user_id: int,
            name: str,
            semaphore: asyncio.Semaphore,
    ) -> dict[str, int | str] | None:
        """
        Проверяет обновления сериала в Кинопоиске и обновляет БД.
        Args:
            mov_id (int): ID фильма в БД.
            kp_id (int): ID фильма в Кинопоиске.
            current_episodes (int): Текущее количество серий.
            user_id (int): ID пользователя.
            name (str): Название сериала.
            semaphore (asyncio.Semaphore): Семафор для ограничения параллельных запросов.

        Returns:
            dict[str, int | str] | None: Словарь с данными для уведомления, если были обновления.
                Иначе None.
        """
        async with semaphore:
            details = await self._kino_client.get_series_details(kp_id)
            new_episodes = details.get("total_episodes", 0)
            new_data_episodes = {"total_episodes": new_episodes}

            await asyncio.sleep(settings.celery.semaphore_timeout_rps)

        current = current_episodes or 0
        if new_episodes > current:
            await self._repo.update(mov_id, new_data_episodes)
            logger.info(f"Сериал {mov_id} (kp_id={kp_id}) обновлён: {current_episodes} → {new_episodes}")
            return {"user_id": user_id, "name": name, "new_episodes": new_episodes}
        return None

    async def _check_notify_all(self, serials: Sequence) -> None:
        """
        Проверяет все отслеживаемые сериалы и отправляет уведомления.

        Args:
            serials (list[tuple[int, int, int, int, str]]): Список сериалов с данными пользователей.
        """
        sem = asyncio.Semaphore(settings.celery.semaphore_limit)

        tasks = [self._check_update_one(
            mov_id, kp_id, current, user_id, name, sem
        )
            for mov_id, kp_id, current, user_id, name in serials
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Ошибка при проверке сериала: {result}")
            elif result and isinstance(result, dict):
                await self._notify_service.send_notification(
                    result["user_id"],  # type: ignore[arg-type]
                    result["name"],  # type: ignore[arg-type]
                    result["new_episodes"],  # type: ignore[arg-type]
                )

    async def get_all_movies_paginated(self, limit: int, page: int) -> list[MovieResponse]:
        """Получить список фильмов с пагинацией.

    Args:
        limit: Количество записей на странице,
        page: Страница записей.

    Returns:
        list[MovieResponse]: Список фильмов для текущей страницы.
    """
        offset = (page - 1) * limit
        movies_orm = await self._repo.get_all_pagination(limit=limit, offset=offset)

        return [MovieResponse.model_validate(m, from_attributes=True) for m in movies_orm]

    async def get_all_movies_popular(self, limit: int) -> list[MovieResponse]:
        """Получить список популярных фильмов с лимитом.

    Args:
        limit: Максимальное количество фильмов в ответе

    Returns:
        list[MovieResponse]: Список схем популярных фильмов.
    """

        movies_orm = await self._repo.get_popular(limit=limit)

        return [MovieResponse.model_validate(m, from_attributes=True) for m in movies_orm]
