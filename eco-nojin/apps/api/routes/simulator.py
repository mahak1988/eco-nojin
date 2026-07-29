"""Ecological simulator endpoints."""

from __future__ import annotations

import math
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from apps.shared_core.deps import require_write_auth

router = APIRouter(prefix="/api/v1/simulator", tags=["simulator"])

CARBON_RATES = {
    "rainforest": 25,
    "temperate": 12,
    "mangrove": 35,
    "grassland": 5,
    "boreal": 8,
    "agroforestry": 10,
}


class CarbonSim(BaseModel):
    area_hectares: float
    forest_type: str
    years: int


class WaterSim(BaseModel):
    area_hectares: float
    region: str
    years: int


@router.post("/carbon/run")
async def run_carbon(
    sim: CarbonSim,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    rate = CARBON_RATES.get(sim.forest_type, 10)
    yearly = []
    cumulative = 0.0
    for y in range(1, max(1, sim.years) + 1):
        growth = 1 - math.exp(-y / 3)
        annual = sim.area_hectares * rate * growth
        cumulative += annual
        yearly.append(
            {
                "year": y,
                "annual_sequestration": round(annual, 2),
                "cumulative": round(cumulative, 2),
            }
        )
    return {"total_sequestration": round(cumulative, 2), "yearly_data": yearly}


@router.post("/water/run")
async def run_water(
    sim: WaterSim,
    _: None = Depends(require_write_auth),
) -> dict[str, Any]:
    yearly = []
    for y in range(1, max(1, sim.years) + 1):
        retention = sim.area_hectares * 1000 * (0.8 + 0.2 * min(y / 5, 1))
        yearly.append({"year": y, "water_retained_m3": round(retention, 2)})
    return {
        "total_water_m3": round(sum(y["water_retained_m3"] for y in yearly), 2),
        "yearly_data": yearly,
        "region": sim.region,
    }


@router.get("/forest-types")
async def get_forest_types() -> list[dict[str, Any]]:
    return [{"value": k, "rate": v} for k, v in CARBON_RATES.items()]
