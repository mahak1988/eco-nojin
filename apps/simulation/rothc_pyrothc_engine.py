"""
Optional pyRothC engine (free pure Python RothC-26.3).

Falls back to in-repo rothc_model if package missing or run fails.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)


def _try_pyrothc(params: dict[str, Any]) -> dict[str, Any] | None:
    try:
        from pyRothC.RothC import RothC
    except ImportError:
        try:
            from pyRothC import RothC  # type: ignore
        except ImportError:
            return None

    years = int(params.get("years", 10))
    years = max(1, min(200, years))
    clay = float(params.get("clay_pct", 30.0))
    soc0 = float(params.get("soc_t_ha", 40.0))
    c_input = float(params.get("c_input_t_ha_y", 2.0))
    temp = float(params.get("temp_c", 15.0))
    rain_y = float(params.get("rain_mm_year", 600.0))
    et_y = float(params.get("et_mm_year", 700.0))
    rain = rain_y / 12.0
    et = et_y / 12.0

    Temp = np.full(12, temp)
    Precip = np.full(12, rain)
    Evp = np.full(12, et)
    iom = 0.049 * (soc0 ** 1.139) if soc0 > 0 else 0.0

    try:
        roth = RothC(
            temperature=Temp,
            precip=Precip,
            evaporation=Evp,
            clay=clay,
            input_carbon=c_input,
            pE=1.0,
            C0=np.array([0.0, 0.0, 0.0, 0.0, iom]),
            years=years,
        )
        df = roth.compute()
        if hasattr(df, "iloc"):
            last = df.iloc[-1]
            soc_final = float(last.sum()) if hasattr(last, "sum") else float(soc0)
        else:
            soc_final = float(soc0)

        return {
            "model": "rothc_26_3_pyrothc",
            "citation": "pyRothC (Python RothC-26.3)",
            "engine": "pyrothc",
            "soc_initial": round(soc0, 3),
            "soc_final": round(soc_final, 3),
            "delta": round(soc_final - soc0, 3),
            "c_input_t_ha_y": c_input,
            "clay_pct": clay,
            "series": [],
            "completed_at": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.warning("pyRothC run failed, will fallback: %s", e)
        return None


def run_rothc_with_optional_pyrothc(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Prefer pyRothC when engine=pyrothc|free; else in-repo RothC."""
    from apps.simulation.rothc_model import run_rothc

    p = dict(params or {})
    engine = str(p.get("engine", "conceptual")).lower()
    if engine in ("pyrothc", "free", "ospy"):
        out = _try_pyrothc(p)
        if out is not None:
            return out
    return run_rothc(p)
