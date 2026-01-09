"""
Example endpoints - Template for new endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import List
from app.core.database import supabase

router = APIRouter()


@router.get("")
async def get_examples():
    """Get all examples"""
    try:
        # Example query to Supabase
        # response = supabase.table("examples").select("*").execute()
        # return response.data
        return {"message": "Example endpoint - Replace with your logic"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{id}")
async def get_example(id: int):
    """Get example by ID"""
    try:
        # response = supabase.table("examples").select("*").eq("id", id).execute()
        # if not response.data:
        #     raise HTTPException(status_code=404, detail="Example not found")
        # return response.data[0]
        return {"id": id, "message": "Example endpoint - Replace with your logic"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

