"""Soil & Water Domain Router."""
from fastapi import APIRouter, Depends, Query
from .schemas.soil_water_schemas import SoilAnalysisRequest, ErosionRiskResponse
from .services.soil_water_service import SoilWaterService
from .repositories.soil_water_repository import SoilWaterRepository


router = APIRouter(prefix="/soil-water", tags=["Soil & Water"])


def get_soil_water_service() -> SoilWaterService:
    repo = SoilWaterRepository()
    return SoilWaterService(repo)


@router.post("/analyze")
async def analyze_soil(
    request: SoilAnalysisRequest,
    service: SoilWaterService = Depends(get_soil_water_service)
):
    """تحلیل سلامت خاک"""
    return await service.analyze_soil_health(
        request.location_lat,
        request.location_lon
    )


@router.get("/erosion-risk/{lat}/{lon}")
async def get_erosion_risk(
    lat: float,
    lon: float,
    service: SoilWaterService = Depends(get_soil_water_service)
):
    """محاسبه ریسک فرسایش"""
    return await service.calculate_rusle(lat, lon)
