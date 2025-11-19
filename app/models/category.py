from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship

# from .user import Base, User
from app.db.session import Base


# id, name, description (optional), user_id (FK), created_at, updated_at
class Category(Base):
    __tablename__ = 'category'
    id = Column(
        Integer, 
        primary_key=True
        )
    name = Column(
        String(100), 
        nullable=False,
        comment="Category name"
        )
    description = Column(
        Text, 
        nullable=True,
        comment="Category description"
        )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        comment="User who owns this category"
    )

    __table_args__ = (
        UniqueConstraint('name', 'user_id', name='uq_user_category_name'),
        Index('ix_category_user_id', 'user_id'),
    )

    user = relationship("User", back_populates="categories")
    task = relationship("Task", back_populates="categories")
