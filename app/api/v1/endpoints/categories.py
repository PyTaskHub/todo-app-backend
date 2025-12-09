
from fastapi import APIRouter, Depends, status
from app.api.deps import CurrentUser
from app.crud.category import create_category, update_category, get_user_categories_with_tasks_count, delete_category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate, CategoryListItem
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.post(
    "/", 
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new category",
    description="Create a new category for the authenticated user",
    responses={
        201: {
            "description": "Category successfully created",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Work",
                        "description": "Tasks related to work",
                        "user_id": 1,
                        "created_at": "2025-11-25T10:00:00Z",
                        "updated_at": "2025-11-25T10:05:00Z",
                    }
                }
            },
        },
        401: {"description": "Not authenticated"},
        409: {"description": "Category with this name already exists"},
        422: {"description": "Validation error. The request body does not match the expected schema"},
    },
)
async def create_new_category(
        current_user: CurrentUser,
        category_in: CategoryCreate,
        db: AsyncSession = Depends(get_db)
) -> CategoryResponse:
    """
    Create a new category for the authenticated user.

    - **name**: category name (must be unique per user)
    - **description**: optional category description

    Returns created category.
    """
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
    summary="Update category",
    description="Update an existing category of the authenticated user",
    responses={
        200: {
            "description": "Category successfully updated",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Personal",
                        "description": "Personal tasks",
                        "user_id": 1,
                        "created_at": "2025-11-25T10:00:00Z",
                        "updated_at": "2025-11-25T11:00:00Z",
                    }
                }
            },
        },
        401: {"description": "Not authenticated."},
        404: {"description": "Category not found or does not belong to the user"},
        409: {"description": "Category with this name already exists"},
        422: {"description": "Validation error. The request body does not match the expected schema"},
    },
)
async def update_the_category(
        category_id: int,
        current_user: CurrentUser,
        category_in: CategoryUpdate,
        db: AsyncSession = Depends(get_db)
) -> CategoryResponse:
    """
    Update an existing category of the authenticated user.

    - Requires authentication
    - Only the owner of the category can update it
    - Category name must remain unique for this user

    Returns updated category.
    """
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
  status_code=status.HTTP_200_OK,
    summary="List user categories",
    description="Get list of all categories for the authenticated user with tasks count",
    responses={
        200: {
            "description": "List of categories with tasks count",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "id": 1,
                            "name": "Work",
                            "description": "Work-related tasks",
                            "tasks_count": 3,
                            "created_at": "2025-11-25T10:00:00Z",
                        },
                        {
                            "id": 2,
                            "name": "Personal",
                            "description": "Personal todos",
                            "tasks_count": 5,
                            "created_at": "2025-11-26T09:30:00Z",
                        },
                    ]
                }
            },
        },
        401: {"description": "Not authenticated"},
    },
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
    summary="Delete category",
    description="Delete a category belonging to the authenticated user",
    responses={
        204: {"description": "Category successfully deleted"},
        401: {"description": "Not authenticated"},
        404: {"description": "Category not found or does not belong to the user"},
        422: {"description": "Validation error. The request does not match the expected schema"},
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
