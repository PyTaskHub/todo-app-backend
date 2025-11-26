"""
CRUD operations for Category model.
"""
from typing import Optional
from fastapi import HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate

async def get_category_by_user(
        db: AsyncSession, 
        category_name: str, 
        current_user_id: int
        ) -> Optional[Category]:
    """
    Get category by user.

    Args:
        db: Database session
        category_name: Category name
        current_user_id: ID of current user

    Returns:
        Category object or None if not found
    """ 
    result = await db.execute(select(Category).where(
        Category.name == category_name,
        Category.user_id == current_user_id
    ))
    return result.scalar_one_or_none()

async def get_category_by_id(
        db: AsyncSession, 
        current_user_id: int, 
        category_id: int = Path(..., title="ID of category")
        ):
    """
    Get category by category id.

    Args:
        db: Database session
        current_user_id: ID of current user
        category_id: Category ID

    Returns:
        Category object or None if not found
    """
    result = await db.execute(select(Category).where(
    Category.id == category_id,
    Category.user_id == current_user_id
    ))
    return result.scalar_one_or_none()


async def create_category(
        db: AsyncSession, 
        current_user_id: int, 
        category: CategoryCreate
        ) -> Category:
    """
    Create new category.

    Args:
        db: Database session
        user_id: Current user id
        category: Category data from request

    Returns:
        Created Category object
    """
    # Check if category already exists
    existing_category = await get_category_by_user(
        db, 
        category_name=category.name,
        current_user_id=current_user_id 
    )
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category already exists"
        )
    # Create category instance
    db_category = Category(
      name=category.name,
      description=category.description,
      user_id=current_user_id, 
    )

    # Add to database
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)

    return db_category



async def update_category(
        db: AsyncSession, 
        new_category: CategoryUpdate, 
        current_user_id: int, 
        category_id: int
        ) -> Category:
    """
    Update category.

    Args:
        db: Database session
        new_category: Category data from request for updating
        current_user_id: Current user id
        category_id: Current category id

    Returns:
        Updated Category object
    """
    # Check if category is exists
    existing_category = await get_category_by_id(
       db,
       current_user_id,
       category_id
    )
    if existing_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category doesn't exists or doesn't belong to current user"
        )
    
    # Check uniq category name
    category_with_same_name = await get_category_by_user(
        db, 
        category_name=new_category.name,
        current_user_id=current_user_id 
    )
    if category_with_same_name:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with same name already exsists"
        )
    
    # Add changes to database
    existing_category.name = new_category.name
    existing_category.description = new_category.description
    
    await db.commit()
    await db.refresh(existing_category)

    return existing_category