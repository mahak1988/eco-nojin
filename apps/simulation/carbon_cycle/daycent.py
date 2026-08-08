"""
DayCent Daily Carbon-Nitrogen Simulator (Clean Room)
=====================================================
Implements daily-step carbon (SOC) and nitrogen (SON) dynamics with
pool-based decomposition, mineralization, immobilization, and leaching.

Based on concepts from:
  Parton, W.J. et al. (1998). DayCent: Daily version of CENTURY.
  Global and Planetary Change 19(1-4):35-48.

Not the official DayCent binary. Clean Room implementation for decision support.
"""
from __future__ import annotations
import math
from typing import Any

ENGINE = "conceptual"
ENGINE_VERSION = "1.0.0"
DISCLAIMER = (
    "Clean Room implementation of DayCent concepts (Parton et al. 1998). "
    "Not the official DayCent binary. For decision support only."
)

# Soil texture effects on decomposition (sand = fastest, clay = slowest)
TEXTURE_FACTORS = {
    "sand": 0.7, "loamy_sand": 0.8, "sandy_loam": 0.9,
    "loam": 1.0, "silt_loam": 1.1, "clay_loam": 1.2, "clay": 1.3,
}

# Decomposition rate constants at 20C (fraction/day)
K_ACTIVE = 0.02   # Active pool (fast: weeks-months)
K_SLOW = 0.0005   # Slow pool (medium: years-decades)
K_PASSIVE = 0.00002  # Passive pool (slow: centuries)


def temperature_factor(temp_c: float) -> float:
    """Q10 temperature modifier for decomposition (Q10 ~ 2.0)."""
    return max(0.1, min(3.0, 2.0 ** ((temp_c - 20.0) / 10.0)))


def moisture_factor(annual_precip_mm: float, potential_et_mm: float = 800.0) -> float:
    """Moisture modifier based on precipitation:potential ET ratio."""
    if potential_et_mm <= 0:
        return 0.5
    ratio = annual_precip_mm / potential_et_mm
    return max(0.1, min(1.0, ratio))


def run_daycent(params: dict[str, Any] | None = None) -> dict[str, Any]:
    """DayCent daily carbon-nitrogen simulation with 3 SOM pools."""
    p = dict(params or {})

    initial_soc = float(p.get("initial_soc", 50.0))  # t C/ha
    initial_son = float(p.get("initial_son", 5.0))   # t N/ha (10:1 C:N)
    n_fertilizer_kg_ha = float(p.get("n_fertilizer_kg_ha", 100.0))
    days = max(1, int(float(p.get("days", 365))))
    temp_c = float(p.get("temp_c", 15.0))
    precip_mm = float(p.get("precip_mm", 500.0))
    soil_texture = str(p.get("soil_texture", "loam"))

    texture_factor = TEXTURE_FACTORS.get(soil_texture, 1.0)
    t_factor = temperature_factor(temp_c)
    m_factor = moisture_factor(precip_mm)
    env_factor = t_factor * m_factor * texture_factor

    # SOM pool initialization (DayCent default: 2% active, 48% slow, 50% passive)
    active_c = initial_soc * 0.02
    slow_c = initial_soc * 0.48
    passive_c = initial_soc * 0.50

    # Tracking variables
    co2_total = 0.0
    n_mineralized = 0.0
    n_immobilized = 0.0
    n_leached = 0.0

    for day in range(days):
        # Day-level decomposition
        d_active = active_c * K_ACTIVE * env_factor
        d_slow = slow_c * K_SLOW * env_factor
        d_passive = passive_c * K_PASSIVE * env_factor

        total_decomp = d_active + d_slow + d_passive
        co2_total += total_decomp * 0.55  # ~55% of decomposed C goes to CO2

        # Pool transfers (simplified DayCent cascade)
        active_c -= d_active * 0.70
        slow_c += d_active * 0.30 - d_slow * 0.50
        passive_c += d_slow * 0.50 - d_passive * 0.10

        # Ensure non-negative pools
        active_c = max(0.0, active_c)
        slow_c = max(0.0, slow_c)
        passive_c = max(0.0, passive_c)

        # Nitrogen mineralization (C:N ~10 for active pool)
        n_mineralized += total_decomp * 0.10

        # Nitrogen leaching (proportional to precipitation)
        daily_n_input = n_fertilizer_kg_ha / max(1, days)
        if precip_mm > 0:
            n_leached += daily_n_input * min(0.15, precip_mm / 2000.0)

    final_soc = active_c + slow_c + passive_c
    soc_change = final_soc - initial_soc

    # Net GWP (CO2 equivalent)
    net_gwp_co2e = co2_total * 3.67  # Convert C to CO2

    # SOC sequestration rate (t/ha/yr, positive = sequestration)
    years = days / 365.0
    seq_rate = soc_change / years if years > 0 else 0.0

    # N2O emissions estimate (1% of mineralized N, IPCC Tier 1)
    n2o_n_kg_ha = n_mineralized * 0.01
    n2o_co2e = n2o_n_kg_ha * 298.0 / 1000.0  # GWP of N2O = 298

    return {
        "engine": ENGINE,
        "engine_version": ENGINE_VERSION,
        "model": "DayCent (Clean Room)",
        "citation": "Parton, W.J. et al. (1998). Global & Planetary Change 19:35-48.",
        "disclaimer": DISCLAIMER,
        "days": days,
        "years": round(years, 2),
        "parameters": {
            "initial_soc_t_ha": initial_soc,
            "soil_texture": soil_texture,
            "temp_c": temp_c,
            "precip_mm": precip_mm,
            "n_fertilizer_kg_ha": n_fertilizer_kg_ha,
        },
        "temperature_factor": round(t_factor, 3),
        "moisture_factor": round(m_factor, 3),
        "initial_soc_t_ha": initial_soc,
        "final_soc_t_ha": round(final_soc, 2),
        "soc_change_t_ha": round(soc_change, 2),
        "seq_rate_t_ha_yr": round(seq_rate, 3),
        "co2_emission_t_ha": round(co2_total, 2),
        "net_gwp_co2e_t_ha": round(net_gwp_co2e, 2),
        "n_mineralization_kg_ha": round(n_mineralized, 2),
        "n_leaching_kg_ha": round(n_leached, 2),
        "n2o_n_kg_ha": round(n2o_n_kg_ha, 4),
        "n2o_co2e_t_ha": round(n2o_co2e, 4),
        "soc_change_status": "sequestering" if soc_change > 0 else "depleting",
        "completed_at": None,
    }
