# -*- coding: utf-8 -*-
"""
Carbon Model Simulator
Advanced simulation of RothC, AquaCrop, and carbon sequestration models
"""

import math
import random
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SoilCarbonPool:
    """RothC soil carbon pools"""
    dpm: float  # Decomposable Plant Material
    rpm: float  # Resistant Plant Material
    bio: float  # Microbial Biomass
    hum: float  # Humified Organic Matter
    iom: float  # Inert Organic Matter

    @property
    def total(self) -> float:
        return self.dpm + self.rpm + self.bio + self.hum + self.iom


@dataclass
class CropGrowth:
    """AquaCrop crop growth parameters"""
    canopy_cover: float  # 0-1
    biomass: float  # kg/ha
    yield_kg: float  # kg/ha
    water_use_efficiency: float  # kg/m3
    growth_stage: str  # germination, vegetative, flowering, maturity


class CarbonModelSimulator:
    """Simulates carbon sequestration using RothC and AquaCrop models"""

    # RothC decomposition rate constants (per year)
    RATE_CONSTANTS = {
        'dpm': 10.0,
        'rpm': 0.3,
        'bio': 0.66,
        'hum': 0.02,
    }

    # Clay content affects decomposition
    CLAY_FACTORS = {
        'sandy': 1.2,
        'loamy': 1.0,
        'clay': 0.8,
    }

    def __init__(
        self,
        latitude: float = 35.6892,
        longitude: float = 51.3890,
        soil_type: str = 'loamy',
        initial_soc: float = 20.0,  # tons C/ha
        clay_content: float = 25.0,  # %
    ):
        self.latitude = latitude
        self.longitude = longitude
        self.soil_type = soil_type
        self.clay_content = clay_content

        # Initialize RothC pools
        self.pools = SoilCarbonPool(
            dpm=initial_soc * 0.05,
            rpm=initial_soc * 0.35,
            bio=initial_soc * 0.05,
            hum=initial_soc * 0.50,
            iom=initial_soc * 0.05,
        )

        # Crop growth
        self.crop = CropGrowth(
            canopy_cover=0.0,
            biomass=0.0,
            yield_kg=0.0,
            water_use_efficiency=15.0,
            growth_stage='germination'
        )

    def _temperature_factor(self, temp_c: float) -> float:
        """Temperature rate modifier for RothC"""
        if temp_c < -5:
            return 0.0
        elif temp_c < 0:
            return 0.1
        else:
            return 0.2 + 0.8 * (1 - math.exp(-0.076 * temp_c))

    def _moisture_factor(self, moisture: float) -> float:
        """Moisture rate modifier (0-1)"""
        if moisture < 0.2:
            return 0.2
        elif moisture < 0.4:
            return 0.2 + 2 * (moisture - 0.2)
        elif moisture < 0.6:
            return 0.6 + (moisture - 0.4)
        else:
            return 0.8

    def _plant_retention_factor(self, canopy_cover: float) -> float:
        """Plant retention factor (reduces decomposition when plants present)"""
        return 1.0 - 0.6 * canopy_cover

    def simulate_rothc_step(
        self,
        time_step: float,  # years
        temp_c: float,
        moisture: float,
        plant_input: float,  # tons C/ha
        canopy_cover: float,
    ) -> Dict:
        """Simulate one time step of RothC model"""

        # Rate modifiers
        temp_mod = self._temperature_factor(temp_c)
        moist_mod = self._moisture_factor(moisture)
        plant_mod = self._plant_retention_factor(canopy_cover)
        clay_mod = self.CLAY_FACTORS.get(self.soil_type, 1.0)

        rate_mod = temp_mod * moist_mod * plant_mod * clay_mod

        # Decomposition
        dpm_decomp = self.pools.dpm * self.RATE_CONSTANTS['dpm'] * rate_mod * time_step
        rpm_decomp = self.pools.rpm * self.RATE_CONSTANTS['rpm'] * rate_mod * time_step
        bio_decomp = self.pools.bio * self.RATE_CONSTANTS['bio'] * rate_mod * time_step
        hum_decomp = self.pools.hum * self.RATE_CONSTANTS['hum'] * rate_mod * time_step

        # Update pools
        self.pools.dpm = max(0, self.pools.dpm - dpm_decomp + plant_input * 0.5)
        self.pools.rpm = max(0, self.pools.rpm - rpm_decomp + plant_input * 0.5)

        # Microbial products
        bio_production = (dpm_decomp + rpm_decomp) * 0.46
        hum_production = (dpm_decomp + rpm_decomp) * 0.54 * 0.65

        self.pools.bio = max(0, self.pools.bio - bio_decomp + bio_production)
        self.pools.hum = max(0, self.pools.hum - hum_decomp + hum_production)

        # CO2 released
        co2_released = (dpm_decomp + rpm_decomp + bio_decomp + hum_decomp) * 3.67  # C to CO2

        return {
            'pools': {
                'dpm': round(self.pools.dpm, 3),
                'rpm': round(self.pools.rpm, 3),
                'bio': round(self.pools.bio, 3),
                'hum': round(self.pools.hum, 3),
                'iom': round(self.pools.iom, 3),
                'total': round(self.pools.total, 3),
            },
            'co2_released_tons': round(co2_released, 3),
            'rate_modifier': round(rate_mod, 3),
        }

    def simulate_aquacrop_growth(
        self,
        days: int,
        water_available_mm: float,
        temp_avg_c: float,
    ) -> List[Dict]:
        """Simulate crop growth using AquaCrop principles"""

        growth_data = []
        canopy = 0.0
        biomass = 0.0

        for day in range(days):
            # Growth stages
            if day < 15:
                stage = 'germination'
                canopy_growth = 0.02
            elif day < 45:
                stage = 'vegetative'
                canopy_growth = 0.03
            elif day < 75:
                stage = 'flowering'
                canopy_growth = 0.01
            else:
                stage = 'maturity'
                canopy_growth = -0.005  # Senescence

            # Canopy development
            canopy = max(0, min(1, canopy + canopy_growth))

            # Biomass production (simplified AquaCrop)
            # WP* * (Tr/ET0) where WP* is water productivity
            if temp_avg_c > 5 and canopy > 0:
                transpiration = min(water_available_mm / days, 5) * canopy
                biomass_increment = 15 * transpiration  # 15 g/m2 per mm
                biomass += biomass_increment
            else:
                biomass_increment = 0

            # Yield formation (after flowering)
            if stage in ['flowering', 'maturity']:
                yield_kg = biomass * 0.4  # 40% harvest index
            else:
                yield_kg = 0

            growth_data.append({
                'day': day,
                'stage': stage,
                'canopy_cover': round(canopy, 3),
                'biomass_kg_ha': round(biomass, 2),
                'yield_kg_ha': round(yield_kg, 2),
                'biomass_increment': round(biomass_increment, 2),
                'timestamp': (datetime.now(timezone.utc) + timedelta(days=day)).isoformat(),
            })

        self.crop.canopy_cover = canopy
        self.crop.biomass = biomass
        self.crop.yield_kg = yield_kg if 'yield_kg' in locals() else 0

        return growth_data

    def simulate_annual_carbon(
        self,
        years: int = 10,
        tree_count: int = 1000,
        species: str = 'quercus_persica',
    ) -> Dict:
        """Simulate annual carbon sequestration"""

        # Species-specific carbon sequestration rates (kg CO2/tree/year)
        species_rates = {
            'quercus_persica': 22.0,  # Persian Oak
            'eucalyptus': 45.0,
            'populus': 35.0,
            'pistacia_atlantica': 18.0,
            'amygdalus_scoparia': 15.0,
        }

        base_rate = species_rates.get(species, 22.0)

        # Growth curve (sigmoid)
        annual_data = []
        cumulative_carbon = 0.0

        for year in range(1, years + 1):
            # Sigmoid growth factor
            growth_factor = 1.0 / (1.0 + math.exp(-0.3 * (year - 10)))

            # Climate modifier (semi-arid Iran)
            climate_mod = 0.75

            # Soil modifier
            soil_mod = 1.0 + (self.pools.hum / 100) * 0.1

            # Annual sequestration per tree
            annual_per_tree = base_rate * growth_factor * climate_mod * soil_mod

            # Total for all trees
            annual_total_kg = annual_per_tree * tree_count
            annual_total_tons = annual_total_kg / 1000

            cumulative_carbon += annual_total_tons

            # Simulate RothC for this year
            avg_temp = 15 + 5 * math.sin(2 * math.pi * (year % 10) / 10)
            avg_moisture = 0.4 + 0.1 * math.sin(2 * math.pi * year / 5)
            plant_input = annual_total_tons * 0.3  # 30% goes to soil

            rothc_result = self.simulate_rothc_step(
                time_step=1.0,
                temp_c=avg_temp,
                moisture=avg_moisture,
                plant_input=plant_input,
                canopy_cover=min(1, year / 10)
            )

            annual_data.append({
                'year': year,
                'carbon_per_tree_kg': round(annual_per_tree, 2),
                'carbon_total_kg': round(annual_total_kg, 2),
                'carbon_total_tons': round(annual_total_tons, 2),
                'cumulative_tons': round(cumulative_carbon, 2),
                'soil_carbon_tons': rothc_result['pools']['total'],
                'co2_released_tons': rothc_result['co2_released_tons'],
                'growth_factor': round(growth_factor, 3),
            })

        return {
            'species': species,
            'tree_count': tree_count,
            'years_simulated': years,
            'total_carbon_tons': round(cumulative_carbon, 2),
            'annual_average_tons': round(cumulative_carbon / years, 2),
            'final_soil_carbon_tons': round(self.pools.total, 2),
            'annual_data': annual_data,
            'confidence': 0.85,
            'methodology': 'RothC + AquaCrop + Species-Specific Growth Curves',
        }

    def simulate_project_impact(
        self,
        activity_type: str,
        area_hectares: float,
        duration_years: int,
        **kwargs
    ) -> Dict:
        """Simulate complete project impact"""

        if activity_type == 'tree_planting':
            tree_count = kwargs.get('tree_count', int(area_hectares * 1000))
            species = kwargs.get('species', 'quercus_persica')

            result = self.simulate_annual_carbon(
                years=duration_years,
                tree_count=tree_count,
                species=species
            )

            # Add crop growth simulation
            crop_growth = self.simulate_aquacrop_growth(
                days=min(365, duration_years * 365),
                water_available_mm=400,
                temp_avg_c=18
            )

            result['crop_growth_sample'] = crop_growth[-10:]  # Last 10 days
            result['activity_type'] = activity_type
            result['area_hectares'] = area_hectares

            return result

        elif activity_type == 'soil_regeneration':
            # Simulate soil carbon increase
            annual_increase = 0.5  # tons C/ha/year
            total_carbon = annual_increase * area_hectares * duration_years * 3.67

            return {
                'activity_type': activity_type,
                'area_hectares': area_hectares,
                'duration_years': duration_years,
                'total_carbon_tons': round(total_carbon, 2),
                'annual_increase_per_ha': annual_increase,
                'methodology': 'RothC Soil Carbon Model',
                'confidence': 0.80,
            }

        else:
            # Generic calculation
            rate = 2.0  # tons CO2/ha/year
            total = rate * area_hectares * duration_years

            return {
                'activity_type': activity_type,
                'area_hectares': area_hectares,
                'duration_years': duration_years,
                'total_carbon_tons': round(total, 2),
                'methodology': 'Generic Ecosystem Model',
                'confidence': 0.70,
            }


# Global simulator
_simulator = None

def get_simulator(**kwargs) -> CarbonModelSimulator:
    global _simulator
    if _simulator is None:
        _simulator = CarbonModelSimulator(**kwargs)
    return _simulator

def reset_simulator(**kwargs):
    global _simulator
    _simulator = CarbonModelSimulator(**kwargs)
