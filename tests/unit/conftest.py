import pytest

from tests.fixtures.data import get_fake_movie, get_fake_movie_from_kinopoisk, get_fake_movie_from_user, get_fake_user
from tests.fixtures.mocks import (
    mock_movie_repo, mock_kino_client,
    mock_user_repo, mock_notify_serv,
    make_http_client, make_async_session_local
)


@pytest.fixture
def make_movie():
    return get_fake_movie


@pytest.fixture
def make_kinopoisk_movie():
    return get_fake_movie_from_kinopoisk


@pytest.fixture
def make_movie_data():
    return get_fake_movie_from_user


@pytest.fixture
def make_user():
    return get_fake_user
