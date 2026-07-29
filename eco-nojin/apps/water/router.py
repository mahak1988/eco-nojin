"""Water / irrigation API with schedules, quality, balance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/water", tags=["Water"])

_SCHEDULES: list[dict] = [
    {
        "id": "sch1",
        "system_id": "irr1",
        "name": "Dawn drip A",
        "start_time": "05:30",
        "duration_min": 45,
        "days": ["mon", "wed", "fri"],
        "volume_m3": 8.5,
        "active": True,
    }
]


class WaterDashboard(BaseModel):
    soil_moisture_pct: float
    reservoir_level_pct: float
    daily_usage_m3: float
    irrigation_active: bool
    sources_count: int
    quality_index: float
    updated_at: str
    alerts: list[str]


class WaterSource(BaseModel):
    id: str
    name: str
    type: str
    capacity_m3: float
    current_m3: float
    status: str


class QualitySample(BaseModel):
    id: str
    source_id: str
    ph: float
    ec_ds_m: float
    nitrate_mg_l: Optional[float] = None
    sampled_at: str
    status: str


class ScheduleIn(BaseModel):
    system_id: str
    name: str
    start_time: str
    duration_min: int = Field(..., ge=1)
    days: list[str]
    volume_m3: float = 0
    active: bool = True


@router.get("/dashboard", response_model=WaterDashboard)
async def water_dashboard(farm_id: Optional[int] = Query(None)):
    _ = farm_id
    return WaterDashboard(
        soil_moisture_pct=42.5,
        reservoir_level_pct=68.0,
        daily_usage_m3=12.4,
        irrigation_active=False,
        sources_count=3,
        quality_index=0.86,
        updated_at=datetime.now(timezone.utc).isoformat(),
        alerts=["Soil moisture below ideal for corn zone B"],
    )


@router.get("/balance")
async def water_balance(
    area_ha: float = Query(1.0, gt=0),
    precip_mm: float = Query(5.0, ge=0),
    et0_mm: float = Query(4.0, gt=0),
    kc: float = Query(1.0, gt=0),
    irrigation_mm: float = Query(0.0, ge=0),
    runoff_mm: float = Query(0.5, ge=0),
):
    """Simplified field water balance: ΔS = P + I − ETc − R."""
    etc = et0_mm * kc
    delta = precip_mm + irrigation_mm - etc - runoff_mm
    return {
        "area_ha": area_ha,
        "precip_mm": precip_mm,
        "irrigation_mm": irrigation_mm,
        "etc_mm": round(etc, 2),
        "runoff_mm": runoff_mm,
        "storage_change_mm": round(delta, 2),
        "volume_change_m3": round(delta * area_ha * 10, 2),
        "formula": "dS = P + I - ETc - R",
    }


@router.get("/sources", response_model=list[WaterSource])
async def water_sources():
    return [
        WaterSource(id="ws1", name="Well #1", type="groundwater", capacity_m3=500, current_m3=320, status="ok"),
        WaterSource(id="ws2", name="Canal intake", type="surface", capacity_m3=1200, current_m3=900, status="ok"),
        WaterSource(id="ws3", name="Rain harvest", type="harvest", capacity_m3=80, current_m3=22, status="low"),
    ]


@router.get("/quality", response_model=list[QualitySample])
async def water_quality():
    now = datetime.now(timezone.utc).isoformat()
    return [
        QualitySample(id="q1", source_id="ws1", ph=7.2, ec_ds_m=1.1, nitrate_mg_l=8.0, sampled_at=now, status="good"),
        QualitySample(id="q2", source_id="ws2", ph=7.8, ec_ds_m=1.6, nitrate_mg_l=15.0, sampled_at=now, status="fair"),
    ]


@router.get("/irrigation/systems")
async def irrigation_systems() -> list[dict[str, Any]]:
    return [
        {"id": "irr1", "name": "Drip block A", "type": "drip", "status": "idle", "zones": 4, "efficiency": 0.9},
        {"id": "irr2", "name": "Sprinkler north", "type": "sprinkler", "status": "scheduled", "zones": 2, "efficiency": 0.75},
        {"id": "irr3", "name": "Furrow south", "type": "furrow", "status": "idle", "zones": 3, "efficiency": 0.55},
    ]


@router.get("/irrigation/schedules")
async def list_schedules():
    return {"data": _SCHEDULES}


@router.get("/irrigation-schedule")
async def irrigation_schedule_alias():
    return {"data": _SCHEDULES}


@router.post("/irrigation/schedules")
async def create_schedule(body: ScheduleIn):
    item = {"id": f"sch{len(_SCHEDULES)+1}", **body.model_dump()}
    _SCHEDULES.append(item)
    return item


@router.post("/irrigation/calculate")
async def water_irrigation_calc(
    area_ha: float = Query(..., gt=0),
    et0_mm_day: float = Query(4.0, gt=0),
    kc: float = Query(1.0, gt=0),
    efficiency: float = Query(0.85, gt=0, le=1),
    days: int = Query(7, ge=1),
):
    etc = et0_mm_day * kc
    gross = (etc * days) / efficiency
    vol = gross * area_ha * 10
    return {
        "etc_mm_day": round(etc, 2),
        "gross_mm_period": round(gross, 2),
        "volume_m3": round(vol, 2),
        "formula": "ETc=ET0*Kc; gross=ETc/eff; V(m3)=gross_mm*area_ha*10",
    }
