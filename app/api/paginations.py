from pydantic import BaseModel, Field

from app.core.config import settings


class PaginationParams(BaseModel):
    limit: int = Field(
        default=settings.pagination.default_limit,
        ge=1,
        le=100
    )
    page: int = Field(
        default=settings.pagination.default_page,
        ge=1
    )

