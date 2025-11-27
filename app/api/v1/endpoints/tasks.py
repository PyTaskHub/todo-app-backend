"""
Task management endpoints.
"""
from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.crud.task import create_task, update_task, get_task_by_id
from app.schemas.task import TaskCreate, TaskResponse

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
    current_user: CurrentUser,
    task_id_in: int,
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
        task_id=task_id_in,
    )

    return task
