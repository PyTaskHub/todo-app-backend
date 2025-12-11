"""
Pydantic schemas for Category model validation.
"""
# from datetime import datetime
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
    """
    Base schema for category fields.
    """
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="Category name (3 - 100 characters)"
    )
    description: Optional[str] = Field(
        None,
        description="Category description (optional field)"
    )

class CategoryCreate(CategoryBase):
    """
    Schema for creating a new category.
    Inherits all fields from CategoryBase.
    """
    pass

class CategoryResponse(CategoryBase):
    """
    Category representation used in API responses.
    """
    id: int = Field(
        ...,
        description="Unique category identifier."
    )
    user_id: int = Field(
        ...,
        description="Identifier of the user who owns the category."
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the category was created.",
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the category was last updated.",
    )
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "user_id": 1,
                    "name": "Work",
                    "description": "Tasks related to work projects",
                    "created_at": "2025-11-25T10:00:00Z",
                    "updated_at": "2025-11-25T10:15:00Z",
                }
            ]
        },
    )

class CategoryUpdate(CategoryBase):
    """
    Schema for updating category. All fields are optional.
    """
    name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="New category name"
    )
    description: Optional[str] = Field(
        None,
        description="New category description"
    )  

class CategoryListItem(CategoryBase):
    """
    Lightweight category representation used in category lists.
    """
    id: int = Field(
        ...,
        description="Unique category identifier."
    )
    tasks_count: int = Field(
        ...,
        description="Number of tasks in this category.",
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the category was created.",
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "id": 1,
                    "name": "Work",
                    "description": "Tasks related to work projects",
                    "tasks_count": 3,
                    "created_at": "2025-11-25T10:00:00Z",
                }
            ]
        },
    )
