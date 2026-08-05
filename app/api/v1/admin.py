from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.core.exceptions.exceptions import TestError
from app.core.logging import get_logger
from app.infrastructure.security import (
    read_log_file,
    read_log_lines,
    verify_admin_password,
)
from app.schemas.user_schemas import UserLoginPass

logger = get_logger(__name__)

admin_rout = APIRouter(prefix="/admin", tags=["admin"])


@admin_rout.get("/trigger-error")
async def trigger_error():
    """
       Тестовый эндпоинт для проверки Hawk.
       Вызывает исключение, которое должно быть отправлено в Hawk.
       """
    logger.warning("Вызван тестовый эндпоинт /trigger-error")
    raise TestError("Тестовая ошибка для Hawk!")

@admin_rout.post("/logs", summary="Получить логи")
async def get_logs(
        request: Request,
        password: UserLoginPass,
) -> JSONResponse:
    """
        Получить содержимое файла логов.
    """
    if not verify_admin_password(password.password):
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"Неудачная попытка доступа к логам с IP: {client_ip}")
        raise HTTPException(status_code=403, detail="Неверный пароль")

    logs = await read_log_file()

    return JSONResponse(
        status_code=200,
        content={
        "logs": logs,
        "size": len(logs.split('\n'))
        }
    )


@admin_rout.post("/logs/latest", summary="Получить последние N логи")
async def get_latest_logs(
        request: Request,
        password: UserLoginPass,
        lines: int = 50,
) -> JSONResponse:
    """Получить последние N строк логов"""
    if not verify_admin_password(password.password):
        client_ip = request.client.host if request.client else "unknown"
        logger.warning(f"Неудачная попытка доступа к логам с IP: {client_ip}")
        raise HTTPException(status_code=403, detail="Неверный пароль")

    logs = await read_log_lines(lines)

    return JSONResponse(
        status_code=200,
        content={
            "logs": logs,
            "lines": lines
        }
    )


