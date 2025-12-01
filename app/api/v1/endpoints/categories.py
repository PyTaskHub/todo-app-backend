
from fastapi import APIRouter, Depends, status
from app.api.deps import CurrentUser
from app.crud.category import create_category, update_category, get_user_categories_with_tasks_count
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate, CategoryListItem
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

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
  
@router.put(
    "/{category_id}",
        response_model=CategoryResponse,
        status_code=status.HTTP_200_OK,
        responses={
            409: {"description": "Category with this name already exists"},
            422: {"description": "Validation error"}
        }
    )
async def update_the_category(
        category_id: int,
        current_user: CurrentUser,
        category_in: CategoryUpdate,
        db: AsyncSession = Depends(get_db)
) -> CategoryResponse:
    edited_category = await update_category(
      db=db,
      new_category=category_in,
      current_user_id=current_user.id,
      category_id=category_id
    )

    return edited_category

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
