"""
CRUD operations for Category model.
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate
from app.models.task import Task

async def get_category_by_user(db: AsyncSession, category_name: str, current_user_id: int) -> Optional[Category]:
    """
    Get category by user.

    Args:
        db: Database session
        category_name: Category name

    Returns:
        Category object or None if not found
    """ 
    result = await db.execute(select(Category).where(
        Category.name == category_name,
        Category.user_id == current_user_id
    ))
    return result.scalar_one_or_none()

async def create_category(db: AsyncSession, current_user_id: int, category: CategoryCreate) -> Category:
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

async def get_user_categories_with_tasks_count(db: AsyncSession, user_id: int):
    """
    Get all categories of user with tasks count.

    - Returns only categories of given user
    - Sorted by category name (A-Z)
    - Includes tasks_count for each category
    """
    stmt = (
        select(
            Category,
            func.count(Task.id).label("tasks_count"),
        )
        .outerjoin(Task, Task.category_id == Category.id)
        .where(Category.user_id == user_id)
        .group_by(Category.id)
        .order_by(Category.name.asc())
    )

    result = await db.execute(stmt)
    # rows: list[Row[Category, int]]
    return result.all()

