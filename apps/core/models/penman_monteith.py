"""FAO-56 Penman-Monteith reference evapotranspiration (ET0).

Reference: Allen et al. (1998), FAO Irrigation and Drainage Paper No. 56, Eq. 6.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class WeatherData:
    t_max: float  # °C
    t_min: float  # °C
    rh_mean: float  # %
    wind_speed_2m: float  # m/s
    solar_radiation: float  # MJ/m²/day
    elevation: float  # m
    latitude: float  # degrees (reserved for Rn expansion)


def calculate_et0(weather: WeatherData) -> float:
    """Return daily ET0 in mm/day (never negative).

    Uses simplified daily Rn = Rs * 0.77 and G ≈ 0.
    """
    t = (weather.t_max + weather.t_min) / 2.0
    p = 101.3 * ((293.0 - 0.0065 * weather.elevation) / 293.0) ** 5.26
    gamma = 0.000665 * p
    delta = (
        4098.0
        * (0.6108 * np.exp(17.27 * t / (t + 237.3)))
        / (t + 237.3) ** 2
    )
    es = (
        0.6108 * np.exp(17.27 * weather.t_max / (weather.t_max + 237.3))
        + 0.6108 * np.exp(17.27 * weather.t_min / (weather.t_min + 237.3))
    ) / 2.0
    ea = es * weather.rh_mean / 100.0
    rn = weather.solar_radiation * 0.77
    g = 0.0
    num = 0.408 * delta * (rn - g) + gamma * (900.0 / (t + 273.0)) * weather.wind_speed_2m * (es - ea)
    den = delta + gamma * (1.0 + 0.34 * weather.wind_speed_2m)
    if den == 0:
        return 0.0
    return float(max(0.0, num / den))
