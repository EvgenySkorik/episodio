from app.clients.sber_ai_client import GigaAiClient


class AiService:
    def __init__(self, client: GigaAiClient):
        self._client = client

    async def enhance_movie_description(self, description: str) -> str:
        """Переписать описание фильма с юмором."""
        SYSTEM = (
            "Ты кинокритик с юмором, бери описание фильма и переделывай его с большой долей сарказма и юмора! "
            "Отвечай сразу описанием, без обращения к пользователю, не длиннее 500 символов"
        )
        USER = f"Переделай текст в смешном , можно даже немного стебном с жаргонными выражениями формате: {description}"

        return await self._client.generate(SYSTEM, USER)
