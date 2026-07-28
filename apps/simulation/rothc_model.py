"""
RothC-26.3 soil organic carbon model (Coleman & Jenkinson).

Open re-implementation of published rate equations — not a binary port of RothC software.
References:
  Coleman K., Jenkinson D.S. (1996/2014). RothC — A model for the turnover of carbon
  in soil. Rothamsted Research.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any


def _rate_temp(t_c: float) -> float:
    """Temperature rate modifying factor a (RothC)."""
    if t_c < -5.0:
        return 0.0
    # a = 47.91 / (1 + exp(106.06 / (T + 18.27)))
    return 47.91 / (1.0 + math.exp(106.06 / (t_c + 18.27)))


def _rate_moisture(rain_mm: float, et_mm: float, clay_pct: float) -> float:
    """
    Moisture factor b (simplified monthly).
    Uses accumulated moisture deficit approximation.
    """
    # Maximum soil moisture deficit (mm) increases with clay
    max_smd = 20.0 + clay_pct  # simplified from RothC tables
    deficit = max(0.0, et_mm - rain_mm)
    smd = min(max_smd, deficit)
    # b = 0.2 + 0.8 * (1 - smd/max_smd) when deficit exists
    if max_smd <= 0:
        return 1.0
    b = 0.2 + 0.8 * (1.0 - smd / max_smd)
    return max(0.2, min(1.0, b))


def _rate_plant_cover(covered: bool) -> float:
    """c = 0.6 if vegetated, 1.0 if bare (RothC)."""
    return 0.6 if covered else 1.0


def _clay_factor(clay_pct: float) -> float:
    """
x = 1.67 * (1.85 + 1.60 * exp(-0.0786 * clay))  # partition to CO2 vs BIO+HUM
    Returns fraction of decomposed C allocated to BIO+HUM (rest → CO2).
    """
    x = 1.67 * (1.85 + 1.60 * math.exp(-0.0786 * clay_pct))
    # Fraction to BIO+HUM = 1 / (x + 1) in classic formulation of evolved CO2 ratio
    # Evolved CO2 / (BIO+HUM) = x → BIO+HUM fraction = 1/(x+1)
    return 1.0 / (x + 1.0)


def run_rothc(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Annual-step RothC compartments: DPM, RPM, BIO, HUM, IOM (t C ha⁻¹).

    Default pools partitioned from total SOC if not provided.
    """
    p = params or {}
    years = int(p.get("years", 10))
    clay = float(p.get("clay_pct", 25.0))
    temp = float(p.get("temp_c", 15.0))
    rain = float(p.get("rain_mm_year", 650.0))
    et = float(p.get("et_mm_year", 700.0))
    covered = bool(p.get("plant_cover", True))
    c_input = float(p.get("c_input_t_ha_y", 1.5))  # plant residue + manure C
    dpm_rpm_ratio = float(p.get("dpm_rpm_ratio", 1.44))  # crops ~1.44, FYM ~1.0

    soc0 = float(p.get("soc_t_ha", 40.0))
    # Initial partition (typical arable approximation)
    iom = float(p.get("iom_t_ha", min(5.0, soc0 * 0.1)))  # inert
    active = max(0.0, soc0 - iom)
    dpm = float(p.get("dpm_t_ha", active * 0.01))
    rpm = float(p.get("rpm_t_ha", active * 0.12))
    bio = float(p.get("bio_t_ha", active * 0.02))
    hum = float(p.get("hum_t_ha", max(0.0, active - dpm - rpm - bio)))

    # Decomposition rate constants (1/year) at standard conditions
    k_dpm, k_rpm, k_bio, k_hum = 10.0, 0.3, 0.66, 0.02

    a = _rate_temp(temp)
    # monthly-equivalent factors scaled to annual using mean conditions
    b = _rate_moisture(rain / 12.0, et / 12.0, clay)
    c = _rate_plant_cover(covered)
    abc = a * b * c
    f_bh = _clay_factor(clay)  # to BIO+HUM
    # Of BIO+HUM pool, 46% BIO, 54% HUM (RothC default split)

    series: list[dict[str, float]] = []
    for y in range(years + 1):
        total = dpm + rpm + bio + hum + iom
        series.append(
            {
                "year": float(y),
                "dpm": round(dpm, 4),
                "rpm": round(rpm, 4),
                "bio": round(bio, 4),
                "hum": round(hum, 4),
                "iom": round(iom, 4),
                "soc_t_ha": round(total, 3),
            }
        )
        if y == years:
            break

        def dec(pool: float, k: float) -> float:
            return pool * (1.0 - math.exp(-k * abc))

        d_dpm = dec(dpm, k_dpm)
        d_rpm = dec(rpm, k_rpm)
        d_bio = dec(bio, k_bio)
        d_hum = dec(hum, k_hum)
        decomposed = d_dpm + d_rpm + d_bio + d_hum

        dpm -= d_dpm
        rpm -= d_rpm
        bio -= d_bio
        hum -= d_hum

        to_bh = decomposed * f_bh
        bio += to_bh * 0.46
        hum += to_bh * 0.54
        # remainder decomposed → CO2 (implicit)

        # Fresh inputs: split DPM/RPM
        dpm_frac = dpm_rpm_ratio / (1.0 + dpm_rpm_ratio)
        dpm += c_input * dpm_frac
        rpm += c_input * (1.0 - dpm_frac)

    soc_final = series[-1]["soc_t_ha"]
    return {
        "model": "rothc_26_3",
        "citation": "Coleman & Jenkinson RothC-26.3 (open reimplementation)",
        "soc_initial": round(soc0, 3),
        "soc_final": soc_final,
        "delta": round(soc_final - soc0, 3),
        "rate_modifiers": {"a_temp": round(a, 4), "b_moisture": round(b, 4), "c_cover": c, "abc": round(abc, 4)},
        "clay_pct": clay,
        "c_input_t_ha_y": c_input,
        "series": series,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
