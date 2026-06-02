from fastapi import APIRouter, Query
from typing import Optional

router = APIRouter()

@router.get("/forecast")
async def get_forecast(location: str = Query(..., description="نام منطقه"), days: int = Query(7, ge=1, le=14)):
    return {
        "location": location,
        "days": days,
        "forecast": "offline_cached_data",
        "source": "local_model"
    }

@router.get("/alerts")
async def get_agricultural_alerts(region: str):
    return {
        "region": region,
        "alerts": [],
        "last_updated": "2026-06-01T00:00:00Z"
    }
