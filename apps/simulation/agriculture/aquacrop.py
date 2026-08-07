"""
AquaCrop Conceptual Engine (FAO-56 Based)
=========================================
A robust, copyright-free implementation of crop water productivity and yield response.
Based on FAO Irrigation and Drainage Paper 56 (Public Domain).
Optimized for arid, semi-arid, and mountainous regions.
"""
from __future__ import annotations
import logging
import math
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

logger = logging.getLogger(__name__)

# ==========================================
# 1. Crop Database (Public Domain Parameters)
# ==========================================
CROP_DATABASE = {
    'wheat_rainfed': {'name_fa': 'گندم دیم', 'ky': 1.15, 'root_max_m': 1.0, 't_base': 0.0, 'season_days':150},
    'wheat_irrigated': {'name_fa': 'گندم آبی', 'ky': 1.15, 'root_max_m': 1.0, 't_base': 0.0, 'season_days':150},
    'maize': {'name_fa': 'ذرت', 'ky': 1.25, 'root_max_m': 1.2, 't_base': 10.0, 'season_days': 120},
    'barley': {'name_fa': 'جو', 'ky': 1.0, 'root_max_m': 1.0, 't_base': 0.0, 'season_days': 120},
    'saffron': {'name_fa': 'زعفران', 'ky': 0.85, 'root_max_m': 0.4, 't_base': 5.0, 'season_days': 200},
    'pistachio': {'name_fa': 'پسته', 'ky': 0.80, 'root_max_m': 2.0, 't_base': 7.0, 'season_days': 365},
}

@dataclass
class SoilProfile:
    fc_mm: float = 200.0
    wp_mm: float = 100.0
    depletion_fraction: float = 0.55

@dataclass
class Management:
    irrigation_events: Dict[int, float] = field(default_factory=dict)

@dataclass
class SimulationResult:
    crop_id: str
    total_yield_t_ha: float
    potential_yield_t_ha: float
    total_water_use_mm: float
    irrigation_applied_mm: float
    avg_water_stress: float
    daily_records: List[Dict[str, Any]]
    status: str = 'success'
    message: str = ''

def run_aquacrop_conceptual(
    crop_id: str,
    climate_data: List[Dict[str, float]],
    soil: SoilProfile = SoilProfile(),
    management: Management = Management(),
    potential_yield_t_ha: float = 8.0
) -> SimulationResult:
    if crop_id not in CROP_DATABASE:
        crop_id = 'wheat_rainfed'
    
    crop = CROP_DATABASE[crop_id]
    taw = soil.fc_mm - soil.wp_mm
    threshold_depletion = taw * soil.depletion_fraction
    
    current_soil_water = soil.fc_mm
    total_et_a, total_et_c, total_irrigation, stress_sum = 0.0, 0.0, 0.0, 0.0
    daily_records = []
    season_len = len(climate_data)
    
    for day_idx, day_data in enumerate(climate_data):
        day = day_idx + 1
        tmax = day_data.get('tmax', 25.0)
        tmin = day_data.get('tmin', 10.0)
        precip = day_data.get('precip', 0.0)
        et0 = day_data.get('et0', 3.0)
        irrigation = management.irrigation_events.get(day, 0.0)
        
        # Frost Stress Check
        if tmin < crop['t_base']:
            kc, frost_stress = 0.0, True
        else:
            frost_stress = False
            progress = day / season_len
            if progress < 0.25: kc = 0.3 + (0.85 * (progress / 0.25))
            elif progress < 0.75: kc = 1.15
            else: kc = 1.15 - (0.85 * ((progress - 0.75) / 0.25))
            kc = max(0.1, min(1.2, kc))
        
        etc = kc * et0
        total_irrigation += irrigation
        
        depletion = soil.fc_mm - current_soil_water
        ks = (taw - depletion) / (taw - threshold_depletion) if depletion > threshold_depletion else 1.0
        ks = max(0.0, min(1.0, ks))
        if frost_stress: ks = 0.0
            
        eta = ks * etc
        current_soil_water = current_soil_water + precip + irrigation - eta
        
        if current_soil_water > soil.fc_mm:
            current_soil_water = soil.fc_mm
            
        total_et_a += eta
        total_et_c += etc
        stress_sum += (1.0 - ks)
        
        daily_records.append({'day': day, 'tmax': tmax, 'tmin': tmin, 'precip': precip, 'et0': et0, 'kc': round(kc, 2), 'ks': round(ks, 2), 'eta_mm': round(eta, 2)})

    # Yield Calculation (FAO-56)
    if total_et_c > 0:
        et_ratio = total_et_a / total_et_c
        yield_reduction = crop['ky'] * (1.0 - et_ratio)
        actual_yield = max(0.0, potential_yield_t_ha * (1.0 - yield_reduction))
    else:
        actual_yield = 0.0
        
    avg_stress = stress_sum / season_len if season_len > 0 else 0.0
    
    return SimulationResult(
        crop_id=crop_id, total_yield_t_ha=round(actual_yield, 2), potential_yield_t_ha=potential_yield_t_ha,
        total_water_use_mm=round(total_et_a, 2), irrigation_applied_mm=round(total_irrigation, 2),
        avg_water_stress=round(avg_stress, 2), daily_records=daily_records, status='success',
        message=f"Simulation completed for {crop['name_fa']}. Yield: {actual_yield:.2f} t/ha"
    )