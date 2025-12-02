"""
Task management endpoints.
"""
from fastapi import APIRouter, Depends, status, Query

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import CurrentUser, get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskListResponse
from app.schemas.task_filters import TaskSortBy, SortOrder, StatusFilter 
from app.crud.task import create_task, delete_the_task, update_task, get_task_by_id, get_tasks_for_user

router = APIRouter()

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_new_task(
    task_in: TaskCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    Create a new task.

    - Authentication required (Bearer token)
    - **title**: must be provided (max 200 characters)
    - Optional fields validated through Pydantic
    - If **category_id** is provided — it must belong to current user

    Returns created task in TaskResponse format.
    """
    task = await create_task(
        db=db,
        task_in=task_in,
        user_id=current_user.id
    )

    return task

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK
)
async def update_existing_task(
    task_id: int,
    task_in: TaskUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """
    Update task belonging to the authenticated user.

    - **Authentication required**
    - Only the task owner can update the task
    - Fields: **title**, **description**, **priority**, **due_date**, **category_id**
    - **status** can be updated via the /complete and /incomplete endpoints
    
    Returns updated task.
    """

    updated_task = await update_task(
        db=db,
        task_id=task_id,
        task_in=task_in,
        user_id=current_user.id
    )

    return updated_task

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK
)
async def get_single_task(
    task_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> TaskResponse:
    """
    Get a single task.

    - Authentication required (Bearer token)
    - Optional fields validated through Pydantic
    - If **category_id** is provided — it must belong to current user
    - If task has the category, response contains category data

    Returns single task in TaskResponse format.
    """
    task = await get_task_by_id(
        db=db,
        user_id=current_user.id,
        task_id=task_id,
    )
    return task

@router.get(
    "/",
    response_model=TaskListResponse,
    status_code=status.HTTP_200_OK
)    
async def get_tasks(
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    status_filter: StatusFilter = StatusFilter.all,
    category_id: Optional[str] = None,
    sort_by: TaskSortBy = TaskSortBy.created_at,
    order: SortOrder = SortOrder.desc,
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    """
    Get paginated and filtered list of tasks for the authenticated user.

    - **Authentication required**
    - Returns only tasks belonging to the current user
    - Sorted by created_at (newest first)
    - Supports pagination via **limit** and **offset**
    - Supports filtering by **status**:
        - **all** (default) — return all tasks
        - **pending** — only incomplete tasks
        - **completed** — only completed tasks
    - Supports filtering by **category_id**:
        - **{id}** — tasks of this category (belongs to user)
        - **null** — tasks without category
        - **omitted** — all tasks
    - Supports sorting by **created_at**, **priority**, **due_date**, **status**
        - asc — tasks are sorted in ascending order
        - desc — tasks are sorted in descending order
    """
    
    items, total = await get_tasks_for_user(
        db=db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
        status_filter=status_filter,
        category_filter=category_id,
        sort_by=sort_by,
        order=order,
    )

    return TaskListResponse(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        401: {"description": "Not authenticated"},
        404: {"description": "Task not found or doesn't belong to user"},
    },
)
async def delete_task(
    task_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
) -> None:
    """
    Delete task.

    - Requires Authorization: Bearer <token>
    - Task owner can delete it only
    - Task is deleted completely

    Returns 204 No Content if success.
    """
    await delete_the_task(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
