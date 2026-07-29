import pytest

from app.core.exceptions.exceptions import MovieNotFoundError
from app.schemas.kinopoisk_schemas import KinopoiskMovieResponse
from app.schemas.movie_schemas import MovieCreate, MovieUpdate
from app.services.movie import MovieService


@pytest.mark.asyncio
async def test_get_movie_by_id_found(mock_movie_repo, make_movie, mock_notify_serv):
    """Фильм найден — возвращаем MovieResponse."""

    movie = make_movie(id=1, name="Матрица")
    mock_movie_repo.get_by_id.return_value = movie
    service = MovieService(repository=mock_movie_repo, kinopoisk_client=None, notification_service=mock_notify_serv)

    result = await service.get_movie_by_id(1)

    assert result.name == "Матрица"
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_movie_by_id_not_found(mock_movie_repo, mock_notify_serv):
    """Фильм не найден — выбрасываем исключение."""
    mock_movie_repo.get_by_id.return_value = None

    service = MovieService(repository=mock_movie_repo, kinopoisk_client=None, notification_service=mock_notify_serv)

    with pytest.raises(MovieNotFoundError):
        await service.get_movie_by_id(999)


@pytest.mark.asyncio
async def test_get_movie_by_name_found(mock_movie_repo, mock_kino_client, make_movie, mock_notify_serv):
    """Фильм найден — возвращаем MovieResponse."""
    movie = make_movie(id=1, name="Матрица")
    mock_movie_repo.search_by_query.return_value = [movie]

    service = MovieService(repository=mock_movie_repo, kinopoisk_client=mock_kino_client, notification_service=mock_notify_serv)

    result = await service.get_movie_by_name("Матрица")

    assert result[0].name == "Матрица"
    assert result[0].id == 1


@pytest.mark.asyncio
async def test_get_movie_by_name_found_with_api_kinopoisk(mock_movie_repo, mock_kino_client, make_kinopoisk_movie,
                                                          make_movie, mock_notify_serv):
    """Фильм найден — возвращаем MovieResponse."""
    mock_movie_repo.search_by_query.return_value = []
    movie = make_kinopoisk_movie(name="Интерстеллар", id_kino=301823748723, movie_type="test type")
    mock_kino_client.search_by_name.return_value = [movie]
    mov_orm = make_movie(id=5, name="Интерстеллар")
    mock_movie_repo.create.return_value = mov_orm

    service = MovieService(repository=mock_movie_repo, kinopoisk_client=mock_kino_client, notification_service=mock_notify_serv)

    result = await service.get_movie_by_name("Интерстеллар")

    assert len(result) == 1
    assert result[0].name == "Интерстеллар"
    assert result[0].id == 5


@pytest.mark.asyncio
async def test_create_movie_by_kinopoisk(mock_movie_repo, mock_kino_client, make_kinopoisk_movie, make_movie, mock_notify_serv):
    """Создаем фильм по АПИ — возвращаем MovieResponse."""
    movi_kp: KinopoiskMovieResponse = make_kinopoisk_movie(name="Титаник", id_kino=4, movie_type="test type tit")
    mock_movie_repo.create.return_value = make_movie(name="Титаник", id_kino=4)

    service = MovieService(repository=mock_movie_repo, kinopoisk_client=mock_kino_client, notification_service=mock_notify_serv)

    result = await service.create_movie(movi_kp)

    assert result.name == "Титаник"
    mock_movie_repo.create.assert_called_once()
    mock_movie_repo.create.assert_called_once_with(movi_kp.model_dump())


@pytest.mark.asyncio
async def test_create_movie_by_user(mock_movie_repo, mock_kino_client, make_movie_data, make_movie, mock_notify_serv):
    """Создаем фильм по данным от пользователя через MovieCreate — возвращаем MovieResponse."""
    movi_kp: MovieCreate = make_movie_data(name="Титаник2", id_kino=3, movie_type="test type tit")
    mock_movie_repo.create.return_value = make_movie(name="Титаник2", id_kino=3)

    service = MovieService(repository=mock_movie_repo, kinopoisk_client=mock_kino_client, notification_service=mock_notify_serv)

    result = await service.create_movie(movi_kp)

    assert result.name == "Титаник2"
    mock_movie_repo.create.assert_called_once_with(movi_kp.model_dump())


@pytest.mark.asyncio
async def test_update_movie_by_user(mock_movie_repo, mock_kino_client, make_movie_data, make_movie, mock_notify_serv):
    """Обновляем фильм по ID через MovieUpdate — возвращаем MovieResponse."""
    movi_data_update: MovieUpdate = make_movie_data(name="Новый", description="Абсолютно новый")
    movi_id = 1
    movi_orm = make_movie(name="Новый", description="Абсолютно новый", id=1)
    mock_movie_repo.update.return_value = movi_orm

    service = MovieService(repository=mock_movie_repo, kinopoisk_client=mock_kino_client, notification_service=mock_notify_serv)

    result = await service.update_movie(movi_id, movi_data_update)

    assert result.name == "Новый"
    mock_movie_repo.update.assert_called_once_with(
        movi_id,
        movi_data_update.model_dump(exclude_unset=True)
    )


@pytest.mark.asyncio
async def test_update_movie_by_user_not_found(mock_movie_repo, mock_kino_client, make_movie_data, make_movie, mock_notify_serv):
    """Фильм не найден — выбрасываем исключение."""
    movi_data_update: MovieUpdate = make_movie_data(name="Новый", description="Абсолютно новый")
    movi_id = 1
    mock_movie_repo.update.return_value = None

    service = MovieService(repository=mock_movie_repo, kinopoisk_client=mock_kino_client, notification_service=mock_notify_serv)

    with pytest.raises(MovieNotFoundError):
        await service.update_movie(movi_id, movi_data_update)
