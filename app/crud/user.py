"""
CRUD operations for User model.
"""
from fastapi import HTTPException, status
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserProfileUpdate


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
        first_name=user_in.first_name,
        last_name=user_in.last_name,
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


async def update_user_profile(
    db: AsyncSession, 
    user: User,
    profile_update: UserProfileUpdate
) -> User:
    """
    Updates the profile of a user, checking for email uniqueness.
    """
    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        return user

    if "email" in update_data:
        new_email = update_data["email"]

        if new_email != user.email:
            existing_user_with_new_email_orm = await db.scalar(
                 select(User).where(
                    User.email == new_email, 
                    User.id != user.id)
            )


            if existing_user_with_new_email_orm:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,  # 409
                    detail="Email already registered"
                )

    for field, value in update_data.items():
        setattr(user, field, value)

    await db.commit()
    await db.refresh(user)

    return user


async def change_user_password(
    db: AsyncSession,
    user: User,
    current_password: str,
    new_password: str
) -> User:
    """
    Change user password with current password verification.
    
    Args:
        db: Database session
        user: User object to update
        current_password: Current password for verification
        new_password: New password to set
    
    Returns:
        Updated User object
    
    Raises:
        HTTPException: 401 if current password is incorrect
    """
    if not user.verify_password(current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password"
        )
    
    user.set_password(new_password)
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user