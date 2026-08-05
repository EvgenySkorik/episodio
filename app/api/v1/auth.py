import json

from fastapi import APIRouter, HTTPException, Request

from app.api.dependencies import ServiceUserDep
from app.core.logging import get_logger
from app.infrastructure.security import create_jwt

logger = get_logger(__name__)

auth_rout = APIRouter(prefix="/auth", tags=["auth"])


@auth_rout.post("/vk")
async def auth_vk(
        request: Request,
        user_service: ServiceUserDep,
) -> dict[str, str]:
    vk_id = None
    try:
        body = await request.json()
        vk_id = body.get("vk_user_id")
    except json.JSONDecodeError:
        pass

    if not vk_id:
        vk_id = request.query_params.get("vk_user_id")

    if not vk_id:
        raise HTTPException(400, "Missing vk_user_id")

    vk_id = int(vk_id)
    await user_service.get_or_create_user(vk_id)

    token = create_jwt(vk_id)
    return {"access_token": token, "token_type": "bearer"}




