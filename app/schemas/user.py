"""
Pydantic schemas for User model validation and serialization.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict


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