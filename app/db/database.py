from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings
from app.core.logging import get_logger
from app.db.models import Base

logger = get_logger(__name__)

AsyncEngine = create_async_engine(settings.postgres.url, echo=False)
AsyncSessionLocal = async_sessionmaker(
    bind=AsyncEngine, expire_on_commit=False, class_=AsyncSession
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Генерирует асинхронную сессию для каждого запроса."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_tables():
    async with AsyncEngine.begin() as conn:
        logger.info("Таблицы созданы")
        await conn.run_sync(Base.metadata.create_all)


async def delete_tables():
    async with AsyncEngine.begin() as conn:
        logger.info("Таблицы удалены")
        await conn.run_sync(Base.metadata.drop_all)
