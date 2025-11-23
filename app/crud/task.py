"""
CRUD operations for Task model.
"""
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.task import Task, Priority, Status
from app.models.category import Category
from app.schemas.task import TaskCreate

async def get_category_if_owned(
        db: AsyncSession,
        category_id: int,
        user_id: int,
) -> Optional[Category]: 
    """
    Get category by id only if it belongs to the given user.

    Args:
        db: database session
        category_id: category id
        user_id: current user id

    Returns:
        Category object if owned by user, otherwise None
    """
    query = select(Category).where(
        Category.id == category_id,
        Category.user_id == user_id
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_task(
        db: AsyncSession,
        task_in: TaskCreate,
        user_id: int
) -> Task:
    """
    Create new task.

    Args:
        db: database session
        task_in: task data from request
        user_id: id from authenticated user which create task
    Returns:
        Created Task object
    """
    
    if task_in.category_id is not None:
        category = await get_category_if_owned(db, task_in.category_id, user_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category doesnt exist or doesnt belong to the user"
            )
        
    # Create task instance
    db_task = Task(
        title=task_in.title,
        description=task_in.description,
        user_id=user_id,
        category_id=task_in.category_id,
        priority=task_in.priority or Priority.medium,
        status=Status.pending,
        due_date=task_in.due_date,
    )

    # Add to database
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)

    return db_task
