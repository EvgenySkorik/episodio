from app.core.config import settings, AppSettings
from app.core.exceptions.exceptions import KinopoiskAPIError
from app.core.logging import get_logger

from app.infrastructure.http_client import HTTPClient
from app.schemas.kinopoisk_schemas import KinopoiskMovieResponse

logger = get_logger(__name__)



class KinopoiskClient:
    """Клиент для работы с АПИ Кинопоиска"""
    def __init__(self, settings: AppSettings, http_client: HTTPClient):
        self._settings = settings
        self._http_client = http_client

    async def get_token_balance(self):
        """Получает оставшееся кол-во токенов из АПИ Кинопоиска"""
        response = await self._http_client.request(
            method="GET",
            url=f"{self._settings.kinopoisk.url}v1.5/token",
            headers=self._settings.kinopoisk.headers,
        )

        response.raise_for_status()

        return response.json()


    async def get_series_details(self, kp_id: int, limit: int = 100) -> dict:
        """Асинхронно получает данные о Movie через API Кинопоиска по id
        Возвращает: кол-во сезонов и серий"""
        params = {"movieId": [kp_id], "limit": limit}
        response = await self._http_client.request(
            method="GET",
            url=f"{self._settings.kinopoisk.url}v1.5/season",
            params=params,
            headers=self._settings.kinopoisk.headers,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("docs"):
            raise KinopoiskAPIError("Ничего не найдено")

        seasons = data.get("docs", [])
        return {
            "total_seasons": len(seasons),
            "total_episodes": sum(s.get("episodesCount", 0) for s in seasons),
        }


    async def search_by_name(self, message: str, limit: int = 10, page: int = 1) -> list[KinopoiskMovieResponse]:
        """Асинхронно получает данные о фильмах через API Кинопоиска по названию"""
        logger.info(f"Поиск в Кинопоиске: '{message}'")
        params = {
            "query": message,
            "limit": limit,
            "page": page,
        }
        response = await self._http_client.request(
            method="GET",
            url=f"{self._settings.kinopoisk.url}v1.4/movie/search",
            params=params,
            headers=self._settings.kinopoisk.headers,
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("docs"):
            raise KinopoiskAPIError("Ничего не найдено")

        return self._parse_movies(data)

    @staticmethod
    def _parse_movies(data: dict) -> list[KinopoiskMovieResponse]:
        """Парсит сырой JSON-ответ API в список Pydantic-схем."""
        docs = data.get("docs", [])
        if not docs:
            return []

        results = []
        for raw in docs:
            rating = raw.get("rating") or {}
            logo_data = raw.get("logo") or {}
            poster_data = raw.get("poster") or {}

            movie_schema = KinopoiskMovieResponse(
                id_kino=raw.get("id"),
                name=raw.get("name"),
                alternative_name=raw.get("alternativeName"),
                movie_type=raw.get("type"),
                year=raw.get("year"),
                description=raw.get("description"),
                short_description=raw.get("shortDescription"),
                is_series=raw.get("isSeries"),
                rating_kp=rating.get("kp"),
                rating_imdb=rating.get("imdb"),
                genres=[g.get("name") for g in raw.get("genres", [])],
                countries=[contr.get("name") for contr in raw.get("countries", [])],
                logo=logo_data.get("url") or logo_data.get("previewUrl"),
                poster=poster_data.get("url") or poster_data.get("previewUrl"),
            )
            results.append(movie_schema)

        return results

