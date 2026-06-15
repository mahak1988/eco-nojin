"""Modules Endpoints"""

from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def list_modules():
    """List modules"""
    return {"modules": [], "message": "Modules endpoint - coming soon"}
