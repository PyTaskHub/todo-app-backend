"""
Task model for managing user tasks.

Includes priority/status enums, relationships to User and Category,
and additional metadata such as due date and completion timestamp.
"""

from enum import Enum

from sqlalchemy import (
    Column, 
    Integer,
    String, 
    Text, 
    DateTime, 
    ForeignKey,
    Enum as SAEnum,
    Index,
)
from sqlalchemy.orm import relationship

from app.db.session import Base

# Pythom Enums - used inside the application and Pydantic

class Priority(str, Enum):
    """
    Task priority levels.

    Values:
        low:    Low priority
        medium: Medium priority (default)
        high:   High priority
    """
    low = "low"
    medium = "medium"
    high = "high"

class Status(str, Enum):
    """
    Task status values.

    Values:
        pending:   Task is not completed (default)
        completed: Task is finished
    """
    pending = "pending"
    completed = "completed"

# SQLAlchemy Enums used at database

PriorityEnum = SAEnum(
    Priority,
    name="priority_enum",
    create_constraint=True,
    comment="Allowed values for task priority",
)

StatusEnum = SAEnum(
    Status,
    name="status_enum",
    create_constraint=True,
    comment="Allowed values for task status",
)


class Task(Base):
    """
    Task model for storing todo items.

    Inherits:
        id, created_at, updated_at from Base.

    Relationships:
        - user:     Owner of the task (User)
        - category: Optional category assigned to the task (Category)
    """

    # Basic fields

    __tablename__ = "tasks"

    title = Column(
        String(200), 
        nullable=False,
        comment="Short title of the task (max 200 characters)"
    
    )
    description = Column(
        Text, 
        nullable=False,
        comment="Optional detailed description of the task"
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the user who created task"
    )

    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID of the category assigned to this task (optional)"
    )

    # Foreign Keys

    priority = Column(
        PriorityEnum, 
        nullable=False, 
        default=Priority.medium,
        comment="Task priority (low, medium, high)"
    )
    
    status = Column(
        StatusEnum, 
        nullable=False, 
        default=Status.pending,
        comment="Task status (pending, completed)"
    )

    # Timestamps for tasks

    due_date = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Deadline of the task (optional)"
    )

    completed_at = Column(
        DateTime(timezone=True), 
        nullable=True,
        comment="Timestamp when the task was marked completed"
    )

    # Relationships

    user = relationship(
        "User", 
        back_populates="tasks",
        doc="User who owns this task"
    )

    category = relationship(
        "Category", 
        back_populates="tasks",
        doc="Category assigned to this task"
    )

    # Indexes

    __table_args__ = (
        Index("idx_tasks_priority", "priority"),
        Index("idx_tasks_status", "status"),
    )

    def __repr__(self) -> str:
        """
        String representation of Task.

        Example:
            <Task(id=1, title='My test task', status='pending')>
        """
        return (
            f"<Task(id={self.id}, title='{self.title}', "
            f"status='{self.status}', priority='{self.priority}')>"
        )