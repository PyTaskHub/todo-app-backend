from pydantic import BaseModel, Field
from typing import Literal

class HealthResponse(BaseModel):
    status: Literal["healthy", "unhealthy"] = Field(
        ...,
        description="Application status"
        )
    database: Literal["connected", "unavailable"] = Field(
        ...,
        description="Database status"
        )
    timestamp: str = Field(
        ..., 
        description="Current UTC timestamp (ISO 8601)"
        )

class RootResponse(BaseModel):
    message: str = Field(example="Welcome to PyTaskHub!")
    version: str = Field(example="1.0.0")
    docs: str = Field(example="/api/docs")
