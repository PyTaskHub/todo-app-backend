
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.crud.category import create_category, delete_category
from app.schemas.category import CategoryCreate, CategoryResponse
from app.db.session import get_db

router = APIRouter()

@router.post(
        "/", 
        response_model=CategoryResponse,
        status_code=status.HTTP_201_CREATED,
        responses={
            409: {"description": "Category with this name already exists"},
            422: {"description": "Validation error"}
        }
     )
async def create_new_category(
        current_user: CurrentUser,
        category_in: CategoryCreate,
        db: AsyncSession = Depends(get_db)
) -> CategoryResponse:
    category = await create_category(
      db=db,
      category=category_in,
      current_user_id=current_user.id,
    )

    return category

@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Category not found or does not belong to the user"},
    },
)
async def delete_existing_category(
    category_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete category belonging to the authenticated user.

    - Requires Authorization: Bearer <token>
    - Only the category owner can delete it
    - All tasks with this category become uncategorized (category_id = null)

    Returns 204 No Content on success.
    """
    await delete_category(
        db=db,
        category_id=category_id,
        user_id=current_user.id,
    )
  