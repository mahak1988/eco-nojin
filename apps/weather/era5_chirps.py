"""ERA5-Land & precipitation via Open-Meteo archive (no API key). CHIRPS-like daily rain."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


async def fetch_era5_land(
    lat: float,
    lon: float,
    start: date,
    end: date,
) -> dict[str, Any]:
    """
    Open-Meteo ERA5 archive — temperature, humidity, soil moisture proxies.
    Docs: https://open-meteo.com/en/docs/era5-api
    """
    try:
        import httpx

        url = "https://archive-api.open-meteo.com/v1/era5"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "temperature_2m_mean",
                    "precipitation_sum",
                    "relative_humidity_2m_mean",
                    "et0_fao_evapotranspiration",
                ]
            ),
            "timezone": "UTC",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        daily = data.get("daily") or {}
        times = daily.get("time") or []
        series = []
        for i, t in enumerate(times):
            series.append(
                {
                    "date": t,
                    "temp_max_c": _at(daily, "temperature_2m_max", i),
                    "temp_min_c": _at(daily, "temperature_2m_min", i),
                    "temp_mean_c": _at(daily, "temperature_2m_mean", i),
                    "precip_mm": _at(daily, "precipitation_sum", i),
                    "humidity_pct": _at(daily, "relative_humidity_2m_mean", i),
                    "et0_mm": _at(daily, "et0_fao_evapotranspiration", i),
                }
            )
        return {"provider": "open-meteo-era5", "lat": lat, "lon": lon, "series": series}
    except Exception as e:
        logger.warning("ERA5 fetch failed: %s", e)
        return synthetic_climate(lat, lon, start, end, reason=str(e)[:80])


async def fetch_forecast_openmeteo(
    lat: float,
    lon: float,
    days: int,
) -> dict[str, Any]:
    """
    Open-Meteo forecast API (free, no API key required).
    Docs: https://open-meteo.com/en/docs
    Provides 7-14 day temperature, precipitation, humidity, wind forecasts.
    """
    try:
        import httpx

        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": ",".join(
                [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "relative_humidity_2m_mean",
                    "windspeed_10m_max",
                ]
            ),
            "timezone": "UTC",
            "forecast_days": min(days, 14),
        }
        async with httpx.AsyncClient(timeout=15.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        daily = data.get("daily") or {}
        times = daily.get("time") or []
        daily_series = []
        for i, t in enumerate(times):
            daily_series.append(
                {
                    "date": t,
                    "temp_max_c": _at(daily, "temperature_2m_max", i),
                    "temp_min_c": _at(daily, "temperature_2m_min", i),
                    "precip_mm": _at(daily, "precipitation_sum", i),
                    "humidity_pct": _at(daily, "relative_humidity_2m_mean", i),
                    "wind_m_s": _at(daily, "windspeed_10m_max", i),
                    "et0_mm": None,
                    "condition": "data",
                }
            )
        return {
            "provider": "open-meteo-forecast",
            "lat": lat,
            "lon": lon,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "daily": daily_series,
        }
    except Exception as e:
        logger.warning("Open-Meteo forecast failed: %s", e)
        return {}


async def fetch_chirps_like(
    lat: float,
    lon: float,
    start: date,
    end: date,
) -> dict[str, Any]:
    """
    Daily precipitation — Open-Meteo (satellite+gauge blend where available).
    Named chirps-like for agri drought pipelines; replace with true CHIRPS when GEE keys exist.
    """
    try:
        import httpx

        url = "https://archive-api.open-meteo.com/v1/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
            "daily": "precipitation_sum",
            "timezone": "UTC",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            r = await client.get(url, params=params)
            r.raise_for_status()
            data = r.json()
        daily = data.get("daily") or {}
        times = daily.get("time") or []
        series = [
            {"date": t, "precip_mm": _at(daily, "precipitation_sum", i)}
            for i, t in enumerate(times)
        ]
        return {"provider": "open-meteo-precip", "lat": lat, "lon": lon, "series": series}
    except Exception as e:
        logger.warning("Precip fetch failed: %s", e)
        base = synthetic_climate(lat, lon, start, end)
        return {
            "provider": "synthetic-precip",
            "lat": lat,
            "lon": lon,
            "series": [{"date": x["date"], "precip_mm": x["precip_mm"]} for x in base["series"]],
            "error": str(e)[:80],
        }


def _at(daily: dict, key: str, i: int) -> Optional[float]:
    arr = daily.get(key) or []
    if i >= len(arr) or arr[i] is None:
        return None
    return float(arr[i])


def synthetic_climate(
    lat: float,
    lon: float,
    start: date,
    end: date,
    reason: str = "",
) -> dict[str, Any]:
    import math

    series = []
    d = start
    while d <= end:
        doy = d.timetuple().tm_yday
        t = 15 + 12 * math.sin(2 * math.pi * (doy - 100) / 365) - abs(lat) / 20
        series.append(
            {
                "date": d.isoformat(),
                "temp_max_c": round(t + 6, 1),
                "temp_min_c": round(t - 5, 1),
                "temp_mean_c": round(t, 1),
                "precip_mm": round(max(0, 4 * math.sin(doy / 40 + lon / 30)), 1),
                "humidity_pct": round(40 + 25 * abs(math.sin(doy / 30)), 1),
                "et0_mm": round(3 + 2 * abs(math.sin(doy / 50)), 2),
            }
        )
        d += timedelta(days=1)
    out: dict[str, Any] = {
        "provider": "synthetic-climate",
        "lat": lat,
        "lon": lon,
        "series": series,
    }
    if reason:
        out["fallback_reason"] = reason
    return out
