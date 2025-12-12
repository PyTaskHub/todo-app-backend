import uuid
import pytest
import pytest_asyncio
from fastapi import HTTPException

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserProfileUpdate
from app.crud.user import (
    get_user_by_id,
    get_user_by_email,
    get_user_by_username,
    create_user,
    update_user,
    update_user_profile,
    change_user_password,
)

# ================== FIXTURES ==================

@pytest_asyncio.fixture
async def test_user(db):
    user = User(
        username=f"user_{uuid.uuid4().hex}",
        email=f"{uuid.uuid4().hex}@example.com",
        is_active=True,
        is_superuser=False,
    )
    user.set_password("password123")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest_asyncio.fixture
async def second_user(db):
    user = User(
        username=f"user_{uuid.uuid4().hex}",
        email=f"{uuid.uuid4().hex}@example.com",
        is_active=True,
        is_superuser=False,
    )
    user.set_password("password123")
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


# ================== READ TESTS (get_user_by_*) ==================

@pytest.mark.asyncio
async def test_get_user_by_id_found(db, test_user):
    found = await get_user_by_id(db, test_user.id)
    assert found is not None
    assert found.id == test_user.id


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db):
    found = await get_user_by_id(db, 999999)
    assert found is None


@pytest.mark.asyncio
async def test_get_user_by_email_found(db, test_user):
    found = await get_user_by_email(db, test_user.email)
    assert found is not None
    assert found.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_by_email_not_found(db):
    found = await get_user_by_email(db, "missing@example.com")
    assert found is None


@pytest.mark.asyncio
async def test_get_user_by_username_found(db, test_user):
    found = await get_user_by_username(db, test_user.username)
    assert found is not None
    assert found.username == test_user.username


@pytest.mark.asyncio
async def test_get_user_by_username_not_found(db):
    found = await get_user_by_username(db, "missing_user")
    assert found is None


# ================== CREATE TESTS ==================

@pytest.mark.asyncio
async def test_create_user_success(db):
    user_in = UserCreate(
        username=f"user_{uuid.uuid4().hex}",
        email=f"{uuid.uuid4().hex}@example.com",
        password="strongpassword",
    )

    user = await create_user(db, user_in)

    assert user.id is not None
    assert user.username == user_in.username
    assert user.email == user_in.email


@pytest.mark.asyncio
async def test_create_user_password_hashed(db):
    user_in = UserCreate(
        username=f"user_{uuid.uuid4().hex}",
        email=f"{uuid.uuid4().hex}@example.com",
        password="strongpassword",
    )

    user = await create_user(db, user_in)

    assert user.password_hash != user_in.password
    assert user.verify_password("strongpassword") is True


@pytest.mark.asyncio
async def test_create_user_flags(db):
    user_in = UserCreate(
        username=f"user_{uuid.uuid4().hex}",
        email=f"{uuid.uuid4().hex}@example.com",
        password="strongpassword",
    )

    user = await create_user(db, user_in)

    assert user.is_active is True
    assert user.is_superuser is False


# ================== UPDATE TESTS ==================

@pytest.mark.asyncio
async def test_update_user_email(db, test_user):
    updated = await update_user(
        db,
        test_user,
        UserUpdate(email="new@example.com"),
    )

    assert updated.email == "new@example.com"


@pytest.mark.asyncio
async def test_update_user_username(db, test_user):
    updated = await update_user(
        db,
        test_user,
        UserUpdate(username="new_username"),
    )

    assert updated.username == "new_username"


@pytest.mark.asyncio
async def test_update_user_password(db, test_user):
    old_hash = test_user.password_hash

    updated = await update_user(
        db,
        test_user,
        UserUpdate(password="newpassword123"),
    )

    assert updated.password_hash != old_hash
    assert updated.verify_password("newpassword123") is True


@pytest.mark.asyncio
async def test_update_user_multiple_fields(db, test_user):
    updated = await update_user(
        db,
        test_user,
        UserUpdate(
            username="multi",
            email="multi@example.com",
            is_active=False,
        ),
    )

    assert updated.username == "multi"
    assert updated.email == "multi@example.com"
    assert updated.is_active is False


@pytest.mark.asyncio
async def test_update_user_empty_update(db, test_user):
    original_email = test_user.email

    updated = await update_user(db, test_user, UserUpdate())

    assert updated.email == original_email


@pytest.mark.asyncio
async def test_update_user_profile_email(db, test_user):
    updated = await update_user_profile(
        db,
        test_user,
        UserProfileUpdate(email="profile@example.com"),
    )

    assert updated.email == "profile@example.com"


@pytest.mark.asyncio
async def test_update_user_profile_first_name(db, test_user):
    updated = await update_user_profile(
        db,
        test_user,
        UserProfileUpdate(first_name="John"),
    )

    assert updated.first_name == "John"


@pytest.mark.asyncio
async def test_update_user_profile_last_name(db, test_user):
    updated = await update_user_profile(
        db,
        test_user,
        UserProfileUpdate(last_name="Doe"),
    )

    assert updated.last_name == "Doe"


@pytest.mark.asyncio
async def test_update_user_profile_all_fields(db, test_user):
    updated = await update_user_profile(
        db,
        test_user,
        UserProfileUpdate(
            email="all@example.com",
            first_name="John",
            last_name="Doe",
        ),
    )

    assert updated.email == "all@example.com"
    assert updated.first_name == "John"
    assert updated.last_name == "Doe"


@pytest.mark.asyncio
async def test_update_user_profile_duplicate_email(db, test_user, second_user):
    with pytest.raises(HTTPException) as exc:
        await update_user_profile(
            db,
            test_user,
            UserProfileUpdate(email=second_user.email),
        )

    assert exc.value.status_code == 409


@pytest.mark.asyncio
async def test_update_user_profile_same_email(db, test_user):
    updated = await update_user_profile(
        db,
        test_user,
        UserProfileUpdate(email=test_user.email),
    )

    assert updated.email == test_user.email


@pytest.mark.asyncio
async def test_update_user_profile_empty_update(db, test_user):
    updated = await update_user_profile(
        db,
        test_user,
        UserProfileUpdate(),
    )

    assert updated.id == test_user.id

@pytest.mark.asyncio
async def test_change_user_password_success(db, test_user):
    updated = await change_user_password(
        db,
        test_user,
        current_password="password123",
        new_password="newpassword123",
    )

    assert updated.verify_password("newpassword123") is True


@pytest.mark.asyncio
async def test_change_user_password_wrong_current(db, test_user):
    with pytest.raises(HTTPException) as exc:
        await change_user_password(
            db,
            test_user,
            current_password="wrong",
            new_password="newpassword123",
        )

    assert exc.value.status_code == 401
