from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator


class KinopoiskMovieResponse(BaseModel):
    id_kino: int
    name: str
    alternative_name: str | None
    movie_type: str
    year: int
    description: str | None
    short_description: str | None
    is_series: bool
    rating_kp: float | None
    rating_imdb: float | None
    genres: list | None
    countries: list | None
    logo: str | None
    poster: str | None

