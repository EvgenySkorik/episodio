from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from app.api.dependencies import AdminVkIdDep, ServiceAiDep
from app.core.logging import get_logger
from app.infrastructure.security import (
    read_log_file,
    read_log_lines,
    verify_admin_password,
)
from app.schemas.user_schemas import UserLoginPass

logger = get_logger(__name__)

admin_rout = APIRouter(prefix="/admin", tags=["admin"])


@admin_rout.get("/check", summary="Проверка, что пользователь — админ")
async def check_admin(
    _vk_id: AdminVkIdDep,
) -> dict[str, bool]:
    """Возвращает is_admin=True, если vk_id в whitelist (иначе 403)."""
    return {"is_admin": True}


@admin_rout.post("/login", summary="Вход в админку")
async def admin_login(
    password: UserLoginPass,
    _vk_id: AdminVkIdDep,
) -> dict[str, bool]:
    """Проверяет пароль. vk_id уже проверен через AdminVkIdDep."""
    if not verify_admin_password(password.password):
        raise HTTPException(403, "Неверный пароль")
    return {"ok": True}


@admin_rout.post("/logs", summary="Получить логи")
async def get_logs(
    _vk_id: AdminVkIdDep,
) -> JSONResponse:
    """
    Получить содержимое файла логов.
    """
    logs = await read_log_file()

    return JSONResponse(
        status_code=200, content={"logs": logs, "size": len(logs.split("\n"))}
    )


@admin_rout.post("/logs/latest", summary="Получить последние N логи")
async def get_latest_logs(
    _vk_id: AdminVkIdDep,
    lines: int = 50,
) -> JSONResponse:
    """Получить последние N строк логов"""
    logs = await read_log_lines(lines)

    return JSONResponse(status_code=200, content={"logs": logs, "lines": lines})


@admin_rout.post("/ai-balance", summary="Баланс GigaChat")
async def ai_balance(
    _vk_id: AdminVkIdDep,
    ai_service: ServiceAiDep,
):
    return await ai_service._client.balance()


@admin_rout.post("/ai-models", summary="Модели для GigaChat")
async def ai_models(
    _vk_id: AdminVkIdDep,
    ai_service: ServiceAiDep,
):
    return await ai_service._client.models()
