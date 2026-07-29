import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient


@pytest.fixture
def movies():
    return [
    {
        "id": 1,
        "title": "Оппенгеймер",
        "year": 2023,
        "rating": 8.5,
        "genre": ["биография", "драма", "история"],
        "director": "Кристофер Нолан"
    },
    {
        "id": 2,
        "title": "Барби",
        "year": 2023,
        "rating": 7.8,
        "genre": ["комедия", "фэнтези"],
        "director": "Грета Гервиг"
    },
    {
        "id": 3,
        "title": "Дюна: Часть вторая",
        "year": 2024,
        "rating": 8.7,
        "genre": ["фантастика", "боевик", "драма"],
        "director": "Дени Вильнёв"
    },
    {
        "id": 4,
        "title": "Бедные-несчастные",
        "year": 2023,
        "rating": 7.9,
        "genre": ["комедия", "драма", "фэнтези"],
        "director": "Йоргос Лантимос"
    }
]




@pytest.fixture(scope="session")
def app():
    """Экземпляр FastAPI"""
    _app: FastAPI = FastAPI(title="Test APP")

    from app.api.v1.movies import movies_rout

    _app.include_router(movies_rout)

    return _app


@pytest.fixture
def client(app: FastAPI):
    """Клиент для тестов"""
    with TestClient(app) as client:
        yield client

# @pytest.fixture(scope="session")
# def setup_database(app):
#     """Создание движка и таблиц БД для тестов"""
#     _engine = create_async_engine(
#         "sqlite+aiosqlite:///:memory:",
#         connect_args={"check_same_thread": False},
#         poolclass=StaticPool,
#     )
#
#     async def init_tables():
#         async with _engine.begin() as conn:
#             await conn.run_sync(Base.metadata.create_all)
#
#     asyncio.run(init_tables())

# TestingSessionLocal = async_sessionmaker(
#     _engine, expire_on_commit=False, class_=AsyncSession
# )
#
# async def override_get_db():
#     async with TestingSessionLocal() as session:
#         yield session

# async def create_test_users():
#     async with TestingSessionLocal() as session:
#         user1 = User(**TEST_USER_1)
#         user2 = User(**TEST_USER_2)
#         user3 = User(**TEST_USER_3)
#         session.add_all([user1, user2, user3])
#         await session.commit()
#
# asyncio.run(create_test_users())
#
# app.dependency_overrides[get_db] = override_get_db  # type: ignore
#
# return _engine


# @pytest.fixture
# def client(app: FastAPI):
#     """Клиент для тестов"""
#     with TestClient(app) as client:
#         yield client
