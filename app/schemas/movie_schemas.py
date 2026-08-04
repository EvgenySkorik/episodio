from datetime import date, datetime

from pydantic import BaseModel, Field, field_validator, ConfigDict

class MovieResponse(BaseModel):
    id: int
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
    created_at: datetime
    updated_at: datetime
    total_seasons: int | None = 0
    total_episodes: int | None = 0


class MovieWithUserRatingResponse(MovieResponse):
    user_rating: float | None = 0
    is_watched: bool | None = False
    is_tracking: bool | None = False


class MovieCreate(BaseModel):
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

    @field_validator('year')
    @classmethod
    def not_by_next_year(cls, value: int) -> int:
        if value > datetime.now().year:
            raise ValueError(f'Year {value} cannot be in the future')
        return value


class MovieUpdate(BaseModel):
    id_kino: int | None = None
    name: str | None = None
    alternative_name: str | None = None
    movie_type: str | None = None
    year: int | None = None
    description: str | None = None
    short_description: str | None = None
    is_series: bool | None = None
    rating_kp: float | None = None
    rating_imdb: float | None = None
    genres: list | None = None
    countries: list | None = None

class RatingSchema(BaseModel):
    rating: float

class TrackingSchema(BaseModel):
    is_tracking: bool
