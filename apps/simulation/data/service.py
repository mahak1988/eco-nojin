"""
Unified DataService: aggregates NASA POWER + Open-Meteo + Open-Elevation.
In-memory cache (TTL) to avoid repeated external calls.
"""
import asyncio
import time
from datetime import date, timedelta

from apps.simulation.data import nasa_power, open_meteo, open_elevation

_CACHE: dict[str, tuple[float, dict]] = {}
_TTL = 3600  # 1 hour


def _cache_get(key: str):
    if key in _CACHE:
        ts, val = _CACHE[key]
        if time.time() - ts < _TTL:
            return val
        del _CACHE[key]
    return None


def _cache_set(key: str, val):
    _CACHE[key] = (time.time(), val)


async def get_climate_series(lat: float, lon: float, start: date, end: date,
                              source: str = "auto") -> dict:
    """
    Returns {date_str: {temp_mean_c, temp_max_c, temp_min_c, precipitation_mm,
                        et0_mm, solar_radiation_kwh_m2, ...}}
    source: 'nasa' | 'openmeteo' | 'auto' (try open-meteo first for ET0, fallback nasa)
    """
    key = f"climate:{lat:.3f}:{lon:.3f}:{start}:{end}:{source}"
    cached = _cache_get(key)
    if cached is not None:
        return cached

    result: dict[str, dict] = {}

    if source in ("openmeteo", "auto"):
        try:
            om = await asyncio.wait_for(
                open_meteo.get_historical(lat, lon, start, end), timeout=35)
            if om:
                result = om
        except Exception:
            pass

    if not result and source in ("nasa", "auto"):
        try:
            np_data = await asyncio.wait_for(
                nasa_power.get_daily_climate(lat, lon, start, end), timeout=35)
            # add Hargreaves ET0 if NASA POWER lacks it
            for d, row in np_data.items():
                if "temp_max_c" in row and "temp_min_c" in row and "temp_mean_c" in row:
                    doy = date(int(d[:4]), int(d[4:6]), int(d[6:8])).timetuple().tm_yday
                    row["et0_mm"] = nasa_power.hargreaves_et0(
                        row["temp_max_c"], row["temp_min_c"], row["temp_mean_c"], doy, lat)
            result = np_data
        except Exception:
            pass

    _cache_set(key, result)
    return result


async def get_elevation(lat: float, lon: float) -> float | None:
    key = f"elev:{lat:.4f}:{lon:.4f}"
    cached = _cache_get(key)
    if cached is not None:
        return cached
    elev = await open_elevation.get_elevation(lat, lon)
    if elev is not None:
        _cache_set(key, elev)
    return elev
