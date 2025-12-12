import uuid

import pytest
from sqlalchemy import text

BASE_URL = "/api/v1/categories"

# ================== FIXTURES ==================


@pytest.fixture
def auth_headers(access_token):
    return {"Authorization": f"Bearer {access_token}"}


@pytest.fixture
def second_auth_headers(client):
    user_data = {
        "username": f"user_{uuid.uuid4().hex}",
        "email": f"{uuid.uuid4().hex}@example.com",
        "password": "password123",
    }

    client.post("/api/v1/auth/register", json=user_data)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]},
    )

    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def created_category(client, auth_headers):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"name": f"Cat_{uuid.uuid4().hex[:6]}"},
    )
    assert response.status_code == 201
    return response.json()


# ================== POST /categories ==================


def test_create_category_success(client, auth_headers):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"name": f"C_{uuid.uuid4().hex[:6]}", "description": "desc"},
    )

    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "desc"


def test_create_category_without_description(client, auth_headers):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"name": f"C_{uuid.uuid4().hex[:6]}"},
    )

    assert response.status_code == 201
    assert response.json()["description"] is None


def test_create_category_unauthorized(client):
    response = client.post(
        BASE_URL + "/",
        json={"name": "Unauthorized"},
    )
    assert response.status_code == 401


def test_create_category_duplicate(client, auth_headers):
    name = f"C_{uuid.uuid4().hex[:6]}"
    client.post(BASE_URL + "/", json={"name": name}, headers=auth_headers)

    response = client.post(BASE_URL + "/", json={"name": name}, headers=auth_headers)
    assert response.status_code == 409


def test_create_category_validation_error(client, auth_headers):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"name": "ab"},
    )
    assert response.status_code == 422


# ================== GET /categories ==================


def test_get_categories_tasks_count(client, auth_headers):
    category_name = f"C_{uuid.uuid4().hex[:6]}"
    cat_resp = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"name": category_name},
    )
    assert cat_resp.status_code == 201
    category = cat_resp.json()
    category_id = category["id"]

    for title in ["T1", "T2"]:
        r = client.post(
            "/api/v1/tasks",
            headers=auth_headers,
            json={"title": title, "category_id": category_id},
        )
        assert r.status_code == 201

    resp = client.get(BASE_URL + "/", headers=auth_headers)
    assert resp.status_code == 200

    categories = resp.json()

    found = next((c for c in categories if c["id"] == category_id), None)
    assert found is not None

    assert found["tasks_count"] == 2


@pytest.mark.asyncio
async def test_get_categories_empty(client, auth_headers, db):
    await db.execute(text("DELETE FROM tasks"))
    await db.execute(text("DELETE FROM categories"))
    await db.commit()

    response = client.get(BASE_URL + "/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == []


def test_get_categories_unauthorized(client):
    response = client.get(BASE_URL + "/")
    assert response.status_code == 401


def test_get_categories_sorted(client, auth_headers):
    client.post(BASE_URL + "/", json={"name": "Cats"}, headers=auth_headers)
    client.post(BASE_URL + "/", json={"name": "Dogs"}, headers=auth_headers)

    response = client.get(BASE_URL + "/", headers=auth_headers)
    assert response.status_code == 200

    names = [c["name"] for c in response.json()]
    assert names == sorted(names)


def test_get_categories_isolation(client, auth_headers, second_auth_headers):
    client.post(BASE_URL + "/", json={"name": "Mine"}, headers=auth_headers)
    client.post(BASE_URL + "/", json={"name": "Foreign"}, headers=second_auth_headers)

    r1 = client.get(BASE_URL + "/", headers=auth_headers)
    r2 = client.get(BASE_URL + "/", headers=second_auth_headers)

    names1 = [c["name"] for c in r1.json()]
    names2 = [c["name"] for c in r2.json()]

    assert "Mine" in names1
    assert "Foreign" not in names1

    assert "Foreign" in names2
    assert "Mine" not in names2


# ================== PUT /categories/{id} ==================


def test_update_category_name(client, auth_headers, created_category):
    response = client.put(
        f"{BASE_URL}/{created_category['id']}",
        headers=auth_headers,
        json={"name": "UpdatedName"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedName"


def test_update_category_description(client, auth_headers, created_category):
    response = client.put(
        f"{BASE_URL}/{created_category['id']}",
        headers=auth_headers,
        json={"description": "New description"},
    )
    assert response.status_code == 200
    assert response.json()["description"] == "New description"


def test_update_category_both(client, auth_headers, created_category):
    response = client.put(
        f"{BASE_URL}/{created_category['id']}",
        headers=auth_headers,
        json={"name": "BothName", "description": "BothDesc"},
    )
    assert response.status_code == 200


def test_update_category_unauthorized(client, created_category):
    response = client.put(
        f"{BASE_URL}/{created_category['id']}",
        json={"name": "Fail"},
    )
    assert response.status_code == 401


def test_update_category_not_found(client, auth_headers):
    response = client.put(
        f"{BASE_URL}/999999",
        headers=auth_headers,
        json={"name": "ValidName"},
    )
    assert response.status_code == 404


def test_update_category_duplicate_name(client, auth_headers):
    _c1 = client.post(BASE_URL + "/", json={"name": "Aaa"}, headers=auth_headers).json()  # ← ДОБАВИТЬ
    c2 = client.post(BASE_URL + "/", json={"name": "Bbb"}, headers=auth_headers).json()

    response = client.put(
        f"{BASE_URL}/{c2['id']}",
        headers=auth_headers,
        json={"name": "Aaa"},
    )
    assert response.status_code == 409


def test_update_category_validation_error(client, auth_headers, created_category):
    response = client.put(
        f"{BASE_URL}/{created_category['id']}",
        headers=auth_headers,
        json={"name": "ab"},
    )
    assert response.status_code == 422


def test_update_category_other_user(client, created_category, second_auth_headers):
    response = client.put(
        f"{BASE_URL}/{created_category['id']}",
        headers=second_auth_headers,
        json={"name": "Another user update"},
    )
    assert response.status_code == 404


# ================== DELETE /categories/{id} ==================


def test_delete_category_success(client, auth_headers, created_category):
    response = client.delete(
        f"{BASE_URL}/{created_category['id']}",
        headers=auth_headers,
    )
    assert response.status_code == 204


def test_delete_category_unauthorized(client, created_category):
    response = client.delete(f"{BASE_URL}/{created_category['id']}")
    assert response.status_code == 401


def test_delete_category_not_found(client, auth_headers):
    response = client.delete(f"{BASE_URL}/999999", headers=auth_headers)
    assert response.status_code == 404


def test_delete_category_other_user(client, created_category, second_auth_headers):
    response = client.delete(
        f"{BASE_URL}/{created_category['id']}",
        headers=second_auth_headers,
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_tasks_become_uncategorized(client, auth_headers):
    c = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"name": f"C_{uuid.uuid4().hex[:6]}"},
    ).json()

    task = client.post(
        "/api/v1/tasks/",
        headers=auth_headers,
        json={"title": "T1", "category_id": c["id"]},
    ).json()

    resp = client.delete(f"{BASE_URL}/{c['id']}", headers=auth_headers)
    assert resp.status_code == 204

    updated = client.get(f"/api/v1/tasks/{task['id']}", headers=auth_headers).json()

    assert updated["category_id"] is None
