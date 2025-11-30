"""
CRUD operations for Category model.
"""
from typing import Optional
from fastapi import HTTPException, status
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.task import Task
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

async def delete_category(db: AsyncSession, category_id: int, user_id: int) -> None:
    """
    Delete category owned by the given user.

    - Checks that category exists and belongs to user
    - Sets category_id = NULL for all user's tasks with this category
    - Deletes category
    """
    # Get category by id and user
    category_query = select(Category).where(
        Category.id == category_id,
        Category.user_id == user_id,
    )
    result = await db.execute(category_query)
    category = result.scalar_one_or_none()

    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found or does not belong to the user",
        )

    # Clear category for all user's tasks with this category
    await db.execute(
        update(Task)
        .where(
            Task.category_id == category_id,
            Task.user_id == user_id,
        )
        .values(category_id=None)
    )

    # Delete the category
    await db.delete(category)
    await db.commit()
