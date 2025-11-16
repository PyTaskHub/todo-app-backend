"""
Pytest configuration and fixtures.
"""
import pytest
from typing import Generator
from fastapi.testclient import TestClient

from app.main import app


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


# Add more fixtures as needed:
# - Database session fixture
# - Test user fixture
# - Authentication token fixture
# etc.