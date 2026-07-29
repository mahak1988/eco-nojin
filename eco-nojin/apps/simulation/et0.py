"""
Reference evapotranspiration.

Hargreaves–Samani (1985) when only Tmin/Tmax available:
  ET0 = 0.0023 * Ra * (Tmean + 17.8) * sqrt(Tmax - Tmin)
  Ra in mm/day equivalent.

FAO-56 Penman–Monteith preferred when radiation/wind/humidity provided.
"""

from __future__ import annotations

import math
from typing import Any


def _ra_mm_day(lat_deg: float, day_of_year: int) -> float:
    """Extraterrestrial radiation approx (MJ/m2/day) → mm/day (÷2.45)."""
    lat = math.radians(lat_deg)
    dr = 1.0 + 0.033 * math.cos(2 * math.pi * day_of_year / 365.0)
    delta = 0.409 * math.sin(2 * math.pi * day_of_year / 365.0 - 1.39)
    ws = math.acos(max(-1.0, min(1.0, -math.tan(lat) * math.tan(delta))))
    gsc = 0.0820  # MJ/m2/min
    ra = (
        (24.0 * 60.0 / math.pi)
        * gsc
        * dr
        * (ws * math.sin(lat) * math.sin(delta) + math.cos(lat) * math.cos(delta) * math.sin(ws))
    )
    return max(0.0, ra / 2.45)  # mm/day


def et0_hargreaves(
    tmin_c: float,
    tmax_c: float,
    lat_deg: float = 32.0,
    day_of_year: int = 180,
) -> float:
    tmean = (tmin_c + tmax_c) / 2.0
    trange = max(0.1, tmax_c - tmin_c)
    ra = _ra_mm_day(lat_deg, day_of_year)
    return max(0.0, 0.0023 * ra * (tmean + 17.8) * math.sqrt(trange))


def et0_penman_monteith_fao56(params: dict[str, Any]) -> float:
    """
    FAO-56 PM simplified daily form.
    Required: tmean_c, rn_mj (net radiation), u2 (m/s), rh_mean (%), elevation_m optional.
    """
    t = float(params.get("tmean_c", 20.0))
    rn = float(params.get("rn_mj", 10.0))
    u2 = float(params.get("u2", 2.0))
    rh = float(params.get("rh_mean", 50.0))
    elev = float(params.get("elevation_m", 100.0))
    # saturation vapor pressure
    es = 0.6108 * math.exp(17.27 * t / (t + 237.3))
    ea = es * (rh / 100.0)
    delta = 4098.0 * es / (t + 237.3) ** 2
    p = 101.3 * ((293.0 - 0.0065 * elev) / 293.0) ** 5.26
    gamma = 0.000665 * p
    # soil heat flux neglected for daily
    num = 0.408 * delta * rn + gamma * (900.0 / (t + 273.0)) * u2 * (es - ea)
    den = delta + gamma * (1.0 + 0.34 * u2)
    return max(0.0, num / den)


def resolve_et0_mm_day(params: dict[str, Any]) -> float:
    if params.get("et0_mm_day") is not None:
        return float(params["et0_mm_day"])
    if all(k in params for k in ("rn_mj", "u2", "rh_mean")):
        return et0_penman_monteith_fao56(params)
    tmin = float(params.get("tmin_c", params.get("temp_min_c", 15.0)))
    tmax = float(params.get("tmax_c", params.get("temp_max_c", 30.0)))
    lat = float(params.get("lat", 32.0))
    doy = int(params.get("day_of_year", 180))
    return et0_hargreaves(tmin, tmax, lat, doy)
