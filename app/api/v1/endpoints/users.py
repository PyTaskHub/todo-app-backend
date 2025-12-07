"""
User management endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import CurrentUser
from app.db.session import get_db
from app.schemas.user import UserResponse, UserProfileUpdate
from app.models.user import User
from app.crud import user as user_crud
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
        current_user: CurrentUser
) -> UserResponse:
    """
    Get current user profile.

    Requires authentication. Returns profile of authenticated user.
    """
    return current_user

# TODO: Task - Implement update user profile endpoint
@router.put("/me", response_model=UserResponse)
async def put_update_user_profile(
        profile_update: UserProfileUpdate,
        current_user: CurrentUser,
        db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """
    Update current user's profile information.

    Requires authentication. Allows updating email, first_name, last_name.
    Checks for email uniqueness if email is changed.
    Returns the updated user profile.
    """
    updated_user = await user_crud.update_user_profile(
        db=db,
        user=current_user,
        profile_update=profile_update
    )
    return updated_user

# TODO: Task - Implement change password endpoint