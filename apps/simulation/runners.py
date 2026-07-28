"""Sync model runners without Celery import side-effects."""

from __future__ import annotations

import logging
from typing import Any, Optional

from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
from apps.simulation.models_swat import run_swat_plus
from apps.simulation.ndvi_canopy import fetch_ndvi_series_sync
from apps.simulation.run_store import save_run_sync

logger = logging.getLogger(__name__)


def run_aquacrop_advanced_local(
    params: dict[str, Any] | None = None,
    *,
    farm_id: Optional[int] = None,
    persist: bool = True,
) -> dict[str, Any]:
    params = dict(params or {})
    use_ndvi = params.pop("use_ndvi_canopy", False)
    lat = params.pop("lat", None)
    lon = params.pop("lon", None)
    if use_ndvi and lat is not None and lon is not None:
        bridge = fetch_ndvi_series_sync(float(lat), float(lon), days=int(params.get("days", 90)))
        params["canopy_cover"] = bridge["canopy_cover"]
        result = run_aquacrop_advanced(params)
        result["ndvi_meta"] = {"provider": bridge["provider"], "count": bridge["count"]}
    else:
        result = run_aquacrop_advanced(params)
    result["mode"] = "sync_local"
    if persist:
        try:
            result["run_id"] = save_run_sync("aquacrop_advanced", params, result, farm_id=farm_id)
        except Exception as e:
            logger.warning("persist aquacrop: %s", e)
            result["run_id"] = None
            result["persist_error"] = str(e)[:120]
    return result


def run_swat_local(
    params: dict[str, Any] | None = None,
    *,
    farm_id: Optional[int] = None,
    persist: bool = True,
) -> dict[str, Any]:
    params = dict(params or {})
    result = run_swat_plus(params)
    result["mode"] = "sync_local"
    if persist:
        try:
            result["run_id"] = save_run_sync("swat_plus_proxy", params, result, farm_id=farm_id)
        except Exception as e:
            logger.warning("persist swat: %s", e)
            result["run_id"] = None
            result["persist_error"] = str(e)[:120]
    return result
