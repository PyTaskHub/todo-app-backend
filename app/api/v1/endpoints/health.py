"""
Health check endpoint.
"""
from fastapi import APIRouter, Depends, status, Response
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
    description="Return application and database status",
        responses={
        200: {
            "description": "Service is healthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "database": "connected",
                        "timestamp": "2025-12-12T15:04:32.662666Z",
                    }
                }
            },
        },
        503: {
            "description": "Service is unhealthy",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "database": "unavailable",
                        "timestamp": "2025-12-12T15:04:32.662666Z",
                    }
                }
            },
        },
    },
)
async def health_check(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> HealthResponse:
    """
    Return application and database status.

    - Checks DB connection with a simple query
    - Returns current UTC timestamp
    """
    try:
        # Check DB connectivity
        await db.execute(text("SELECT 1"))
        response.status_code = status.HTTP_200_OK
        app_status = "healthy"
        db_status = "connected"
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        db_status = "unavailable"
        app_status = "unhealthy"

    # Current UTC time in ISO format
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    return {
        "status": app_status,
        "database": db_status,
        "timestamp": timestamp,
    }
