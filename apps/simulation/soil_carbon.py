"""
Soil organic carbon process models (open reimplementations).

Models:
  - RothC-26.3 → apps.simulation.rothc_model
  - ICBM (Andrén & Kätterer 1997) — 2 pools Young/Old
  - CENTURY-style 3-pool (Active/Slow/Passive) — simplified annual
  - Yasso07-lite — 5 litter/SOM pools AWEN+H annual step

Not official binaries of Rothamsted / NREL / SYKE software.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any


def _temp_factor_q10(t_c: float, t_ref: float = 10.0, q10: float = 2.0) -> float:
    return q10 ** ((t_c - t_ref) / 10.0)


def _moisture_factor(rain: float, et: float) -> float:
    if et <= 0:
        return 1.0
    ratio = rain / et
    return max(0.2, min(1.0, 0.2 + 0.8 * min(1.0, ratio)))


def run_icbm(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    ICBM: two pools Y (young) and O (old).

    dY = i − k_Y·r_e·Y
    dO = h·k_Y·r_e·Y − k_O·r_e·O
    """
    p = params or {}
    years = int(p.get("years", 20))
    i_in = float(p.get("c_input_t_ha_y", 1.5))
    soc0 = float(p.get("soc_t_ha", 40.0))
    y_frac = float(p.get("young_frac", 0.15))
    y = soc0 * y_frac
    o = soc0 * (1.0 - y_frac)
    k_y = float(p.get("k_young", 0.8))
    k_o = float(p.get("k_old", 0.006))
    h = float(p.get("humification", 0.125))
    temp = float(p.get("temp_c", 15.0))
    rain = float(p.get("rain_mm_year", 650.0))
    et = float(p.get("et_mm_year", 700.0))
    r_e = (
        float(p.get("r_e"))
        if p.get("r_e") is not None
        else (_temp_factor_q10(temp, 10.0, 2.0) * _moisture_factor(rain, et))
    )
    r_e = max(0.05, min(3.0, r_e))

    series: list[dict[str, float]] = []
    for yr in range(years + 1):
        series.append(
            {
                "year": float(yr),
                "young": round(y, 4),
                "old": round(o, 4),
                "soc_t_ha": round(y + o, 3),
            }
        )
        if yr == years:
            break
        dy = i_in - k_y * r_e * y
        do = h * k_y * r_e * y - k_o * r_e * o
        y = max(0.0, y + dy)
        o = max(0.0, o + do)

    soc_f = series[-1]["soc_t_ha"]
    return {
        "model": "icbm",
        "citation": "Andrén & Kätterer (1997) ICBM — open annual reimplementation",
        "soc_initial": round(soc0, 3),
        "soc_final": soc_f,
        "delta": round(soc_f - soc0, 3),
        "r_e": round(r_e, 4),
        "params": {
            "years": years,
            "c_input_t_ha_y": i_in,
            "k_young": k_y,
            "k_old": k_o,
            "humification": h,
            "temp_c": temp,
            "rain_mm_year": rain,
            "et_mm_year": et,
        },
        "series": series,
        "completed_at": datetime.now(UTC).isoformat(),
    }


def run_century3(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    CENTURY-style 3-pool annual model (Active / Slow / Passive).

    Simplified from Parton et al. structure — not full CENTURY/DAYCENT.
    """
    p = params or {}
    years = int(p.get("years", 20))
    soc0 = float(p.get("soc_t_ha", 40.0))
    cin = float(p.get("c_input_t_ha_y", 1.5))
    temp = float(p.get("temp_c", 15.0))
    rain = float(p.get("rain_mm_year", 650.0))
    et = float(p.get("et_mm_year", 700.0))
    clay = float(p.get("clay_pct", 25.0)) / 100.0

    # Initial partition (typical cultivated)
    active = float(p.get("active_t_ha", soc0 * 0.05))
    slow = float(p.get("slow_t_ha", soc0 * 0.55))
    passive = float(p.get("passive_t_ha", max(0.0, soc0 - active - slow)))

    # Base rates (1/y) moderated by climate
    ft = _temp_factor_q10(temp, 20.0, 2.0)
    fw = _moisture_factor(rain, et)
    # clay reduces active decay slightly, favors passive formation
    k_a = 0.7 * ft * fw * (1.0 - 0.3 * clay)
    k_s = 0.05 * ft * fw
    k_p = 0.0015 * ft * fw

    # Input split to active/slow
    f_met = float(p.get("metabolic_frac", 0.55))  # metabolic → active
    series: list[dict[str, float]] = []
    for yr in range(years + 1):
        series.append(
            {
                "year": float(yr),
                "active": round(active, 4),
                "slow": round(slow, 4),
                "passive": round(passive, 4),
                "soc_t_ha": round(active + slow + passive, 3),
            }
        )
        if yr == years:
            break
        da = k_a * active
        ds = k_s * slow
        dp = k_p * passive
        active -= da
        slow -= ds
        passive -= dp
        # transfers: portion of active → slow/passive; slow → passive
        to_slow = da * (0.4 + 0.2 * clay)
        to_pass_a = da * (0.05 + 0.15 * clay)
        to_pass_s = ds * (0.15 + 0.1 * clay)
        # remainder of da, ds, dp → CO2
        active += cin * f_met
        slow += cin * (1.0 - f_met) + to_slow
        passive += to_pass_a + to_pass_s
        active = max(0.0, active)
        slow = max(0.0, slow)
        passive = max(0.0, passive)

    soc_f = series[-1]["soc_t_ha"]
    return {
        "model": "century3",
        "citation": "Parton-style 3-pool SOM (simplified annual; not full CENTURY)",
        "soc_initial": round(soc0, 3),
        "soc_final": soc_f,
        "delta": round(soc_f - soc0, 3),
        "rate_modifiers": {"ft": round(ft, 4), "fw": round(fw, 4), "k_a": round(k_a, 4)},
        "params": {
            "years": years,
            "c_input_t_ha_y": cin,
            "temp_c": temp,
            "rain_mm_year": rain,
            "et_mm_year": et,
            "clay_pct": clay * 100,
        },
        "series": series,
        "completed_at": datetime.now(UTC).isoformat(),
    }


def run_yasso_lite(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Yasso07-inspired 5-pool annual lite model (A,W,E,N,H).

    Not the official SYKE Yasso07 parameterization; climate factors simplified.
    """
    p = params or {}
    years = int(p.get("years", 20))
    soc0 = float(p.get("soc_t_ha", 40.0))
    cin = float(p.get("c_input_t_ha_y", 1.5))
    temp = float(p.get("temp_c", 15.0))
    rain = float(p.get("rain_mm_year", 650.0))

    # Initial: mostly humus + some AWEN
    a = float(p.get("a_t_ha", soc0 * 0.02))
    w = float(p.get("w_t_ha", soc0 * 0.03))
    e = float(p.get("e_t_ha", soc0 * 0.05))
    n = float(p.get("n_t_ha", soc0 * 0.15))
    h = float(p.get("h_t_ha", max(0.0, soc0 - a - w - e - n)))

    # Base mass-loss rates (1/y) ~ order of Yasso literature magnitudes
    ft = math.exp(0.095 * (temp - 10.0))  # approx temp response
    fw = max(0.3, min(1.2, rain / 800.0))
    k_a, k_w, k_e, k_n, k_h = (
        0.6 * ft * fw,
        0.4 * ft * fw,
        0.3 * ft * fw,
        0.1 * ft * fw,
        0.002 * ft * fw,
    )

    # Input AWEN fractions (foliar-like)
    fa, fw_in, fe, fn = 0.5, 0.2, 0.15, 0.15

    series: list[dict[str, float]] = []
    for yr in range(years + 1):
        series.append(
            {
                "year": float(yr),
                "A": round(a, 4),
                "W": round(w, 4),
                "E": round(e, 4),
                "N": round(n, 4),
                "H": round(h, 4),
                "soc_t_ha": round(a + w + e + n + h, 3),
            }
        )
        if yr == years:
            break
        da, dw, de, dn, dh = k_a * a, k_w * w, k_e * e, k_n * n, k_h * h
        a -= da
        w -= dw
        e -= de
        n -= dn
        h -= dh
        # fraction to H vs CO2
        to_h = 0.2 * (da + dw + de + dn) + 0.1 * dh
        h += to_h
        a += cin * fa
        w += cin * fw_in
        e += cin * fe
        n += cin * fn
        a, w, e, n, h = max(0, a), max(0, w), max(0, e), max(0, n), max(0, h)

    soc_f = series[-1]["soc_t_ha"]
    return {
        "model": "yasso07_lite",
        "citation": "Yasso07-inspired AWEN+H annual lite (not official SYKE Yasso07)",
        "soc_initial": round(soc0, 3),
        "soc_final": soc_f,
        "delta": round(soc_f - soc0, 3),
        "rate_modifiers": {"ft": round(ft, 4), "fw": round(fw, 4)},
        "params": {
            "years": years,
            "c_input_t_ha_y": cin,
            "temp_c": temp,
            "rain_mm_year": rain,
        },
        "series": series,
        "completed_at": datetime.now(UTC).isoformat(),
    }


def run_ensemble(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Run RothC + ICBM + Century3 + Yasso-lite with shared inputs; compare ΔSOC."""
    from apps.simulation.rothc_model import run_rothc

    p = dict(params or {})
    p.setdefault("years", 20)
    p.setdefault("soc_t_ha", 40.0)
    p.setdefault("c_input_t_ha_y", 1.5)

    models = {
        "rothc": run_rothc(p),
        "icbm": run_icbm(p),
        "century3": run_century3(p),
        "yasso07_lite": run_yasso_lite(p),
    }
    rows = []
    for name, res in models.items():
        rows.append(
            {
                "model": name,
                "soc_initial": res.get("soc_initial"),
                "soc_final": res.get("soc_final"),
                "delta": res.get("delta"),
            }
        )
    deltas = [r["delta"] for r in rows if isinstance(r["delta"], (int, float))]
    mean_d = sum(deltas) / len(deltas) if deltas else 0.0
    return {
        "model": "soil_carbon_ensemble",
        "citation": "Multi-model SOC comparison (process approximations)",
        "shared_params": {
            "years": p["years"],
            "soc_t_ha": p["soc_t_ha"],
            "c_input_t_ha_y": p["c_input_t_ha_y"],
            "temp_c": p.get("temp_c", 15),
            "rain_mm_year": p.get("rain_mm_year", 650),
            "et_mm_year": p.get("et_mm_year", 700),
            "clay_pct": p.get("clay_pct", 25),
        },
        "comparison": rows,
        "ensemble_mean_delta": round(mean_d, 3),
        "agreement": "high" if max(deltas) - min(deltas) < 5 else "moderate" if deltas else "n/a",
        "results": models,
        "completed_at": datetime.now(UTC).isoformat(),
        "notes_fa": (
            "میانگین ΔSOC بین مدل‌ها؛ اختلاف زیاد یعنی حساسیت به ساختار استخرها. "
            "هیچ‌کدام جایگزین اندازه‌گیری میدانی SOC نیستند."
        ),
    }


def catalog() -> dict[str, Any]:
    return {
        "items": [
            {
                "id": "rothc",
                "name": "RothC-26.3",
                "pools": ["DPM", "RPM", "BIO", "HUM", "IOM"],
                "endpoint": "POST /api/v1/science/rothc/run",
                "best_for_fa": "زراعت معتدل؛ استاندارد MRV کربن خاک",
            },
            {
                "id": "icbm",
                "name": "ICBM",
                "pools": ["Young", "Old"],
                "endpoint": "POST /api/v1/science/soil-carbon/icbm",
                "best_for_fa": "ساده، کالیبراسیون سریع، دو استخر",
            },
            {
                "id": "century3",
                "name": "CENTURY-style 3-pool",
                "pools": ["Active", "Slow", "Passive"],
                "endpoint": "POST /api/v1/science/soil-carbon/century3",
                "best_for_fa": "بلندمدت؛ تفکیک فعال/کند/پاسیو",
            },
            {
                "id": "yasso07_lite",
                "name": "Yasso07-lite",
                "pools": ["A", "W", "E", "N", "H"],
                "endpoint": "POST /api/v1/science/soil-carbon/yasso",
                "best_for_fa": "لایه لاشبرگ و اقلیم؛ الهام از جنگل",
            },
            {
                "id": "ensemble",
                "name": "Multi-model ensemble",
                "pools": [],
                "endpoint": "POST /api/v1/science/soil-carbon/ensemble",
                "best_for_fa": "مقایسه هم‌زمان و میانگین ΔSOC",
            },
        ],
        "disclaimer_fa": "پیاده‌سازی‌های فرآیندی متن‌باز؛ باینری رسمی مدل‌ها نیستند.",
    }
