"""
مدل‌های اقتصادی و شبیه‌سازی مونت‌کارلو
"""
import math
import random
import statistics
from typing import Any, Dict, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/economic", tags=["Economic Models"])


class SimulationInput(BaseModel):
    area_ha: float = Field(10, description="سطح زیر کشت (هکتار)")
    yield_base: float = Field(1.35, description="عملکرد پایه (تن/هکتار)")
    price_per_ton: float = Field(12000, description="قیمت بازار (تومان)")
    water_cost: float = Field(1500000, description="هزینه کل آب")
    labor_cost: float = Field(2000000, description="هزینه نیروی کار")
    other_costs: float = Field(8000000, description="سایر هزینه‌ها")
    climate_risk: float = Field(0.2, ge=0, le=1, description="ضریب ریسک اقلیمی")
    iterations: int = Field(1000, ge=100, le=5000)


class ProfitResult(BaseModel):
    expected_profit: float
    revenue: float
    total_cost: float
    roi_percent: float


@router.post("/simulate/profit", response_model=ProfitResult)
async def calculate_profit(data: SimulationInput):
    revenue = data.area_ha * data.yield_base * data.price_per_ton
    total_cost = data.water_cost + data.labor_cost + (data.area_ha * data.other_costs)
    profit = revenue * (1 - data.climate_risk) - total_cost
    return ProfitResult(
        expected_profit=profit,
        revenue=revenue,
        total_cost=total_cost,
        roi_percent=((profit / total_cost) * 100) if total_cost > 0 else 0,
    )


@router.post("/simulate/montecarlo")
async def run_monte_carlo(data: SimulationInput):
    profits = []
    for _ in range(data.iterations):
        yield_var = data.yield_base * (1 + random.gauss(0, 0.15))
        price_var = data.price_per_ton * (1 + random.gauss(0, 0.1))
        rev = data.area_ha * yield_var * price_var
        cost = data.water_cost + data.labor_cost + (data.area_ha * data.other_costs)
        profits.append(rev * (1 - data.climate_risk) - cost)

    return {
        "mean_profit": statistics.mean(profits),
        "p10_profit": sorted(profits)[int(data.iterations * 0.1)],
        "p90_profit": sorted(profits)[int(data.iterations * 0.9)],
        "std_dev": statistics.stdev(profits),
        "break_even_prob": sum(1 for p in profits if p > 0) / len(profits),
    }
