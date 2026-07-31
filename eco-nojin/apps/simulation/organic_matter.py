"""
Organic matter (OM) dynamics — multi-pool turnover with optional C:N coupling.

Models:
  1) om_two_pool — labile + stable OM (first-order)
  2) om_cn_coupled — C and N linked mineralization / immobilization
  3) litter_cascade — surface litter → subsurface OM → stable

Units: t OM/ha or t C/ha (when carbon_fraction applied).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _climate_factor(temp_c: float, moisture: float) -> float:
    """moisture in 0–1; Q10-style temperature."""
    ft = 2.0 ** ((temp_c - 15.0) / 10.0)
    fw = max(0.15, min(1.0, moisture))
    return max(0.05, ft * fw)


def run_om_two_pool(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Labile (fast) + Stable (slow) organic matter.

    dL/dt = I·f_L − k_L·f·L
    dS/dt = I·(1−f_L) + α·k_L·f·L − k_S·f·S
    """
    p = params or {}
    years = int(p.get("years", 20))
    steps_per_year = int(p.get("steps_per_year", 12))
    dt = 1.0 / steps_per_year

    om0 = float(p.get("om_t_ha", 80.0))
    labile_frac = float(p.get("labile_frac", 0.2))
    L = om0 * labile_frac
    S = om0 * (1.0 - labile_frac)
    I = float(p.get("om_input_t_ha_y", 3.0))  # total OM input / year
    f_L = float(p.get("input_labile_frac", 0.6))
    k_L = float(p.get("k_labile", 1.2))  # 1/y
    k_S = float(p.get("k_stable", 0.05))
    alpha = float(p.get("stabilization_frac", 0.25))  # labile → stable
    temp = float(p.get("temp_c", 15.0))
    moist = float(p.get("moisture_frac", 0.55))
    c_frac = float(p.get("carbon_fraction", 0.58))  # OM → C

    f_clim = _climate_factor(temp, moist)
    series: list[dict[str, float]] = []
    total_steps = years * steps_per_year
    for step in range(total_steps + 1):
        year = step * dt
        if step % steps_per_year == 0 or step == total_steps:
            series.append(
                {
                    "year": round(year, 3),
                    "labile": round(L, 4),
                    "stable": round(S, 4),
                    "om_t_ha": round(L + S, 3),
                    "soc_t_ha": round((L + S) * c_frac, 3),
                }
            )
        if step == total_steps:
            break
        dL = I * f_L * dt - k_L * f_clim * L * dt
        dS = I * (1.0 - f_L) * dt + alpha * k_L * f_clim * L * dt - k_S * f_clim * S * dt
        # CO2 loss from non-stabilized labile decay is implicit
        L = max(0.0, L + dL)
        S = max(0.0, S + dS)

    om_f = series[-1]["om_t_ha"]
    return {
        "model": "om_two_pool",
        "citation": "Two-pool first-order OM dynamics (labile/stable)",
        "om_initial": round(om0, 3),
        "om_final": om_f,
        "delta_om": round(om_f - om0, 3),
        "soc_final": series[-1]["soc_t_ha"],
        "climate_factor": round(f_clim, 4),
        "params": {
            "years": years,
            "om_input_t_ha_y": I,
            "k_labile": k_L,
            "k_stable": k_S,
            "stabilization_frac": alpha,
            "temp_c": temp,
            "moisture_frac": moist,
            "carbon_fraction": c_frac,
        },
        "series": series,
        "completed_at": datetime.now(UTC).isoformat(),
    }


def run_om_cn_coupled(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    C–N coupled mineralization.

    Microbial demand: if residue C:N > critical, immobilize mineral N;
    else net mineralization. Simplified annual/monthly pool.
    """
    p = params or {}
    years = int(p.get("years", 15))
    steps_per_year = int(p.get("steps_per_year", 12))
    dt = 1.0 / steps_per_year

    c_om = float(p.get("soc_t_ha", 40.0))  # organic C
    cn_om = float(p.get("cn_ratio", 12.0))
    n_om = c_om / max(cn_om, 1.0)
    n_min = float(p.get("n_mineral_t_ha", 0.08))

    c_input = float(p.get("c_input_t_ha_y", 1.5))
    cn_input = float(p.get("cn_input", 25.0))
    cn_crit = float(p.get("cn_critical", 20.0))
    k_dec = float(p.get("k_decomp", 0.15))  # 1/y organic C
    temp = float(p.get("temp_c", 15.0))
    moist = float(p.get("moisture_frac", 0.55))
    f_clim = _climate_factor(temp, moist)
    microbial_cn = float(p.get("microbial_cn", 8.0))
    efficiency = float(p.get("carbon_use_efficiency", 0.4))

    series: list[dict[str, float]] = []
    n_min_cum = 0.0
    total_steps = years * steps_per_year
    for step in range(total_steps + 1):
        year = step * dt
        if step % steps_per_year == 0 or step == total_steps:
            series.append(
                {
                    "year": round(year, 3),
                    "soc_t_ha": round(c_om, 3),
                    "n_organic": round(n_om, 4),
                    "n_mineral": round(n_min, 4),
                    "cn_ratio": round(c_om / max(n_om, 1e-6), 2),
                }
            )
        if step == total_steps:
            break

        # decomposition of organic C
        dec_c = k_dec * f_clim * c_om * dt
        # N released proportional to current OM C:N
        cn_now = c_om / max(n_om, 1e-6)
        n_from_om = dec_c / cn_now

        # microbial assimilation of C
        assim_c = efficiency * dec_c
        co2 = dec_c - assim_c
        n_demand = assim_c / microbial_cn

        net_n = n_from_om - n_demand  # >0 mineralize, <0 immobilize
        if net_n < 0:
            take = min(n_min, -net_n)
            n_min -= take
            immobilized = take
            mineralized = 0.0
            # if not enough mineral N, reduce assim
            if take < -net_n:
                short = -net_n - take
                assim_c = max(0.0, assim_c - short * microbial_cn)
        else:
            n_min += net_n
            mineralized = net_n
            immobilized = 0.0

        n_min_cum += mineralized - immobilized

        c_om = max(0.1, c_om - dec_c + c_input * dt)
        n_in = (c_input * dt) / max(cn_input, 1.0)
        n_om = max(0.01, n_om - n_from_om + n_in + immobilized)
        # return microbial N/C into OM roughly
        c_om += assim_c * 0.5  # half of biomass to OM (simple)
        n_om += (assim_c * 0.5) / microbial_cn

    return {
        "model": "om_cn_coupled",
        "citation": "Simplified C–N coupled OM mineralization/immobilization",
        "soc_initial": float(p.get("soc_t_ha", 40.0)),
        "soc_final": series[-1]["soc_t_ha"],
        "delta_soc": round(series[-1]["soc_t_ha"] - float(p.get("soc_t_ha", 40.0)), 3),
        "n_mineral_final": series[-1]["n_mineral"],
        "cn_final": series[-1]["cn_ratio"],
        "climate_factor": round(f_clim, 4),
        "params": {
            "years": years,
            "c_input_t_ha_y": c_input,
            "cn_input": cn_input,
            "cn_critical": cn_crit,
            "k_decomp": k_dec,
            "temp_c": temp,
            "moisture_frac": moist,
        },
        "series": series,
        "completed_at": datetime.now(UTC).isoformat(),
        "notes_fa": (
            "اگر C:N ورودی بالا باشد، نیتروژن معدنی موقتاً قفل می‌شود (immobilization)."
        ),
    }


def run_litter_cascade(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """
    Surface litter → metabolic/structural → soil OM → passive.
    """
    p = params or {}
    years = int(p.get("years", 15))
    litter0 = float(p.get("litter_t_ha", 2.0))
    om0 = float(p.get("om_t_ha", 70.0))
    passive0 = float(p.get("passive_t_ha", 30.0))
    litter_in = float(p.get("litter_input_t_ha_y", 2.5))
    k_lit = float(p.get("k_litter", 1.5))
    k_om = float(p.get("k_om", 0.08))
    k_pas = float(p.get("k_passive", 0.005))
    to_om = float(p.get("frac_litter_to_om", 0.35))
    to_pas = float(p.get("frac_om_to_passive", 0.12))
    temp = float(p.get("temp_c", 15.0))
    moist = float(p.get("moisture_frac", 0.55))
    f = _climate_factor(temp, moist)
    c_frac = float(p.get("carbon_fraction", 0.5))

    lit, om, pas = litter0, om0, passive0
    series: list[dict[str, float]] = []
    for y in range(years + 1):
        series.append(
            {
                "year": float(y),
                "litter": round(lit, 4),
                "om": round(om, 4),
                "passive": round(pas, 4),
                "total_om": round(lit + om + pas, 3),
                "soc_proxy": round((lit + om + pas) * c_frac, 3),
            }
        )
        if y == years:
            break
        d_lit = k_lit * f * lit
        d_om = k_om * f * om
        d_pas = k_pas * f * pas
        lit = max(0.0, lit - d_lit + litter_in)
        om = max(0.0, om - d_om + to_om * d_lit)
        pas = max(0.0, pas - d_pas + to_pas * d_om)

    return {
        "model": "litter_cascade",
        "citation": "Litter → OM → passive cascade (first-order)",
        "total_initial": round(litter0 + om0 + passive0, 3),
        "total_final": series[-1]["total_om"],
        "delta": round(series[-1]["total_om"] - (litter0 + om0 + passive0), 3),
        "climate_factor": round(f, 4),
        "series": series,
        "params": {
            "years": years,
            "litter_input_t_ha_y": litter_in,
            "k_litter": k_lit,
            "k_om": k_om,
            "temp_c": temp,
            "moisture_frac": moist,
        },
        "completed_at": datetime.now(UTC).isoformat(),
    }


def om_catalog() -> dict[str, Any]:
    return {
        "items": [
            {
                "id": "om_two_pool",
                "name": "Two-pool OM",
                "endpoint": "POST /api/v1/science/organic-matter/two-pool",
                "best_for_fa": "مواد آلی لابل و پایدار",
            },
            {
                "id": "om_cn_coupled",
                "name": "C–N coupled OM",
                "endpoint": "POST /api/v1/science/organic-matter/cn",
                "best_for_fa": "معدنی‌سازی/تثبیت نیتروژن با C:N",
            },
            {
                "id": "litter_cascade",
                "name": "Litter cascade",
                "endpoint": "POST /api/v1/science/organic-matter/litter",
                "best_for_fa": "لاشبرگ سطحی تا استخر پاسیو",
            },
        ],
        "calibration": {
            "endpoint": "POST /api/v1/science/soil-carbon/calibrate",
            "models": ["rothc", "icbm", "century3", "yasso07_lite"],
        },
    }
