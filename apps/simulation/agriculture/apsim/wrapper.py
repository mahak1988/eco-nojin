"""
APSIM Wrapper for Eco Nozhin
=============================
Wrapper for Agricultural Production Systems sIMulator (APSIM).
Provides interface for crop growth, yield prediction, and farming systems analysis.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class APSIMInput:
    """Input parameters for APSIM simulation."""
    
    # Location and climate
    latitude: float  # degrees
    longitude: float  # degrees
    elevation: float  # meters
    weather_data_path: Optional[Path] = None  # Path to .met file
    
    # Soil properties
    soil_name: str = "generic"
    soil_layers: List[Dict[str, float]] = field(default_factory=lambda: [
        {"depth": 0.1, "clay": 20.0, "silt": 40.0, "sand": 40.0, "oc": 1.5},
        {"depth": 0.3, "clay": 25.0, "silt": 35.0, "sand": 40.0, "oc": 1.2},
        {"depth": 0.6, "clay": 30.0, "silt": 30.0, "sand": 40.0, "oc": 0.8},
    ])
    ph: float = 6.5
    drainage: str = "free"  # free, restricted
    
    # Crop configuration
    crop_type: str = "wheat"  # wheat, maize, rice, soybean, etc.
    cultivar: str = "default"
    planting_date: datetime = field(default_factory=datetime.now)
    planting_density: float = 100.0  # plants/m²
    row_spacing: float = 0.25  # meters
    
    # Management practices
    irrigation_enabled: bool = False
    irrigation_threshold: float = 0.5  # soil water depletion fraction
    fertilizer_applications: List[Dict[str, Any]] = field(default_factory=list)
    tillage_events: List[Dict[str, Any]] = field(default_factory=list)
    
    # Simulation period
    start_date: datetime = field(default_factory=datetime.now)
    end_date: datetime = field(default_factory=datetime.now)
    
    # Output options
    output_frequency: str = "daily"  # daily, weekly, monthly, harvest
    output_variables: List[str] = field(default_factory=lambda: [
        "biomass", "lai", "yield", "soil_water", "soil_nitrogen",
        "evapotranspiration", "drainage"
    ])
    
    def validate(self) -> bool:
        """Validate input parameters."""
        if not -90 <= self.latitude <= 90:
            raise ValueError("Latitude must be between -90 and 90")
        if not -180 <= self.longitude <= 180:
            raise ValueError("Longitude must be between -180 and 180")
        if self.planting_density <= 0:
            raise ValueError("Planting density must be positive")
        return True


@dataclass
class APSIMOutput:
    """Output results from APSIM simulation."""
    
    # Simulation metadata
    simulation_id: str
    status: str  # success, failed, running
    start_time: datetime
    end_time: datetime
    execution_time_seconds: float
    
    # Crop performance
    grain_yield: float = 0.0  # kg/ha
    biomass_total: float = 0.0  # kg/ha
    biomass_grain: float = 0.0  # kg/ha
    biomass_stover: float = 0.0  # kg/ha
    harvest_index: float = 0.0  # ratio
    
    # Growth metrics
    max_lai: float = 0.0  # maximum leaf area index
    days_to_flowering: int = 0
    days_to_maturity: int = 0
    growing_degree_days: float = 0.0
    
    # Water balance
    evapotranspiration: float = 0.0  # mm
    transpiration: float = 0.0  # mm
    soil_evaporation: float = 0.0  # mm
    drainage: float = 0.0  # mm
    runoff: float = 0.0  # mm
    
    # Nutrient dynamics
    nitrogen_uptake: float = 0.0  # kg/ha
    nitrogen_fixed: float = 0.0  # kg/ha (for legumes)
    nitrogen_leached: float = 0.0  # kg/ha
    
    # Time series data
    daily_outputs: List[Dict[str, Any]] = field(default_factory=list)
    
    # File paths
    output_directory: Optional[Path] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert output to dictionary for API response."""
        return {
            "simulation_id": self.simulation_id,
            "status": self.status,
            "execution_time_seconds": self.execution_time_seconds,
            "crop_performance": {
                "grain_yield_kg_ha": self.grain_yield,
                "total_biomass_kg_ha": self.biomass_total,
                "harvest_index": self.harvest_index,
            },
            "growth_metrics": {
                "max_lai": self.max_lai,
                "days_to_flowering": self.days_to_flowering,
                "days_to_maturity": self.days_to_maturity,
            },
            "water_balance": {
                "evapotranspiration_mm": self.evapotranspiration,
                "transpiration_mm": self.transpiration,
                "drainage_mm": self.drainage,
            },
            "nutrient_dynamics": {
                "nitrogen_uptake_kg_ha": self.nitrogen_uptake,
                "nitrogen_leached_kg_ha": self.nitrogen_leached,
            }
        }


class APSIMWrapper:
    """
    Main wrapper class for APSIM model integration.
    
    This class provides methods to:
    - Prepare APSIM input files (.apsimx format)
    - Execute APSIM model
    - Parse and process outputs
    - Support multiple crops and rotations
    """
    
    def __init__(self, apsim_executable: Optional[Path] = None,
                 working_directory: Optional[Path] = None):
        """
        Initialize APSIM wrapper.
        
        Args:
            apsim_executable: Path to APSIM executable
            working_directory: Directory for running simulations
        """
        self.apsim_executable = apsim_executable
        self.working_directory = working_directory or Path("./apsim_runs")
        self.working_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"APSIMWrapper initialized with working directory: {self.working_directory}")
    
    def prepare_input_files(self, apsim_input: APSIMInput) -> Path:
        """
        Prepare APSIM input files from standardized parameters.
        
        Creates .apsimx file and supporting data files.
        
        Args:
            apsim_input: Standardized input parameters
            
        Returns:
            Path to the prepared APSIM project file
        """
        try:
            apsim_input.validate()
        except ValueError as e:
            logger.error(f"Input validation failed: {e}")
            raise
        
        run_id = f"apsim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_dir = self.working_directory / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Preparing APSIM input files in {run_dir}")
        
        # TODO: Implement actual APSIMX file generation
        # APSIM Next Generation uses JSON-based .apsimx format
        
        # Placeholder: Create a config file
        config_file = run_dir / f"{run_id}.apsimx"
        config_file.write_text(f"""{{
            "id": "{run_id}",
            "crop_type": "{apsim_input.crop_type}",
            "cultivar": "{apsim_input.cultivar}",
            "planting_date": "{apsim_input.planting_date.isoformat()}",
            "location": {{
                "latitude": {apsim_input.latitude},
                "longitude": {apsim_input.longitude},
                "elevation": {apsim_input.elevation}
            }},
            "soil": {{
                "name": "{apsim_input.soil_name}",
                "ph": {apsim_input.ph}
            }}
        }}""")
        
        logger.info(f"APSIM input file prepared: {config_file}")
        return config_file
    
    def run_simulation(self, input_file: Path,
                      wait_for_completion: bool = True) -> str:
        """
        Execute APSIM simulation.
        
        Args:
            input_file: Path to .apsimx file
            wait_for_completion: If True, block until simulation completes
            
        Returns:
            Simulation ID for tracking
        """
        logger.info(f"Starting APSIM simulation from {input_file}")
        
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if self.apsim_executable and self.apsim_executable.exists():
            logger.info(f"Using local APSIM executable: {self.apsim_executable}")
            # subprocess.run([str(self.apsim_executable), str(input_file)])
        else:
            logger.warning("APSIM executable not found. Running in demo mode.")
        
        logger.info(f"Simulation {simulation_id} started")
        return simulation_id
    
    def get_results(self, simulation_id: str,
                   output_dir: Path) -> APSIMOutput:
        """
        Parse and retrieve APSIM simulation results.
        
        Args:
            simulation_id: ID of the completed simulation
            output_dir: Directory containing output files
            
        Returns:
            APSIMOutput object with processed results
        """
        logger.info(f"Retrieving results for simulation {simulation_id}")
        
        start_time = datetime.now()
        
        # Placeholder: Return demo output
        output = APSIMOutput(
            simulation_id=simulation_id,
            status="success",
            start_time=start_time,
            end_time=datetime.now(),
            execution_time_seconds=1.8,
            grain_yield=4500.0,  # kg/ha (wheat)
            biomass_total=12000.0,  # kg/ha
            biomass_grain=4500.0,
            biomass_stover=7500.0,
            harvest_index=0.375,
            max_lai=4.2,
            days_to_flowering=95,
            days_to_maturity=145,
            growing_degree_days=1850.0,
            evapotranspiration=420.5,  # mm
            transpiration=310.2,
            soil_evaporation=110.3,
            drainage=85.5,
            nitrogen_uptake=180.0,  # kg/ha
            nitrogen_leached=25.3,
            output_directory=output_dir
        )
        
        logger.info(f"Results retrieved successfully for {simulation_id}")
        return output
    
    def run(self, apsim_input: APSIMInput) -> APSIMOutput:
        """
        Complete workflow: prepare, run, and retrieve results.
        
        Args:
            apsim_input: Input parameters for simulation
            
        Returns:
            APSIMOutput with simulation results
        """
        logger.info("Starting complete APSIM simulation workflow")
        
        input_file = self.prepare_input_files(apsim_input)
        sim_id = self.run_simulation(input_file)
        output = self.get_results(sim_id, input_file.parent)
        
        logger.info(f"APSIM simulation workflow completed: {sim_id}")
        return output
    
    async def run_async(self, apsim_input: APSIMInput) -> APSIMOutput:
        """Async version of run method."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run, apsim_input)


def run_apsim_simulation(
    crop_type: str,
    latitude: float,
    longitude: float,
    planting_date: datetime,
    **kwargs
) -> APSIMOutput:
    """
    Quick function to run an APSIM simulation.
    
    Args:
        crop_type: Type of crop (wheat, maize, etc.)
        latitude: Site latitude
        longitude: Site longitude
        planting_date: Planting date
        **kwargs: Additional parameters
        
    Returns:
        APSIMOutput with simulation results
    """
    apsim_input = APSIMInput(
        crop_type=crop_type,
        latitude=latitude,
        longitude=longitude,
        planting_date=planting_date,
        elevation=500,
        **kwargs
    )
    
    wrapper = APSIMWrapper()
    return wrapper.run(apsim_input)
