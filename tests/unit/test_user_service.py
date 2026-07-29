import pytest

from app.schemas.user_schemas import UserResponse, UserCreate, UserUpdate
from app.core.exceptions import UserNotFoundError
from app.services.user import UserService


@pytest.mark.asyncio
async def test_get_user_by_id_found(mock_user_repo, make_user):
    """Пользователь найден — возвращаем UserResponse."""

    user = make_user(first_name="Пётр", id=5)
    mock_user_repo.get_by_id.return_value = user
    service = UserService(user_repo=mock_user_repo)

    result = await service.get_user_by_id(1)

    assert result.first_name == "Пётр"
    assert result.id == 5
    assert isinstance(result, UserResponse)
    mock_user_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(mock_user_repo):
    """Пользователь не найден — выбрасываем исключение."""
    mock_user_repo.get_by_id.return_value = None

    service = UserService(user_repo=mock_user_repo)

    with pytest.raises(UserNotFoundError):
        await service.get_user_by_id(999)


@pytest.mark.asyncio
async def test_get_user_by_vk_id_found(mock_user_repo, make_user):
    """Пользователь найден по VK ID — возвращаем UserResponse."""
    user = make_user(first_name="Пётр", id=5, id_vk=555)
    mock_user_repo.get_by_vk_id.return_value = user
    service = UserService(user_repo=mock_user_repo)

    result = await service.get_user_by_vk_id(555)

    assert result.first_name == "Пётр"
    assert result.id == 5
    assert result.id_vk == 555
    assert isinstance(result, UserResponse)
    mock_user_repo.get_by_vk_id.assert_called_once_with(555)


@pytest.mark.asyncio
async def test_get_user_by_vk_id_not_found(mock_user_repo, make_user):
    """Пользователь не найден по VK ID — выбрасываем исключение"""
    mock_user_repo.get_by_vk_id.return_value = None
    service = UserService(user_repo=mock_user_repo)

    with pytest.raises(UserNotFoundError):
        await service.get_user_by_vk_id(999)


@pytest.mark.asyncio
async def test_update_user_found(mock_user_repo, make_user):
    """Обновляем пользователя — проверяем вызов репозитория."""
    updated_user = make_user(first_name="TEST", last_name="t", telephone="234", avatar="ww")
    mock_user_repo.update.return_value = updated_user

    service = UserService(user_repo=mock_user_repo)

    result = await service.update_user(
        user_id=5,
        user=UserUpdate(first_name='TEST', last_name='t', telephone='234', avatar='ww')
    )

    assert result.first_name == "TEST"
    assert result.id == updated_user.id
    assert isinstance(result, UserResponse)
    mock_user_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_user_not_found(mock_user_repo):
    """Пользователь не найден при обновлении — выбрасываем исключение."""
    mock_user_repo.update.return_value = None
    service = UserService(user_repo=mock_user_repo)

    with pytest.raises(UserNotFoundError):
        await service.update_user(999, UserUpdate(first_name="X", last_name='t', telephone='234', avatar='ww'))


@pytest.mark.asyncio
async def test_create_user(mock_user_repo, make_user):
    mock_user_repo.create.return_value = make_user(id=1, first_name="Пётр")

    service = UserService(user_repo=mock_user_repo)

    result = await service.create_user(UserCreate(
        first_name='Пётр',
        id_vk=555,
        last_name='t',
        telephone='234',
        avatar='ww'
    )
    )

    assert isinstance(result, UserResponse)
    assert result.first_name == "Пётр"
    assert result.id == 1
    mock_user_repo.create.assert_called_once()

@pytest.mark.asyncio
async def test_delete_user_found(mock_user_repo):
    """Пользователь удалён — без ошибок."""
    mock_user_repo.delete.return_value = True
    service = UserService(user_repo=mock_user_repo)

    await service.delete_user(5)
    mock_user_repo.delete.assert_called_once_with(5)

@pytest.mark.asyncio
async def test_delete_user_not_found(mock_user_repo):
    """Пользователь не найден при удалении — выбрасываем исключение."""
    mock_user_repo.delete.return_value = False
    service = UserService(user_repo=mock_user_repo)

    with pytest.raises(UserNotFoundError):
        await service.delete_user(999)