"""
SQLAlchemy models.

All models are imported here for Alembic autogenerate to work.
"""
from app.db.session import Base
from app.models.user import User

__all__ = [
    "Base",
    "User",
]