"""
Authentication endpoints: registration, login, refresh token.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.crud.user import get_user_by_email, get_user_by_username, create_user


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Register new user.

    - **username**: unique username (3-50 characters)
    - **email**: valid email address (must be unique)
    - **password**: strong password (min 8 characters)

    Returns created user without password_hash.
    """
    # Check if email already exists
    existing_user = await get_user_by_email(db, email=user_in.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Check if username already exists
    existing_user = await get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )

    # Create new user
    user = await create_user(db, user_in=user_in)

    return user


# TODO: Task #9 - Implement login endpoint
# TODO: Task #9 - Implement refresh token endpoint