"""
Optional AquaCrop-OSPy engine (free, pure Python).

Falls back to conceptual aquacrop_advanced if package missing or run fails.
Not the official FAO binary — AquaCrop-OSPy mirrors FAO AquaCrop concepts.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def _try_ospy(params: dict[str, Any]) -> dict[str, Any] | None:
    try:
        from aquacrop import AquaCropModel, Soil, Crop, InitialWaterContent
        import pandas as pd
        import numpy as np
    except ImportError:
        return None

    days = int(params.get("days", 90))
    days = max(7, min(365, days))
    crop_name = str(params.get("crop", "wheat")).lower()
    crop_map = {
        "wheat": "Wheat",
        "maize": "Maize",
        "barley": "Barley",
        "potato": "Potato",
        "tomato": "Tomato",
        "sorghum": "Sorghum",
    }
    crop_key = crop_map.get(crop_name, "Wheat")

    et0 = float(params.get("et0_mm_day", 4.5))
    rain = float(params.get("rain_mm_day", 0.5))
    area_ha = float(params.get("area_ha", 1.0))

    dates = pd.date_range("2024-01-01", periods=days, freq="D")
    weather = pd.DataFrame(
        {
            "MinTemp": np.full(days, 10.0),
            "MaxTemp": np.full(days, 25.0),
            "Precipitation": np.full(days, rain),
            "ReferenceET": np.full(days, et0),
            "Date": dates,
        }
    )
    weather = weather.set_index("Date")

    end_month = 1 + (days - 1) // 30
    end_day = min(28, 1 + (days - 1) % 30)
    try:
        model = AquaCropModel(
            sim_start_time="2024/01/01",
            sim_end_time=f"2024/{end_month:02d}/{end_day:02d}",
            weather_df=weather,
            soil=Soil(soil_type="SandyLoam"),
            crop=Crop(crop_key, planting_date="01/01"),
            initial_water_content=InitialWaterContent(value=["FC"]),
        )
        model.run_model(till_termination=True)
        res = model.get_simulation_results()
        if res is None or getattr(res, "empty", True):
            return None

        yield_col = None
        for col in ("Yield (tonne/ha)", "Yield(tonne/ha)", "Dry yield (tonne/ha)"):
            if col in res.columns:
                yield_col = col
                break
        yield_t = float(res[yield_col].iloc[-1]) if yield_col else 0.0

        return {
            "engine": "aquacrop_ospy",
            "engine_version": "ospy",
            "model": "aquacrop_ospy",
            "citation": "AquaCrop-OSPy (open-source Python, mirrors FAO AquaCrop concepts)",
            "disclaimer": (
                "Optional free engine based on AquaCrop-OSPy. "
                "Not the official FAO AquaCrop binary. For decision support."
            ),
            "disclaimer_fa": (
                "موتور اختیاری رایگان بر پایه AquaCrop-OSPy. "
                "باینری رسمی FAO نیست. فقط پشتیبانی تصمیم."
            ),
            "crop": crop_key.lower(),
            "area_ha": area_ha,
            "days": days,
            "et0_mm_day": round(et0, 3),
            "rain_mm_day": round(rain, 3),
            "yield_t_ha": round(yield_t, 3),
            "yield_total_t": round(yield_t * area_ha, 3),
            "yield_relative": None,
            "ndvi_calibrated": False,
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "params_echo": {
                "crop": crop_key,
                "days": days,
                "et0_mm_day": et0,
                "rain_mm_day": rain,
                "area_ha": area_ha,
            },
        }
    except Exception as e:
        logger.warning("AquaCrop-OSPy run failed, will fallback: %s", e)
        return None


def run_aquacrop_with_optional_ospy(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Prefer OSPy when engine=ospy|free and package available; else conceptual."""
    from apps.simulation.aquacrop_advanced import run_aquacrop_advanced

    p = dict(params or {})
    engine = str(p.get("engine", "conceptual")).lower()
    if engine in ("ospy", "aquacrop_ospy", "free"):
        out = _try_ospy(p)
        if out is not None:
            return out
    return run_aquacrop_advanced(p)
