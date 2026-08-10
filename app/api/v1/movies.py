from typing import Annotated

from fastapi import APIRouter, status
from fastapi.params import Query

from app.api.dependencies import PaginationDep, ServiceMovieDep
from app.core.logging import get_logger
from app.schemas.movie_schemas import MovieCreate, MovieResponse, MovieUpdate

logger = get_logger(__name__)

movies_rout = APIRouter(prefix="/movies", tags=["movies"])


@movies_rout.get("/search", summary='Поиск фильма', response_model=list[MovieResponse])
async def search_movie(
        service: ServiceMovieDep,
        q: Annotated[str, Query(..., min_length=1)],
):
    return await service.get_movie_by_name(q)


@movies_rout.get("", summary='Все фильмы', response_model=list[MovieResponse])
async def get_all_movies(
        service: ServiceMovieDep,
):
    """Ручка получения списка всех фильмов"""

    return await service.get_all_movies()

@movies_rout.get("/paginated", summary='Получить все с пагинацией')
async def get_all_movies_paginated(
        service: ServiceMovieDep,
        pagination: PaginationDep,

) -> list[MovieResponse]:
    """Ручка получения списка всех фильмов с пагинацией"""
    return await service.get_all_movies_paginated(limit=pagination.limit, page=pagination.page)
@movies_rout.get("/popular", summary='Получить все популярные')
async def get_all_movies_popular(
        service: ServiceMovieDep,
        limit: Annotated[int, Query(20, ge=1, le=100, description="Сколько фильмов вернуть")] = 20,

) -> list[MovieResponse]:
    """Ручка получения списка всех популярных фильмов с limit(default)=20"""
    return await service.get_all_movies_popular(limit=limit)

@movies_rout.get("/kinopoisktoken", summary='Информация о токенах Кинопоиска')
async def get_token_balance(
        service: ServiceMovieDep,
):
    """Ручка получения кол-ва токенов"""
    return await service.get_token_balance()

@movies_rout.get("/{id}", summary='Фильм по ID', response_model=MovieResponse)
async def get_movie(
        service: ServiceMovieDep,
        id: int,
):
    """Ручка получения фильма по ID"""
    return await service.get_movie_by_id(id)

@movies_rout.get("/detail/{id}", summary='Фильм по ID KP')
async def get_series_information(
        service: ServiceMovieDep,
        id: int,
):
    """Ручка получения фильма по ID DETAIL!!!"""
    return await service.get_series_detail_information(id)



@movies_rout.post("", summary='Создать фильм', response_model=MovieResponse, status_code=status.HTTP_201_CREATED)
async def create_movie(
        service: ServiceMovieDep,
        movie: MovieCreate
):
    """Ручка создания фильма"""
    return await service.create_movie(movie)


@movies_rout.put("/{id}", summary='Обновить фильм', response_model=MovieResponse)
async def update_movie(
        service: ServiceMovieDep,
        id: int,
        movie: MovieUpdate,
):
    """Ручка обновления фильма"""
    updated_movie = await service.update_movie(id, movie)
    return updated_movie


@movies_rout.delete("/{id}", summary='Удалить фильм', response_model=None, status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
        service: ServiceMovieDep,
        id: int,
) -> None:
    """Ручка удаления фильма"""
    await service.delete_movie(id)



