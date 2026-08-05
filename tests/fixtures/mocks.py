from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_movie_repo():
    """Фейковый MovieRepository."""
    return AsyncMock()


@pytest.fixture
def mock_user_repo():
    """Фейковый UserRepository."""
    return AsyncMock()


@pytest.fixture
def mock_kino_client():
    """Фейковый KinopoiskClient."""
    return AsyncMock()

@pytest.fixture
def mock_notify_serv():
    """Фейковый NotificationService."""
    return AsyncMock()

@pytest.fixture
def make_async_session_local():
    """Фейковая асинхронная сессия."""
    return AsyncMock()

@pytest.fixture
def make_http_client():
    """Фейковый http client."""
    return AsyncMock()