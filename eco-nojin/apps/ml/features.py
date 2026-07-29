"""Feature engineering for farm / climate / remote-sensing proxies."""

from __future__ import annotations

from typing import Any

FEATURE_NAMES = [
    "et0_mm_day",
    "rain_mm_day",
    "mean_ndvi",
    "mean_canopy",
    "soil_moisture",
    "air_temp_c",
    "irrigation_need_mm",
    "yield_relative_proxy",
    "runoff_mm_year",
    "soc_delta",
]


def vector_from_dict(d: dict[str, Any]) -> list[float]:
    defaults = {
        "et0_mm_day": 4.5,
        "rain_mm_day": 0.5,
        "mean_ndvi": 0.45,
        "mean_canopy": 0.5,
        "soil_moisture": 30.0,
        "air_temp_c": 28.0,
        "irrigation_need_mm": 120.0,
        "yield_relative_proxy": 0.75,
        "runoff_mm_year": 40.0,
        "soc_delta": 0.0,
    }
    out: list[float] = []
    for name in FEATURE_NAMES:
        v = d.get(name, defaults[name])
        try:
            out.append(float(v))
        except (TypeError, ValueError):
            out.append(float(defaults[name]))
    return out


def normalize(x: list[float], means: list[float], stds: list[float]) -> list[float]:
    return [(xi - m) / (s if s > 1e-9 else 1.0) for xi, m, s in zip(x, means, stds)]
