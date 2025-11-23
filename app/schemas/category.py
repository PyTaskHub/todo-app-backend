"""
Pydantic schemas for Category model validation.
"""
# from datetime import datetime
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class CategoryBase(BaseModel):
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
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True) #разрешаем создание из ORM объектов
    