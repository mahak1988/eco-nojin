"""
NASA POWER API Client - Fetches real-world historical weather data.
Docs: https://power.larc.nasa.gov/docs/

Enhanced with ALLSKY_SFC_SW_DWN (solar radiation) and Hargreaves ET0.
Clean Room Implementation - uses public API, no proprietary code.
"""

import logging
import math
from datetime import date
from typing import Any

import httpx

logger = logging.getLogger(__name__)
USER_AGENT = "EcoNojin/2.0"
DEFAULT_TIMEOUT = 30.0

NASA_PARAMETERS = [
    "T2M",  # Temperature at 2m (C)
    "T2M_MAX",  # Max temperature (C)
    "T2M_MIN",  # Min temperature (C)
    "PRECTOTCORR",  # Corrected precipitation (mm/day)
    "ALLSKY_SFC_SW_DWN",  # All-sky insolation (MJ/m^2/day)
]


async def fetch_nasa_power_data(
    lat: float, lon: float, start_date: str, end_date: str
) -> dict[str, Any]:
    """
    Fetch daily temperature, precipitation, and solar radiation from NASA POWER.

    Args:
        lat: Latitude (-90 to 90)
        lon: Longitude (-180 to 180)
        start_date: YYYYMMDD format
        end_date: YYYYMMDD format

    Returns:
        Dict with source, coordinates, temperature, precipitation, and solar data.
        status="success" or status="error" with message.
    """
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {
        "parameters": ",".join(NASA_PARAMETERS),
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

            timeseries = data.get("properties", {}).get("parameter", {})
            return {
                "source": "NASA POWER",
                "lat": lat,
                "lon": lon,
                "temp_c": timeseries.get("T2M", {}),
                "temp_c_max": timeseries.get("T2M_MAX", {}),
                "temp_c_min": timeseries.get("T2M_MIN", {}),
                "precip_mm": timeseries.get("PRECTOTCORR", {}),
                "solar_mj_m2": timeseries.get("ALLSKY_SFC_SW_DWN", {}),
                "status": "success",
            }
    except Exception as e:
        logger.warning("NASA POWER fetch failed: %s", e)
        return {"source": "NASA POWER", "status": "error", "message": str(e)}


def hargreaves_et0(tmax: float, tmin: float, tmean: float, doy: int, lat: float) -> float:
    """
    Hargreaves reference evapotranspiration (ET0).

    Formula: ET0 = 0.0023 * Ra * (Tmean + 17.8) * sqrt(Tmax - Tmin)

    Where Ra is extraterrestrial radiation computed from latitude and day-of-year.
    Note: Returns ET0 in mm/day (divided by latent heat of vaporization 2.45 MJ/kg).

    Args:
        tmax: Daily maximum temperature (C)
        tmin: Daily minimum temperature (C)
        tmean: Daily mean temperature (C)
        doy: Day of year (1-366)
        lat: Latitude in decimal degrees (-90 to 90)

    Returns:
        ET0 in mm/day. Returns 0.0 for invalid inputs.
    """
    # Input validation
    if not (-90.0 <= lat <= 90.0) or not (1 <= doy <= 366):
        return 0.0
    if tmax < tmin or tmax == tmin:
        return 0.0

    # Solar constant (MJ/m^2/min)
    Gsc = 0.0820
    phi = math.radians(lat)

    # Inverse relative distance Earth-Sun
    Dr = 1.0 + 0.033 * math.cos(2.0 * math.pi * doy / 365.0)

    # Solar declination (rad)
    delta = 0.409 * math.sin(2.0 * math.pi * doy / 365.0 - 1.39)

    # Sunset hour angle (rad)
    cos_ws = -math.tan(phi) * math.tan(delta)
    cos_ws = max(-1.0, min(1.0, cos_ws))
    ws = math.acos(cos_ws)

    # Extraterrestrial radiation (MJ/m^2/day)
    Ra = (
        (24.0 * 60.0 / math.pi)
        * Gsc
        * Dr
        * (ws * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(ws))
    )

    if Ra <= 0.0:
        return 0.0

    # Hargreaves equation (mm/day)
    et0 = 0.0023 * Ra * (tmean + 17.8) * math.sqrt(tmax - tmin)

    # Convert from MJ/m^2 to mm (dividing by latent heat of vaporization)
    et0_mm = et0 / 2.45

    return max(0.0, round(et0_mm, 2))


def validate_climate_value(value: Any, default: float = 0.0) -> float:
    """Validate a climate value, replacing NaN/Inf with default."""
    try:
        v = float(value)
        if math.isnan(v) or math.isinf(v):
            return default
        return v
    except (TypeError, ValueError):
        return default


async def get_daily_climate(
    lat: float, lon: float, start: date, end: date
) -> dict[str, dict[str, float]]:
    """
    Fetch daily climate data from NASA POWER and compute ET0.

    Returns a dict keyed by YYYYMMDD date string, each containing:
        temp_mean_c, temp_max_c, temp_min_c, precipitation_mm, et0_mm

    Missing values are filled with reasonable defaults.
    """
    start_str = start.strftime("%Y%m%d")
    end_str = end.strftime("%Y%m%d")
    result = await fetch_nasa_power_data(lat, lon, start_str, end_str)

    if result.get("status") != "success":
        logger.warning("NASA POWER unavailable, returning empty climate data")
        return {}

    means = result.get("temp_c", {}) or {}
    maxs = result.get("temp_c_max", {}) or {}
    mins = result.get("temp_c_min", {}) or {}
    precs = result.get("precip_mm", {}) or {}
    solar = result.get("solar_mj_m2", {}) or {}

    out: dict[str, dict[str, float]] = {}

    for dk in set(list(means.keys()) + list(maxs.keys()) + list(mins.keys())):
        tmean = validate_climate_value(means.get(dk), 15.0)
        tmax = validate_climate_value(maxs.get(dk), tmean + 3.0)
        tmin = validate_climate_value(mins.get(dk), tmean - 3.0)
        precip = validate_climate_value(precs.get(dk), 0.0)

        # Compute ET0 from the daily data
        try:
            d = date(int(dk[:4]), int(dk[4:6]), int(dk[6:8]))
            doy = d.timetuple().tm_yday
        except (ValueError, IndexError):
            doy = 180  # Fallback mid-year

        et0 = hargreaves_et0(tmax, tmin, tmean, doy, lat)

        out[dk] = {
            "temp_mean_c": tmean,
            "temp_max_c": tmax,
            "temp_min_c": tmin,
            "precipitation_mm": precip,
            "et0_mm": et0,
        }

    return out


async def fetch_climate_with_et0(lat: float, lon: float, start: date, end: date) -> dict[str, Any]:
    """
    Complete climate fetch including all NASA POWER parameters and computed ET0.

    This is the recommended entry point for simulation engines.
    """
    daily = await get_daily_climate(lat, lon, start, end)

    if not daily:
        return {"status": "error", "message": "No climate data available"}

    # Compute summary statistics
    et0_values = [d["et0_mm"] for d in daily.values()]
    precip_values = [d["precipitation_mm"] for d in daily.values()]
    temp_values = [d["temp_mean_c"] for d in daily.values()]

    return {
        "status": "success",
        "source": "NASA POWER + Hargreaves ET0",
        "lat": lat,
        "lon": lon,
        "period": {"start": start.isoformat(), "end": end.isoformat()},
        "days": len(daily),
        "summary": {
            "total_et0_mm": round(sum(et0_values), 1),
            "total_precipitation_mm": round(sum(precip_values), 1),
            "mean_temp_c": round(sum(temp_values) / len(temp_values), 1) if temp_values else None,
            "mean_et0_mm_day": round(sum(et0_values) / len(et0_values), 2) if et0_values else None,
        },
        "daily": daily,
    }
