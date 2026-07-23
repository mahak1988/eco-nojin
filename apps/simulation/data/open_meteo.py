"""
Open-Meteo API client (no API key for non-commercial use).
Provides FAO ET0 directly + historical/forecast weather.
Docs: https://open-meteo.com/en/docs
"""
import asyncio
import json
import urllib.request
from datetime import date

BASE = "https://archive-api.open-meteo.com/v1/archive"


async def get_historical(lat: float, lon: float, start: date, end: date) -> dict:
    """Historical weather incl. FAO ET0 (et0_fao_evapotranspiration)."""
    url = (
        f"{BASE}?latitude={lat}&longitude={lon}"
        f"&start_date={start.isoformat()}&end_date={end.isoformat()}"
        "&daily=temperature_2m_max,temperature_2m_min,temperature_2m_mean,"
        "precipitation_sum,et0_fao_evapotranspiration,shortwave_radiation_sum,"
        "wind_speed_10m_max,relative_humidity_2m_mean"
        "&timezone=auto"
    )

    def _fetch():
        req = urllib.request.Request(url, headers={"User-Agent": "EcoNojin/2.0"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode())

    data = await asyncio.to_thread(_fetch)
    daily = data.get("daily", {})
    dates = daily.get("time", [])
    out: dict[str, dict[str, float]] = {}
    mapping = {
        "temperature_2m_mean": "temp_mean_c",
        "temperature_2m_max": "temp_max_c",
        "temperature_2m_min": "temp_min_c",
        "precipitation_sum": "precipitation_mm",
        "et0_fao_evapotranspiration": "et0_mm",
        "shortwave_radiation_sum": "solar_radiation_kwh_m2",
        "wind_speed_10m_max": "wind_speed_ms",
        "relative_humidity_2m_mean": "relative_humidity_pct",
    }
    for i, d in enumerate(dates):
        row = {}
        for key, friendly in mapping.items():
            vals = daily.get(key)
            if vals and i < len(vals) and vals[i] is not None:
                row[friendly] = float(vals[i])
        if row:
            out[d] = row
    return out
