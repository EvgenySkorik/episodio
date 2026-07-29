from app.clients.vk_client import VkClient
from app.core.logging import get_logger
from app.repositories.bases.base_movie import BaseMovieRepository
from app.repositories.bases.base_user import BaseUserRepository


logger = get_logger(__name__)

class NotificationService:
    """Сервис для работы с Уведомлениями"""

    def __init__(self, movie_repository: BaseMovieRepository, user_repository: BaseUserRepository, vk_client: VkClient):
        self._movi_repo = movie_repository
        self._user_repo = user_repository
        self._vk_client = vk_client

    async def send_notification(self, user_id: int, name: str, new_episodes: int) -> None:
        """Отправляет уведомление пользователю о новой серии."""
        await self._vk_client.send_message(
            user_id,
            f"Ура! У сериала {name} вышел эпизод № {new_episodes}"
        )
        logger.info(f"Уведомление отправлено пользователю {user_id} о сериале '{name}'")