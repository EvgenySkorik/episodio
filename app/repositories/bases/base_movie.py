from abc import ABC, abstractmethod

from app.db.models import Movie


class BaseMovieRepository(ABC):
    """Базовый интерфейс репозитория для CRUD-операций c Movie"""
    @abstractmethod
    async def get_all(self) -> list[Movie]:
        pass

    @abstractmethod
    async def get_by_id(self, movie_id: int) -> Movie | None:
        pass

    @abstractmethod
    async def get_by_name(self, name: str) -> Movie | None:
        pass

    @abstractmethod
    async def create(self, movie: dict) -> Movie:
        pass

    @abstractmethod
    async def update(self, movie_id: int, movie: dict) -> Movie | None:
        pass

    @abstractmethod
    async def delete(self, movie_id: int) -> bool:
        pass

    @abstractmethod
    async def get_tracked_series(self) -> list[tuple[int, int, int, int, str]]:
        pass



