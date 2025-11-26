
from fastapi import APIRouter, Depends, status
from app.api.deps import CurrentUser
from app.crud.category import create_category, update_category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
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
