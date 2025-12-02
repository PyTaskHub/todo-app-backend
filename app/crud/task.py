"""
CRUD operations for Task model.
"""
from typing import Optional

from sqlalchemy import select, func, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from app.models.task import Task, Priority, Status
from app.models.category import Category
from app.schemas.task import TaskCreate, TaskUpdate
from app.schemas.task_filters import TaskSortBy, SortOrder, StatusFilter

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
    offset: int = 0,
    status_filter: StatusFilter = StatusFilter.all,
    search: Optional[str] = None,
    category_filter: Optional[str] = None,
    sort_by: TaskSortBy = TaskSortBy.created_at,
    order: SortOrder = SortOrder.desc,
) -> tuple[list[Task], int]:
    """
    Get list of tasks for the user with optional status/category filtering, sorting and pagination.
    
    Args:
        limit: pagination limit
        offset: pagination offset
        status_filter: task status filter:
            - "all"        — return all tasks
            - "pending"    — only incomplete tasks
            - "completed"  — only finished tasks
        search: search term for task title (case-insensitive, optional)
        category_filter:
            - None         — no category
            - "null"       — only tasks without category
            - integer id   — tasks with this category (must belong to user)
        sort_by: field to sort by ('created_at', 'priority', 'due_date', 'status')
        order: asc/desc order
    
    Returns:
            items: list of Task objects
            total: total number of tasks matching the filter
    """
    query = (
        select(Task)
        .where(Task.user_id == user_id)
    )

    if status_filter == "pending":
        query = query.where(Task.status == Status.pending)
    elif status_filter == "completed":
        query = query.where(Task.status == Status.completed)


    parsed_category_id: Optional[int] = None

    if category_filter == "null":
        query = query.where(Task.category_id.is_(None))
    elif category_filter is not None:
        try:
            parsed_category_id = int(category_filter)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid category_id format"
            )
        
        category = await get_category_if_owned(
            db=db,
            category_id=parsed_category_id,
            user_id=user_id
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found or doesn't belong to the user"  
            )
    
        query = query.where(Task.category_id == parsed_category_id)

    if search and search.strip():
        search_term = search.strip()
        query = query.where(Task.title.ilike(f"%{search_term}%"))

    sort_fields = {
        TaskSortBy.created_at: Task.created_at,
        TaskSortBy.due_date: Task.due_date,
        TaskSortBy.priority: Task.priority,
        TaskSortBy.status: Task.status
    }

    sort_column = sort_fields[sort_by]
    order_func = desc if order == SortOrder.desc else asc

    query = (
        query.order_by(order_func(sort_column))
        .limit(limit)
        .offset(offset)
    )
    
    result = await db.execute(query)
    items = result.scalars().all()

    count_query = select(func.count()).where(Task.user_id == user_id)

    if status_filter == "pending":
        count_query = count_query.where(Task.status == Status.pending)
    elif status_filter == "completed":
        count_query = count_query.where(Task.status == Status.completed)

    if category_filter == "null":
        count_query = count_query.where(Task.category_id.is_(None))
    elif parsed_category_id is not None:
        count_query = count_query.where(Task.category_id == parsed_category_id)

    if search and search.strip():
        search_term = search.strip()
        count_query = count_query.where(Task.title.ilike(f"%{search_term}%"))

    total = (await db.execute(count_query)).scalar()

    return items, total

async def delete_the_task(
        db: AsyncSession,
        task_id: int,
        user_id: int
) -> None:
    """
    Delete task.

    Args:
        db: database session
        task_id: task id from request
        user_id: id from authenticated user which create task
    """
    # Get task by id and user id
    task_data = select(Task).where(
        Task.id == task_id,
        Task.user_id == user_id,
    )
    result = await db.execute(task_data)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or doesn't belong to current user",
        )
    # Delete task
    await db.delete(task)
    await db.commit()
