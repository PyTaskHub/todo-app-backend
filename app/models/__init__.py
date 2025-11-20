"""
SQLAlchemy models.

All models are imported here for Alembic autogenerate to work.
"""
from app.db.session import Base
from app.models.user import User

from app.models.category import Category
from app.models.task import Task

__all__ = [
    "Base",
    "User",
    "Category",
    "Task",
]