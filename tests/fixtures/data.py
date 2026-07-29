from datetime import datetime
from app.db.models import Movie, User
from app.schemas.kinopoisk_schemas import KinopoiskMovieResponse
from app.schemas.movie_schemas import MovieCreate


def get_fake_movie(**overrides) -> Movie:
    """Создаёт фейковый ORM-объект Movie. Поля можно переопределить через **overrides."""
    defaults = {
        "id": 1,
        "name": "Матрица",
        "year": 1999,
        "id_kino": 301,
        "movie_type": "movie",
        "is_series": False,
        "created_at": datetime(2025, 1, 1),
        "updated_at": datetime(2025, 1, 1),
    }
    defaults.update(overrides)
    return Movie(**defaults)

def get_fake_movie_from_kinopoisk(**overrides) -> KinopoiskMovieResponse:
    """Создаёт фейковый ORM-объект Movie. Поля можно переопределить через **overrides."""
    defaults = {
        "id_kino": 301782342,
        "name": "Интерстеллар",
        "alternative_name": None,
        "movie_type": "movie",
        "year": 2014,
        "description": None,
        "short_description": None,
        "is_series": False,
        "rating_kp": None,
        "rating_imdb": None,
        "genres": None,
        "countries": None,
        "logo": None,
        "poster": None,
    }
    defaults.update(overrides)
    return KinopoiskMovieResponse(**defaults)

def get_fake_movie_from_user(**overrides) -> MovieCreate:
    """Создаёт фейковый ORM-объект Movie. Поля можно переопределить через **overrides."""
    defaults = {
        "id_kino": 301782342,
        "name": "Интерстеллар",
        "alternative_name": None,
        "movie_type": "movie",
        "year": 2014,
        "description": None,
        "short_description": None,
        "is_series": False,
        "rating_kp": None,
        "rating_imdb": None,
        "genres": None,
        "countries": None,
        "logo": None,
        "poster": None,
    }
    defaults.update(overrides)
    return MovieCreate(**defaults)


def get_fake_user(**overrides) -> User:
    """Создаёт фейковый ORM-объект User. Поля можно переопределить через **overrides."""
    defaults = {
        "id": 1,
        "id_vk": 123,
        "first_name": "test_user",
        "last_name": "test_user_last_name",
        "telephone": "+795555555",
        "avatar": "ava.png",
        "created_at": datetime.now()
    }
    defaults.update(overrides)
    return User(**defaults)