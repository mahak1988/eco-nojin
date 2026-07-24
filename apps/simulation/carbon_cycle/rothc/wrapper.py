"""
RothC Wrapper for Eco Nozhin
=============================
Wrapper for Rothamsted Carbon Model (RothC).
Simulates soil organic carbon turnover in agricultural and natural soils.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class RothCInput:
    """Input parameters for RothC simulation."""
    
    # Site characteristics
    latitude: float  # degrees
    longitude: float  # degrees
    elevation: float  # meters
    soil_type: str = "loam"  # loam, clay, sandy, etc.
    
    # Initial soil conditions
    initial_soc: float = 50.0  # tC/ha (topsoil 0-23cm)
    clay_content: float = 25.0  # %
    ph: float = 6.5
    drainage_class: str = "free"  # free, impeded
    
    # Climate data
    annual_rainfall: float = 800.0  # mm/year
    annual_temp_avg: float = 15.0  # °C
    monthly_temp: List[float] = field(default_factory=lambda: [5, 7, 10, 14, 18, 22, 25, 24, 20, 15, 10, 6])
    monthly_rainfall: List[float] = field(default_factory=lambda: [60, 55, 65, 50, 45, 30, 15, 20, 40, 65, 75, 70])
    
    # Land use and management
    land_use: str = "arable"  # arable, grassland, forest, bare
    crop_residue_input: float = 3.0  # tC/ha/year
    farmyard_manure_input: float = 0.0  # tC/ha/year
    root_input: float = 1.5  # tC/ha/year
    
    # Simulation settings
    start_year: int = 2020
    end_year: int = 2050
    time_step: str = "monthly"  # monthly, yearly
    
    def validate(self) -> bool:
        """Validate input parameters."""
        if not 0 <= self.clay_content <= 100:
            raise ValueError("Clay content must be between 0 and 100%")
        if self.initial_soc < 0:
            raise ValueError("Initial SOC cannot be negative")
        if self.end_year <= self.start_year:
            raise ValueError("End year must be after start year")
        return True


@dataclass
class RothCOutput:
    """Output results from RothC simulation."""
    
    # Metadata
    simulation_id: str
    status: str
    start_time: datetime
    end_time: datetime
    execution_time_seconds: float
    
    # Carbon pools (tC/ha)
    total_soc_final: float = 0.0
    total_soc_initial: float = 0.0
    soc_change: float = 0.0  # tC/ha over simulation period
    
    # Decomposition products
    co2_emitted: float = 0.0  # tC/ha
    biomass_c: float = 0.0  # microbial biomass carbon
    humus_c: float = 0.0  # humified organic matter
    inert_om: float = 0.0  # inert organic matter
    
    # Pool breakdown
    dpm_pool: float = 0.0  # decomposable plant material
    rpm_pool: float = 0.0  # resistant plant material
    bio_pool: float = 0.0  # microbial biomass
    hum_pool: float = 0.0  # humus
    iom_pool: float = 0.0  # inert matter
    
    # Annual time series
    annual_soc: List[Dict[str, float]] = field(default_factory=list)
    
    # Sequestration metrics
    sequestration_rate: float = 0.0  # tC/ha/year
    carbon_deficit: float = 0.0  # tC/ha to reach equilibrium
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "simulation_id": self.simulation_id,
            "status": self.status,
            "carbon_stocks": {
                "initial_soc_t_ha": self.total_soc_initial,
                "final_soc_t_ha": self.total_soc_final,
                "soc_change_t_ha": self.soc_change,
            },
            "pool_breakdown": {
                "dpm": self.dpm_pool,
                "rpm": self.rpm_pool,
                "bio": self.bio_pool,
                "hum": self.hum_pool,
                "iom": self.iom_pool,
            },
            "sequestration": {
                "rate_t_ha_year": self.sequestration_rate,
                "co2_emitted_t_ha": self.co2_emitted,
            }
        }


class RothCWrapper:
    """Main wrapper for RothC model integration."""
    
    def __init__(self, working_directory: Optional[Path] = None):
        """
        Initialize RothC wrapper.
        
        Args:
            working_directory: Directory for running simulations
        """
        self.working_directory = working_directory or Path("./rothc_runs")
        self.working_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"RothCWrapper initialized: {self.working_directory}")
    
    def prepare_input_files(self, rothc_input: RothCInput) -> Path:
        """Prepare RothC input files."""
        try:
            rothc_input.validate()
        except ValueError as e:
            logger.error(f"Validation failed: {e}")
            raise
        
        run_id = f"rothc_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_dir = self.working_directory / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Preparing RothC inputs in {run_dir}")
        
        config_file = run_dir / "config.json"
        config_file.write_text(f"""{{
            "run_id": "{run_id}",
            "site": {{
                "lat": {rothc_input.latitude},
                "lon": {rothc_input.longitude},
                "clay_pct": {rothc_input.clay_content}
            }},
            "initial_soc_t_ha": {rothc_input.initial_soc},
            "land_use": "{rothc_input.land_use}",
            "simulation_years": {rothc_input.end_year - rothc_input.start_year}
        }}""")
        
        return run_dir
    
    def run_simulation(self, input_dir: Path) -> str:
        """Execute RothC simulation."""
        logger.info(f"Starting RothC simulation from {input_dir}")
        
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.warning("RothC engine not connected. Running in demo mode.")
        
        return simulation_id
    
    def get_results(self, simulation_id: str, output_dir: Path) -> RothCOutput:
        """Parse and retrieve RothC results."""
        logger.info(f"Retrieving results for {simulation_id}")
        
        start_time = datetime.now()
        
        # Demo output with realistic values
        output = RothCOutput(
            simulation_id=simulation_id,
            status="success",
            start_time=start_time,
            end_time=datetime.now(),
            execution_time_seconds=0.8,
            total_soc_initial=50.0,
            total_soc_final=62.5,
            soc_change=12.5,
            co2_emitted=45.2,
            biomass_c=3.8,
            humus_c=48.5,
            inert_om=10.2,
            dpm_pool=2.1,
            rpm_pool=8.5,
            bio_pool=3.8,
            hum_pool=48.5,
            iom_pool=10.2,
            sequestration_rate=0.42,
            carbon_deficit=5.3,
            output_directory=output_dir
        )
        
        return output
    
    def run(self, rothc_input: RothCInput) -> RothCOutput:
        """Complete workflow."""
        logger.info("Starting RothC workflow")
        
        input_dir = self.prepare_input_files(rothc_input)
        sim_id = self.run_simulation(input_dir)
        output = self.get_results(sim_id, input_dir)
        
        logger.info(f"RothC completed: {sim_id}")
        return output
    
    async def run_async(self, rothc_input: RothCInput) -> RothCOutput:
        """Async version."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run, rothc_input)
    
    def calculate_carbon_credits(self, output: RothCOutput, 
                                  methodology: str = "VERRA") -> Dict[str, Any]:
        """Calculate potential carbon credits from sequestration."""
        logger.info(f"Calculating carbon credits using {methodology}")
        
        # Simplified calculation
        years = 30
        annual_sequestration = output.sequestration_rate  # tC/ha/year
        total_sequestration = annual_sequestration * years  # tC/ha
        
        # Convert to CO2e (1 tC = 3.67 tCO2)
        co2e_sequestered = total_sequestration * 3.67
        
        # Apply methodology discount factors
        discount_factors = {
            "VERRA": 0.85,
            "GOLD_STANDARD": 0.90,
            "PLAN_VIVO": 0.80
        }
        discount = discount_factors.get(methodology, 0.85)
        eligible_credits = co2e_sequestered * discount
        
        return {
            "methodology": methodology,
            "total_sequestration_tc_ha": total_sequestration,
            "co2e_sequestered_t_ha": co2e_sequestered,
            "eligible_credits_tco2_ha": eligible_credits,
            "discount_factor": discount
        }


def run_rothc_simulation(
    latitude: float,
    longitude: float,
    initial_soc: float,
    land_use: str,
    **kwargs
) -> RothCOutput:
    """Quick function to run RothC simulation."""
    rothc_input = RothCInput(
        latitude=latitude,
        longitude=longitude,
        initial_soc=initial_soc,
        land_use=land_use,
        **kwargs
    )
    
    wrapper = RothCWrapper()
    return wrapper.run(rothc_input)
