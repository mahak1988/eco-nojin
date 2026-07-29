"""Celery tasks for heavy satellite processing."""

from __future__ import annotations

import logging
from datetime import date
from typing import Any

logger = logging.getLogger(__name__)

try:
    from apps.shared_core.celery_app import celery_app
except Exception:  # pragma: no cover
    celery_app = None  # type: ignore


def _change_detection_sync(
    lat: float,
    lon: float,
    period_a_start: str,
    period_a_end: str,
    period_b_start: str,
    period_b_end: str,
    farm_id: int | None = None,
) -> dict[str, Any]:
    import asyncio

    from apps.satellite.processors.change_detection import delta_status, mean_safe
    from apps.satellite.providers.base import BBox
    from apps.satellite.service import get_satellite_service

    async def _run() -> dict[str, Any]:
        svc = get_satellite_service()
        bbox = BBox.from_point(lat, lon)
        a = await svc.get_ndvi_timeseries(
            farm_id or 0,
            bbox,
            date.fromisoformat(period_a_start),
            date.fromisoformat(period_a_end),
        )
        b = await svc.get_ndvi_timeseries(
            farm_id or 0,
            bbox,
            date.fromisoformat(period_b_start),
            date.fromisoformat(period_b_end),
        )
        mean_a = mean_safe([r.mean_ndvi for r in a])
        mean_b = mean_safe([r.mean_ndvi for r in b])
        delta = mean_b - mean_a
        status = delta_status(mean_a, mean_b)
        return {
            "farm_id": farm_id,
            "mean_ndvi_a": round(mean_a, 4),
            "mean_ndvi_b": round(mean_b, 4),
            "delta_ndvi": round(delta, 4),
            "status": status,
            "provider": (a[0].provider if a else None) or (b[0].provider if b else None),
        }

    return asyncio.run(_run())


if celery_app is not None:

    @celery_app.task(name="satellite.change_detection", bind=True, max_retries=3, time_limit=300)
    def change_detection_task(
        self,
        lat: float = 32.65,
        lon: float = 51.67,
        period_a_start: str = "",
        period_a_end: str = "",
        period_b_start: str = "",
        period_b_end: str = "",
        farm_id: int | None = None,
    ) -> dict[str, Any]:
        return _change_detection_sync(
            lat, lon, period_a_start, period_a_end, period_b_start, period_b_end, farm_id
        )

else:

    def change_detection_task(**kwargs: Any) -> dict[str, Any]:  # type: ignore
        return _change_detection_sync(
            kwargs.get("lat", 32.65),
            kwargs.get("lon", 51.67),
            kwargs["period_a_start"],
            kwargs["period_a_end"],
            kwargs["period_b_start"],
            kwargs["period_b_end"],
            kwargs.get("farm_id"),
        )


def weekly_vegetation_check_sync() -> dict[str, Any]:
    """Scan demo points for NDVI decline (beat schedule hook)."""
    from datetime import timedelta

    today = date.today()
    result = _change_detection_sync(
        32.65,
        51.67,
        (today - timedelta(days=17)).isoformat(),
        (today - timedelta(days=7)).isoformat(),
        (today - timedelta(days=10)).isoformat(),
        today.isoformat(),
        farm_id=0,
    )
    result["task"] = "weekly_vegetation_check"
    return result
