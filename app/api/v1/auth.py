from fastapi import APIRouter, HTTPException, Request

from app.api.dependencies import VkUserIdDep, ServiceUserDep
from app.core.logging import get_logger
from app.infrastructure.security import create_jwt

logger = get_logger(__name__)

auth_rout = APIRouter(prefix="/auth", tags=["auth"])


@auth_rout.post("/vk")
async def auth_vk(
        request: Request,
        user_service: ServiceUserDep,
):
    vk_id = int(request.query_params.get("vk_user_id", 0))
    if not vk_id:
        raise HTTPException(400, "Missing vk_user_id")

    await user_service.get_or_create_user(vk_id)

    token = create_jwt(vk_id)
    return {"access_token": token, "token_type": "bearer"}


