"""Weather — forecast, ERA5-Land, CHIRPS-like precip, smart alerts."""

from __future__ import annotations

import math
from datetime import date, datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Query

from apps.shared_core.config import settings
from apps.weather.alerts import evaluate_alerts
from apps.weather.era5_chirps import fetch_chirps_like, fetch_era5_land, synthetic_climate

router = APIRouter(prefix="/api/v1/weather", tags=["Weather"])


def _synthetic_forecast(lat: float, lon: float, days: int) -> dict[str, Any]:
    base = 18 + 8 * math.sin(lat / 20)
    daily = []
    now = datetime.now(timezone.utc)
    for i in range(days):
        d = now + timedelta(days=i)
        t = base + 4 * math.sin(i / 2 + lon / 50)
        daily.append(
            {
                "date": d.date().isoformat(),
                "temp_max_c": round(t + 5, 1),
                "temp_min_c": round(t - 4, 1),
                "humidity_pct": int(45 + 20 * abs(math.sin(i))),
                "precip_mm": round(max(0, 3 * math.sin(i * 1.3)), 1),
                "wind_m_s": round(2 + abs(math.sin(i)), 1),
                "et0_mm": round(3.5 + 1.2 * abs(math.sin(i / 2)), 2),
                "condition": ["clear", "clouds", "rain", "clear"][i % 4],
            }
        )
    return {
        "provider": "synthetic-local",
        "lat": lat,
        "lon": lon,
        "generated_at": now.isoformat(),
        "daily": daily,
    }


@router.get("/forecast")
async def forecast(
    lat: float = Query(32.6),
    lon: float = Query(51.7),
    days: int = Query(7, ge=1, le=14),
):
    api_key = getattr(settings, "OPENWEATHER_API_KEY", None) or ""
    if not api_key or str(api_key).startswith("change"):
        return _synthetic_forecast(lat, lon, days)
    try:
        import httpx

        url = "https://api.openweathermap.org/data/2.5/forecast"
        async with httpx.AsyncClient(timeout=8.0) as client:
            r = await client.get(
                url, params={"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}
            )
            r.raise_for_status()
            data = r.json()
        return {"provider": "openweathermap", "lat": lat, "lon": lon, "raw": data}
    except Exception:
        out = _synthetic_forecast(lat, lon, days)
        out["provider"] = "synthetic-fallback"
        return out


@router.get("/era5")
async def era5(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(30, ge=7, le=90),
):
    end = date.today() - timedelta(days=5)  # archive lag
    start = end - timedelta(days=days)
    return await fetch_era5_land(lat, lon, start, end)


@router.get("/chirps")
async def chirps(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(30, ge=7, le=90),
):
    end = date.today() - timedelta(days=2)
    start = end - timedelta(days=days)
    return await fetch_chirps_like(lat, lon, start, end)


@router.get("/alerts")
async def climate_alerts(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(30, ge=14, le=90),
):
    end = date.today() - timedelta(days=5)
    start = end - timedelta(days=days)
    climate = await fetch_era5_land(lat, lon, start, end)
    series = climate.get("series") or []
    alerts = evaluate_alerts(series)
    return {
        "provider": climate.get("provider"),
        "lat": lat,
        "lon": lon,
        "alerts": alerts,
        "alert_count": len(alerts),
        "series_days": len(series),
    }


@router.get("/climate")
async def climate_bundle(
    lat: float = Query(32.65),
    lon: float = Query(51.67),
    days: int = Query(30, ge=7, le=90),
):
    end = date.today() - timedelta(days=5)
    start = end - timedelta(days=days)
    era = await fetch_era5_land(lat, lon, start, end)
    precip = await fetch_chirps_like(lat, lon, start, end)
    alerts = evaluate_alerts(era.get("series") or [])
    return {"era5": era, "precip": precip, "alerts": alerts}
