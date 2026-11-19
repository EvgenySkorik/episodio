# BETA
from fastapi import WebSocket

from app.core.logging import get_logger
from app.infrastructure.redis_client import RedisChatClient

logger = get_logger(__name__)


class ConnectionManager:
    def __init__(self, redis_client: RedisChatClient) -> None:
        self.active_connections: list[WebSocket] = []
        self._redis = redis_client

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)
        history = await self._redis.get_history()
        await websocket.send_json({"type": "history", "messages": history})

    async def broadcast(self, payload: dict) -> None:
        await self._redis.add_message(payload)
        for connection in list(self.active_connections):
            try:
                await connection.send_json(payload)
            except Exception as e:  # noqa: BLE001
                logger.warning(f"Ошибка отправки сообщения: {e}")
                self.disconnect(connection)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
