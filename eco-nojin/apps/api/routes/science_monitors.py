"""Science model monitors API — dynamic thresholds + watch."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/science", tags=["Phase3 Science Monitors"])


class EvaluateBody(BaseModel):
    metrics: dict[str, float] = Field(default_factory=dict)
    monitor_ids: list[str] | None = None


class WatchBody(BaseModel):
    lat: float = 32.65
    lon: float = 51.67
    include_sensors: bool = True
    days: int = Field(40, ge=7, le=120)


class ThresholdItem(BaseModel):
    warning: float | None = None
    critical: float | None = None
    operator: str | None = Field(None, pattern="^(lt|lte|gt|gte)$")
    enabled: bool | None = None


class ThresholdsPutBody(BaseModel):
    overrides: dict[str, ThresholdItem] = Field(default_factory=dict)
    merge: bool = True
    preset: str | None = None


class PresetBody(BaseModel):
    preset: str


@router.get("/monitors")
async def list_monitors() -> dict[str, Any]:
    from apps.simulation.model_monitors import effective_catalog
    from apps.simulation.threshold_store import CLIMATE_PRESETS, get_store

    store = get_store()
    items = effective_catalog()
    return {
        "count": len(items),
        "items": items,
        "store": {
            "preset": store.get("preset"),
            "updated_at": store.get("updated_at"),
            "override_count": len(store.get("overrides") or {}),
        },
        "presets": {
            k: {"label_fa": v.get("label_fa"), "label_en": v.get("label_en")}
            for k, v in CLIMATE_PRESETS.items()
        },
        "notes_fa": "آستانه‌ها پویا هستند: پیش‌فرض اقلیمی + override دستی در data/monitor_thresholds.json",
        "notes_en": "Thresholds are dynamic: climate preset + manual overrides.",
    }


@router.get("/monitors/thresholds")
async def get_thresholds() -> dict[str, Any]:
    from apps.simulation.model_monitors import MONITOR_CATALOG, effective_catalog
    from apps.simulation.threshold_store import CLIMATE_PRESETS, get_store

    store = get_store()
    return {
        "defaults": [
            {"id": m["id"], "warning": m["warning"], "critical": m["critical"], "operator": m["operator"], "model": m["model"]}
            for m in MONITOR_CATALOG
        ],
        "effective": effective_catalog(),
        "overrides": store.get("overrides") or {},
        "preset": store.get("preset", "default"),
        "presets": list(CLIMATE_PRESETS.keys()),
        "updated_at": store.get("updated_at"),
    }


@router.put("/monitors/thresholds")
async def put_thresholds(body: ThresholdsPutBody) -> dict[str, Any]:
    from apps.simulation.model_monitors import MONITOR_CATALOG, effective_catalog
    from apps.simulation.threshold_store import set_overrides, set_preset

    valid_ids = {m["id"] for m in MONITOR_CATALOG}
    clean: dict[str, dict[str, Any]] = {}
    for mid, item in body.overrides.items():
        if mid not in valid_ids:
            raise HTTPException(400, f"unknown monitor_id: {mid}")
        payload = item.model_dump(exclude_none=True)
        if "warning" in payload and "critical" in payload:
            # soft check: for lt critical should be "worse" than warning
            pass
        clean[mid] = payload
    if body.preset:
        try:
            set_preset(body.preset)
        except ValueError as e:
            raise HTTPException(400, str(e)) from e
    store = set_overrides(clean, merge=body.merge)
    return {
        "ok": True,
        "store": store,
        "effective": effective_catalog(),
    }


@router.post("/monitors/thresholds/preset")
async def apply_preset(body: PresetBody) -> dict[str, Any]:
    from apps.simulation.model_monitors import effective_catalog
    from apps.simulation.threshold_store import set_preset

    try:
        store = set_preset(body.preset)
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return {"ok": True, "preset": store.get("preset"), "effective": effective_catalog()}


@router.post("/monitors/thresholds/reset")
async def reset_thresholds() -> dict[str, Any]:
    from apps.simulation.model_monitors import effective_catalog
    from apps.simulation.threshold_store import reset_store

    store = reset_store()
    return {"ok": True, "store": store, "effective": effective_catalog()}


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
