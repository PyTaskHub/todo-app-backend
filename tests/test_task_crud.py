import uuid

import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.crud.task import (
    create_task,
    delete_the_task,
    get_task_by_id,
    get_task_statistics_for_user,
    get_tasks_for_user,
    mark_task_as_completed,
    mark_task_as_pending,
    update_task,
)
from app.models.category import Category
from app.models.task import Priority, Status
from app.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.task_filters import SortOrder, StatusFilter, TaskSortBy

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
async def owned_category(db, test_user):
    category = Category(
        name="Owned Category",
        user_id=test_user.id,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@pytest_asyncio.fixture
async def foreign_category(db, second_user):
    category = Category(
        name="Foreign Category",
        user_id=second_user.id,
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@pytest_asyncio.fixture
async def test_task(db, test_user):
    task = await create_task(
        db=db,
        task_in=TaskCreate(title="Test task"),
        user_id=test_user.id,
    )
    return task


# ================== CREATE TESTS ==================


@pytest.mark.asyncio
async def test_create_task_success(db, test_user):
    task = await create_task(
        db=db,
        task_in=TaskCreate(title="New task"),
        user_id=test_user.id,
    )
    assert task.id is not None
    assert task.user_id == test_user.id
    assert task.title == "New task"
    assert task.status == Status.pending


@pytest.mark.asyncio
async def test_create_task_with_owned_category(db, test_user, owned_category):
    task = await create_task(
        db=db,
        task_in=TaskCreate(title="With cat", category_id=owned_category.id),
        user_id=test_user.id,
    )
    assert task.category_id == owned_category.id


@pytest.mark.asyncio
async def test_create_task_with_foreign_category_raises(
    db,
    test_user,
    foreign_category,
):
    with pytest.raises(HTTPException) as exc:
        await create_task(
            db=db,
            task_in=TaskCreate(title="Invalid", category_id=foreign_category.id),
            user_id=test_user.id,
        )

    assert exc.value.status_code == 400


# ================== READ TESTS ==================


@pytest.mark.asyncio
async def test_get_task_by_id_success(db, test_user, test_task):
    task = await get_task_by_id(db, test_user.id, test_task.id)
    assert task.id == test_task.id


@pytest.mark.asyncio
async def test_get_task_not_owned_raises(db, test_task, second_user):
    with pytest.raises(HTTPException) as exc:
        await get_task_by_id(
            db=db,
            user_id=second_user.id,
            task_id=test_task.id,
        )
    assert exc.value.status_code == 404


# ================== READ (FILTERING/SORTING) TESTS ==================


@pytest.mark.asyncio
async def test_get_tasks_category_filter_null(db, test_user):
    await create_task(db, TaskCreate(title="No category"), test_user.id)

    items, total = await get_tasks_for_user(
        db,
        user_id=test_user.id,
        category_filter="null",
    )

    assert total == 1
    assert items[0].category_id is None


@pytest.mark.asyncio
async def test_get_tasks_invalid_category_filter(db, test_user):
    with pytest.raises(HTTPException) as exc:
        await get_tasks_for_user(
            db,
            user_id=test_user.id,
            category_filter="abc",
        )

    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_get_tasks_foreign_category_filter(db, test_user, foreign_category):
    with pytest.raises(HTTPException) as exc:
        await get_tasks_for_user(
            db,
            user_id=test_user.id,
            category_filter=str(foreign_category.id),
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_get_tasks_search_empty_string(db, test_user):
    await create_task(db, TaskCreate(title="Task"), test_user.id)

    items, total = await get_tasks_for_user(
        db,
        user_id=test_user.id,
        search="   ",
    )

    assert total == 1


@pytest.mark.asyncio
async def test_get_tasks_sort_by_status_asc(db, test_user):
    await create_task(db, TaskCreate(title="A"), test_user.id)

    items, total = await get_tasks_for_user(
        db,
        user_id=test_user.id,
        sort_by=TaskSortBy.status,
        order=SortOrder.asc,
    )

    assert total == 1


@pytest.mark.asyncio
async def test_get_tasks_status_filter_pending(db, test_user):
    await create_task(db, TaskCreate(title="Pending task"), test_user.id)

    items, total = await get_tasks_for_user(
        db,
        user_id=test_user.id,
        status_filter=StatusFilter.pending,
    )

    assert total == 1
    assert items[0].status == Status.pending


@pytest.mark.asyncio
async def test_get_tasks_status_filter_completed(db, test_user):
    task = await create_task(db, TaskCreate(title="Completed task"), test_user.id)
    task.status = Status.completed
    await db.commit()

    items, total = await get_tasks_for_user(
        db,
        user_id=test_user.id,
        status_filter=StatusFilter.completed,
    )

    assert total == 1
    assert items[0].status == Status.completed


@pytest.mark.asyncio
async def test_get_tasks_status_filter_all(db, test_user):
    await create_task(db, TaskCreate(title="Task 1"), test_user.id)
    await create_task(db, TaskCreate(title="Task 2"), test_user.id)

    items, total = await get_tasks_for_user(
        db,
        user_id=test_user.id,
        status_filter=StatusFilter.all,
    )

    assert total == 2


@pytest.mark.asyncio
async def test_get_tasks_completed_total_count(db, test_user):
    t1 = await create_task(db, TaskCreate(title="Done 1"), test_user.id)
    t2 = await create_task(db, TaskCreate(title="Done 2"), test_user.id)

    t1.status = Status.completed
    t2.status = Status.completed
    await db.commit()

    items, total = await get_tasks_for_user(
        db,
        user_id=test_user.id,
        status_filter=StatusFilter.completed,
    )

    assert total == 2


# ================== UPDATE TESTS ==================


@pytest.mark.asyncio
async def test_update_task_title(db, test_user, test_task):
    updated = await update_task(
        db=db,
        task_id=test_task.id,
        task_in=TaskUpdate(title="Updated title"),
        user_id=test_user.id,
    )
    assert updated.title == "Updated title"


@pytest.mark.asyncio
async def test_update_task_multiple_fields(db, test_user, test_task):
    updated = await update_task(
        db=db,
        task_id=test_task.id,
        task_in=TaskUpdate(
            title="Updated",
            priority=Priority.high,
        ),
        user_id=test_user.id,
    )
    assert updated.title == "Updated"
    assert updated.priority == Priority.high


@pytest.mark.asyncio
async def test_update_task_not_owned_raises(db, test_task, second_user):
    with pytest.raises(HTTPException) as exc:
        await update_task(
            db=db,
            task_id=test_task.id,
            task_in=TaskUpdate(title="Task from another user"),
            user_id=second_user.id,
        )
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_task_with_foreign_category_raises(
    db,
    test_user,
    test_task,
    foreign_category,
):
    with pytest.raises(HTTPException) as exc:
        await update_task(
            db=db,
            task_id=test_task.id,
            task_in=TaskUpdate(category_id=foreign_category.id),
            user_id=test_user.id,
        )
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_update_task_no_fields(db, test_user, test_task):
    updated = await update_task(
        db,
        task_id=test_task.id,
        task_in=TaskUpdate(),
        user_id=test_user.id,
    )

    assert updated.id == test_task.id


@pytest.mark.asyncio
async def test_update_task_remove_category(db, test_user, test_task):
    updated = await update_task(
        db,
        task_id=test_task.id,
        task_in=TaskUpdate(category_id=None),
        user_id=test_user.id,
    )

    assert updated.category_id is None


@pytest.mark.asyncio
async def test_mark_task_as_completed_success(db, test_user, test_task):
    task = await mark_task_as_completed(
        db=db,
        task_id=test_task.id,
        user_id=test_user.id,
    )

    assert task.status == Status.completed
    assert task.completed_at is not None


@pytest.mark.asyncio
async def test_mark_task_as_completed_idempotent(db, test_user, test_task):
    await mark_task_as_completed(db, test_task.id, test_user.id)

    task = await mark_task_as_completed(
        db=db,
        task_id=test_task.id,
        user_id=test_user.id,
    )

    assert task.status == Status.completed


@pytest.mark.asyncio
async def test_mark_task_as_completed_not_owned_raises(
    db,
    test_task,
    second_user,
):
    with pytest.raises(HTTPException) as exc:
        await mark_task_as_completed(
            db=db,
            task_id=test_task.id,
            user_id=second_user.id,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_mark_task_as_completed_not_found_raises(db, test_user):
    with pytest.raises(HTTPException) as exc:
        await mark_task_as_completed(
            db=db,
            task_id=999999,
            user_id=test_user.id,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_mark_task_as_pending_success(db, test_user, test_task):
    await mark_task_as_completed(db, test_task.id, test_user.id)

    task = await mark_task_as_pending(
        db=db,
        task_id=test_task.id,
        user_id=test_user.id,
    )

    assert task.status == Status.pending
    assert task.completed_at is None


@pytest.mark.asyncio
async def test_mark_task_as_pending_idempotent(db, test_user, test_task):
    task = await mark_task_as_pending(
        db=db,
        task_id=test_task.id,
        user_id=test_user.id,
    )

    assert task.status == Status.pending
    assert task.completed_at is None


@pytest.mark.asyncio
async def test_mark_task_as_pending_not_owned_raises(
    db,
    test_task,
    second_user,
):
    with pytest.raises(HTTPException) as exc:
        await mark_task_as_pending(
            db=db,
            task_id=test_task.id,
            user_id=second_user.id,
        )

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_mark_task_as_pending_not_found_raises(db, test_user):
    with pytest.raises(HTTPException) as exc:
        await mark_task_as_pending(
            db=db,
            task_id=999999,
            user_id=test_user.id,
        )

    assert exc.value.status_code == 404


# ================== LIST TESTS ==================


@pytest.mark.asyncio
async def test_get_tasks_for_user_only_own(db, test_user, second_user):
    await create_task(db, TaskCreate(title="Mine"), test_user.id)
    await create_task(db, TaskCreate(title="Not mine"), second_user.id)

    items, total = await get_tasks_for_user(db, test_user.id)

    assert total == 1
    assert items[0].user_id == test_user.id


@pytest.mark.asyncio
async def test_get_tasks_empty_for_other_user(db, test_user):
    items, total = await get_tasks_for_user(db, test_user.id)
    assert items == []
    assert total == 0


@pytest.mark.asyncio
async def test_task_statistics_empty(db, test_user):
    stats = await get_task_statistics_for_user(db, test_user.id)

    assert stats["total"] == 0
    assert stats["completed"] == 0
    assert stats["completion_rate"] == 0.0


@pytest.mark.asyncio
async def test_task_statistics_completed(db, test_user):
    task = await create_task(db, TaskCreate(title="Done"), test_user.id)
    task.status = Status.completed
    await db.commit()

    stats = await get_task_statistics_for_user(db, test_user.id)

    assert stats["total"] == 1
    assert stats["completed"] == 1
    assert stats["completion_rate"] == 100.0


# ================== DELETE TESTS ==================


@pytest.mark.asyncio
async def test_delete_task_success(db, test_user, test_task):
    await delete_the_task(db, test_task.id, test_user.id)

    with pytest.raises(HTTPException):
        await get_task_by_id(db, test_user.id, test_task.id)


@pytest.mark.asyncio
async def test_delete_task_not_owned_raises(db, test_task, second_user):
    with pytest.raises(HTTPException) as exc:
        await delete_the_task(db, test_task.id, second_user.id)
    assert exc.value.status_code == 404
