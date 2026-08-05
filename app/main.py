from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from hawk_python_sdk.modules.fastapi import HawkFastapi
from prometheus_fastapi_instrumentator import Instrumentator
from starlette.middleware.cors import CORSMiddleware

from app.api.except_handlers import register_exception_handlers
from app.api.v1.admin import admin_rout
from app.api.v1.auth import auth_rout
from app.api.v1.movies import movies_rout
from app.api.v1.users import users_rout
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.database import create_tables
from app.infrastructure.hawk_client import HawkClient
from app.infrastructure.http_client import HTTPClient


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.http_client = HTTPClient()
    app.state.hawk_client = HawkClient()
    await create_tables()
    yield
    await app.state.http_client.close()
    # await delete_tables()


setup_logging()
app = FastAPI(
    title=settings.title,
    description=settings.description,
    version=settings.version,
    lifespan=lifespan,
)

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

hawk = HawkFastapi({
    'app_instance': app,
    'token': settings.hawk_secret_token,
})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(movies_rout)
app.include_router(users_rout)
app.include_router(auth_rout)
app.include_router(admin_rout)
@app.get("/")
async def root():
    return {"status": "ok"}



