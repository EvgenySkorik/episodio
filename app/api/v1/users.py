from fastapi import APIRouter, status, Query

from app.schemas.movie_schemas import MovieWithUserRatingResponse
from app.api.dependencies import ServiceUserDep, CurrentUserVkIdDep, VkUserIdDep
from app.schemas.user_schemas import UserResponse, UserCreate, UserUpdate

users_rout = APIRouter(prefix="/users", tags=["users"])

@users_rout.post("/", summary='Создать пользователя', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    service: ServiceUserDep,
):
    return await service.create_user(user_data)

@users_rout.get("/me", summary='Получить текущего пользователя по VK ID', response_model=UserResponse)
async def get_me(
    service: ServiceUserDep,
    vk_id: VkUserIdDep,

):
    return await service.get_or_create_user(vk_id)


@users_rout.get("/me/movies", summary='Получить фильмы пользователя по VK ID', response_model=list[MovieWithUserRatingResponse])
async def get_my_movies(
    vk_id: VkUserIdDep,
    service: ServiceUserDep,
):
    return await service.get_user_movies_with_rating(vk_id)


@users_rout.post("/me/movies", summary='Добавить фильм в коллекцию', status_code=status.HTTP_201_CREATED)
async def add_movie_to_collection(
    service: ServiceUserDep,
    vk_id: CurrentUserVkIdDep,
    movie_id: int = Query(...),

):
    return await service.add_movie_to_collection(vk_id, movie_id)

@users_rout.delete("/me/movies", summary='Удалить фильм из коллекции')
async def delete_movie_from_collection(
    vk_id: CurrentUserVkIdDep,
    movie_id: int,
    service: ServiceUserDep,
):
    await service.delete_movie_from_collection(vk_id, movie_id)

@users_rout.put("/me/movies/rating", summary='Оценить фильм')
async def rate_movie(
    vk_id: CurrentUserVkIdDep,
    movie_id: int,
    rating: float,
    service: ServiceUserDep,
):
    return await service.rate_movie(vk_id, movie_id, rating)

@users_rout.put("/me/movies/track")
async def toggle_tracking(
    vk_id: CurrentUserVkIdDep,
    service: ServiceUserDep,
    movie_id: int = Query(...),
    is_tracking: bool = Query(...),

):
    return await service.toggle_movie_tracking(vk_id, movie_id, is_tracking)

@users_rout.get("/{user_id}", summary='Получить по ID', response_model=UserResponse)
async def get_user(
    user_id: int,
    service: ServiceUserDep,
):
    return await service.get_user_by_id(user_id)


@users_rout.put("/{user_id}", summary='Обновить пользователя', response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    service: ServiceUserDep,
):
    return await service.update_user(user_id, user_data)

@users_rout.delete("/{user_id}", summary='Удалить пользователя', status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    service: ServiceUserDep,
):
    await service.delete_user(user_id)

