"""Celery tasks — import only when worker/async_mode needs them."""

from __future__ import annotations

import logging
from typing import Any

from apps.shared_core.celery_app import celery_app
from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.ndvi_canopy import fetch_ndvi_series_sync
from apps.simulation.run_store import save_run_sync

logger = logging.getLogger(__name__)


@celery_app.task(name="science.run_aquacrop_advanced", bind=True)
def task_aquacrop_advanced(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = dict(params or {})
    farm_id = params.pop("farm_id", None)
    use_ndvi = params.pop("use_ndvi_canopy", False)
    lat = params.pop("lat", None)
    lon = params.pop("lon", None)
    if use_ndvi and lat is not None and lon is not None:
        bridge = fetch_ndvi_series_sync(float(lat), float(lon), days=int(params.get("days", 90)))
        params["canopy_cover"] = bridge["canopy_cover"]
        params["_ndvi_meta"] = {"provider": bridge["provider"], "count": bridge["count"]}
    result = run_aquacrop_advanced(params)
    if "_ndvi_meta" in params:
        result["ndvi_meta"] = params["_ndvi_meta"]
    task_id = getattr(self.request, "id", None)
    try:
        result["run_id"] = save_run_sync(
            "aquacrop_advanced", params, result, task_id=task_id, farm_id=farm_id
        )
    except Exception as e:
        result["run_id"] = None
        result["persist_error"] = str(e)[:120]
    result["task_id"] = task_id
    result["mode"] = "celery"
    return result


@celery_app.task(name="science.run_swat", bind=True)
def task_swat(self, params: dict[str, Any] | None = None) -> dict[str, Any]:
    params = dict(params or {})
    farm_id = params.pop("farm_id", None)
    result = run_swat_plus(params)
    task_id = getattr(self.request, "id", None)
    try:
        result["run_id"] = save_run_sync(
            "swat_plus_proxy", params, result, task_id=task_id, farm_id=farm_id
        )
    except Exception as e:
        result["run_id"] = None
        result["persist_error"] = str(e)[:120]
    result["task_id"] = task_id
    result["mode"] = "celery"
    return result
