from urllib.parse import parse_qsl

from fastapi import APIRouter, HTTPException, Request

from app.api.dependencies import ServiceUserDep
from app.core.config import settings
from app.core.exceptions.exceptions import SecurityError
from app.core.logging import get_logger
from app.infrastructure.security import create_jwt, verify_vk_sign

logger = get_logger(__name__)

auth_rout = APIRouter(prefix="/auth", tags=["auth"])


@auth_rout.post("/vk")
async def auth_vk(
    request: Request,
    user_service: ServiceUserDep,
) -> dict[str, str]:
    """
    Авторизация VK Mini App.

    Принимает launch-параметры VK (query-строку или тело), проверяет
    подпись `sign` секретным ключом приложения и выдаёт JWT.
    """
    body: dict = {}
    try:
        body = await request.json()
    except Exception:  # noqa: BLE001 — тело может быть не JSON
        body = {}

    raw_params: str | None = body.get("launch_params")

    if not raw_params:
        # ХАРДКОР ДЛЯ ЛОКИ — удалить перед продом
        if settings.environment == "development":
            legacy_vk_id = body.get("vk_user_id")
            if legacy_vk_id:
                logger.warning(f"DEV: legacy auth для vk_user_id={legacy_vk_id}")
                await user_service.get_or_create_user(int(legacy_vk_id))
                token = create_jwt(int(legacy_vk_id))
                return {"access_token": token, "token_type": "bearer"}
        raise HTTPException(400, "Missing VK launch params")

    params = dict(parse_qsl(raw_params.lstrip("?"), keep_blank_values=True))

    try:
        # ХАРДКОР ДЛЯ ЛОКИ — удалить перед продом
        if settings.environment == "development" and params.get("sign") == "dev":
            vk_id = int(params["vk_user_id"])
            logger.warning(f"DEV: пропускаем проверку подписи для vk_user_id={vk_id}")
        else:
            vk_id = verify_vk_sign(params, settings.vk.secret_key)
    except SecurityError as e:
        logger.warning(f"VK sign verification failed: {e}")
        raise HTTPException(status_code=403, detail="Invalid VK signature")

    await user_service.get_or_create_user(vk_id)

    token = create_jwt(vk_id)
    logger.info(f"Успешная авторизация VK user_id={vk_id}")
    return {"access_token": token, "token_type": "bearer"}
