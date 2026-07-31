from fastapi import APIRouter

from app.api.dependencies import VkUserIdDep
from app.core.logging import get_logger
from app.infrastructure.security import create_jwt

logger = get_logger(__name__)

auth_rout = APIRouter(prefix="/auth", tags=["auth"])


@auth_rout.post("/vk")
async def auth_vk(vk_id: VkUserIdDep):
    """Обменивает VK параметры на JWT токен."""
    token = create_jwt(vk_id)
    return {"access_token": token, "token_type": "bearer"}


