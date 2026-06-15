"""Hydrology API Router"""
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List
from datetime import datetime
from .schemas.hydrology_schemas import (
    WatershedCreate,
    WatershedResponse,
    ScenarioCreate,
    ScenarioResponse,
    SimulationResultResponse,
    WaterBalanceRequest
)
from .repositories.hydrology_repository import HydrologyRepository
from .services.hydrology_service import HydrologyService


router = APIRouter(prefix="/hydrology", tags=["Hydrology"])


def get_hydrology_repository() -> HydrologyRepository:
    """Dependency Injection"""
    return HydrologyRepository()


def get_hydrology_service(
    repo: HydrologyRepository = Depends(get_hydrology_repository)
) -> HydrologyService:
    """Dependency Injection"""
    return HydrologyService(repo)


# Watershed Endpoints
@router.post("/watersheds", response_model=WatershedResponse)
async def create_watershed(
    watershed: WatershedCreate,
    service: HydrologyService = Depends(get_hydrology_service)
):
    """ایجاد حوضه آبخیز جدید"""
    return await service.create_watershed(
        watershed_id=watershed.watershed_id,
        name=watershed.name,
        area_km2=watershed.area_km2,
        outlet_lat=watershed.outlet_lat,
        outlet_lon=watershed.outlet_lon,
        pilot_site=watershed.pilot_site
    )


@router.get("/watersheds/{watershed_id}", response_model=WatershedResponse)
async def get_watershed(
    watershed_id: str,
    repo: HydrologyRepository = Depends(get_hydrology_repository)
):
    """دریافت اطلاعات حوضه آبخیز"""
    watershed = await repo.get_watershed(watershed_id)
    if not watershed:
        raise HTTPException(status_code=404, detail="Watershed not found")
    return watershed


# Simulation Endpoints
@router.post("/simulate/swat")
async def run_swat_simulation(
    watershed_id: str,
    scenario_name: str,
    start_year: int,
    end_year: int,
    climate_data: Dict,
    service: HydrologyService = Depends(get_hydrology_service)
):
    """اجرای شبیه‌سازی SWAT"""
    return await service.run_swat_simulation(
        watershed_id=watershed_id,
        scenario_name=scenario_name,
        start_year=start_year,
        end_year=end_year,
        climate_data=climate_data
    )


@router.post("/simulate/weap")
async def run_weap_allocation(
    watershed_id: str,
    scenario_name: str,
    start_year: int,
    end_year: int,
    demand_data: Dict,
    supply_data: Dict,
    service: HydrologyService = Depends(get_hydrology_service)
):
    """اجرای تخصیص آب WEAP"""
    return await service.run_weap_allocation(
        watershed_id=watershed_id,
        scenario_name=scenario_name,
        start_year=start_year,
        end_year=end_year,
        demand_data=demand_data,
        supply_data=supply_data
    )


@router.post("/analyze/climate-scenario")
async def analyze_climate_scenario(
    watershed_id: str,
    scenario_name: str,
    climate_change: Dict,
    demand_growth: Dict,
    service: HydrologyService = Depends(get_hydrology_service)
):
    """تحلیل سناریوی تغییر اقلیم"""
    return await service.analyze_climate_scenario(
        watershed_id=watershed_id,
        scenario_name=scenario_name,
        climate_change=climate_change,
        demand_growth=demand_growth
    )


# Results Endpoints
@router.get("/results/watershed/{watershed_id}")
async def get_watershed_results(
    watershed_id: str,
    start_date: datetime = None,
    end_date: datetime = None,
    repo: HydrologyRepository = Depends(get_hydrology_repository)
):
    """دریافت نتایج شبیه‌سازی یک حوضه"""
    results = await repo.get_results_by_watershed(watershed_id, start_date, end_date)
    return {
        "watershed_id": watershed_id,
        "num_results": len(results),
        "results": results
    }


@router.post("/water-balance")
async def get_water_balance(
    request: WaterBalanceRequest,
    service: HydrologyService = Depends(get_hydrology_service)
):
    """محاسبه بیلان آبی"""
    return await service.get_water_balance(
        watershed_id=request.watershed_id,
        start_date=request.start_date,
        end_date=request.end_date
    )
