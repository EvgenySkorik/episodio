from gigachat import Chat, GigaChat, Messages, MessagesRole, RateLimitError, ServerError

from app.core.config import AppSettings
from app.core.exceptions.exceptions import GigaChatError


class GigaAiClient:
    def __init__(self, settings: AppSettings):
        self._client = GigaChat(
            base_url=settings.giga_ai.base_url,
            credentials=settings.giga_ai.credentials,
            model=settings.giga_ai.model,
            scope="GIGACHAT_API_PERS",
            max_retries=3,
            retry_backoff_factor=0.5,
        )

    async def generate(self, system_prompt: str, user_prompt: str) -> str:
        """Универсальный метод: принимает промты, возвращает ответ."""

        chat = Chat(
            messages=[
                Messages(role=MessagesRole.SYSTEM, content=system_prompt),
                Messages(role=MessagesRole.USER, content=user_prompt),
            ],
        )

        try:
            response = await self._client.achat(chat)
        except RateLimitError:
            raise GigaChatError("Превышен лимит запросов к GigaChat")
        except ServerError:
            raise GigaChatError("GigaChat временно недоступен")
        return response.choices[0].message.content

    async def models(self) -> list[str]:
        """Получить список доступных моделей от СберAI"""
        try:
            response = await self._client.aget_models()
        except (ServerError, RateLimitError):
            raise GigaChatError("GigaChat временно недоступен")
        return [m.id_ for m in response.data]

    async def balance(self) -> list[tuple[str, float]]:
        """Получить баланс токенов моделей
        Returns: List[tuple[str, float]]
        """
        try:
            response = await self._client.aget_balance()
        except (ServerError, RateLimitError):
            raise GigaChatError("GigaChat временно недоступен")
        return [(b.usage, b.value) for b in response.balance]
