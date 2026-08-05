from abc import ABC, abstractmethod
from typing import Sequence

from app.db.models import User, Movie, UserMovie


class BaseUserRepository(ABC):
    """Базовый интерфейс репозитория для Пользователя"""

    @abstractmethod
    async def get_by_id(self, id: int) -> User | None:
        pass

    @abstractmethod
    async def get_by_vk_id(self, vk_id: int) -> User | None:
        pass

    @abstractmethod
    async def create(self, user: dict) -> User:
        pass

    @abstractmethod
    async def update(self, id: int, user: dict) -> User | None:
        pass

    @abstractmethod
    async def delete(self, id: int) -> bool:
        pass

    @abstractmethod
    async def save(self, user: User) -> User:
        pass

    @abstractmethod
    async def rate_movie(self, user_id: int, movie_id: int, rating: float) -> None:
        pass

    @abstractmethod
    async def get_movies_with_user_rating(self, vk_id: int) -> Sequence[tuple[Movie, UserMovie]]:
        pass

    @abstractmethod
    async def add_movie_to_user(self, user_id: int, movie_id: int) -> bool:
        pass

    @abstractmethod
    async def delete_movie_from_user(self, user_id: int, movie_id: int) -> bool:
        pass

    @abstractmethod
    async def toggle_tracking(self, user_id: int, movie_id: int, is_tracking: bool) -> bool:
        pass





