from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.db.models import Movie, UserMovie
from app.repositories.bases.base_movie import BaseMovieRepository

logger = get_logger(__name__)


class MovieRepository(BaseMovieRepository):
    """Репозиторий для работы БД и Видео """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_all(self) -> list[Movie]:
        """Получить список всех ORM-объектов фильмов из БД."""
        result = await self._session.execute(select(Movie))
        movies = list(result.scalars().all())
        logger.info(f"Получены все Movie из БД, количество: {len(movies)}")
        return movies

    async def get_by_id(self, movie_id: int) -> Movie | None:
        """Получить ORM-объект фильма по ID из БД."""
        result = await self._session.execute(select(Movie).where(Movie.id == movie_id))
        movie = result.scalars().first()
        logger.info(f"Получен Movie id={movie_id} из БД")
        return movie

    async def get_by_name(self, movie_name: str) -> Movie | None:
        """Получить ORM-объект фильма по имени из БД."""
        result = await self._session.execute(select(Movie).where(Movie.name.ilike(movie_name)))
        movie = result.scalars().first()
        logger.info(f"Получен Movie name='{movie_name}' из БД")
        return movie

    async def create(self, movie: dict) -> Movie:
        """Создать ORM-объект фильма по данным из словаря в БД."""
        movie_orm = Movie(**movie)
        self._session.add(movie_orm)
        await self._session.commit()
        await self._session.refresh(movie_orm)
        logger.info(f"Добавлен Movie в БД: name='{movie_orm.name}'")
        return movie_orm

    async def update(self, movie_id: int, movie: dict) -> Movie | None:
        """Обновить ORM-объект фильма по ID и словарю с данными в БД."""
        movie_orm = await self.get_by_id(movie_id)
        if not movie_orm:
            return None

        for key, value in movie.items():
            setattr(movie_orm, key, value)

        await self._session.commit()
        await self._session.refresh(movie_orm)
        logger.info(f"Обновлён Movie id={movie_orm.id}, name='{movie_orm.name}'")
        return movie_orm

    async def delete(self, movie_id: int) -> bool:
        """Удалить ORM-объект фильма по ID из БД."""
        movie_orm = await self.get_by_id(movie_id)
        if not movie_orm:
            return False
        await self._session.delete(movie_orm)
        await self._session.commit()
        logger.info(f"Удалён Movie id={movie_id} из БД")
        return True

    async def search_by_query(self, query: str, limit: int = 10) -> list[Movie]:
        """Получить список ORM-объектов фильмов по совпадению имени из БД с лимитом."""
        result = await self._session.execute(
            select(Movie)
            .where(Movie.name.ilike(f"%{query}%"))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_tracked_series(self) -> list[tuple[int, int, int, int, str]]:
        """Получить все сериалы, которые отслеживают пользователи,
        Returns:
            - id (int): ID фильма в БД.
            - id_kino (int): ID фильма в Кинопоиске.
            - total_episodes (int): Текущее количество серий.
            - user_id (int): ID пользователя, который отслеживает сериал.
            - name (str): Название сериала.
        """
        stmt = (select(Movie.id, Movie.id_kino, Movie.total_episodes, UserMovie.user_id, Movie.name)
                .join(UserMovie, UserMovie.movie_id == Movie.id)
                .where(UserMovie.is_tracking == True)
                .where(Movie.is_series == True)
                .distinct()
                )
        result = await self._session.execute(stmt)
        return result.all()
