"""API Router برای سنجش‌ازدور"""
from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


router = APIRouter(prefix="/remote-sensing", tags=["Remote Sensing"])


class VegetationHealthResponse(BaseModel):
    location_lat: float
    location_lon: float
    ndvi: float
    health_class: int
    health_label: str
    analysis_date: str
    satellite: str


class SpectralIndexRequest(BaseModel):
    lat: float
    lon: float
    start_date: datetime
    end_date: datetime
    satellite: str = "Sentinel-2"
    index_type: str = "NDVI"


@router.get("/vegetation-health/{lat}/{lon}")
async def get_vegetation_health(
    lat: float,
    lon: float,
    date: Optional[datetime] = None
):
    """دریافت سلامت پوشش گیاهی در یک نقطه"""
    # TODO: اتصال به Service
    return {
        "location_lat": lat,
        "location_lon": lon,
        "ndvi": 0.45,
        "health_class": 4,
        "health_label": "Good",
        "analysis_date": datetime.utcnow().isoformat(),
        "satellite": "Sentinel-2"
    }


@router.post("/calculate-index")
async def calculate_spectral_index(request: SpectralIndexRequest):
    """محاسبه شاخص طیفی در یک منطقه"""
    # TODO: اتصال به Service
    return {
        "index_type": request.index_type,
        "satellite": request.satellite,
        "mean_value": 0.52,
        "min_value": 0.12,
        "max_value": 0.89,
        "calculated_at": datetime.utcnow().isoformat()
    }


@router.get("/water-bodies/{lat}/{lon}")
async def detect_water_bodies(
    lat: float,
    lon: float,
    radius_km: float = Query(default=5.0, ge=0.1, le=50.0)
):
    """تشخیص پیکره‌های آبی در یک منطقه"""
    # TODO: اتصال به Service
    return {
        "center_lat": lat,
        "center_lon": lon,
        "radius_km": radius_km,
        "water_percentage": 12.5,
        "water_area_km2": 0.98,
        "analysis_date": datetime.utcnow().isoformat()
    }


@router.get("/soil-salinity/{lat}/{lon}")
async def analyze_soil_salinity(
    lat: float,
    lon: float
):
    """تحلیل شوری خاک"""
    # TODO: اتصال به Service
    return {
        "location_lat": lat,
        "location_lon": lon,
        "ndsi": 0.18,
        "salinity_class": 2,
        "salinity_label": "Slightly saline",
        "analysis_date": datetime.utcnow().isoformat()
    }
