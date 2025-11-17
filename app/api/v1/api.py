"""
API v1 router aggregation.
"""
from fastapi import APIRouter

from app.api.v1.endpoints import auth


api_router = APIRouter()

# Include endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# TODO: - Add users router
# TODO: Task #10-14 - Add tasks router
# TODO: Task #15-17 - Add categories router