from collections.abc import Sequence

from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql.dml import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.logging import get_logger
from app.db.models import Movie, User, UserMovie
from app.repositories.bases.base_user import BaseUserRepository

logger = get_logger(__name__)


class UserRepository(BaseUserRepository):
    """Репозиторий для работы БД и Пользователя"""

    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_by_id(self, id: int) -> User | None:
        """Получить ORM-объект Пользователя по ID из БД."""
        stmt = (
            select(User)
            .where(User.id == id)
            .options(selectinload(User.movie_collections))
        )
        result = await self._session.execute(stmt)
        user = result.scalars().first()

        logger.info(f"Получили модель из БД по id: first_name={user.first_name if user else None}")
        return user

    async def get_by_vk_id(self, vk_id: int) -> User | None:
        """Получить ORM-объект Пользователя по VK ID из БД."""
        stmt = (
            select(User)
            .where(User.id_vk == vk_id)
            .options(selectinload(User.movie_collections))
        )
        result = await self._session.execute(stmt)
        user = result.scalars().first()

        logger.info(f"Получили модель из БД по VK ID: first_name={user.first_name if user else None}")
        return user

    async def create(self, user: dict) -> User:
        """Создать ORM-объект Пользователя в БД."""
        user_orm = User(**user)
        self._session.add(user_orm)
        await self._session.commit()
        await self._session.refresh(user_orm)
        logger.info(f"Добавили Пользователя в БД, name={user_orm.first_name}")
        return user_orm

    async def update(self, user_id: int, user: dict) -> User | None:
        """Обновить ORM-объект Пользователя в БД."""
        user_orm = await self._session.get(User, user_id)
        if not user_orm:
            return None

        for key, value in user.items():
            setattr(user_orm, key, value)

        await self._session.commit()
        await self._session.refresh(user_orm)

        stmt = select(User).where(User.id == user_id).options(selectinload(User.movie_collections))
        result = await self._session.execute(stmt)
        logger.info(f"Обновили пользователя {user_orm.first_name}")
        return result.scalars().first()

    async def delete(self, user_id: int) -> bool:
        """Удалить ORM-объект пользователя из БД. Возвращает bool."""
        user_orm = await self._session.get(User, user_id)
        if not user_orm:
            return False
        await self._session.delete(user_orm)
        await self._session.commit()
        logger.info(f"Удалили из БД id={user_id}")
        return True

    async def save(self, user: User) -> User:
        """Сохранить ORM-объект в БД, возвращаем модель User"""
        await self._session.commit()
        await self._session.refresh(user)
        return user

    async def rate_movie(self, user_id: int, movie_id: int, rating: float) -> None:
        """Добавить в связь UserMovie рейтинг от пользователя"""
        stmt = update(UserMovie).where(
            UserMovie.user_id == user_id,
            UserMovie.movie_id == movie_id
        ).values(user_rating=rating)
        await self._session.execute(stmt)
        await self._session.commit()
        logger.info("Добавлен рейтинг в БД")

    async def get_movies_with_user_rating(self, vk_id: int) -> Sequence[tuple[Movie, UserMovie]]:
        """Получить список фильмов пользователя с его рейтингом и статусом просмотра по VK ID."""
        stmt = (
            select(Movie, UserMovie)
            .join(UserMovie, Movie.id == UserMovie.movie_id)
            .join(User, User.id == UserMovie.user_id)
            .where(User.id_vk == vk_id)
            .order_by(Movie.name.asc())
        )
        result = (await self._session.execute(stmt)).all()
        logger.info("Получен список фильмов с рейтингом из БД")
        return result # type: ignore[return-value]

    async def add_movie_to_user(self, user_id: int, movie_id: int) -> bool:
        """Добавить фильм/сериал к модели User в коллекцию, только для PostgreSQL"""
        stmt = pg_insert(UserMovie).values(
            user_id=user_id,
            movie_id=movie_id,
        ).on_conflict_do_nothing()

        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0 # type: ignore


    async def delete_movie_from_user(self, user_id: int, movie_id: int) -> bool:
        """Удалить фильм/сериал у модели User из коллекции"""
        stmt = delete(UserMovie).where(
            UserMovie.user_id==user_id,
            UserMovie.movie_id==movie_id,
        )

        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0 # type: ignore

    async def toggle_tracking(self, user_id: int, movie_id: int, is_tracking: bool) -> bool:
        """Отслеживать или нет сериал у модели User в связи UserMovie - is_tracking"""
        stmt = (
            update(UserMovie)
            .where(UserMovie.user_id == user_id, UserMovie.movie_id == movie_id)
            .values(is_tracking=is_tracking)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.rowcount > 0 # type: ignore