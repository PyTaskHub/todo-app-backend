"""
Authentication endpoints: registration, login, refresh token.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, create_refresh_token, verify_token
from app.crud.user import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
)
from app.db.session import get_db
from app.schemas.token import AccessTokenResponse, RefreshTokenRequest, Token
from app.schemas.user import UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account with a unique username and email",
    responses={
        201: {
            "description": "User successfully registered.",
        },
        409: {
            "description": "User with the same email or username already exists.",
            "content": {
                "application/json": {
                    "examples": {
                        "email_conflict": {
                            "summary": "Email already registered",
                            "value": {"detail": "Email already registered"},
                        },
                        "username_conflict": {
                            "summary": "Username already taken",
                            "value": {"detail": "Username already taken"},
                        },
                    }
                }
            },
        },
        422: {
            "description": "Validation error. The request body does not match the expected schema.",
        },
    },
)
async def register(
    user_in: UserCreate, db: AsyncSession = Depends(get_db)
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
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    # Check if username already exists
    existing_user = await get_user_by_username(db, username=user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        )

    # Create new user
    user = await create_user(db, user_in=user_in)

    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login user",
    description="Authenticate user by email and password and return a pair of JWT tokens",
    responses={
        200: {
            "description": "Successful authentication. Returns access and refresh tokens.",
        },
        401: {
            "description": "Invalid credentials or inactive user.",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_credentials": {
                            "summary": "Wrong email or password",
                            "value": {"detail": "Incorrect email or password"},
                        },
                        "inactive_user": {
                            "summary": "Inactive user",
                            "value": {"detail": "Inactive user"},
                        },
                    }
                }
            },
        },
        422: {
            "description": "Validation error. The request body does not match the expected schema.",
        },
    },
)
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)) -> Token:
    """
    Login user and return access/refresh tokens.

    - **email**: user email address
    - **password**: user password

    Returns access_token and refresh_token.
    """
    # Get user by email
    user = await get_user_by_email(db, email=credentials.email)

    # Check if user exists
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password
    if not user.verify_password(credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create tokens
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "username": user.username}
    )
    refresh_token = create_refresh_token(data={"sub": user.email, "user_id": user.id})

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post(
    "/refresh",
    response_model=AccessTokenResponse,
    summary="Refresh access token",
    description="Exchange a valid refresh token for a new access token",
    responses={
        200: {
            "description": "Access token successfully refreshed.",
        },
        401: {
            "description": "Invalid or expired refresh token, user not found or inactive.",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_token": {
                            "summary": "Invalid token",
                            "value": {"detail": "Invalid token"},
                        },
                        "user_not_found": {
                            "summary": "User not found",
                            "value": {"detail": "User not found"},
                        },
                        "inactive_user": {
                            "summary": "Inactive user",
                            "value": {"detail": "Inactive user"},
                        },
                    }
                }
            },
        },
        422: {
            "description": "Validation error. The request body does not match the expected schema.",
        },
    },
)
async def refresh_access_token(
    request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)
) -> AccessTokenResponse:
    """
    Refresh access token using refresh token.

    - **refresh_token**: valid refresh token from login

    Returns new access_token.
    """
    # Verify and decode refresh token
    payload = verify_token(request.refresh_token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check token type
    token_type = payload.get("type")
    if token_type != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract user_id from token
    user_id: int = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get user from database
    user = await get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create new access token
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id, "username": user.username}
    )

    return AccessTokenResponse(access_token=access_token, token_type="bearer")
