import re
import pytest
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession


BASE_URL = "/health"


# ================== INTEGRATION TESTS ==================

def test_health_success_full_payload(client):
    resp = client.get("/health")

    assert resp.status_code == status.HTTP_200_OK

    data = resp.json()
    assert data == {
        "status": "healthy",
        "database": "connected",
        "timestamp": data["timestamp"],
    }


def test_health_response_structure(client):
    resp = client.get(BASE_URL)
    data = resp.json()

    assert "status" in data
    assert "database" in data
    assert "timestamp" in data


def test_health_status_healthy(client):
    resp = client.get(BASE_URL)
    assert resp.json()["status"] == "healthy"


def test_health_database_connected(client):
    resp = client.get(BASE_URL)
    assert resp.json()["database"] == "connected"


def test_health_timestamp_iso_format(client):
    resp = client.get(BASE_URL)
    timestamp = resp.json()["timestamp"]

    iso_regex = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"
    assert re.match(iso_regex, timestamp)


# ================== UNIT TESTS (monkeypatch) ==================

@pytest.mark.asyncio
async def test_health_db_exception_returns_503(client, monkeypatch):
    async def broken_execute(*args, **kwargs):
        raise Exception("DB is down")

    monkeypatch.setattr(
        AsyncSession,
        "execute",
        broken_execute,
    )

    resp = client.get(BASE_URL)
    assert resp.status_code == status.HTTP_503_SERVICE_UNAVAILABLE


@pytest.mark.asyncio
async def test_health_db_exception_status_unhealthy(client, monkeypatch):
    async def broken_execute(*args, **kwargs):
        raise Exception("DB is down")

    monkeypatch.setattr(
        AsyncSession,
        "execute",
        broken_execute,
    )

    resp = client.get(BASE_URL)
    data = resp.json()

    assert data["status"] == "unhealthy"
    assert data["database"] == "unavailable"


@pytest.mark.asyncio
async def test_health_db_exception_has_timestamp(client, monkeypatch):
    async def broken_execute(*args, **kwargs):
        raise Exception("DB is down")

    monkeypatch.setattr(
        AsyncSession,
        "execute",
        broken_execute,
    )

    resp = client.get(BASE_URL)
    assert "timestamp" in resp.json()

@pytest.mark.asyncio
async def test_health_db_exception_timestamp_is_string(client, monkeypatch):
    async def broken_execute(*args, **kwargs):
        raise Exception("DB down")

    monkeypatch.setattr(
        AsyncSession,
        "execute",
        broken_execute,
    )

    resp = client.get("/health")
    timestamp = resp.json()["timestamp"]

    assert isinstance(timestamp, str)
    assert timestamp.endswith("Z")