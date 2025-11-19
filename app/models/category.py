from sqlalchemy import Column, Integer, String, Text, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from app.db.session import Base

class Category(Base):
    __tablename__ = 'categories'
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
    # task = relationship("Task", back_populates="category")
