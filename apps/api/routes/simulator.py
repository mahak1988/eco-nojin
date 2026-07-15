"""شبیه‌سازهای بوم‌شناختی Econojin"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import math

router = APIRouter(prefix="/api/simulator", tags=["simulator"])


class CarbonSim(BaseModel):
    area_hectares: float
    forest_type: str
    years: int


class WaterSim(BaseModel):
    area_hectares: float
    region: str
    years: int


class BioSim(BaseModel):
    area_hectares: float
    ecosystem_type: str
    restoration_level: float
    years: int


CARBON_RATES = {"rainforest": 25, "temperate": 12, "mangrove": 35, "grassland": 5, "boreal": 8, "agroforestry": 10}
WATER_RATES = {"wetland": 5000, "forest": 2000, "grassland": 800, "agriculture": 300}
BIO_BASELINE = {"rainforest": 0.85, "temperate": 0.65, "wetland": 0.75, "grassland": 0.45, "coral_reef": 0.90}


@router.post("/carbon/run")
async def run_carbon(sim: CarbonSim):
    rate = CARBON_RATES.get(sim.forest_type, 10)
    yearly = []
    cumulative = 0
    for y in range(1, sim.years + 1):
        growth = 1 - math.exp(-y / 3)
        annual = sim.area_hectares * rate * growth
        cumulative += annual
        yearly.append({
            "year": y,
            "annual_sequestration": round(annual, 2),
            "cumulative": round(cumulative, 2),
            "eco_reward": round(annual * 10, 2),
            "carbon_value_usd": round(annual * 30, 2),
        })
    return {
        "total_sequestration": round(cumulative, 2),
        "total_eco_reward": round(cumulative * 10, 2),
        "total_value_usd": round(cumulative * 30, 2),
        "yearly_data": yearly,
        "chart_data": {
            "labels": [f"سال {y['year']}" for y in yearly],
            "annual": [y["annual_sequestration"] for y in yearly],
            "cumulative": [y["cumulative"] for y in yearly],
        },
    }


@router.post("/water/run")
async def run_water(sim: WaterSim):
    rate = WATER_RATES.get(sim.region.lower(), 1000)
    yearly = []
    for y in range(1, sim.years + 1):
        retention = sim.area_hectares * rate * (0.8 + 0.2 * min(y / 5, 1))
        yearly.append({
            "year": y,
            "water_retained_m3": round(retention, 2),
            "water_quality_index": round(min(95, 60 + y * 5), 1),
        })
    return {
        "total_water_m3": round(sum(y["water_retained_m3"] for y in yearly), 2),
        "yearly_data": yearly,
        "chart_data": {
            "labels": [f"سال {y['year']}" for y in yearly],
            "retention": [y["water_retained_m3"] for y in yearly],
        },
    }


@router.post("/biodiversity/run")
async def run_biodiversity(sim: BioSim):
    baseline = BIO_BASELINE.get(sim.ecosystem_type, 0.5)
    target = baseline + (1 - baseline) * sim.restoration_level
    yearly = []
    for y in range(1, sim.years + 1):
        current = baseline + (target - baseline) * (1 - math.exp(-y / 3))
        species = int(sim.area_hectares * current * 50)
        yearly.append({
            "year": y,
            "biodiversity_index": round(current, 3),
            "estimated_species": species,
            "eco_reward": round((current - baseline) * sim.area_hectares * 20, 2),
        })
    return {
        "baseline_index": baseline,
        "final_index": round(yearly[-1]["biodiversity_index"], 3) if yearly else baseline,
        "yearly_data": yearly,
        "chart_data": {
            "labels": [f"سال {y['year']}" for y in yearly],
            "biodiversity": [y["biodiversity_index"] for y in yearly],
            "species": [y["estimated_species"] for y in yearly],
        },
    }


@router.get("/forest-types")
async def get_forest_types():
    return [
        {"value": "rainforest", "label": "جنگل بارانی", "rate": 25, "icon": "🌴"},
        {"value": "temperate", "label": "جنگل معتدل", "rate": 12, "icon": "🌳"},
        {"value": "mangrove", "label": "جنگل حرا", "rate": 35, "icon": "🌊"},
        {"value": "grassland", "label": "مرتع", "rate": 5, "icon": "🌾"},
        {"value": "boreal", "label": "جنگل شمالی", "rate": 8, "icon": "🌲"},
        {"value": "agroforestry", "label": "آگروفارستری", "rate": 10, "icon": "🌱"},
    ]


@router.get("/ecosystem-types")
async def get_ecosystem_types():
    return [
        {"value": "rainforest", "label": "جنگل بارانی", "baseline": 0.85, "icon": "🌴"},
        {"value": "temperate", "label": "جنگل معتدل", "baseline": 0.65, "icon": "🌳"},
        {"value": "wetland", "label": "تالاب", "baseline": 0.75, "icon": "🦆"},
        {"value": "grassland", "label": "مرتع", "baseline": 0.45, "icon": "🌾"},
        {"value": "coral_reef", "label": "صخره مرجانی", "baseline": 0.90, "icon": "🪸"},
    ]
