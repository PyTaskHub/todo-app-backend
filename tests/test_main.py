"""
Basic tests for the main application.
"""

from fastapi.testclient import TestClient


def test_root_endpoint(client: TestClient):
    """
    Test root endpoint returns correct response.
    """
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert data["version"] == "1.0.0"


def test_docs_available(client: TestClient):
    """
    Test that API documentation is accessible.
    """
    response = client.get("/api/docs")
    assert response.status_code == 200


def test_openapi_schema(client: TestClient):
    """
    Test that OpenAPI schema is available.
    """
    response = client.get("/api/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "PyTaskHub"
