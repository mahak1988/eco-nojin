"""Water / irrigation API — Phase1 skeleton."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/water", tags=["Water"])


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
    sampled_at: str
    status: str


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


@router.get("/sources", response_model=list[WaterSource])
async def water_sources():
    return [
        WaterSource(
            id="ws1", name="Well #1", type="groundwater", capacity_m3=500, current_m3=320, status="ok"
        ),
        WaterSource(
            id="ws2", name="Canal intake", type="surface", capacity_m3=1200, current_m3=900, status="ok"
        ),
        WaterSource(
            id="ws3", name="Rain harvest", type="harvest", capacity_m3=80, current_m3=22, status="low"
        ),
    ]


@router.get("/quality", response_model=list[QualitySample])
async def water_quality():
    now = datetime.now(timezone.utc).isoformat()
    return [
        QualitySample(id="q1", source_id="ws1", ph=7.2, ec_ds_m=1.1, sampled_at=now, status="good"),
        QualitySample(id="q2", source_id="ws2", ph=7.8, ec_ds_m=1.6, sampled_at=now, status="fair"),
    ]


@router.get("/irrigation/systems")
async def irrigation_systems() -> list[dict[str, Any]]:
    return [
        {"id": "irr1", "name": "Drip block A", "type": "drip", "status": "idle", "zones": 4},
        {"id": "irr2", "name": "Sprinkler north", "type": "sprinkler", "status": "scheduled", "zones": 2},
    ]
