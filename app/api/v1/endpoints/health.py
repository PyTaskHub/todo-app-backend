"""
Health check endpoint.
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter()


@router.get("/health")
async def health_check(
    db: AsyncSession = Depends(get_db),
):
    """
    Return application and database status.

    - Checks DB connection with a simple query
    - Returns current UTC timestamp
    """
    try:
        # Check DB connectivity
        await db.execute(text("SELECT 1"))
        app_status = "healthy"
        db_status = "connected"
        http_status = status.HTTP_200_OK
    except Exception:
        db_status = "unavailable"
        app_status = "unhealthy"
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    # Current UTC time in ISO format
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Build health payload
    return JSONResponse(
        status_code=http_status,
        content={
            "status": app_status,
            "database": db_status,
            "timestamp": timestamp,
        },
    )
