from api.services.drought.chirps import chirps
# api/modules/drought/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import random
import math

from api.services.drought_core import (
    SPI, SPEI, PDSI, VHI, KBDI, RAI, CDD,
    DroughtForecast, ClimateChangeAnalysis, DroughtRecommendations
)
from api.services.drought_databases import (
    get_all_plains, get_all_dams, get_all_basins, get_all_aquifers,
    get_all_climates, get_all_satellites, get_references,
    FORBIDDEN_PLAINS, DAMS, AQUIFERS
)



class DroughtStatsResponse(BaseModel):
    """Auto-generated response model for /statistics"""
    total_plains: int = 0
    total_dams: int = 0
    total_basins: int = 0
    severe_drought_areas: int = 0
    average_spi: float = 0.0
    water_deficit_percentage: float = 0.0


router = APIRouter(prefix="/drought", tags=["Drought"])


class SPIRequest(BaseModel):
    precipitation: List[float]
    time_scale: int = 3


class SPEIRequest(BaseModel):
    precipitation: List[float]
    temperature: List[float]
    time_scale: int = 3
    latitude: float = 35.0


class PDSIRequest(BaseModel):
    precipitation: List[float]
    pet: List[float]
    awc: float = 150.0


class VHIRequest(BaseModel):
    ndvi: List[float]
    temperature: List[float]
    alpha: float = 0.5


class KBDIRequest(BaseModel):
    daily_rainfall: List[float]
    daily_max_temp: List[float]
    annual_rainfall: float = 1000
    initial_kbdi: float = 200


class ClimateProjectionRequest(BaseModel):
    baseline_precipitation: Optional[List[float]] = None
    baseline_temperature: Optional[List[float]] = None
    scenario: str = "SSP2-4.5"
    target_year: int = 2050


@router.get("/indices", response_model=Dict[str, Any])
async def list_indices():
    """لیست تمام شاخص‌های خشکسالی"""
    return {
        "indices": [
            {"code": "SPI", "name": "Standardized Precipitation Index", "reference": "McKee et al. (1993), WMO"},
            {"code": "SPEI", "name": "Standardized Precipitation Evapotranspiration Index", "reference": "Vicente-Serrano (2010)"},
            {"code": "PDSI", "name": "Palmer Drought Severity Index", "reference": "Palmer (1965)"},
            {"code": "VHI", "name": "Vegetation Health Index", "reference": "Kogan (1995)"},
            {"code": "KBDI", "name": "Keetch-Byram Drought Index", "reference": "Keetch & Byram (1968)"},
            {"code": "RAI", "name": "Rainfall Anomaly Index", "reference": "Van Rooy (1965)"},
            {"code": "CDD", "name": "Consecutive Dry Days", "reference": "WMO"},
        ]
    }


@router.post("/spi", response_model=Dict[str, Any])
async def calculate_spi(request: SPIRequest):
    """محاسبه SPI"""
    results = SPI.calculate(request.precipitation, request.time_scale)
    return {"time_scale": request.time_scale, "data": results}


@router.post("/spei", response_model=Dict[str, Any])
async def calculate_spei(request: SPEIRequest):
    """محاسبه SPEI"""
    results = SPEI.calculate(
        request.precipitation, request.temperature,
        request.time_scale, request.latitude
    )
    return {"time_scale": request.time_scale, "data": results}


@router.post("/pdsi", response_model=Dict[str, Any])
async def calculate_pdsi(request: PDSIRequest):
    """محاسبه PDSI"""
    results = PDSI.calculate(request.precipitation, request.pet, request.awc)
    return {"data": results}


@router.post("/vhi", response_model=Dict[str, Any])
async def calculate_vhi(request: VHIRequest):
    """محاسبه VHI"""
    results = VHI.calculate(request.ndvi, request.temperature, request.alpha)
    return {"data": results}


@router.post("/kbdi", response_model=Dict[str, Any])
async def calculate_kbdi(request: KBDIRequest):
    """محاسبه KBDI"""
    results = KBDI.calculate_series(
        request.daily_rainfall, request.daily_max_temp,
        request.annual_rainfall, request.initial_kbdi
    )
    return {"data": results}


@router.get("/plains", response_model=Dict[str, Any])
async def list_plains(status: Optional[str] = None):
    """لیست دشت‌های ممنوعه"""
    plains = get_all_plains()
    if status:
        plains = [p for p in plains if status in p["status"]]
    return {"count": len(plains), "plains": plains}


@router.get("/dams", response_model=Dict[str, Any])
async def list_dams(province: Optional[str] = None):
    """لیست سدها"""
    dams = get_all_dams()
    if province:
        dams = [d for d in dams if d["province"] == province]
    return {"count": len(dams), "dams": dams}


@router.get("/basins", response_model=Dict[str, Any])
async def list_basins():
    """لیست حوضه‌های آبریز"""
    return {"basins": get_all_basins()}


@router.get("/aquifers", response_model=Dict[str, Any])
async def list_aquifers():
    """لیست آبخوان‌ها"""
    return {"aquifers": get_all_aquifers()}


@router.get("/climates", response_model=Dict[str, Any])
async def list_climates():
    """لیست اقلیم‌ها"""
    return {"climates": get_all_climates()}


@router.get("/satellites", response_model=Dict[str, Any])
async def list_satellites():
    """لیست ماهواره‌های پایش خشکسالی"""
    return {"satellites": get_all_satellites()}


@router.get("/references", response_model=Dict[str, Any])
async def list_references():
    """لیست مراجع بین‌المللی"""
    return {"references": get_references()}


@router.post("/climate-projection", response_model=Dict[str, Any])
async def climate_projection(request: ClimateProjectionRequest):
    """پیش‌بینی خشکسالی در سناریوهای تغییر اقلیم"""
    # داده‌های نمونه در صورت عدم ارائه
    baseline_precip = request.baseline_precipitation or [random.uniform(20, 80) for _ in range(30 * 12)]
    baseline_temp = request.baseline_temperature or [15 + 10 * math.sin(2 * math.pi * i / 12) for i in range(30 * 12)]
    
    result = ClimateChangeAnalysis.project_drought(
        baseline_precip, baseline_temp,
        request.scenario, request.target_year
    )
    return result


@router.get("/scenarios", response_model=Dict[str, Any])
async def list_scenarios():
    """لیست سناریوهای CMIP6"""
    return {
        "scenarios": ClimateChangeAnalysis.SCENARIOS
    }


@router.post("/forecast", response_model=Dict[str, Any])
async def drought_forecast(spi_history: List[float] = Query(...)):
    """پیش‌بینی خشکسالی ۳ ماهه"""
    return DroughtForecast.forecast_3month(spi_history)


@router.get("/recommendations/{severity}", response_model=Dict[str, Any])
async def get_recommendations(severity: str, sector: str = "agriculture"):
    """دریافت توصیه‌های مدیریتی"""
    return {
        "severity": severity,
        "recommendations": DroughtRecommendations.generate(severity, affected_sector=sector)
    }


@router.get("/statistics", response_model=DroughtStatsResponse)
async def drought_statistics():
    """آمار کلی خشکسالی"""
    critical_plains = sum(1 for p in FORBIDDEN_PLAINS if "بحرانی" in p["status"])
    low_dams = sum(1 for d in DAMS if d["current_percent"] < 40)
    critical_aquifers = sum(1 for a in AQUIFERS if a["status"] == "بحرانی")
    
    return {
        "total_plains": len(FORBIDDEN_PLAINS),
        "critical_plains": critical_plains,
        "total_dams": len(DAMS),
        "low_dams": low_dams,
        "total_aquifers": len(AQUIFERS),
        "critical_aquifers": critical_aquifers,
        "total_basins": 6,
    }