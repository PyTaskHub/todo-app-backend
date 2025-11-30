"""
CRUD operations for Task model.
"""
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, Path, status

from app.models.task import Task, Priority, Status
from app.models.category import Category
from app.schemas.task import TaskCreate, TaskUpdate

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
                detail="Category doesn't exist or doesn't belong to the user"
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

async def get_task_if_owned(
        db: AsyncSession,
        task_id: int,
        user_id: int
) -> Optional[Task]:
    """
    Get task by id only if it belongs to the given user.

    Args:
        db: database session
        task_id: task identifier
        user_id: current user id

    Returns:
        Task object if owned by user, otherwise None
    """
    query = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def update_task(
        db: AsyncSession,
        task_id: int,
        task_in: TaskUpdate,
        user_id: int
) -> Task:
    """
    Update existing task.

    Args:
        db: database session
        task_id: task id to update
        task_in: update fields
        user_id: owner id (only authenticated user)

    Returns:
        Updated Task object
    """
    task = await get_task_if_owned(db, task_id, user_id)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or doesn't belong to the user"
        )
    
    if task_in.category_id is not None:
        category = await get_category_if_owned(db, task_in.category_id, user_id)
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category doesn't exist or doesn't belong to the user"
            )
        
    update_data = task_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(task, field, value)

    db.add(task)
    await db.commit()
    await db.refresh(task)

    return task

async def get_task_by_id(
        db: AsyncSession,
        user_id: int,
        task_id: int
) -> Task:
    """
    Get single task by id.

    Args:
        db: database session
        user_id: id from authenticated user which create task
        task_id: task id from request
    Returns:
        Task object
    """
    task_by_id = await get_task_if_owned(db, task_id, user_id)

    # Check if task is exists
    if task_by_id is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # If task contains category
    if task_by_id.category_id is not None:
        category = await get_category_if_owned(db, task_by_id.category_id, user_id)
        if category:  
          task_by_id.category_name = category.name
          task_by_id.category_description = category.description
          
    return task_by_id

async def get_tasks_for_user(
    db: AsyncSession,
    user_id: int,
    limit: int = 20,
    offset: int = 0
) -> tuple[list[Task], int]:
    """
    Get list of tasks for the user with pagination.
    
    Args: 
        limit: pagination limit
        offset: pagination offset
    
    Returns:
        items, total
    """
    query = (
        select(Task)
        .where(Task.user_id == user_id)
        .order_by(Task.created_at.desc())
        .limit(limit)
        .offset(offset)
    )
    
    result = await db.execute(query)
    items = result.scalars().all()

    count_query = select(func.count()).where(Task.user_id == user_id)
    total = (await db.execute(count_query)).scalar()

    return items, total
