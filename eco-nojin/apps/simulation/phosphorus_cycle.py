"""
Soil phosphorus dynamics — multi-pool simplified model.

Pools (kg P/ha):
  - P_labile     labile / solution-exchangeable
  - P_active     active mineral (slowly available)
  - P_stable     stable / occluded
  - P_organic    organic P

Processes: fertilizer, mineralization, immobilization, sorption,
           desorption, plant uptake, runoff/erosion loss, leaching (small).

Not a full EPIC/APSIM-P replacement — screening / educational process model.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def _clamp(x: float, lo: float = 0.0) -> float:
    return max(lo, x)


def run_phosphorus_cycle(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    years = int(p.get("years", 10))
    steps_y = int(p.get("steps_per_year", 12))
    dt = 1.0 / steps_y

    # Initial pools kg P/ha
    p_lab = float(p.get("p_labile_kg_ha", 25.0))
    p_act = float(p.get("p_active_kg_ha", 80.0))
    p_stb = float(p.get("p_stable_kg_ha", 200.0))
    p_org = float(p.get("p_organic_kg_ha", 60.0))

    # Rates 1/y
    k_min = float(p.get("k_mineralization", 0.03))
    k_imm = float(p.get("k_immobilization", 0.01))
    k_sorp = float(p.get("k_sorption", 0.4))  # labile -> active
    k_des = float(p.get("k_desorption", 0.08))
    k_occ = float(p.get("k_occlusion", 0.02))  # active -> stable
    k_rel = float(p.get("k_release", 0.005))  # stable -> active
    k_uptake = float(p.get("k_uptake", 1.5))
    max_uptake = float(p.get("max_uptake_kg_ha_y", 25.0))

    fert_y = float(p.get("fertilizer_p_kg_ha_y", 40.0))
    residue_p = float(p.get("residue_p_kg_ha_y", 5.0))
    erosion_y = float(p.get("erosion_loss_frac_y", 0.01))
    leach_y = float(p.get("leach_frac_y", 0.005))

    # Soil chemistry modifiers
    ph = float(p.get("ph", 7.0))
    clay = float(p.get("clay_pct", 25.0))
    # P availability lower in very acid or calcareous soils
    if ph < 6.0:
        avail_f = max(0.4, 1.0 - (6.0 - ph) * 0.15)
    elif ph > 7.8:
        avail_f = max(0.45, 1.0 - (ph - 7.8) * 0.2)
    else:
        avail_f = 1.0
    sorp_f = 1.0 + 0.02 * max(0.0, clay - 20.0)  # more clay -> more sorption

    temp = float(p.get("temp_c", 15.0))
    moist = float(p.get("moisture_frac", 0.55))
    f_bio = max(0.15, min(2.0, (2.0 ** ((temp - 15.0) / 10.0)) * max(0.2, min(1.0, moist))))

    p_plant = 0.0
    p_lost_er = 0.0
    p_lost_le = 0.0
    p_fert = 0.0

    series: list[dict[str, float]] = []
    total = years * steps_y

    for step in range(total + 1):
        year = step * dt
        if step % steps_y == 0 or step == total:
            series.append(
                {
                    "year": round(year, 4),
                    "p_labile": round(p_lab, 3),
                    "p_active": round(p_act, 3),
                    "p_stable": round(p_stb, 3),
                    "p_organic": round(p_org, 3),
                    "p_total": round(p_lab + p_act + p_stb + p_org, 2),
                    "p_available": round(p_lab * avail_f, 3),
                    "p_plant_cum": round(p_plant, 3),
                }
            )
        if step == total:
            break

        # Inputs
        fert = fert_y * dt
        res = residue_p * dt
        p_fert += fert
        p_lab += fert * 0.7  # most fertilizer to labile
        p_act += fert * 0.3
        p_org += res

        # Mineralization / immobilization organic <-> labile
        min_p = k_min * f_bio * p_org * dt
        min_p = min(min_p, p_org * 0.4)
        imm_p = k_imm * f_bio * p_lab * dt
        imm_p = min(imm_p, p_lab * 0.3)
        p_org = _clamp(p_org - min_p + imm_p)
        p_lab = _clamp(p_lab + min_p - imm_p)

        # Sorption / desorption labile <-> active
        sorp = k_sorp * sorp_f * p_lab * dt
        sorp = min(sorp, p_lab)
        des = k_des * p_act * dt
        des = min(des, p_act)
        p_lab = _clamp(p_lab - sorp + des)
        p_act = _clamp(p_act + sorp - des)

        # Occlusion / release active <-> stable
        occ = k_occ * p_act * dt
        occ = min(occ, p_act)
        rel = k_rel * p_stb * dt
        rel = min(rel, p_stb)
        p_act = _clamp(p_act - occ + rel)
        p_stb = _clamp(p_stb + occ - rel)

        # Plant uptake from available labile
        avail = p_lab * avail_f
        up_cap = max_uptake * dt
        up = min(up_cap, k_uptake * avail * dt, p_lab)
        p_lab = _clamp(p_lab - up)
        p_plant += up

        # Erosion (mostly surface labile + organic fraction)
        er = erosion_y * dt
        loss_er = er * (0.6 * p_lab + 0.2 * p_org)
        p_lab = _clamp(p_lab - er * 0.6 * p_lab)
        p_org = _clamp(p_org - er * 0.2 * p_org)
        p_lost_er += loss_er

        # Small leaching of labile
        le = leach_y * dt * p_lab
        p_lab = _clamp(p_lab - le)
        p_lost_le += le

    return {
        "model": "soil_p_cycle",
        "citation": "Four-pool soil P (labile/active/stable/organic) process model",
        "years": years,
        "ph": ph,
        "availability_factor": round(avail_f, 3),
        "sorption_factor": round(sorp_f, 3),
        "climate_bio_factor": round(f_bio, 3),
        "initial_total": round(
            float(p.get("p_labile_kg_ha", 25))
            + float(p.get("p_active_kg_ha", 80))
            + float(p.get("p_stable_kg_ha", 200))
            + float(p.get("p_organic_kg_ha", 60)),
            2,
        ),
        "final": series[-1],
        "balances_kg_ha": {
            "fertilizer_cum": round(p_fert, 2),
            "plant_uptake_cum": round(p_plant, 2),
            "erosion_loss_cum": round(p_lost_er, 3),
            "leach_loss_cum": round(p_lost_le, 3),
        },
        "series": series,
        "notes_fa": (
            "واحد kg P/ha. در pH اسیدی یا قلیایی شدید، فسفر قابل‌جذب کم می‌شود. "
            "مدل غربالگری است."
        ),
        "completed_at": datetime.now(UTC).isoformat(),
    }
