import uuid

import pytest

BASE_URL = "/api/v1/users"


# ================== HELPERS ==================


def create_user_and_login(client):
    user_data = {
        "username": f"user_{uuid.uuid4().hex}",
        "email": f"{uuid.uuid4().hex}@example.com",
        "password": "password123",
    }

    r = client.post("/api/v1/auth/register", json=user_data)
    assert r.status_code == 201

    login = client.post(
        "/api/v1/auth/login",
        json={
            "email": user_data["email"],
            "password": user_data["password"],
        },
    )
    assert login.status_code == 200

    token = login.json()["access_token"]
    return user_data, {"Authorization": f"Bearer {token}"}


# ================== FIXTURES ==================


@pytest.fixture
def user_and_auth_headers(client):
    return create_user_and_login(client)


@pytest.fixture
def auth_headers(user_and_auth_headers):
    _, headers = user_and_auth_headers
    return headers


# ================== GET /me ==================


def test_get_me_success(client, auth_headers):
    resp = client.get(f"{BASE_URL}/me", headers=auth_headers)
    assert resp.status_code == 200

    data = resp.json()
    assert "id" in data
    assert "email" in data
    assert "username" in data
    assert "password_hash" not in data


def test_get_me_unauthorized(client):
    resp = client.get(f"{BASE_URL}/me")
    assert resp.status_code == 401


# ================== PUT /me ==================


def test_update_me_email(client, auth_headers):
    resp = client.put(
        f"{BASE_URL}/me",
        headers=auth_headers,
        json={"email": f"{uuid.uuid4().hex}@example.com"},
    )
    assert resp.status_code == 200
    assert "email" in resp.json()


def test_update_me_first_name(client, auth_headers):
    resp = client.put(
        f"{BASE_URL}/me",
        headers=auth_headers,
        json={"first_name": "John"},
    )
    assert resp.status_code == 200
    assert resp.json()["first_name"] == "John"


def test_update_me_last_name(client, auth_headers):
    resp = client.put(
        f"{BASE_URL}/me",
        headers=auth_headers,
        json={"last_name": "Doe"},
    )
    assert resp.status_code == 200
    assert resp.json()["last_name"] == "Doe"


def test_update_me_all_fields(client, auth_headers):
    resp = client.put(
        f"{BASE_URL}/me",
        headers=auth_headers,
        json={
            "email": f"{uuid.uuid4().hex}@example.com",
            "first_name": "Jane",
            "last_name": "Smith",
        },
    )
    assert resp.status_code == 200


def test_update_me_duplicate_email(client):
    user1, headers1 = create_user_and_login(client)
    _, headers2 = create_user_and_login(client)

    resp = client.put(
        f"{BASE_URL}/me",
        headers=headers2,
        json={"email": user1["email"]},
    )

    assert resp.status_code == 409


def test_update_me_same_email_allowed(client, auth_headers):
    me = client.get(f"{BASE_URL}/me", headers=auth_headers).json()

    resp = client.put(
        f"{BASE_URL}/me",
        headers=auth_headers,
        json={"email": me["email"]},
    )

    assert resp.status_code == 200


def test_update_me_validation_error(client, auth_headers):
    resp = client.put(
        f"{BASE_URL}/me",
        headers=auth_headers,
        json={"email": "not-an-email"},
    )
    assert resp.status_code == 422


def test_update_me_unauthorized(client):
    resp = client.put(
        f"{BASE_URL}/me",
        json={"first_name": "Fail"},
    )
    assert resp.status_code == 401


def test_update_me_empty_payload_returns_same_user(client, auth_headers):
    resp = client.put("/api/v1/users/me", headers=auth_headers, json={})

    assert resp.status_code == 200


# ================== POST /me/change-password ==================


def test_change_password_success(client, user_and_auth_headers):
    user, headers = user_and_auth_headers

    resp = client.post(
        f"{BASE_URL}/me/change-password",
        headers=headers,
        json={
            "current_password": user["password"],
            "new_password": "newpassword123",
        },
    )

    assert resp.status_code == 200
    assert resp.json()["message"] == "Password changed successfully"


def test_change_password_wrong_current(client, user_and_auth_headers):
    _, headers = user_and_auth_headers

    resp = client.post(
        f"{BASE_URL}/me/change-password",
        headers=headers,
        json={
            "current_password": "wrong",
            "new_password": "newpassword123",
        },
    )

    assert resp.status_code == 401


def test_change_password_validation_error(client, auth_headers):
    resp = client.post(
        f"{BASE_URL}/me/change-password",
        headers=auth_headers,
        json={
            "current_password": "123",
            "new_password": "short",
        },
    )

    assert resp.status_code == 422


def test_change_password_unauthorized(client):
    resp = client.post(
        f"{BASE_URL}/me/change-password",
        json={
            "current_password": "x",
            "new_password": "newpassword123",
        },
    )
    assert resp.status_code == 401


def test_change_password_and_login_with_new_password(client):
    user, headers = create_user_and_login(client)

    client.post(
        f"{BASE_URL}/me/change-password",
        headers=headers,
        json={
            "current_password": user["password"],
            "new_password": "newpassword123",
        },
    )

    old_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": user["password"],
        },
    )
    assert old_login.status_code == 401

    new_login = client.post(
        "/api/v1/auth/login",
        json={
            "email": user["email"],
            "password": "newpassword123",
        },
    )
    assert new_login.status_code == 200


def test_change_password_response_message(client):
    user, headers = create_user_and_login(client)

    resp = client.post(
        "/api/v1/users/me/change-password",
        headers=headers,
        json={
            "current_password": user["password"],
            "new_password": "NewStrongPass123",
        },
    )

    assert resp.status_code == 200
    assert resp.json()["message"] == "Password changed successfully"
