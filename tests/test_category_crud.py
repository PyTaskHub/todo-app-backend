import uuid

import pytest
import pytest_asyncio
from fastapi import HTTPException
from sqlalchemy import select

from app.crud.category import (
    create_category,
    delete_category,
    get_category_by_id,
    get_category_by_user,
    get_user_categories_with_tasks_count,
    update_category,
)
from app.crud.task import create_task
from app.models.category import Category
from app.models.task import Task
from app.models.user import User
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.schemas.task import TaskCreate

# ================== FIXTURES ==================


@pytest_asyncio.fixture
async def test_user(db):
    uid = uuid.uuid4().hex
    user = User(
        username=f"user_{uid}",
        email=f"user_{uid}@example.com",
        password_hash="test",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def second_user(db):
    uid = uuid.uuid4().hex
    user = User(
        username=f"user_{uid}",
        email=f"user_{uid}@example.com",
        password_hash="hashed",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def test_category(db, test_user):
    category = await create_category(
        db=db,
        current_user_id=test_user.id,
        category=CategoryCreate(
            name="Test Category", description="Category description"
        ),
    )
    return category


@pytest_asyncio.fixture
async def create_category_factory(db):
    async def _create(user_id, name="Category", description=None):
        return await create_category(
            db=db,
            current_user_id=user_id,
            category=CategoryCreate(name=name, description=description),
        )

    return _create


@pytest_asyncio.fixture
async def create_task_factory(db):
    async def _create(user_id, title="Task", category_id=None):
        return await create_task(
            db=db,
            user_id=user_id,
            task_in=TaskCreate(title=title, category_id=category_id),
        )

    return _create


# ================== READ TESTS (get_category_by_user) ==================


@pytest.mark.asyncio
async def test_get_category_by_user_found(db, test_user, test_category):
    found = await get_category_by_user(db, test_category.name, test_user.id)
    assert found is not None
    assert found.id == test_category.id


@pytest.mark.asyncio
async def test_get_category_by_user_not_found(db, test_user):
    found = await get_category_by_user(db, "DoesNotExist", test_user.id)
    assert found is None


@pytest.mark.asyncio
async def test_get_category_by_user_other_user(
    db, create_category_factory, test_user, second_user
):
    found = await get_category_by_user(db, "private", second_user.id)
    assert found is None


# ================== READ TESTS (get_category_by_id) ==================


@pytest.mark.asyncio
async def test_get_category_by_id_found(db, test_user, test_category):
    found = await get_category_by_id(db, test_user.id, test_category.id)
    assert found is not None
    assert found.id == test_category.id


@pytest.mark.asyncio
async def test_get_category_by_id_not_found(db, test_user):
    found = await get_category_by_id(db, test_user.id, 99999)
    assert found is None


@pytest.mark.asyncio
async def test_get_category_by_id_other_user(
    db, create_category_factory, test_user, second_user
):
    category = await create_category_factory(test_user.id, name="secret")
    found = await get_category_by_id(db, second_user.id, category.id)
    assert found is None


# ================== LIST TESTS ==================


@pytest.mark.asyncio
async def test_get_user_categories_with_tasks_count_basic(
    db, test_user, create_category_factory, create_task_factory
):
    category_1 = await create_category_factory(test_user.id, name="work")
    _category_2 = await create_category_factory(test_user.id, name="home")

    await create_task_factory(test_user.id, title="t1", category_id=category_1.id)
    await create_task_factory(test_user.id, title="t2", category_id=category_1.id)

    rows = await get_user_categories_with_tasks_count(db, test_user.id)

    result = {row[0].name: row[1] for row in rows}
    assert result["work"] == 2
    assert result["home"] == 0


@pytest.mark.asyncio
async def test_get_user_categories_empty(db, test_user):
    rows = await get_user_categories_with_tasks_count(db, test_user.id)
    assert rows == []


@pytest.mark.asyncio
async def test_get_user_categories_sorting(db, test_user, create_category_factory):
    await create_category_factory(test_user.id, name="dogs")
    await create_category_factory(test_user.id, name="cats")
    await create_category_factory(test_user.id, name="others")

    rows = await get_user_categories_with_tasks_count(db, test_user.id)
    names = [row[0].name for row in rows]

    assert names == ["cats", "dogs", "others"]


@pytest.mark.asyncio
async def test_get_user_categories_isolation(
    db, create_category_factory, test_user, second_user
):
    await create_category_factory(test_user.id, name="mine")
    await create_category_factory(second_user.id, name="not mine")

    rows = await get_user_categories_with_tasks_count(db, test_user.id)
    assert len(rows) == 1
    assert rows[0][0].name == "mine"


@pytest.mark.asyncio
async def test_get_user_categories_with_multiple_tasks_per_category(
    db, test_user, create_category_factory, create_task_factory
):
    """Test that tasks_count correctly counts multiple tasks."""
    cat1 = await create_category_factory(test_user.id, name="work")
    cat2 = await create_category_factory(test_user.id, name="home")

    # 5 tasks in work, 3 in home
    for i in range(5):
        await create_task_factory(test_user.id, title=f"work_{i}", category_id=cat1.id)
    for i in range(3):
        await create_task_factory(test_user.id, title=f"home_{i}", category_id=cat2.id)

    rows = await get_user_categories_with_tasks_count(db, test_user.id)
    result = {row[0].name: row[1] for row in rows}

    assert result["work"] == 5
    assert result["home"] == 3


# ================== CREATE TESTS ==================


@pytest.mark.asyncio
async def test_create_category_with_description(db, test_user):
    created = await create_category(
        db=db,
        current_user_id=test_user.id,
        category=CategoryCreate(name="gym", description="desc"),
    )
    assert created.name == "gym"
    assert created.description == "desc"


@pytest.mark.asyncio
async def test_create_category_without_description(db, test_user):
    created = await create_category(
        db=db, current_user_id=test_user.id, category=CategoryCreate(name="notes")
    )
    assert created.description is None


@pytest.mark.asyncio
async def test_create_category_duplicate(db, test_user, create_category_factory):
    await create_category_factory(test_user.id, name="dup")

    with pytest.raises(HTTPException) as exc:
        await create_category(
            db=db, current_user_id=test_user.id, category=CategoryCreate(name="dup")
        )

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_create_category_minimal_name_length(db, test_user):
    """Test category creation with minimal allowed name length (3 chars)."""
    created = await create_category(
        db=db, current_user_id=test_user.id, category=CategoryCreate(name="ABC")
    )
    assert created.name == "ABC"
    assert len(created.name) == 3


# ================== UPDATE TESTS ==================


@pytest.mark.asyncio
async def test_update_category_name(db, test_user, create_category_factory):
    category = await create_category_factory(test_user.id, name="old")

    updated = await update_category(
        db=db,
        new_category=CategoryUpdate(name="new"),
        current_user_id=test_user.id,
        category_id=category.id,
    )
    assert updated.name == "new"


@pytest.mark.asyncio
async def test_update_category_description(db, test_user, create_category_factory):
    category = await create_category_factory(test_user.id, name="cat")

    updated = await update_category(
        db=db,
        new_category=CategoryUpdate(description="added"),
        current_user_id=test_user.id,
        category_id=category.id,
    )
    assert updated.description == "added"


@pytest.mark.asyncio
async def test_update_category_two_fields(db, test_user, create_category_factory):
    category = await create_category_factory(
        test_user.id, name="cat", description="old"
    )

    updated = await update_category(
        db=db,
        new_category=CategoryUpdate(name="new", description="desc"),
        current_user_id=test_user.id,
        category_id=category.id,
    )

    assert updated.name == "new"
    assert updated.description == "desc"


@pytest.mark.asyncio
async def test_update_category_not_found(db, test_user):
    with pytest.raises(HTTPException) as exc:
        await update_category(
            db=db,
            new_category=CategoryUpdate(name="xxx"),
            current_user_id=test_user.id,
            category_id=99999,
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_category_conflict(db, test_user, create_category_factory):
    await create_category_factory(test_user.id, name="one")
    category_2 = await create_category_factory(test_user.id, name="two")

    with pytest.raises(HTTPException) as exc:
        await update_category(
            db=db,
            new_category=CategoryUpdate(name="one"),
            current_user_id=test_user.id,
            category_id=category_2.id,
        )
    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_update_category_other_user(
    db, create_category_factory, test_user, second_user
):
    category = await create_category_factory(test_user.id, name="private")

    with pytest.raises(HTTPException) as exc:
        await update_category(
            db=db,
            new_category=CategoryUpdate(name="another_user_category"),
            current_user_id=second_user.id,
            category_id=category.id,
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_category_empty_update(db, test_user, create_category_factory):
    category = await create_category_factory(
        test_user.id, name="same", description="desc"
    )

    updated = await update_category(
        db=db,
        new_category=CategoryUpdate(),
        current_user_id=test_user.id,
        category_id=category.id,
    )

    assert updated.name == "same"
    assert updated.description == "desc"


# ================== DELETE TESTS ==================


@pytest.mark.asyncio
async def test_delete_category_success_and_tasks_cleaned(
    db, test_user, create_category_factory, create_task_factory
):
    category = await create_category_factory(test_user.id, name="cat_for_remove")

    task_1 = await create_task_factory(
        test_user.id, title="t1", category_id=category.id
    )
    task_2 = await create_task_factory(
        test_user.id, title="t2", category_id=category.id
    )

    await delete_category(db, category.id, test_user.id)

    tasks = (
        (await db.execute(select(Task).where(Task.user_id == test_user.id)))
        .scalars()
        .all()
    )

    assert len(tasks) == 2
    assert {t.id for t in tasks} == {task_1.id, task_2.id}
    assert all(t.category_id is None for t in tasks)

    cat_after = await db.execute(select(Category).where(Category.id == category.id))
    assert cat_after.scalar_one_or_none() is None


@pytest.mark.asyncio
async def test_delete_category_not_found(db, test_user):
    with pytest.raises(HTTPException) as exc:
        await delete_category(db, 99999, test_user.id)

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_delete_category_other_user(
    db, test_user, create_category_factory, second_user
):
    cat = await create_category_factory(test_user.id, name="secret")

    with pytest.raises(HTTPException) as exc:
        await delete_category(db, cat.id, second_user.id)

    assert exc.value.status_code == 404
