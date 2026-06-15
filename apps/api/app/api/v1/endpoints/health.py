"""Health Check Endpoints"""

from fastapi import APIRouter


router = APIRouter()


@router.get("/")
async def health_check():
    """Basic health check"""
    return {"status": "healthy", "service": "econojin-api"}
