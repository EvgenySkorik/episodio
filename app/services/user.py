from app.core.exceptions.exceptions import MovieNotFoundError, UserNotFoundError
from app.core.logging import get_logger
from app.repositories.bases.base_movie import BaseMovieRepository
from app.repositories.bases.base_user import BaseUserRepository
from app.schemas.movie_schemas import MovieResponse, MovieWithUserRatingResponse
from app.schemas.user_schemas import UserCreate, UserResponse, UserUpdate

logger = get_logger(__name__)


class UserService:
    """Сервис для работы с Пользователем"""

    def __init__(self, user_repo: BaseUserRepository, movie_repo: BaseMovieRepository):
        self._user_repo = user_repo
        self._movie_repo = movie_repo

    async def get_user_by_id(self, user_id: int) -> UserResponse:
        """Получить пользователя по ID, отдает схему"""
        user_orm = await self._user_repo.get_by_id(user_id)
        if user_orm is None:
            logger.warning(f"Пользователь c id={user_id} не найден")
            raise UserNotFoundError(f"Пользователь {user_id} не найден")
        logger.info(f"Получен пользователь {user_orm.first_name} c id={user_id}")
        return UserResponse.model_validate(user_orm, from_attributes=True)

    async def get_user_by_vk_id(self, vk_id: int) -> UserResponse:
        """Получить пользователя по VK ID, отдает схему"""
        user_orm = await self._user_repo.get_by_vk_id(vk_id)
        if user_orm is None:
            logger.warning(f"Пользователь c  vk_id={vk_id} не найден")
            raise UserNotFoundError(f"Пользователь с VK ID={vk_id} не найден")
        logger.info(f"Получен пользователь {user_orm.first_name} c id={user_orm.id}")
        return UserResponse.model_validate(user_orm, from_attributes=True)

    async def create_user(self, user: UserCreate) -> UserResponse:
        """"Создает Пользователя по схеме UserCreate, отдает схему"""
        user_orm = await self._user_repo.create(user.model_dump())
        logger.info(f"Пользователь {user_orm.first_name}, id={user_orm.id} создан")
        return UserResponse(
            id=user_orm.id,
            id_vk=user_orm.id_vk,
            first_name=user_orm.first_name,
            last_name=user_orm.last_name,
            telephone=user_orm.telephone,
            avatar=user_orm.avatar,
            created_at=user_orm.created_at,
            movie_collections=[],
        )

    async def get_or_create_user(self, vk_id: int) -> UserResponse:
        """Получить или создать пользователя по VK ID."""
        user_orm = await self._user_repo.get_by_vk_id(vk_id)
        if user_orm:
            return UserResponse.model_validate(user_orm, from_attributes=True)

        user_data = {
            "id_vk": vk_id,
            "first_name": f"User_{vk_id}",
        }
        user_orm = await self._user_repo.create(user_data)
        logger.info(f"Создан новый пользователь с VK ID {vk_id}")
        return UserResponse(
            id=user_orm.id,
            id_vk=user_orm.id_vk,
            first_name=user_orm.first_name,
            last_name=user_orm.last_name,
            telephone=user_orm.telephone,
            avatar=user_orm.avatar,
            created_at=user_orm.created_at,
            movie_collections=[],
        )

    async def update_user(self, user_id: int, user: UserUpdate) -> UserResponse:
        """"Обновляет Пользователя по схеме UserUpdate, отдает схему"""
        user_orm = await self._user_repo.update(user_id, user.model_dump(exclude_unset=True))
        if not user_orm:
            logger.warning(f"Пользователь c id={user_id} не найден")
            raise UserNotFoundError(f"Пользователь {user_id} не найден")
        logger.info(f"Пользователь c id={user_id} обновлён")
        return UserResponse.model_validate(user_orm, from_attributes=True)

    async def delete_user(self, user_id: int) -> None:
        """"Удаляет Пользователя по id, отдает схему"""
        deleted = await self._user_repo.delete(user_id)
        if not deleted:
            logger.warning(f"Пользователь {user_id} не найден")
            raise UserNotFoundError(f"Пользователь {user_id} не найден")
        logger.info(f"Пользователь {user_id} удалён")

    async def get_user_movies(self, vk_id: int) -> list[MovieResponse]:
        """Получить список фильмов пользователя по VK ID."""
        user_orm = await self._user_repo.get_by_vk_id(vk_id)
        if user_orm is None:
            logger.warning(f"Пользователь c  vk_id={vk_id} не найден")
            raise UserNotFoundError(f"Пользователь с VK ID={vk_id} не найден")
        logger.info(f"Получен пользователь {user_orm.first_name} c id={user_orm.id} со списком его коллекции фильмов")
        return [
            MovieResponse.model_validate(movie, from_attributes=True)
            for movie in user_orm.movie_collections
        ]

    async def get_user_movies_with_rating(self, vk_id: int) -> list[MovieWithUserRatingResponse]:
        """Получить список фильмов пользователя с рейтингом и статусом is_watched по VK ID."""

        rows = await self._user_repo.get_movies_with_user_rating(vk_id)

        if not rows:
            logger.info("Фильмы не обнаружены")
            return []

        movies = []
        for movie, user_movie in rows:
            movie_resp = MovieResponse.model_validate(movie, from_attributes=True)
            mov_with_rait = MovieWithUserRatingResponse(
                **movie_resp.model_dump(exclude_unset=True),
                user_rating=user_movie.user_rating or 0,
                is_watched=user_movie.is_watched or False,
                is_tracking=user_movie.is_tracking or False,
            )
            movies.append(mov_with_rait)
            logger.info("Получен список фильмов пользователя по vk_id")
        return movies


    async def add_movie_to_collection(self, vk_id: int, movie_id: int) -> bool:
        """Добавить фильм по id к пользователю в коллекцию по VK_ID"""
        user_orm = await self._user_repo.get_by_vk_id(vk_id)
        if not user_orm:
            raise UserNotFoundError(f"Пользователь с VK ID {vk_id} не найден")

        movie_orm = await self._movie_repo.get_by_id(movie_id)
        if not movie_orm:
            raise MovieNotFoundError(f"Фильм с movie_id {movie_id} не найден")

        added = await self._user_repo.add_movie_to_user(user_orm.id, movie_orm.id)
        action = "уже в" if not added else "добавлен в"
        logger.info(f'Фильм {movie_orm.name} {action} коллекции пользователя {user_orm.first_name}')
        return added

    async def delete_movie_from_collection(self, vk_id: int, movie_id: int) -> bool:
        """Удалить фильм по id у пользователя в коллекцию по VK_ID"""
        user_orm = await self._user_repo.get_by_vk_id(vk_id)
        if not user_orm:
            raise UserNotFoundError(f"Пользователь с VK ID {vk_id} не найден")

        movie_orm = await self._movie_repo.get_by_id(movie_id)
        if not movie_orm:
            raise MovieNotFoundError(f"Фильм с movie_id {movie_id} не найден")

        deleted_movie = await self._user_repo.delete_movie_from_user(user_orm.id, movie_orm.id)

        action = "отсутствует в" if not deleted_movie else "удален из"
        logger.info(f'Фильм {movie_orm.name} {action} коллекции пользователя {user_orm.first_name}')
        return deleted_movie


    async def rate_movie(self, vk_id: int, movie_id: int, rating: float) -> dict:
        """Добавить рейтинг фильму по id"""

        user_orm = await self._user_repo.get_by_vk_id(vk_id)
        if not user_orm:
            logger.warning(f"Пользователь с VK ID {vk_id} не найден")
            raise UserNotFoundError(f"Пользователь с VK ID {vk_id} не найден")

        movie_orm = await self._movie_repo.get_by_id(movie_id)
        if not movie_orm:
            logger.warning(f"Фильм с movie_id {movie_id} не найден")
            raise MovieNotFoundError(f"Фильм с movie_id {movie_id} не найден")

        await self._user_repo.rate_movie(user_orm.id, movie_orm.id, rating)
        logger.info(f"Пользователь {user_orm.first_name} оценил фильм '{movie_orm.name}' на {rating}")
        return {"user_rating": rating}


    async def toggle_movie_tracking(self, vk_id: int, movie_id: int, is_tracking: bool) -> dict:
        """Включить/выключить отслеживание пользователем сериала"""
        user_orm = await self._user_repo.get_by_vk_id(vk_id)
        if not user_orm:
            logger.warning(f"Пользователь с VK ID {vk_id} не найден")
            raise UserNotFoundError(f"Пользователь с VK ID {vk_id} не найден")

        movie_orm = await self._movie_repo.get_by_id(movie_id)
        if not movie_orm:
            logger.warning(f"Фильм с movie_id {movie_id} не найден")
            raise MovieNotFoundError(f"Фильм с movie_id {movie_id} не найден")

        await self._user_repo.toggle_tracking(user_orm.id, movie_orm.id, is_tracking)
        logger.info(f"Трекинг {'включён' if is_tracking else 'выключен'} для {movie_orm.name}")
        return {"is_tracking": is_tracking}
