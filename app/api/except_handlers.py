from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from httpx import HTTPStatusError
from sqlalchemy.exc import SQLAlchemyError

from app.core.exceptions.exceptions import UserNotFoundError, MovieNotFoundError, KinopoiskAPIError, AppError
from app.core.logging import get_logger

logger = get_logger(__name__)

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(UserNotFoundError)
    async def user_not_found_handler(request: Request, exc: UserNotFoundError):
        logger.warning(f"User not found: {exc}")
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(SQLAlchemyError)
    async def db_error_handler(request: Request, exc: SQLAlchemyError):
        logger.error(f"Database error: {exc}", exc_info=True)
        return JSONResponse(
            status_code=500,
            content={"detail": "Ошибка базы данных. Мы уже чиним!"},
        )

    @app.exception_handler(MovieNotFoundError)
    async def movie_not_found_handler(request: Request, exc: MovieNotFoundError):
        logger.warning(f"Movie not found: {exc}")
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @app.exception_handler(KinopoiskAPIError)
    async def kinopoisk_api_error_handler(request: Request, exc: KinopoiskAPIError):
        logger.error(f"Kinopoisk API error: {exc}")
        return JSONResponse(status_code=503, content={"detail": "Сервис Кинопоиска временно недоступен"})

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        logger.error(f"App error: {exc}")
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(HTTPStatusError)
    async def http_status_error_handler(request: Request, exc: HTTPStatusError):
        logger.error(f"API error: {exc}")
        return JSONResponse(
            status_code=exc.response.status_code,
            content={"detail": "Ошибка внешнего сервиса"}
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {exc}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": "Внутренняя ошибка сервера"})