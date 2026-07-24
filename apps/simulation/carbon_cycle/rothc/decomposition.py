"""
Decomposition Engine for RothC Model
=====================================
Handles organic matter decomposition calculations based on RothC methodology.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DecompositionParams:
    """Parameters controlling decomposition rates."""
    
    # Pool-specific decomposition rates (per year)
    dpm_rate: float = 10.0  # Decomposable Plant Material
    rpm_rate: float = 0.3   # Resistant Plant Material
    bio_rate: float = 0.66  # Microbial Biomass
    hum_rate: float = 0.02  # Humus
    
    # Environmental modifiers
    temperature_factor: float = 1.0
    moisture_factor: float = 1.0
    soil_cover_factor: float = 1.0
    
    # Carbon partitioning ratios
    biomass_fraction: float = 0.54  # Fraction to microbial biomass
    co2_fraction: float = 0.46      # Fraction lost as CO2
    humification_fraction: float = 0.03  # Fraction to humus


@dataclass
class DecompositionState:
    """Current state of carbon pools."""
    
    dpm: float = 0.0  # tC/ha - Decomposable Plant Material
    rpm: float = 0.0  # tC/ha - Resistant Plant Material
    bio: float = 0.0  # tC/ha - Microbial Biomass
    hum: float = 0.0  # tC/ha - Humus
    iom: float = 0.0  # tC/ha - Inert Organic Matter
    
    total_soc: float = 0.0  # Total Soil Organic Carbon
    
    def update_total(self):
        """Recalculate total SOC from pools."""
        self.total_soc = self.dpm + self.rpm + self.bio + self.hum + self.iom
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "dpm_t_ha": self.dpm,
            "rpm_t_ha": self.rpm,
            "bio_t_ha": self.bio,
            "hum_t_ha": self.hum,
            "iom_t_ha": self.iom,
            "total_soc_t_ha": self.total_soc
        }


@dataclass
class DecompositionOutput:
    """Results from decomposition calculation."""
    
    timestep: int
    date: datetime
    initial_state: DecompositionState
    final_state: DecompositionState
    
    # Fluxes during timestep
    co2_emitted: float = 0.0  # tC/ha
    residue_added: float = 0.0  # tC/ha
    manure_added: float = 0.0  # tC/ha
    
    # Environmental conditions
    temperature: float = 0.0  # °C
    rainfall: float = 0.0  # mm
    evapotranspiration: float = 0.0  # mm
    
    # Rate modifiers
    rate_modifier: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "timestep": self.timestep,
            "date": self.date.isoformat(),
            "carbon_pools_initial": self.initial_state.to_dict(),
            "carbon_pools_final": self.final_state.to_dict(),
            "fluxes": {
                "co2_emitted_t_ha": self.co2_emitted,
                "residue_added_t_ha": self.residue_added,
                "manure_added_t_ha": self.manure_added
            },
            "environment": {
                "temperature_c": self.temperature,
                "rainfall_mm": self.rainfall,
                "rate_modifier": self.rate_modifier
            }
        }


class DecompositionEngine:
    """
    Core decomposition engine implementing RothC methodology.
    
    The RothC model simulates the turnover of organic carbon in 
    non-waterlogged topsoil (0-23 cm depth).
    """
    
    def __init__(self, params: Optional[DecompositionParams] = None):
        """
        Initialize decomposition engine.
        
        Args:
            params: Decomposition parameters. Uses defaults if not provided.
        """
        self.params = params or DecompositionParams()
        logger.info("DecompositionEngine initialized")
    
    def initialize_state(
        self,
        total_soc: float,
        clay_content: float,
        equilibrium: bool = True
    ) -> DecompositionState:
        """
        Initialize carbon pool distribution from total SOC.
        
        Args:
            total_soc: Total soil organic carbon (tC/ha)
            clay_content: Clay content (%)
            equilibrium: If True, assume pools are at equilibrium
            
        Returns:
            Initial decomposition state
        """
        state = DecompositionState()
        
        # Calculate IOM (Inert Organic Matter) based on clay content
        # IOM = TOC * (0.49 + 0.0048 * %clay)^(-1) * 100
        if clay_content > 0:
            iom_factor = (0.49 + 0.0048 * clay_content) / 100.0
            state.iom = total_soc * iom_factor
        else:
            state.iom = total_soc * 0.10  # Default 10%
        
        # Active carbon (excluding IOM)
        active_carbon = total_soc - state.iom
        
        if equilibrium:
            # Equilibrium distribution (typical ratios)
            state.dpm = active_carbon * 0.02  # 2%
            state.rpm = active_carbon * 0.13  # 13%
            state.bio = active_carbon * 0.04  # 4%
            state.hum = active_carbon * 0.81  # 81%
        else:
            # Non-equilibrium: use default initialization
            state.dpm = active_carbon * 0.05
            state.rpm = active_carbon * 0.15
            state.bio = active_carbon * 0.03
            state.hum = active_carbon * 0.77
        
        state.update_total()
        
        logger.debug(f"Initialized state: {state.to_dict()}")
        return state
    
    def calculate_rate_modifier(
        self,
        temperature: float,
        rainfall: float,
        potential_evapotranspiration: float,
        soil_cover: float = 1.0
    ) -> float:
        """
        Calculate environmental rate modifier.
        
        RothC uses temperature, moisture, and soil cover factors.
        
        Args:
            temperature: Monthly average temperature (°C)
            rainfall: Monthly rainfall (mm)
            potential_evapotranspiration: Potential ET (mm)
            soil_cover: Soil cover factor (0-1)
            
        Returns:
            Combined rate modifier (0-1+)
        """
        # Temperature factor (optimal ~25°C)
        if temperature > 0:
            temp_factor = 47.91 / (1 + math.exp(106.91 / (temperature + 18.34)))
        else:
            temp_factor = 0.1
        
        # Moisture factor based on rainfall/PET ratio
        if potential_evapotranspiration > 0:
            moisture_ratio = rainfall / potential_evapotranspiration
            if moisture_ratio < 0.2:
                moist_factor = 0.2
            elif moisture_ratio > 1.5:
                moist_factor = 0.6  # Waterlogging reduces decomposition
            else:
                moist_factor = 0.2 + 0.53 * moisture_ratio
        else:
            moist_factor = 0.5
        
        # Soil cover factor (bare soil = faster decomposition)
        cover_factor = 0.6 + 0.4 * soil_cover
        
        # Combined modifier
        rate_modifier = temp_factor * moist_factor * cover_factor
        
        logger.debug(
            f"Rate modifier: {rate_modifier:.3f} "
            f"(T={temp_factor:.3f}, M={moist_factor:.3f}, C={cover_factor:.3f})"
        )
        
        return rate_modifier
    
    def step(
        self,
        state: DecompositionState,
        temperature: float,
        rainfall: float,
        pet: float,
        residue_input: float = 0.0,
        manure_input: float = 0.0,
        root_input: float = 0.0,
        soil_cover: float = 1.0,
        timestep_days: int = 30
    ) -> DecompositionOutput:
        """
        Perform one decomposition timestep (typically monthly).
        
        Args:
            state: Current carbon pool state
            temperature: Monthly avg temperature (°C)
            rainfall: Monthly rainfall (mm)
            pet: Potential evapotranspiration (mm)
            residue_input: Crop residue input (tC/ha/month)
            manure_input: Farmyard manure input (tC/ha/month)
            root_input: Root input (tC/ha/month)
            soil_cover: Soil cover factor
            timestep_days: Length of timestep in days
            
        Returns:
            Decomposition output with updated state
        """
        import math
        
        # Store initial state
        initial_state = DecompositionState(
            dpm=state.dpm,
            rpm=state.rpm,
            bio=state.bio,
            hum=state.hum,
            iom=state.iom
        )
        initial_state.update_total()
        
        # Calculate rate modifier
        rate_mod = self.calculate_rate_modifier(
            temperature, rainfall, pet, soil_cover
        )
        
        # Time fraction (monthly = 1/12 year)
        dt = timestep_days / 365.0
        
        # Add organic inputs to DPM and RPM pools
        # Residue splits: 60% DPM, 40% RPM (typical)
        state.dpm += residue_input * 0.6
        state.rpm += residue_input * 0.4
        
        # Manure splits based on type (assume mixed: 40% DPM, 60% RPM)
        state.dpm += manure_input * 0.4
        state.rpm += manure_input * 0.6
        
        # Roots go directly to appropriate pools
        state.dpm += root_input * 0.7
        state.rpm += root_input * 0.3
        
        # Decomposition calculations
        params = self.params
        
        # DPM decomposition
        dpm_decomp = state.dpm * (1 - math.exp(-params.dpm_rate * rate_mod * dt))
        
        # RPM decomposition
        rpm_decomp = state.rpm * (1 - math.exp(-params.rpm_rate * rate_mod * dt))
        
        # BIO decomposition
        bio_decomp = state.bio * (1 - math.exp(-params.bio_rate * rate_mod * dt))
        
        # HUM decomposition
        hum_decomp = state.hum * (1 - math.exp(-params.hum_rate * rate_mod * dt))
        
        # Partitioning of decomposed material
        # From DPM and RPM: goes to BIO, HUM, and CO2
        dpm_rpm_total = dpm_decomp + rpm_decomp
        
        # CO2 emissions
        co2_from_dpm_rpm = dpm_rpm_total * params.co2_fraction
        
        # To biomass
        bio_production = dpm_rpm_total * params.biomass_fraction
        
        # To humus
        hum_production = dpm_rpm_total * params.humification_fraction
        
        # BIO decomposition products
        co2_from_bio = bio_decomp * params.co2_fraction
        hum_from_bio = bio_decomp * (1 - params.co2_fraction)
        
        # HUM decomposition (mostly to CO2)
        co2_from_hum = hum_decomp * 0.8
        
        # Update pools
        state.dpm -= dpm_decomp
        state.rpm -= rpm_decomp
        state.bio = state.bio - bio_decomp + bio_production
        state.hum = state.hum - hum_decomp + hum_production + hum_from_bio
        
        # Total CO2 emitted
        total_co2 = co2_from_dpm_rpm + co2_from_bio + co2_from_hum
        
        # Ensure non-negative pools
        state.dpm = max(0.0, state.dpm)
        state.rpm = max(0.0, state.rpm)
        state.bio = max(0.0, state.bio)
        state.hum = max(0.0, state.hum)
        
        state.update_total()
        
        # Create output
        output = DecompositionOutput(
            timestep=0,  # Will be set by caller
            date=datetime.now(),
            initial_state=initial_state,
            final_state=state,
            co2_emitted=total_co2,
            residue_added=residue_input,
            manure_added=manure_input,
            temperature=temperature,
            rainfall=rainfall,
            evapotranspiration=pet,
            rate_modifier=rate_mod
        )
        
        logger.debug(
            f"Decomposition step: SOC {initial_state.total_soc:.2f} -> "
            f"{state.total_soc:.2f} tC/ha, CO2: {total_co2:.3f} tC/ha"
        )
        
        return output
    
    def simulate(
        self,
        initial_soc: float,
        clay_content: float,
        climate_data: List[Dict[str, float]],
        management_data: List[Dict[str, float]],
        start_year: int = 2020,
        years: int = 30
    ) -> List[DecompositionOutput]:
        """
        Run multi-year decomposition simulation.
        
        Args:
            initial_soc: Initial total SOC (tC/ha)
            clay_content: Clay content (%)
            climate_data: List of monthly climate dicts
            management_data: List of monthly management dicts
            start_year: Starting year
            years: Number of years to simulate
            
        Returns:
            List of decomposition outputs for each timestep
        """
        logger.info(f"Starting {years}-year decomposition simulation")
        
        # Initialize state
        state = self.initialize_state(initial_soc, clay_content)
        
        results = []
        total_months = years * 12
        
        for month_idx in range(total_months):
            # Get climate data (cycle through if shorter than simulation)
            climate_idx = month_idx % len(climate_data)
            climate = climate_data[climate_idx]
            
            # Get management data
            mgmt_idx = month_idx % len(management_data)
            mgmt = management_data[mgmt_idx]
            
            # Calculate year and month
            year = start_year + (month_idx // 12)
            month = (month_idx % 12) + 1
            
            # Perform timestep
            output = self.step(
                state=state,
                temperature=climate.get("temperature", 15.0),
                rainfall=climate.get("rainfall", 50.0),
                pet=climate.get("pet", 80.0),
                residue_input=mgmt.get("residue", 0.0),
                manure_input=mgmt.get("manure", 0.0),
                root_input=mgmt.get("root", 0.0),
                soil_cover=mgmt.get("soil_cover", 1.0),
                timestep_days=30
            )
            
            output.timestep = month_idx
            output.date = datetime(year, month, 15)
            
            results.append(output)
        
        logger.info(f"Simulation complete: {len(results)} timesteps")
        return results


# Import math at module level
import math
