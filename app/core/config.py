from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict


load_dotenv()


class DatabaseSettings(BaseSettings):
    """Класс с настройками PostgreSQL"""
    server: str = "localhost"
    user: str = "postgres"
    password: str = "postgres234"
    db: str = "kinomovie"

    @property
    def url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}@{self.server}/{self.db}"
        )


class KinopoiskSettings(BaseSettings):
    """Класс с настройками АПИ Кинопоиска"""
    url: str = f"https://api.poiskkino.dev/"
    api_key: str = ""

    @property
    def headers(self) -> dict:
        return {
            "accept": "application/json",
            "X-API-KEY": self.api_key,
        }

class VkSettings(BaseSettings):
    token: str = "default"
    secret_key: str = ""
    api_url: str = "https://api.vk.com/method/"
    api_version: str = "5.199"


class CelerySettings(BaseSettings):
    """Класс с настройками Celery, Redis"""
    broker_url: str = "redis://localhost:6379/0"
    result_backend: str = "redis://localhost:6379/0"
    task_serializer: str = "json"
    result_serializer: str = "json"
    accept_content: list[str] = ["json"]
    timezone: str = "UTC"
    enable_utc: bool = True
    semaphore_limit: int = 5
    semaphore_timeout_rps: float = 0.2
    check_series_hour: int = 6
    check_series_minute: int = 6
    check_series_day: int = 2

class AppSettings(BaseSettings):
    """Класс с общими настройками"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        extra="ignore",
    )

    postgres: DatabaseSettings = DatabaseSettings()
    kinopoisk: KinopoiskSettings = KinopoiskSettings()
    vk: VkSettings = VkSettings()
    celery: CelerySettings = CelerySettings()

    secret_jwt_key: str = ""
    hawk_secret_token: str = ""
    title: str = "Kino Movie API"
    description: str = "API для поиска и хранения фильмов (БД + Кинопоиск)"
    version: str = "2.0.0"


settings: AppSettings = AppSettings()

