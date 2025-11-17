"""
CRUD operations for User model.
"""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    """
    Get user by ID.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        User object or None if not found
    """
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    """
    Get user by email.

    Args:
        db: Database session
        email: User email

    Returns:
        User object or None if not found
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
    """
    Get user by username.

    Args:
        db: Database session
        username: Username

    Returns:
        User object or None if not found
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    """
    Create new user.

    Args:
        db: Database session
        user_in: User data from request

    Returns:
        Created User object
    """
    # Create user instance
    db_user = User(
        username=user_in.username,
        email=user_in.email,
        is_active=True,
        is_superuser=False,
    )

    # Hash password
    db_user.set_password(user_in.password)

    # Add to database
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    return db_user


async def update_user(
        db: AsyncSession,
        db_user: User,
        user_in: UserUpdate
) -> User:
    """
    Update user information.

    Args:
        db: Database session
        db_user: Existing user object
        user_in: Update data

    Returns:
        Updated User object
    """
    update_data = user_in.model_dump(exclude_unset=True)

    # Handle password separately
    if "password" in update_data:
        password = update_data.pop("password")
        db_user.set_password(password)

    # Update other fields
    for field, value in update_data.items():
        setattr(db_user, field, value)

    await db.commit()
    await db.refresh(db_user)

    return db_user