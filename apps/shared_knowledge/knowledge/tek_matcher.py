"""
TEK Pattern Matcher
===================
Earth Memory matching algorithm - Section 3.4 of Hydroma-Nojin paper.

Matches current environmental conditions against 3000-year historical
patterns to generate adaptive recommendations.

Algorithm:
  match_score = climate_match(0.3) + rainfall_match(0.2) +
                groundwater_match(0.2) + age_bonus(0.3)
"""

import logging
import math
from typing import Any

logger = logging.getLogger(__name__)

# Climate zone compatibility matrix
# Which modern Koppen zones match each TEK climate requirement
CLIMATE_ZONE_ALIASES: dict[str, list[str]] = {
    "arid": ["BWk", "BWh", "BSh"],
    "semi_arid": ["BSk", "BSh", "BWk"],
    "highland": ["ETH", "ET", "Cwb", "Cwc", "Dsb", "Dsc"],
    "tropical": ["Af", "Am", "Aw", "As"],
    "temperate": ["Cfa", "Cfb", "Cfc", "Csa", "Csb"],
    "mediterranean": ["Csa", "Csb", "Csc"],
}


def match_climate_zone(current_zone: str, pattern_zones: list[str]) -> float:
    """
    Check if current climate zone is compatible with pattern zones.
    Returns 0.0 to 1.0.
    """
    if not current_zone or not pattern_zones:
        return 0.5  # Unknown -> neutral score

    if current_zone in pattern_zones:
        return 1.0

    # Check aliases
    for alias, zones in CLIMATE_ZONE_ALIASES.items():
        if current_zone in zones and any(z in pattern_zones for z in zones):
            return 0.7

    return 0.1


def match_rainfall(
    current_rainfall_mm: float | None,
    conditions: dict[str, Any],
) -> float:
    """Match annual rainfall against pattern conditions."""
    if current_rainfall_mm is None:
        return 0.5

    max_rain = conditions.get("max_rainfall_mm")
    min_rain = conditions.get("min_rainfall_mm")

    score = 0.0
    if max_rain is not None:
        if current_rainfall_mm <= max_rain:
            score += 0.5
        else:
            # Partial score if within 20% of threshold
            if current_rainfall_mm <= max_rain * 1.2:
                score += 0.3

    if min_rain is not None:
        if current_rainfall_mm >= min_rain:
            score += 0.5
        else:
            if current_rainfall_mm >= min_rain * 0.8:
                score += 0.3

    # If only one condition is set, double the score
    if max_rain is None or min_rain is None:
        score = min(1.0, score * 2)

    return score


def match_groundwater(
    current_depth_m: float | None,
    conditions: dict[str, Any],
) -> float:
    """Match groundwater depth against pattern conditions."""
    if current_depth_m is None:
        return 0.5

    min_depth = conditions.get("min_groundwater_depth_m")
    max_depth = conditions.get("max_groundwater_depth_m")

    score = 0.0

    if min_depth is not None:
        if current_depth_m >= min_depth:
            score += 0.5
        else:
            if current_depth_m >= min_depth * 0.8:
                score += 0.3

    if max_depth is not None:
        if current_depth_m <= max_depth:
            score += 0.5
        else:
            if current_depth_m <= max_depth * 1.2:
                score += 0.3

    if min_depth is None or max_depth is None:
        score = min(1.0, score * 2)

    return score


def match_elevation(
    current_elevation_m: float | None,
    conditions: dict[str, Any],
) -> float:
    """Match elevation against pattern conditions."""
    if current_elevation_m is None:
        return 0.5

    min_elev = conditions.get("min_elevation_m")
    max_elev = conditions.get("max_elevation_m")

    if min_elev is not None and max_elev is not None:
        if min_elev <= current_elevation_m <= max_elev:
            return 1.0
        # Partial match if close
        if abs(current_elevation_m - min_elev) < min_elev * 0.2:
            return 0.6
        if abs(current_elevation_m - max_elev) < max_elev * 0.1:
            return 0.6

    return 0.5


def match_soil_carbon(
    current_soc_pct: float | None,
    conditions: dict[str, Any],
) -> float:
    """Match soil organic carbon against pattern conditions."""
    if current_soc_pct is None:
        return 0.5

    max_soc = conditions.get("max_soil_organic_carbon_pct")

    if max_soc is not None and current_soc_pct <= max_soc:
        return 1.0

    return 0.5


def match_frost(
    frost_risk: bool | None,
    conditions: dict[str, Any],
) -> float:
    """Match frost risk against pattern conditions."""
    if frost_risk is None:
        return 0.5

    pattern_needs_frost = conditions.get("frost_risk_required", False)

    if frost_risk == pattern_needs_frost:
        return 1.0

    return 0.2


def calculate_age_bonus(age_years: int) -> float:
    """
    Older patterns get a bonus - they have survived longer trials.

    Formula from paper: age_bonus = min(0.3, age_years / 10000)
    A 3000-year pattern gets 0.3 bonus (max).
    A 1000-year pattern gets 0.1 bonus.
    """
    return min(0.3, age_years / 10000.0)


def match_pattern(
    climate_zone: str,
    annual_rainfall_mm: float | None,
    groundwater_depth_m: float | None,
    elevation_m: float | None,
    soil_organic_carbon_pct: float | None,
    frost_risk: bool | None,
    pattern_climate_zones: list[str],
    pattern_conditions: dict[str, Any],
    pattern_age_years: int,
) -> tuple[float, dict[str, float]]:
    """
    Calculate similarity score between current conditions and a historical pattern.

    Weights (from paper Section 3.4.2):
      - Climate match: 0.30
      - Rainfall match: 0.20
      - Groundwater match: 0.20
      - Age bonus: 0.30

    Additional optional factors (reduce other weights proportionally):
      - Elevation match: up to 0.10
      - Soil carbon match: up to 0.10
      - Frost match: up to 0.10

    Returns:
        Tuple of (total_score, component_scores_dict)
    """
    components: dict[str, float] = {}

    # Core factors
    components["climate"] = match_climate_zone(climate_zone, pattern_climate_zones)
    components["rainfall"] = match_rainfall(annual_rainfall_mm, pattern_conditions)
    components["groundwater"] = match_groundwater(groundwater_depth_m, pattern_conditions)
    components["age"] = calculate_age_bonus(pattern_age_years)

    # Optional factors
    components["elevation"] = match_elevation(elevation_m, pattern_conditions)
    components["soil_carbon"] = match_soil_carbon(soil_organic_carbon_pct, pattern_conditions)
    components["frost"] = match_frost(frost_risk, pattern_conditions)

    # Weighted total - core weights
    total = (
        components["climate"] * 0.30
        + components["rainfall"] * 0.20
        + components["groundwater"] * 0.20
        + components["age"] * 0.30
    )

    # Boost with optional factors (up to +0.15 bonus total)
    if elevation_m is not None:
        total += components["elevation"] * 0.05
    if soil_organic_carbon_pct is not None:
        total += components["soil_carbon"] * 0.05
    if frost_risk is not None:
        total += components["frost"] * 0.05

    return (min(1.0, total), components)


def format_recommendation(
    template: str,
    pattern_name: str,
    civilization: str,
    age_years: int,
    score: float,
    **kwargs,
) -> str:
    """
    Format a recommendation from template with variable substitution.
    """
    replacements = {
        "{pattern_name}": pattern_name,
        "{civilization}": civilization,
        "{age_years}": str(age_years),
        "{age_millennia}": f"{age_years / 1000:.1f}",
        "{match_score}": f"{score:.0%}",
        **{f"{{{k}}}": str(v) for k, v in kwargs.items()},
    }

    result = template
    for key, val in replacements.items():
        result = result.replace(key, val)

    return result


# Qanat/Mirab water flow formula (Darcy's Law for underground channels)
def calculate_qanat_flow(
    slope_pct: float,
    aquifer_transmissivity_m2_day: float,
    channel_width_m: float = 0.8,
) -> float:
    """
    Calculate estimated Qanat flow rate based on Darcy's Law.

    Q = T * i * W
    where:
      Q = flow rate (m^3/day)
      T = transmissivity (m^2/day)
      i = hydraulic gradient = slope_pct / 100
      W = channel width (m)

    Returns:
        Estimated flow rate in m^3/day
    """
    i = slope_pct / 100.0
    Q = aquifer_transmissivity_m2_day * i * channel_width_m
    return max(0.0, Q)


# Waru Waru thermal buffer formula
def calculate_waru_waru_thermal_buffer(
    water_volume_m3: float,
    soil_volume_m3: float,
    water_temp_day_c: float = 15.0,
    night_air_temp_c: float = -3.0,
) -> float:
    """
    Calculate night-time temperature increase from Waru Waru water channels.

    The water absorbs heat during the day and releases it at night,
    creating a microclimate buffer.

    delta_T = (C_water * V_water * delta_T_stored) / (V_soil * rho_soil * c_soil)

    Simplified for practical use:
      thermal_buffer_c = water_volume_m3 * 4.18 * (water_temp_day_c - night_air_temp_c)
                         / (soil_volume_m3 * 1.3 * 0.8)

    Returns:
        Temperature increase in Celsius at night
    """
    if soil_volume_m3 <= 0:
        return 0.0

    c_water = 4.18  # kJ/(kg*K) specific heat of water
    rho_soil = 1.3  # bulk density g/cm^3 (t/m^3)
    c_soil = 0.8  # kJ/(kg*K) specific heat of dry soil

    delta_t_stored = max(0.0, water_temp_day_c - night_air_temp_c)
    energy_stored = c_water * water_volume_m3 * delta_t_stored
    thermal_buffer = energy_stored / (soil_volume_m3 * rho_soil * c_soil)

    return round(thermal_buffer, 2)


# Terra Preta biochar decomposition formula
def calculate_biochar_soc_change(
    biochar_input_t_ha: float,
    years: int,
    decomposition_rate_k: float = 0.05,
) -> float:
    """
    Calculate soil organic carbon change from biochar application.

    Formula from paper:
      SOC_change = Biochar_input * (1 - e^(-k * t))

    Biochar decomposes very slowly (k ~ 0.05/year vs 0.5-2.0 for raw biomass).

    Returns:
        SOC increase in t/ha after specified years
    """
    return biochar_input_t_ha * (1.0 - math.exp(-decomposition_rate_k * years))


# Milpa nitrogen fixation formula
def calculate_milpa_nitrogen(
    bean_biomass_kg_ha: float,
    rhizobia_efficiency: float = 0.6,
) -> float:
    """
    Calculate biological nitrogen fixation from legume in Milpa polyculture.

    N_fixed = bean_biomass * N_content * rhizobia_efficiency
    where N_content ~ 0.025 (2.5% nitrogen in legume biomass)

    Returns:
        Nitrogen fixed in kg N/ha
    """
    n_content = 0.025  # 2.5% N in legume dry matter
    return bean_biomass_kg_ha * n_content * rhizobia_efficiency


# Subak water distribution formula
def calculate_subak_water_allocation(
    total_flow_m3_s: float,
    field_areas_ha: list[float],
    priority_factors: list[float] | None = None,
) -> list[float]:
    """
    Calculate equitable water distribution per Subak principles.

    Formula: Q_field = Q_total * (A_field * P_field) / sum(A_i * P_i)
    This ensures all water is allocated proportionally to area-weighted priority.

    Args:
        total_flow_m3_s: Total available water flow (m^3/s)
        field_areas_ha: List of field areas in hectares
        priority_factors: Optional priority factors (default: equal = 1.0)

    Returns:
        List of water allocations in m^3/s per field, summing exactly to total_flow
    """
    if not field_areas_ha:
        return []
    if total_flow_m3_s <= 0:
        return [0.0] * len(field_areas_ha)

    if priority_factors is None:
        priority_factors = [1.0] * len(field_areas_ha)

    # Weighted area = area * priority
    weighted_areas = [area * max(0.1, pf) for area, pf in zip(field_areas_ha, priority_factors)]
    total_weighted = sum(weighted_areas)

    if total_weighted <= 0:
        # Fallback: equal distribution
        return [total_flow_m3_s / len(field_areas_ha)] * len(field_areas_ha)

    allocations = [round(total_flow_m3_s * wa / total_weighted, 4) for wa in weighted_areas]

    return allocations
