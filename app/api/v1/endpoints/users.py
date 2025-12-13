"""
User management endpoints.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.crud import user as user_crud
from app.db.session import get_db
from app.schemas.user import ChangePassword, UserProfileUpdate, UserResponse

router = APIRouter()


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Return profile of the authenticated user",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Not authenticated"},
    },
)
async def get_current_user_profile(current_user: CurrentUser) -> UserResponse:
    """
    Get current user profile.

    Requires authentication. Returns profile of authenticated user.
    """
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update current user",
    description="Update profile information of the authenticated user",
    responses={
        200: {"description": "User profile successfully updated"},
        401: {"description": "Not authenticated"},
        409: {"description": "Email already registered"},
    },
)
async def put_update_user_profile(
    profile_update: UserProfileUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """
    Update current user's profile information.

    Requires authentication. Allows updating email, first_name, last_name.
    Checks for email uniqueness if email is changed.
    Returns the updated user profile.
    """
    updated_user = await user_crud.update_user_profile(
        db=db, user=current_user, profile_update=profile_update
    )
    return updated_user


@router.post(
    "/me/change-password",
    status_code=status.HTTP_200_OK,
    summary="Change password",
    description="Change password for the authenticated user",
    responses={
        200: {"description": "Password changed successfully"},
        400: {"description": "Invalid input data"},
        401: {"description": "Incorrect current password"},
        422: {"description": "Validation error"},
    },
)
async def change_password(
    password_data: ChangePassword,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Change password for authenticated user.

    Requires authentication.
    - Verifies current password
    - Validates new password (min 8 characters)
    - Hashes and stores new password

    Returns success message.
    """
    await user_crud.change_user_password(
        db=db,
        user=current_user,
        current_password=password_data.current_password,
        new_password=password_data.new_password,
    )

    return {"message": "Password changed successfully"}
