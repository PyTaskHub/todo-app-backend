import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import auth as auth_endpoints
from app.schemas.user import UserCreate, UserLogin
from app.schemas.token import RefreshTokenRequest


# =============== /auth/register ===============


def test_register_success(client):
    payload = {
        "username": "new_user",
        "email": "new_user@example.com",
        "password": "securepass123",
    }

    response = client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["is_active"] is True
    assert "id" in data


def test_register_duplicate_email(client):
    first = {
        "username": "dup_user1",
        "email": "duplicate@example.com",
        "password": "password123",
    }
    second = {
        "username": "dup_user2",
        "email": "duplicate@example.com",
        "password": "password123",
    }

    resp1 = client.post("/api/v1/auth/register", json=first)
    assert resp1.status_code == 201

    resp2 = client.post("/api/v1/auth/register", json=second)
    # In the implementation, 409 is used for conflicts
    assert resp2.status_code == 409
    assert resp2.json()["detail"] in [
        "Email already registered",
        "Username already taken",
    ]


def test_register_validation_error(client):
    # Missing username and too short password - should fail validation with 422
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "wrong", "password": "123"},
    )
    assert response.status_code == 422


def test_register_empty_fields(client):
    # Empty strings for all fields - validation error
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "", "email": "", "password": ""},
    )
    assert response.status_code == 422


def test_register_missing_fields(client):
    # No fields provided - validation error
    response = client.post("/api/v1/auth/register", json={})
    assert response.status_code == 422


# =============== /auth/login ===============


def test_login_success(client, register_user):
    response = client.post("/api/v1/auth/login", json=register_user)

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client, register_user):
    wrong_data = {
        "email": register_user["email"],
        "password": "wrongpass123",
    }

    response = client.post("/api/v1/auth/login", json=wrong_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "no_user@example.com", "password": "password123"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_long_email(client):
    long_email = "a" * 300 + "@example.com"
    response = client.post(
        "/api/v1/auth/login",
        json={"email": long_email, "password": "password123"},
    )

    # Invalid email format 422
    assert response.status_code == 422


# =============== /auth/refresh ===============


def test_refresh_valid_token(client, register_user):
    login_resp = client.post("/api/v1/auth/login", json=register_user)
    assert login_resp.status_code == 200

    tokens = login_resp.json()
    refresh_token = tokens["refresh_token"]

    resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_refresh_invalid_token(client):
    resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "not_a_real_token"},
    )

    assert resp.status_code == 401
    assert resp.json()["detail"] in [
        "Invalid token",
        "Invalid refresh token",
    ]


# =============== Protected route / JWT ===============


def test_protected_route_with_valid_token(client, access_token):
    headers = {"Authorization": f"Bearer {access_token}"}

    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert "username" in data


def test_protected_route_without_token(client):
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_protected_route_with_invalid_token(client):
    headers = {"Authorization": "Bearer invalid_token"}

    response = client.get("/api/v1/users/me", headers=headers)

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"


# =============== Direct endpoint unit tests (monkeypatched) ===============


@pytest.mark.asyncio
async def test_register_email_conflict_direct(monkeypatch):
    async def fake_get_user_by_email(db, email):
        # Return truthy value - email is already taken
        return object()

    async def fake_get_user_by_username(db, username):
        # Username is free
        return None

    monkeypatch.setattr(auth_endpoints, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_endpoints, "get_user_by_username", fake_get_user_by_username)

    user_in = UserCreate(
        username="newuser",
        email="existing@example.com",
        password="StrongPass123",
    )

    with pytest.raises(HTTPException) as exc_info:
        await auth_endpoints.register(user_in, db=None)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Email already registered"


@pytest.mark.asyncio
async def test_register_username_conflict_direct(monkeypatch):
    async def fake_get_user_by_email(db, email):
        # Email is free
        return None

    async def fake_get_user_by_username(db, username):
        # Username is already taken
        return object()

    monkeypatch.setattr(auth_endpoints, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_endpoints, "get_user_by_username", fake_get_user_by_username)

    user_in = UserCreate(
        username="taken",
        email="free@example.com",
        password="StrongPass123",
    )

    with pytest.raises(HTTPException) as exc_info:
        await auth_endpoints.register(user_in, db=None)

    assert exc_info.value.status_code == 409
    assert exc_info.value.detail == "Username already taken"


@pytest.mark.asyncio
async def test_register_success_direct(monkeypatch):
    async def fake_get_user_by_email(db, email):
        # Email is free
        return None

    async def fake_get_user_by_username(db, username):
        # Username is free
        return None

    class DummyUser:
        def __init__(self):
            self.id = 1
            self.username = "newuser"
            self.email = "new@example.com"
            self.is_active = True

    async def fake_create_user(db, user_in):
        return DummyUser()

    monkeypatch.setattr(auth_endpoints, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_endpoints, "get_user_by_username", fake_get_user_by_username)
    monkeypatch.setattr(auth_endpoints, "create_user", fake_create_user)

    user_in = UserCreate(
        username="newuser",
        email="new@example.com",
        password="StrongPass123",
    )

    user = await auth_endpoints.register(user_in, db=None)

    assert user.username == "newuser"
    assert user.email == "new@example.com"


@pytest.mark.asyncio
async def test_login_inactive_user_direct(monkeypatch):
    class DummyUser:
        def __init__(self):
            self.email = "user@example.com"
            self.id = 1
            self.username = "user"
            self.is_active = False

        def verify_password(self, password: str) -> bool:
            # Password is correct, but user is inactive
            return True

    async def fake_get_user_by_email(db, email):
        return DummyUser()

    monkeypatch.setattr(auth_endpoints, "get_user_by_email", fake_get_user_by_email)

    credentials = UserLogin(
        email="user@example.com",
        password="any-password",
    )

    with pytest.raises(HTTPException) as exc_info:
        await auth_endpoints.login(credentials, db=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Inactive user"


@pytest.mark.asyncio
async def test_login_success_direct(monkeypatch):
    class DummyUser:
        def __init__(self):
            self.id = 1
            self.email = "user@example.com"
            self.username = "user"
            self.is_active = True

        def verify_password(self, password: str) -> bool:
            return True

    async def fake_get_user_by_email(db, email):
        return DummyUser()

    def fake_create_access_token(data):
        return "access-token"

    def fake_create_refresh_token(data):
        return "refresh-token"

    monkeypatch.setattr(auth_endpoints, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(auth_endpoints, "create_access_token", fake_create_access_token)
    monkeypatch.setattr(auth_endpoints, "create_refresh_token", fake_create_refresh_token)

    credentials = UserLogin(
        email="user@example.com",
        password="password123",
    )

    token = await auth_endpoints.login(credentials, db=None)

    assert token.access_token == "access-token"
    assert token.refresh_token == "refresh-token"
    assert token.token_type == "bearer"


@pytest.mark.asyncio
async def test_refresh_success_direct(monkeypatch):
    def fake_verify_token(token: str):
        return {"type": "refresh", "user_id": 1}

    class DummyUser:
        def __init__(self):
            self.id = 1
            self.email = "user@example.com"
            self.username = "user"
            self.is_active = True

    async def fake_get_user_by_id(db, user_id: int):
        return DummyUser()

    def fake_create_access_token(data):
        return "new-access-token"

    monkeypatch.setattr(auth_endpoints, "verify_token", fake_verify_token)
    monkeypatch.setattr(auth_endpoints, "get_user_by_id", fake_get_user_by_id)
    monkeypatch.setattr(auth_endpoints, "create_access_token", fake_create_access_token)

    request = RefreshTokenRequest(refresh_token="dummy")

    resp = await auth_endpoints.refresh_access_token(request, db=None)

    assert resp.access_token == "new-access-token"
    assert resp.token_type == "bearer"


@pytest.mark.asyncio
async def test_refresh_invalid_token_type_direct(monkeypatch):
    def fake_verify_token(token: str):
        # Token type is not "refresh"
        return {"type": "access", "user_id": 1}

    monkeypatch.setattr(auth_endpoints, "verify_token", fake_verify_token)

    request = RefreshTokenRequest(refresh_token="dummy")

    with pytest.raises(HTTPException) as exc_info:
        await auth_endpoints.refresh_access_token(request, db=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token type"


@pytest.mark.asyncio
async def test_refresh_invalid_payload_no_user_id_direct(monkeypatch):
    def fake_verify_token(token: str):
        # Missing user_id in payload
        return {"type": "refresh"}

    monkeypatch.setattr(auth_endpoints, "verify_token", fake_verify_token)

    request = RefreshTokenRequest(refresh_token="dummy")

    with pytest.raises(HTTPException) as exc_info:
        await auth_endpoints.refresh_access_token(request, db=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token payload"


@pytest.mark.asyncio
async def test_refresh_user_not_found_direct(monkeypatch):
    def fake_verify_token(token: str):
        return {"type": "refresh", "user_id": 999}

    async def fake_get_user_by_id(db, user_id: int):
        # User not found in DB
        return None

    monkeypatch.setattr(auth_endpoints, "verify_token", fake_verify_token)
    monkeypatch.setattr(auth_endpoints, "get_user_by_id", fake_get_user_by_id)

    request = RefreshTokenRequest(refresh_token="dummy")

    with pytest.raises(HTTPException) as exc_info:
        await auth_endpoints.refresh_access_token(request, db=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "User not found"


@pytest.mark.asyncio
async def test_refresh_inactive_user_direct(monkeypatch):
    def fake_verify_token(token: str):
        return {"type": "refresh", "user_id": 1}

    class DummyUser:
        def __init__(self):
            self.id = 1
            self.email = "user@example.com"
            self.username = "user"
            self.is_active = False

    async def fake_get_user_by_id(db, user_id: int):
        return DummyUser()

    monkeypatch.setattr(auth_endpoints, "verify_token", fake_verify_token)
    monkeypatch.setattr(auth_endpoints, "get_user_by_id", fake_get_user_by_id)

    request = RefreshTokenRequest(refresh_token="dummy")

    with pytest.raises(HTTPException) as exc_info:
        await auth_endpoints.refresh_access_token(request, db=None)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Inactive user"