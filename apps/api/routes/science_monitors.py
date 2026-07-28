"""Science model monitors API — mounted alongside science router."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/science", tags=["Phase3 Science Monitors"])


class EvaluateBody(BaseModel):
    metrics: dict[str, float] = Field(default_factory=dict)
    monitor_ids: Optional[list[str]] = None


class WatchBody(BaseModel):
    lat: float = 32.65
    lon: float = 51.67
    include_sensors: bool = True
    days: int = Field(40, ge=7, le=120)


@router.get("/monitors")
async def list_monitors() -> dict[str, Any]:
    from apps.simulation.model_monitors import MONITOR_CATALOG

    return {
        "count": len(MONITOR_CATALOG),
        "items": MONITOR_CATALOG,
        "notes_fa": "پایشگرها خروجی مدل‌ها و سنسورها را با آستانه هشدار/بحرانی مقایسه می‌کنند.",
        "notes_en": "Monitors compare model/sensor metrics against warning/critical thresholds.",
    }


@router.post("/monitors/evaluate")
async def evaluate(body: EvaluateBody) -> dict[str, Any]:
    from apps.simulation.model_monitors import evaluate_monitors

    events = evaluate_monitors(body.metrics, monitor_ids=body.monitor_ids)
    return {
        "events": events,
        "counts": {
            "ok": sum(1 for e in events if e["severity"] == "ok"),
            "warning": sum(1 for e in events if e["severity"] == "warning"),
            "critical": sum(1 for e in events if e["severity"] == "critical"),
        },
    }


@router.post("/monitors/watch")
async def watch_all(body: WatchBody) -> dict[str, Any]:
    """Run all models + sensors and return monitor events."""
    from apps.simulation.model_monitors import run_full_watch

    return run_full_watch(
        lat=body.lat,
        lon=body.lon,
        include_sensors=body.include_sensors,
        aquacrop_params={
            "days": body.days,
            "rain_mm_day": 0.4,
            "et0_mm_day": 5.0,
            "crop": "wheat",
            "lat": body.lat,
            "lon": body.lon,
        },
    )


@router.get("/monitors/watch")
async def watch_get(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(40, ge=7, le=120),
) -> dict[str, Any]:
    from apps.simulation.model_monitors import run_full_watch

    return run_full_watch(
        lat=lat,
        lon=lon,
        include_sensors=True,
        aquacrop_params={
            "days": days,
            "rain_mm_day": 0.4,
            "et0_mm_day": 5.0,
            "crop": "wheat",
            "lat": lat,
            "lon": lon,
        },
    )
