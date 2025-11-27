"""
Pydantic schemas for User model validation and serialization.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.models.user import User


class UserBase(BaseModel):
    """
    Base User schema with common fields.
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Username (3-50 characters)",
        examples=["john_doe"]
    )
    email: EmailStr = Field(
        ...,
        description="Valid email address",
        examples=["john@example.com"]
    )
    first_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="User's first name",
        examples=["John"]
    )
    last_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="User's last name",
        examples=["Doe"]
    )


class UserCreate(UserBase):
    """
    Schema for creating a new user.
    Includes password field.
    """
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (min 8 characters)",
        examples=["MySecurePass123!"]
    )


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    All fields are optional.
    """
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New username"
    )
    email: Optional[EmailStr] = Field(
        None,
        description="New email address"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="New password"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Active status"
    )


class UserInDB(UserBase):
    """
    Schema for User as stored in database.
    Includes all fields including password_hash.
    """
    id: int
    password_hash: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """
    Schema for User in API responses.
    Excludes sensitive information like password_hash.
    """
    id: int
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """
    Schema for user login.
    """
    email: EmailStr = Field(
        ...,
        description="User email",
        examples=["john@example.com"]
    )
    password: str = Field(
        ...,
        description="User password",
        examples=["MySecurePass123!"]
    )


class UserProfileUpdate(BaseModel):
    """
    Schema for updating user profile information.
    Allows updating email, first_name, and last_name.
    All fields are optional.
    """
    email: Optional[EmailStr] = Field(
        None,
        description="New email address (must be unique)"
    )
    first_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New first name"
    )
    last_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        description="New last name"
    )


async def update_user_profile(
        db: AsyncSession,
        user: User,
        profile_update: UserProfileUpdate 
) -> User:
    """
    Updates the profile of a user, checking for email uniqueness if email is changed.
    Allows updating email, first_name, and last_name.

    Args:
        db: Database session
        user: The User ORM object to update.
        profile_update: User profile update data from the UserProfileUpdate schema.

    Returns:
        The updated User ORM object.

    Raises:
        HTTPException: If the email is already in use by another user.
    """

    update_data = profile_update.model_dump(exclude_unset=True)

    if not update_data:
        return user

    if "email" in update_data:
        new_email = update_data["email"]
        if new_email != user.email:
            existing_user_with_new_email = await db.scalar(
                select(User).where(
                    User.email == new_email,
                    User.id != user.id
                )
            )
            if existing_user_with_new_email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email address is already in use by another user."
                )
            
            setattr(user, "email", new_email)
            del update_data["email"] 

    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)

    return user