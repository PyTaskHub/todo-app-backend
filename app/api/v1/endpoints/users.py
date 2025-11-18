"""
User management endpoints.
"""
from fastapi import APIRouter

from app.api.deps import CurrentUser
from app.schemas.user import UserResponse

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
# TODO: Task - Implement change password endpoint