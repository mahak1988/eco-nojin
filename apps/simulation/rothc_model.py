"""
RothC-26.3 soil organic carbon model (Coleman & Jenkinson).

Open re-implementation — not a binary port of RothC software.
Parameters resolved via apps.simulation.rothc_params.resolve_params.
"""

from __future__ import annotations

import math
from datetime import UTC, datetime
from typing import Any

from apps.simulation.rothc_params import BIO_FRAC_OF_BH, HUM_FRAC_OF_BH, resolve_params


def _rate_temp(t_c: float) -> float:
    """Temperature rate modifying factor a (RothC)."""
    if t_c < -5.0:
        return 0.0
    return 47.91 / (1.0 + math.exp(106.06 / (t_c + 18.27)))


def _rate_moisture(rain_mm_month: float, et_mm_month: float, clay_pct: float) -> float:
    """Moisture factor b (monthly deficit approximation)."""
    max_smd = 20.0 + clay_pct
    deficit = max(0.0, et_mm_month - rain_mm_month)
    smd = min(max_smd, deficit)
    if max_smd <= 0:
        return 1.0
    b = 0.2 + 0.8 * (1.0 - smd / max_smd)
    return max(0.2, min(1.0, b))


def _rate_plant_cover(covered: bool) -> float:
    return 0.6 if covered else 1.0


def _clay_factor(clay_pct: float) -> float:
    """Fraction of decomposed C allocated to BIO+HUM (rest → CO2)."""
    x = 1.67 * (1.85 + 1.60 * math.exp(-0.0786 * clay_pct))
    return 1.0 / (x + 1.0)


def run_rothc(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """Annual-step RothC: DPM, RPM, BIO, HUM, IOM (t C ha⁻¹)."""
    p = resolve_params(params)
    years = int(p["years"])
    clay = float(p["clay_pct"])
    temp = float(p["temp_c"])
    rain = float(p["rain_mm_year"])
    et = float(p["et_mm_year"])
    covered = bool(p["plant_cover"])
    c_input = float(p["c_input_t_ha_y"])
    dpm_rpm_ratio = float(p["dpm_rpm_ratio"])
    soc0 = float(p["soc_t_ha"])

    dpm = float(p["dpm_t_ha"])
    rpm = float(p["rpm_t_ha"])
    bio = float(p["bio_t_ha"])
    hum = float(p["hum_t_ha"])
    iom = float(p["iom_t_ha"])

    k_dpm = float(p["k_dpm"])
    k_rpm = float(p["k_rpm"])
    k_bio = float(p["k_bio"])
    k_hum = float(p["k_hum"])

    a = _rate_temp(temp)
    b = _rate_moisture(rain / 12.0, et / 12.0, clay)
    c = _rate_plant_cover(covered)
    abc = a * b * c
    f_bh = _clay_factor(clay)

    series: list[dict[str, float]] = []
    co2_cum = 0.0
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
                "co2_cum_t_ha": round(co2_cum, 3),
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
        to_co2 = decomposed - to_bh
        co2_cum += to_co2
        bio += to_bh * BIO_FRAC_OF_BH
        hum += to_bh * HUM_FRAC_OF_BH

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
        "co2_total_t_ha": round(co2_cum, 3),
        "rate_modifiers": {
            "a_temp": round(a, 4),
            "b_moisture": round(b, 4),
            "c_cover": c,
            "abc": round(abc, 4),
            "f_bio_hum": round(f_bh, 4),
        },
        "params_resolved": {
            k: p[k]
            for k in (
                "years",
                "soc_t_ha",
                "iom_t_ha",
                "dpm_t_ha",
                "rpm_t_ha",
                "bio_t_ha",
                "hum_t_ha",
                "c_input_t_ha_y",
                "dpm_rpm_ratio",
                "plant_cover",
                "clay_pct",
                "temp_c",
                "rain_mm_year",
                "et_mm_year",
                "k_dpm",
                "k_rpm",
                "k_bio",
                "k_hum",
            )
        },
        "clay_pct": clay,
        "c_input_t_ha_y": c_input,
        "series": series,
        "completed_at": datetime.now(UTC).isoformat(),
    }
