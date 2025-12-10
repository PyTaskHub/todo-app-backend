import uuid
import pytest

BASE_URL = "/api/v1/tasks"

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
def created_task(client, auth_headers):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"title": "Test task"},
    )
    assert response.status_code == 201
    return response.json()

@pytest.fixture
def foreign_category(client, second_auth_headers):
    response = client.post(
        "/api/v1/categories/",
        headers=second_auth_headers,
        json={"name": "Foreign category"},
    )
    assert response.status_code == 201
    return response.json()

# ================== POST /tasks ==================

def test_create_task_success(client, auth_headers):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"title": "My first task"},
    )

    assert response.status_code == 201
    assert response.json()["title"] == "My first task"


def test_create_task_unauthorized(client):
    response = client.post(
        BASE_URL + "/",
        json={"title": "Unauthorized"},
    )
    assert response.status_code == 401


def test_create_task_title_too_long(client, auth_headers):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"title": "x" * 300},
    )
    assert response.status_code == 422


def test_create_task_empty_payload(client, auth_headers):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={},
    )
    assert response.status_code == 422
    
def test_cannot_create_task_with_foreign_category(
    client,
    auth_headers,
    foreign_category,
):
    response = client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={
            "title": "Task with чужой category",
            "category_id": foreign_category["id"],
        },
    )

    assert response.status_code == 400

# ================== GET /tasks ==================

def test_get_tasks_list(client, auth_headers):
    response = client.get(
        BASE_URL + "/",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_get_tasks_unauthorized(client):
    response = client.get(BASE_URL + "/")
    assert response.status_code == 401


def test_get_tasks_pagination(client, auth_headers):
    response = client.get(
        BASE_URL + "/?limit=1&offset=0",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_get_tasks_filter_pending(client, auth_headers):
    response = client.get(
        BASE_URL + "/?status_filter=pending",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_get_tasks_filter_completed(client, auth_headers):
    response = client.get(
        BASE_URL + "/?status_filter=completed",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_get_tasks_sort_by_priority(client, auth_headers):
    response = client.get(
        BASE_URL + "/?sort_by=priority&order=asc",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_get_tasks_sort_by_due_date(client, auth_headers):
    response = client.get(
        BASE_URL + "/?sort_by=due_date&order=desc",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_get_tasks_search_by_title(client, auth_headers):
    client.post(
        BASE_URL + "/",
        headers=auth_headers,
        json={"title": "Unique title"},
    )

    response = client.get(
        BASE_URL + "/?search=Unique",
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_get_tasks_large_offset(client, auth_headers):
    response = client.get(
        BASE_URL + "/?offset=9999",
        headers=auth_headers,
    )
    assert response.status_code == 200

# ================== GET /tasks/{id} ==================

def test_get_task_by_id_success(client, auth_headers, created_task):
    response = client.get(
        f"{BASE_URL}/{created_task['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_task["id"]


def test_get_task_not_found(client, auth_headers):
    response = client.get(
        f"{BASE_URL}/999999",
        headers=auth_headers,
    )
    assert response.status_code == 404

# ================== PUT /tasks/{id} ==================

def test_update_task_success(client, auth_headers, created_task):
    response = client.put(
        f"{BASE_URL}/{created_task['id']}",
        headers=auth_headers,
        json={"title": "Updated title"},
    )

    assert response.status_code == 200
    assert response.json()["title"] == "Updated title"


def test_update_task_invalid_title(client, auth_headers, created_task):
    response = client.put(
        f"{BASE_URL}/{created_task['id']}",
        headers=auth_headers,
        json={"title": ""},
    )

    assert response.status_code == 422


def test_update_task_not_found(client, auth_headers):
    response = client.put(
        f"{BASE_URL}/999999",
        headers=auth_headers,
        json={"title": "Not existed task"},
    )

    assert response.status_code == 404
    
def test_cannot_update_task_with_foreign_category(
    client,
    auth_headers,
    created_task,
    foreign_category,
):
    response = client.put(
        f"{BASE_URL}/{created_task['id']}",
        headers=auth_headers,
        json={
            "category_id": foreign_category["id"],
        },
    )

    assert response.status_code == 400

def test_complete_task_success(client, auth_headers, created_task):
    response = client.patch(
        f"{BASE_URL}/{created_task['id']}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "completed"
    assert data["completed_at"] is not None

def test_complete_task_idempotent(client, auth_headers, created_task):
    client.patch(
        f"{BASE_URL}/{created_task['id']}/complete",
        headers=auth_headers,
    )

    response = client.patch(
        f"{BASE_URL}/{created_task['id']}/complete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_complete_task_unauthorized(client, created_task):
    response = client.patch(
        f"{BASE_URL}/{created_task['id']}/complete",
    )

    assert response.status_code == 401

def test_complete_task_not_owned(client, created_task, second_auth_headers):
    response = client.patch(
        f"{BASE_URL}/{created_task['id']}/complete",
        headers=second_auth_headers,
    )

    assert response.status_code == 404

def test_complete_task_not_found(client, auth_headers):
    response = client.patch(
        f"{BASE_URL}/999999/complete",
        headers=auth_headers,
    )

    assert response.status_code == 404

def test_uncomplete_task_success(client, auth_headers, created_task):
    client.patch(
        f"{BASE_URL}/{created_task['id']}/complete",
        headers=auth_headers,
    )

    response = client.patch(
        f"{BASE_URL}/{created_task['id']}/uncomplete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "pending"
    assert data["completed_at"] is None

def test_uncomplete_task_idempotent(client, auth_headers, created_task):
    response = client.patch(
        f"{BASE_URL}/{created_task['id']}/uncomplete",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["status"] == "pending"

def test_uncomplete_task_unauthorized(client, created_task):
    response = client.patch(
        f"{BASE_URL}/{created_task['id']}/uncomplete",
    )

    assert response.status_code == 401

def test_uncomplete_task_not_owned(client, created_task, second_auth_headers):
    response = client.patch(
        f"{BASE_URL}/{created_task['id']}/uncomplete",
        headers=second_auth_headers,
    )

    assert response.status_code == 404

def test_uncomplete_task_not_found(client, auth_headers):
    response = client.patch(
        f"{BASE_URL}/999999/uncomplete",
        headers=auth_headers,
    )

    assert response.status_code == 404


# ================== DELETE /tasks/{id} ==================

def test_delete_task_success(client, auth_headers, created_task):
    response = client.delete(
        f"{BASE_URL}/{created_task['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 204


def test_delete_task_not_found(client, auth_headers):
    response = client.delete(
        f"{BASE_URL}/999999",
        headers=auth_headers,
    )

    assert response.status_code == 404

# ================== ISOLATION TESTS ==================

def test_cannot_get_task_of_other_user(client, created_task, second_auth_headers):
    response = client.get(
        f"{BASE_URL}/{created_task['id']}",
        headers=second_auth_headers,
    )

    assert response.status_code == 404

def test_cannot_update_task_of_other_user(client, created_task, second_auth_headers):
    response = client.put(
        f"{BASE_URL}/{created_task['id']}",
        headers=second_auth_headers,
        json={"title": "Task by another user"},
    )

    assert response.status_code == 404

def test_cannot_delete_task_of_other_user(client, created_task, second_auth_headers):
    response = client.delete(
        f"{BASE_URL}/{created_task['id']}",
        headers=second_auth_headers,
    )

    assert response.status_code == 404


