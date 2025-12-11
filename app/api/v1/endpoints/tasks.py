"""
Task management endpoints.
"""
from fastapi import APIRouter, Depends, status, Query

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.api.deps import CurrentUser, get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate, TaskListResponse, TaskStatsResponse
from app.schemas.task_filters import TaskSortBy, SortOrder, StatusFilter 
from app.crud.task import create_task, delete_the_task, update_task, get_task_by_id, get_tasks_for_user, get_task_statistics_for_user, mark_task_as_completed, mark_task_as_pending

router = APIRouter()

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Create a new task belonging to the authenticated user",
    responses={
        201: {
            "description": "Task successfully created.",
            "content": {
                "application/json": {
                    "example": {
                        "title": "Buy groceries",
                        "description": "Milk, eggs, tea, coffee",
                        "category_id": 1,
                        "priority": "medium",
                        "due_date": "2025-12-11T10:08:01.869000Z",
                        "id": 12,
                        "user_id": 1,
                        "status": "completed",
                        "created_at": "2025-12-11T10:10:34.672454Z",
                        "updated_at": "2025-12-11T10:12:10.123000Z",
                        "completed_at": "2025-12-11T10:12:10.123000Z",
                        "category_name": "Personal",
                        "category_description": "Tasks related to personal life"
                        }
                    }
                }
            },
        400: {"description": "Category doesn't exist or doesn't belong to the user"},
        401: {"description": "Not authenticated"},
        422: {"description": "Validation error. The request body does not match the expected schema"},
    }
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
    status_code=status.HTTP_200_OK,
    summary="Update an existing task",
    description="Update fields of a task belonging to the authenticated user",
    responses={
        200: {
            "description": "Task successfully updated.",
            "content": {
                "application/json": {
                    "example": {
                        "title": "Buy groceries (updated)",
                        "description": "Milk, eggs, tea, coffee, juice",
                        "category_id": 1,
                        "priority": "high",
                        "due_date": "2025-12-12T10:00:00Z",
                        "id": 12,
                        "user_id": 1,
                        "status": "completed",
                        "created_at": "2025-12-11T10:10:34.672454Z",
                        "updated_at": "2025-12-11T11:00:00.000000Z",
                        "completed_at": "2025-12-11T10:12:10.123000Z",
                        "category_name": "Personal",
                        "category_description": "Tasks related to personal life"
                    }
                }
            }
        },
        400: {"description": "Category doesn't exist or doesn't belong to the user"},
        401: {"description": "Not authenticated"},
        404: {"description": "Task not found or doesn't belong to the user"},
        422: {"description": "Validation error. The path parameter or request body does not match the expected schema"},
    }
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
    "/stats",
    response_model=TaskStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get task statistics",
    description="Return statistics for tasks belonging to the authenticated user",
    responses={
        200: {
            "description": "Statistics successfully retrieved.",
            "content": {
                "application/json": {
                    "example": {
                        "total": 14,
                        "completed": 8,
                        "pending": 6,
                        "completion_rate": 57.14
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
    }
)
async def get_task_statistics(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Get statistics for the current user's tasks.

    - Requires Authorization: Bearer <token>
    - Counts tasks with status = "completed" and "pending"
    - Returns:
        - total - total number of tasks
        - completed - number of completed tasks
        - pending - number of pending tasks
        - completion_rate - completion percentage (0–100, rounded to 2 decimals)
    """
    stats = await get_task_statistics_for_user(
        db=db,
        user_id=current_user.id,
    )
    return stats

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single task",
    description="Retrieve one task belonging to the authenticated user",
    responses={
        200: {
            "description": "Task successfully retrieved.",
            "content": {
                "application/json": {
                    "example": {
                        "title": "Buy groceries",
                        "description": "Milk, eggs, tea, coffee",
                        "category_id": 1,
                        "priority": "medium",
                        "due_date": "2025-12-11T10:08:01.869000Z",
                        "id": 12,
                        "user_id": 1,
                        "status": "completed",
                        "created_at": "2025-12-11T10:10:34.672454Z",
                        "updated_at": "2025-12-11T10:12:10.123000Z",
                        "completed_at": "2025-12-11T10:12:10.123000Z",
                        "category_name": "Personal",
                        "category_description": "Tasks related to personal life"
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
        404: {"description": "Task not found or doesn't belong to the user"},
        422: {"description": "Validation error. Invalid path parameter"},
   }
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
    status_code=status.HTTP_200_OK,
    summary="Get tasks",
    description="Return a filtered and paginated list of tasks belonging to the authenticated user",
    responses={
        200: {
            "description": "Tasks successfully retrieved.",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "title": "Buy groceries",
                                "description": "Milk, eggs, tea, coffee",
                                "category_id": 1,
                                "priority": "medium",
                                "due_date": "2025-12-11T10:08:01.869000Z",
                                "id": 12,
                                "user_id": 1,
                                "status": "pending",
                                "created_at": "2025-12-11T10:10:34.672454Z",
                                "updated_at": "2025-12-11T10:12:10.123000Z",
                                "completed_at": None,
                                "category_name": "Personal",
                                "category_description": "Tasks related to personal life"
                            },
                            {
                                "title": "Call mom",
                                "description": "Weekly check-in",
                                "category_id": 2,
                                "priority": "low",
                                "due_date": "2025-12-12T15:00:00Z",
                                "id": 13,
                                "user_id": 1,
                                "status": "completed",
                                "created_at": "2025-12-10T09:00:00Z",
                                "updated_at": "2025-12-11T09:30:00Z",
                                "completed_at": "2025-12-11T09:30:00Z",
                                "category_name": "Family",
                                "category_description": "Family-related tasks"
                            }
                        ],
                        "total": 2,
                        "limit": 20,
                        "offset": 0
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
        404: {"description": "Category not found or doesn't belong to the user"},
        422: {"description": "Validation error. Invalid query parameters"},
        }
)  
async def get_tasks(
    current_user: CurrentUser,
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tasks to return"),
    offset: int = Query(0, ge=0, description="Number of tasks to skip before starting to return results"),
    status_filter: StatusFilter = Query(StatusFilter.all, description="Filter by task status"),
    search: Optional[str] = Query(None, description="Search term for case-insensitive searching (optional)"),
    category_id: Optional[int] = Query(None, description="Filter by category id belonging to the current user (optional)"),
    sort_by: TaskSortBy = Query(TaskSortBy.created_at, description="Field to sort tasks by"),
    order: SortOrder = Query(SortOrder.desc, description="Sort direction"), 
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
    - Supports case-insensitive searching by **title**:
        - **{search_term}** — search in task titles
        - **null** — all tasks
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
        search=search,
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
    summary="Delete a task",
    description="Delete a task belonging to the authenticated user",
    responses={
        204: {"description": "Task successfully deleted"},
        401: {"description": "Not authenticated"},
        404: {"description": "Task not found or doesn't belong to the user"},
        422: {"description": "Validation error. Invalid path parameter"},    
    }
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


@router.patch(
    "/{task_id}/complete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark task as completed",
    description="Set task status to 'completed' and update timestamps",
    responses={
        200: {
            "description": "Task marked as completed.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 12,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, tea, coffee",
                        "category_id": 1,
                        "priority": "medium",
                        "due_date": "2025-12-11T10:08:01.869000Z",
                        "user_id": 1,
                        "status": "completed",
                        "created_at": "2025-12-11T10:10:34.672454Z",
                        "updated_at": "2025-12-11T11:15:00.000000Z",
                        "completed_at": "2025-12-11T11:15:00.000000Z",
                        "category_name": "Personal",
                        "category_description": "Tasks related to personal life"
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
        404: {"description": "Task not found or doesn't belong to the user"},
        422: {"description": "Validation error. Invalid path parameter"},
    }
)
async def complete_task(
    task_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """
    Mark task as completed.

    - Requires Authorization: Bearer <token>
    - Only task owner can mark it as completed
    - Sets **status** to "completed"
    - Sets **completed_at** to current UTC timestamp
    - Updates **updated_at** timestamp
    - Idempotent: if task is already completed, returns it unchanged

    Returns updated task in TaskResponse format.
    """
    task = await mark_task_as_completed(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
    return task


@router.patch(
    "/{task_id}/uncomplete",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Mark task as pending",
    description="Set task status to 'pending' and clear completed_at timestamp.",
    responses={
        200: {
            "description": "Task marked as pending.",
            "content": {
                "application/json": {
                    "example": {
                        "id": 12,
                        "title": "Buy groceries",
                        "description": "Milk, eggs, tea, coffee",
                        "category_id": 1,
                        "priority": "medium",
                        "due_date": "2025-12-11T10:08:01.869000Z",
                        "user_id": 1,
                        "status": "pending",
                        "created_at": "2025-12-11T10:10:34.672454Z",
                        "updated_at": "2025-12-11T11:20:00.000000Z",
                        "completed_at": None,
                        "category_name": "Personal",
                        "category_description": "Tasks related to personal life"
                    }
                }
            }
        },
        401: {"description": "Not authenticated"},
        404: {"description": "Task not found or doesn't belong to the user"},
        422: {"description": "Validation error. Invalid path parameter"},    
    }
)
async def uncomplete_task(
    task_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """
    Mark task as pending/incomplete.

    - Requires Authorization: Bearer <token>
    - Only task owner can mark it as pending
    - Sets **status** to "pending"
    - Clears **completed_at** (sets to null)
    - Updates **updated_at** timestamp
    - Idempotent: if task is already pending, returns it unchanged

    Returns updated task in TaskResponse format.
    """
    task = await mark_task_as_pending(
        db=db,
        task_id=task_id,
        user_id=current_user.id
    )
    return task