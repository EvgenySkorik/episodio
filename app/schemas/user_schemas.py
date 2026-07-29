from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.movie_schemas import MovieResponse


class UserResponse(BaseModel):
    id: int
    id_vk: int
    first_name: str | None
    last_name: str | None
    telephone: str | None
    avatar: str | None
    created_at: datetime
    movie_collections: list[MovieResponse] = []


class UserCreate(BaseModel):
    id_vk: int
    first_name: str
    last_name: str | None
    telephone: str | None
    avatar: str | None = None


class UserUpdate(BaseModel):
    first_name: str | None
    last_name: str | None
    telephone: str | None
    avatar: str | None
