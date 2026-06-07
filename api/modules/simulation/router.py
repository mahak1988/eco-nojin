from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from typing import Dict, Any
from fastapi import APIRouter, Body

from api.services.simulation_engine import simulate_aquacrop, simulate_coupling, simulate_rothc

router = APIRouter(tags=["Simulation"])


@router.post("/rothc", response_model=Dict[str, Any])
async def run_rothc(data: dict = Body(...)):
    return simulate_rothc(
        initial_soc=float(data.get("initial_soc", 50)),
        clay_percent=float(data.get("clay_percent", 25)),
        mean_temp_c=float(data.get("mean_temp_c", 15)),
        annual_rain_mm=float(data.get("annual_rain_mm", 400)),
        years=int(data.get("years", 5)),
    )


@router.post("/aquacrop", response_model=Dict[str, Any])
async def run_aquacrop(data: dict = Body(...)):
    return simulate_aquacrop(
        crop=str(data.get("crop", "wheat")),
        area_ha=float(data.get("area_ha", 1)),
        irrigation_mm=float(data.get("irrigation_mm", 250)),
        rainfall_mm=float(data.get("rainfall_mm", 350)),
    )


@router.post("/coupling", response_model=Dict[str, Any])
async def run_coupling(data: dict = Body(...)):
    return simulate_coupling(data.get("modules", []))
