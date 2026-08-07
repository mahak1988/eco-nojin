"""
NASA POWER API Client — Fetches real-world historical weather data.
Docs: https://power.larc.nasa.gov/docs/
"""
import logging

logger = logging.getLogger(__name__)
USER_AGENT = "EcoNojin/2.0"
DEFAULT_TIMEOUT = 30.0
import math
import httpx
from typing import Optional

async def fetch_nasa_power_data(lat: float, lon: float, start_date: str, end_date: str) -> dict:
    """
    Fetches daily temperature and precipitation data.
    Note: For production, add your API key or handle rate limits.
    """
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": "T2M,T2M_MAX,T2M_MIN,PRECTOTCORR",  # Temperature at 2m, Corrected Precipitation
        "community": "RE",
        "format": "JSON",
        "start": start_date,
        "end": end_date,
        "latitude": lat,
        "longitude": lon,
    }
    try:
        async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
            headers = {"User-Agent": USER_AGENT}
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Extract and format the time series
            timeseries = data.get("properties", {}).get("parameter", {})
            return {
                "source": "NASA POWER",
                "lat": lat,
                "lon": lon,
                "temp_c": timeseries.get("T2M", {}),
                "temp_c_max": timeseries.get("T2M_MAX", {}),
                "temp_c_min": timeseries.get("T2M_MIN", {}),
                "precip_mm": timeseries.get("PRECTOTCORR", {}),
                "status": "success"
            }
    except Exception as e:
        return {"source": "NASA POWER", "status": "error", "message": str(e)}


def hargreaves_et0(tmax, tmin, tmean, doy, lat):
    if not (-90.0 <= lat <= 90.0) or not (1 <= doy <= 366) or tmax < tmin or tmax == tmin:
        return 0.0
    Gsc = 0.0820
    phi = math.radians(lat)
    Dr = 1.0 + 0.033 * math.cos(2.0 * math.pi * doy / 365.0)
    delta = 0.409 * math.sin(2.0 * math.pi * doy / 365.0 - 1.39)
    cos_ws = -math.tan(phi) * math.tan(delta)
    cos_ws = max(-1.0, min(1.0, cos_ws))
    ws = math.acos(cos_ws)
    Ra = (24.0 * 60.0 / math.pi) * Gsc * Dr * (ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws))
    if Ra <= 0.0:
        return 0.0
    et0 = 0.0023 * Ra * (tmean + 17.8) * math.sqrt(tmax - tmin)
    return max(0.0, round(et0 / 2.45, 2))


async def get_daily_climate(lat, lon, start, end):
    from datetime import timedelta
    start_str = start.strftime("%Y%m%d")
    end_str = end.strftime("%Y%m%d")
    result = await fetch_nasa_power_data(lat, lon, start_str, end_str)
    if result.get("status") != "success":
        return {}
    means = result.get("temp_c", {}) or {}
    maxs = result.get("temp_c_max", {}) or {}
    mins = result.get("temp_c_min", {}) or {}
    precs = result.get("precip_mm", {}) or {}
    out = {}
    for dk in means:
        row = {}
        if means.get(dk) is not None:
            row["temp_mean_c"] = float(means[dk])
        if maxs.get(dk) is not None:
            row["temp_max_c"] = float(maxs[dk])
        elif "temp_mean_c" in row:
            row["temp_max_c"] = row["temp_mean_c"] + 3.0
        if mins.get(dk) is not None:
            row["temp_min_c"] = float(mins[dk])
        elif "temp_mean_c" in row:
            row["temp_min_c"] = row["temp_mean_c"] - 3.0
        if precs.get(dk) is not None:
            row["precipitation_mm"] = float(precs[dk])
        else:
            row["precipitation_mm"] = 0.0
        if mins.get(dk) is not None:
            row["temp_min_c"] = float(mins[dk])
        elif "temp_mean_c" in row:
            row["temp_min_c"] = row["temp_mean_c"] - 3.0
        if precs.get(dk) is not None:
            row["precipitation_mm"] = float(precs[dk])
        else:
            row["precipitation_mm"] = 0.0
        if row:
            out[dk] = row
    return out
