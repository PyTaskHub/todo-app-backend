"""
Task management endpoints.
"""
from fastapi import APIRouter, Depends, status

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentUser, get_db
from app.schemas.task import TaskCreate, TaskResponse
from app.crud.task import create_task

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])

@router.post(
    "",
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