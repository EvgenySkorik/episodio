from unittest.mock import AsyncMock, patch

import pytest

from app.factories import create_container
from app.services.movie import MovieService
from app.services.notification import NotificationService
from app.services.user import UserService


@pytest.mark.asyncio
async def test_create_container_returns_container():
    """Контейнер возвращает все три сервиса с правильными типами."""

    with (patch("app.factories.AsyncSessionLocal") as mock_session_factory,
          patch("app.factories.HTTPClient") as mock_http_client_factory):

        mock_session_factory.return_value = AsyncMock()
        mock_http_client_factory.return_value = AsyncMock()

        async with create_container() as c:
            assert isinstance(c.movie_service, MovieService)
            assert isinstance(c.user_service, UserService)
            assert isinstance(c.notification_service, NotificationService)

@pytest.mark.asyncio
async def test_create_container_closes_session():
    """Сессия БД закрывается после выхода из контекста."""
    with (
        patch("app.factories.AsyncSessionLocal") as mock_session_factory,
        patch("app.factories.HTTPClient") as mock_http_client_factory,
    ):
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session
        mock_http_client_factory.return_value = AsyncMock()

        async with create_container():
            pass

        mock_session.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_container_closes_http_client():
    """HTTP-клиент закрывается после выхода из контекста."""
    with (
        patch("app.factories.AsyncSessionLocal") as mock_session_factory,
        patch("app.factories.HTTPClient") as mock_http_client_factory,
    ):
        mock_session_factory.return_value = AsyncMock()
        mock_client = AsyncMock()
        mock_http_client_factory.return_value = mock_client

        async with create_container():
            pass

        mock_client.close.assert_awaited_once()

@pytest.mark.asyncio
async def test_create_container_closes_resources_on_exception():
    """Ресурсы закрываются даже при исключении внутри контекста."""
    with (
        patch("app.factories.AsyncSessionLocal") as mock_session_factory,
        patch("app.factories.HTTPClient") as mock_http_client_factory,
    ):
        mock_session = AsyncMock()
        mock_session_factory.return_value = mock_session
        mock_client = AsyncMock()
        mock_http_client_factory.return_value = mock_client

        with pytest.raises(ValueError, match="Тестовое исключение"):
            async with create_container():
                raise ValueError("Тестовое исключение")

        mock_session.close.assert_awaited_once()
        mock_client.close.assert_awaited_once()