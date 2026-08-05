from fastapi import APIRouter, HTTPException, Request

from app.api.dependencies import ServiceUserDep
from app.core.config import settings
from app.core.logging import get_logger
from app.infrastructure.security import create_jwt
from scripts.scr1 import get_logs_file

logger = get_logger(__name__)

auth_rout = APIRouter(prefix="/auth", tags=["auth"])


@auth_rout.post("/vk")
async def auth_vk(
        request: Request,
        user_service: ServiceUserDep,
):
    vk_id = None
    try:
        body = await request.json()
        vk_id = body.get("vk_user_id")
    except:
        pass

    if not vk_id:
        vk_id = request.query_params.get("vk_user_id")

    if not vk_id:
        raise HTTPException(400, "Missing vk_user_id")

    vk_id = int(vk_id)
    await user_service.get_or_create_user(vk_id)

    token = create_jwt(vk_id)
    return {"access_token": token, "token_type": "bearer"}

#-----------Сервисные ручки-----------
@auth_rout.get("/trigger-error")
async def trigger_error():
    raise Exception("Тестовая ошибка для Hawk!")

@auth_rout.get("/logs")
async def get_logs(
        password: str
):
    if password != settings.logs_password:
        return {"status": "нет доступа"}
    try:
        f = get_logs_file()
        return {"logs": f}
    except FileNotFoundError:
        return {"status": "Файл логов не найден"}
    except Exception as e:
        return {"status": f"Ошибка: {str(e)}"}


