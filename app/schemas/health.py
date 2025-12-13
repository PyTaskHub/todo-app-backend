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
