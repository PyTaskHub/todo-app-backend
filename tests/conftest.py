"""
Pytest configuration and fixtures.
"""
import asyncio
from typing import Generator, AsyncGenerator, Dict

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.main import app
from app.db.session import Base, get_db


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_db.sqlite"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    future=True,
)
TestingSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def _init_db() -> None:
    """
    Create all tables in the test database.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
def prepare_database() -> Generator[None, None, None]:
    """
    Initialize the test database before running tests.
    """
    asyncio.run(_init_db())
    yield
    asyncio.run(test_engine.dispose())


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency override: use the test database instead of the production one.
    """
    async with TestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def override_dependencies(prepare_database: None) -> Generator[None, None, None]:
    """
    Override application dependencies with test implementations.
    """
    app.dependency_overrides[get_db] = override_get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="module")
def client() -> Generator:
    """
    Create a test client for the FastAPI application.
    """
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture(scope="session")
def event_loop():
    """
    Create an event loop for async tests.
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def test_user_data() -> Dict[str, str]:
    """
    Provide test user registration data.
    """
    return {
        "username": "test_user",
        "email": "test_user@example.com",
        "password": "testpassword123",
    }


@pytest.fixture
def register_user(client: TestClient, test_user_data: Dict[str, str]) -> Dict[str, str]:
    """
    Register a test user and return credentials for login.
    """
    response = client.post("/api/v1/auth/register", json=test_user_data)
    # user can be created (201) or already exist from previous test (409)
    assert response.status_code in (201, 409)

    return {
        "email": test_user_data["email"],
        "password": test_user_data["password"],
    }


@pytest.fixture
def access_token(client: TestClient, register_user: Dict[str, str]) -> str:
    """
    Obtain an access token for the registered test user.
    """
    response = client.post("/api/v1/auth/login", json=register_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    return data["access_token"]
    
# Add more fixtures as needed (e.g. database session)