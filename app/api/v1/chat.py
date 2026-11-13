# BETA
from datetime import UTC, datetime
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.infrastructure.redis_client import RedisChatClient
from app.infrastructure.websocket_manager import ConnectionManager

chat_rout = APIRouter(tags=["chat"])

@chat_rout.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket) -> None:
    redis_client: RedisChatClient = websocket.app.state.redis_chat_client
    manager = ConnectionManager(redis_client)
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            message_text = str(data.get("message", "")).strip()
            if not message_text:
                continue
            payload = {
                "type": "message",
                "user_id": int(data.get("user_id", 0)),
                "user_name": str(data.get("user_name") or "Аноним"),
                "message": message_text[:2000],
                "timestamp": datetime.now(UTC).isoformat(),
            }
            await manager.broadcast(payload)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)