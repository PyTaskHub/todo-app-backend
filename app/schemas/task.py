from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.task import Priority, Status


class TaskBase(BaseModel):
    """
    Base Task schema with common fields.
    """

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="title (1-200 characters)",
        examples=["buy groceries"],
    )

    description: Optional[str] = Field(
        None,
        description="detailed task description",
        examples=["buy milk, eggs, tea, coffee..."],
    )

    category_id: Optional[int] = Field(
        None,
        description="category ID assigned to this task",
    )

    priority: Optional[Priority] = Field(
        None,
        description="Task priority: low, medium, high",
    )

    due_date: Optional[datetime] = Field(
        None,
        description="Deadline of the task",
    )

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v):
        """
        Validate that due_date is in ISO format, not Unix timestamp.

        Accepts:
        - None (optional field)
        - datetime objects
        - ISO format strings (e.g., "2025-12-31T23:59:59")

        Rejects:
        - Numeric values (int/float) which would be interpreted as Unix timestamps
        """
        if v is None:
            return v

        # Reject numeric Unix timestamps
        if isinstance(v, (int, float)):
            raise ValueError(
                "due_date must be in ISO 8601 format (e.g., '2025-12-31T23:59:59'), "
                "not a Unix timestamp"
            )

        # Accept datetime objects and strings (Pydantic will parse ISO strings)
        return v

class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    Inherits all fields from TaskBase.
    """

    pass


class TaskUpdate(BaseModel):
    """
    Schema for updating task information.
    All fields are optional.
    """

    title: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="New title",
    )

    description: Optional[str] = Field(None, description="New description")
    category_id: Optional[int] = Field(None, description="New Category ID")
    priority: Optional[Priority] = Field(
        None, description="New priority (low, medium, high)"
    )
    due_date: Optional[datetime] = Field(None, description="New due date")

    @field_validator("due_date", mode="before")
    @classmethod
    def validate_due_date(cls, v):
        """
        Validate that due_date is in ISO format, not Unix timestamp.

        Accepts:
        - None (optional field)
        - datetime objects
        - ISO format strings (e.g., "2025-12-31T23:59:59")

        Rejects:
        - Numeric values (int/float) which would be interpreted as Unix timestamps
        """
        if v is None:
            return v

        # Reject numeric Unix timestamps
        if isinstance(v, (int, float)):
            raise ValueError(
                "due_date must be in ISO 8601 format (e.g., '2025-12-31T23:59:59'), "
                "not a Unix timestamp"
            )

        # Accept datetime objects and strings (Pydantic will parse ISO strings)
        return v

class TaskResponse(TaskBase):
    """
    Schema for returning task information in API responses.
    Inherits all fields from TaskBase and add owns.
    """

    id: int = Field(..., description="task id")

    user_id: int = Field(..., description="owner id")

    status: Status = Field(..., description="task status (pending, completed)")

    created_at: datetime = Field(..., description="timestamp when task was created")

    updated_at: datetime = Field(..., description="timestamp when task was updated")

    completed_at: Optional[datetime] = Field(
        None, description="timestamp when task was completed"
    )

    category_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Category name (3 - 100 characters, optional field)",
    )

    category_description: Optional[str] = Field(
        None, description="Category description (optional field)"
    )

    model_config = ConfigDict(from_attributes=True)


class TaskListResponse(BaseModel):
    """
    Response schema for returning a paginated list of tasks.
    """

    items: list[TaskResponse] = Field(
        ...,
        description="Lists of tasks",
    )

    total: int = Field(
        ...,
        description="Total number of tasks for the current user",
    )

    limit: int = Field(
        ...,
        description="Pagination limit",
        examples=[20],
    )

    offset: int = Field(
        ...,
        description="Pagination offset",
        examples=[0],
    )

    model_config = ConfigDict(from_attributes=True)


class TaskStatsResponse(BaseModel):
    """
    Statistics for current user's tasks.
    """

    total: int = Field(
        ...,
        description="Total number of tasks for the user",
        examples=[25],
    )
    completed: int = Field(
        ...,
        description="Number of completed tasks",
        examples=[15],
    )
    pending: int = Field(
        ...,
        description="Number of pending (incomplete) tasks",
        examples=[10],
    )
    completion_rate: float = Field(
        ...,
        description="Completion percentage (0-100)",
        examples=[60.25],
    )
