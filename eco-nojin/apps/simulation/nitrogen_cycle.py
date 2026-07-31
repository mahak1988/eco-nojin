"""
Soil nitrogen cycle — simplified multi-pool annual/monthly model.

Pools (t N/ha unless noted):
  - N_org   organic N (linked to SOM C via C:N)
  - NH4     ammonium
  - NO3     nitrate
  - N_plant cumulative plant uptake (diagnostic)
  - N_lost  cumulative leaching + denitrification (diagnostic)

Processes:
  mineralization, immobilization, nitrification, denitrification,
  leaching, fertilizer, atmospheric deposition, plant uptake.

Not a full APSIM/DAYCENT replacement — educational / screening process model.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from apps.simulation.evaluation_metrics import evaluate_series


def _clamp(x: float, lo: float = 0.0) -> float:
    return max(lo, x)


def _climate(temp_c: float, moisture: float) -> dict[str, float]:
    """Relative rates 0–1+."""
    # mineralization/nitrification increase with T and moisture
    ft = max(0.1, min(2.5, 2.0 ** ((temp_c - 15.0) / 10.0)))
    fw = max(0.15, min(1.0, moisture))
    # denitrification prefers wet
    f_denit = max(0.05, min(1.0, (moisture - 0.55) / 0.35)) if moisture > 0.55 else 0.05 * moisture
    # leaching with drainage proxy
    f_leach = max(0.0, min(1.0, (moisture - 0.5) * 1.5))
    return {"ft": ft, "fw": fw, "f_bio": ft * fw, "f_denit": f_denit, "f_leach": f_leach}


def run_nitrogen_cycle(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    years = int(p.get("years", 10))
    steps_per_year = int(p.get("steps_per_year", 12))
    dt = 1.0 / steps_per_year

    # Initial pools
    soc = float(p.get("soc_t_ha", 40.0))
    cn = float(p.get("cn_ratio", 12.0))
    n_org = float(p.get("n_org_t_ha", soc / max(cn, 1.0)))
    nh4 = float(p.get("nh4_t_ha", 0.02))
    no3 = float(p.get("no3_t_ha", 0.05))

    # Rates (1/year at reference)
    k_min = float(p.get("k_mineralization", 0.04))
    k_nit = float(p.get("k_nitrification", 8.0))  # NH4 fast relative
    k_den = float(p.get("k_denitrification", 0.3))
    k_leach = float(p.get("k_leaching", 0.4))
    k_uptake = float(p.get("k_uptake", 2.5))

    fert_n = float(p.get("fertilizer_n_t_ha_y", 0.12))  # ~120 kg N/ha/y
    fert_nh4_frac = float(p.get("fert_nh4_frac", 0.5))
    deposition = float(p.get("deposition_n_t_ha_y", 0.01))
    residue_n = float(p.get("residue_n_t_ha_y", 0.03))
    max_uptake = float(p.get("max_uptake_t_ha_y", 0.18))

    temp = float(p.get("temp_c", 15.0))
    moist = float(p.get("moisture_frac", 0.55))
    clim = _climate(temp, moist)

    # Optional organic C for immobilization demand
    c_input = float(p.get("c_input_t_ha_y", 1.0))
    cn_crit = float(p.get("cn_critical", 20.0))
    cn_micro = float(p.get("microbial_cn", 8.0))

    n_plant = 0.0
    n_leached = 0.0
    n_denit = 0.0
    n_fert_cum = 0.0

    series: list[dict[str, float]] = []
    total_steps = years * steps_per_year

    for step in range(total_steps + 1):
        year = step * dt
        if step % steps_per_year == 0 or step == total_steps:
            series.append(
                {
                    "year": round(year, 4),
                    "n_org": round(n_org, 5),
                    "nh4": round(nh4, 5),
                    "no3": round(no3, 5),
                    "n_inorganic": round(nh4 + no3, 5),
                    "n_total": round(n_org + nh4 + no3, 4),
                    "n_plant_cum": round(n_plant, 5),
                    "n_leached_cum": round(n_leached, 5),
                    "n_denit_cum": round(n_denit, 5),
                }
            )
        if step == total_steps:
            break

        # Inputs this step
        fert = fert_n * dt
        dep = deposition * dt
        res = residue_n * dt
        n_fert_cum += fert
        nh4 += fert * fert_nh4_frac + dep * 0.3
        no3 += fert * (1.0 - fert_nh4_frac) + dep * 0.7
        n_org += res

        # Gross mineralization
        min_n = k_min * clim["f_bio"] * n_org * dt
        min_n = min(min_n, n_org * 0.5)
        n_org -= min_n
        nh4 += min_n

        # Immobilization proxy from C input
        # microbes need N for assimilating residue C
        c_assimilable = c_input * dt * 0.4
        n_demand = c_assimilable / cn_micro
        imm = min(n_demand * 0.5, nh4 + no3)
        if imm > 0:
            from_nh4 = min(nh4, imm * 0.6)
            from_no3 = min(no3, imm - from_nh4)
            nh4 -= from_nh4
            no3 -= from_no3
            n_org += from_nh4 + from_no3
            imm_done = from_nh4 + from_no3
        else:
            imm_done = 0.0

        # Nitrification NH4 → NO3
        nit = k_nit * clim["f_bio"] * nh4 * dt
        nit = min(nit, nh4)
        nh4 -= nit
        no3 += nit

        # Plant uptake from NH4+NO3 (prefer NO3 slightly)
        avail = nh4 + no3
        uptake_cap = max_uptake * dt
        uptake = min(uptake_cap, k_uptake * clim["fw"] * avail * dt, avail)
        if avail > 1e-12:
            u_no3 = uptake * (no3 / avail)
            u_nh4 = uptake - u_no3
        else:
            u_no3 = u_nh4 = 0.0
        no3 = _clamp(no3 - u_no3)
        nh4 = _clamp(nh4 - u_nh4)
        n_plant += uptake

        # Denitrification on NO3
        den = k_den * clim["f_denit"] * no3 * dt
        den = min(den, no3)
        no3 -= den
        n_denit += den

        # Leaching on NO3
        leach = k_leach * clim["f_leach"] * no3 * dt
        leach = min(leach, no3)
        no3 -= leach
        n_leached += leach

        nh4 = _clamp(nh4)
        no3 = _clamp(no3)
        n_org = _clamp(n_org, 0.01)

    # Annual totals for reporting
    return {
        "model": "soil_n_cycle",
        "citation": "Simplified multi-pool soil N cycle (min/nitrif/denit/leach/uptake)",
        "years": years,
        "climate": {k: round(v, 4) for k, v in clim.items()},
        "initial": {
            "n_org": float(p.get("n_org_t_ha", soc / max(cn, 1.0))),
            "nh4": float(p.get("nh4_t_ha", 0.02)),
            "no3": float(p.get("no3_t_ha", 0.05)),
        },
        "final": series[-1],
        "balances_t_ha": {
            "fertilizer_cum": round(n_fert_cum, 4),
            "plant_uptake_cum": round(n_plant, 4),
            "leached_cum": round(n_leached, 4),
            "denitrified_cum": round(n_denit, 4),
            "residual_inorganic": round(nh4 + no3, 5),
        },
        "params": {
            "k_mineralization": k_min,
            "k_nitrification": k_nit,
            "k_denitrification": k_den,
            "k_leaching": k_leach,
            "fertilizer_n_t_ha_y": fert_n,
            "temp_c": temp,
            "moisture_frac": moist,
        },
        "series": series,
        "notes_fa": (
            "واحدها t N/ha. کود ۱۲۰ kg N/ha ≈ ۰.۱۲ t/ha. "
            "مدل غربالگری است نه جایگزین اندازه‌گیری مزرعه."
        ),
        "completed_at": datetime.now(UTC).isoformat(),
    }


def evaluate_n_series(
    result: dict[str, Any],
    observed: dict[str, list[float]],
) -> dict[str, Any]:
    """
    Compare model series to observations.
    observed keys e.g. no3, n_org, n_inorganic — values annual points.
    """
    series = result.get("series") or []
    reports = {}
    for key, obs in observed.items():
        sim = [float(row.get(key, float("nan"))) for row in series]
        # if obs shorter, take matching years from start
        reports[key] = evaluate_series(obs, sim[: len(obs)], variable=key)
    return {
        "model": result.get("model", "soil_n_cycle"),
        "metrics_by_variable": reports,
        "completed_at": datetime.now(UTC).isoformat(),
    }
