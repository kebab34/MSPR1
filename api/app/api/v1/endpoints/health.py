"""
Health check endpoints
"""
from fastapi import APIRouter
from app.core.database import supabase

router = APIRouter()


@router.get("")
async def health():
    """Health check endpoint"""
    try:
        # Test Supabase connection
        supabase.table("_health").select("*").limit(1).execute()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}


