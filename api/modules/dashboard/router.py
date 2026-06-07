from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from pydantic import BaseModel
from typing import Dict, Any
from fastapi import APIRouter

class DashboardStatsResponse(BaseModel):
    """Auto-generated response model for get_dashboard_stats"""
    total_users: int = 0
    active_users: int = 0
    total_sensors: int = 0
    total_actions: int = 0
    carbon_sequestered: float = 0.0
    water_saved: float = 0.0


router = APIRouter(tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
async def dashboard_stats():
    return {
        "active_users": 12450,
        "active_modules": 15,
        "monthly_growth_percent": 24.5,
        "api_status": "healthy",
        "modules_online": [
            "weather",
            "accounting",
            "calendar",
            "gis",
            "auth",
            "farmer",
            "education",
            "psychology",
            "ecomining",
            "community",
            "games",
            "settings",
            "store",
            "library",
            "desktop",
        ],
    }
