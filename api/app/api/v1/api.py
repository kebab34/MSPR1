"""
API v1 Router
"""
from fastapi import APIRouter
from app.api.v1.endpoints import health, example, auth

api_router = APIRouter()

# Include routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(example.router, prefix="/example", tags=["example"])
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])


