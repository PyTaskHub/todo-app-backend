
from fastapi import APIRouter, Depends, status
from app.api.deps import CurrentUser
from app.crud.category import create_category
from app.schemas.category import CategoryCreate, CategoryResponse
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
  