
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser
from app.crud.category import create_category, get_user_categories_with_tasks_count, delete_category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryListItem
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

@router.get(
  "/",
  response_model=list[CategoryListItem],
  status_code=status.HTTP_200_OK
  )

async def get_user_categories(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> list[CategoryListItem]:
    """
    Get list of all categories for current user.

    - Requires Authorization header with Bearer token
    - Returns only categories of current user
    - Sorted by name in ascending order (A-Z)
    - Includes tasks_count for each category
    """
    rows = await get_user_categories_with_tasks_count(
        db=db,
        user_id=current_user.id,
    )

    return [
        CategoryListItem(
            id=category.id,
            name=category.name,
            description=category.description,
            tasks_count=tasks_count,
            created_at=category.created_at,
        )
        for category, tasks_count in rows
    ]

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