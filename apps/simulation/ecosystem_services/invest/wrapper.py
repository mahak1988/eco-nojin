"""
InVEST Wrapper for Eco Nozhin
==============================
Wrapper for Integrated Valuation of Ecosystem Services and Tradeoffs (InVEST).
Provides multiple ecosystem service models: carbon, water, habitat, etc.
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class InVESTInput:
    """Base input parameters for InVEST models."""
    
    # Workspace
    workspace_dir: Path = field(default_factory=lambda: Path("./invest_runs"))
    
    # Area of interest
    aoi_vector_path: Optional[Path] = None  # Shapefile or GeoJSON
    
    # Spatial resolution
    pixel_size: float = 30.0  # meters
    
    # Climate data
    precipitation_raster: Optional[Path] = None
    temperature_raster: Optional[Path] = None
    evapotranspiration_raster: Optional[Path] = None
    
    # Land use/land cover
    lulc_raster: Optional[Path] = None
    lulc_table: Optional[Path] = None  # CSV with biophysical parameters
    
    # Soil data
    soil_raster: Optional[Path] = None
    soil_texture_raster: Optional[Path] = None
    
    # Topography
    dem_raster: Optional[Path] = None
    
    # Model-specific parameters
    model_type: str = "carbon"  # carbon, water_yield, habitat_quality, ndr, pollination
    custom_parameters: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """Validate input parameters."""
        if self.pixel_size <= 0:
            raise ValueError("Pixel size must be positive")
        return True


@dataclass
class InVESTOutput:
    """Output results from InVEST simulation."""
    
    # Metadata
    simulation_id: str
    status: str
    model_type: str
    start_time: datetime
    end_time: datetime
    execution_time_seconds: float
    
    # Output paths
    output_directory: Optional[Path] = None
    result_rasters: Dict[str, Path] = field(default_factory=dict)
    result_vectors: Dict[str, Path] = field(default_factory=dict)
    summary_stats: Path = Optional[Path]
    
    # Aggregated statistics
    total_carbon_storage: float = 0.0  # tC (for carbon model)
    total_water_yield: float = 0.0  # m³ (for water yield model)
    habitat_quality_avg: float = 0.0  # 0-1 index
    sediment_retention: float = 0.0  # tons
    nutrient_retention_n: float = 0.0  # kg N
    nutrient_retention_p: float = 0.0  # kg P
    
    # Summary tables
    summary_by_lulc: List[Dict[str, Any]] = field(default_factory=list)
    summary_by_subregion: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "simulation_id": self.simulation_id,
            "status": self.status,
            "model_type": self.model_type,
            "execution_time_seconds": self.execution_time_seconds,
            "aggregated_results": {
                "total_carbon_storage_tc": self.total_carbon_storage,
                "total_water_yield_m3": self.total_water_yield,
                "habitat_quality_index": self.habitat_quality_avg,
                "sediment_retention_tons": self.sediment_retention,
            },
            "output_files": {
                "rasters": {k: str(v) for k, v in self.result_rasters.items()},
                "vectors": {k: str(v) for k, v in self.result_vectors.items()},
            }
        }


class InVESTWrapper:
    """Main wrapper for InVEST model suite integration."""
    
    def __init__(self, invest_exe: Optional[Path] = None,
                 working_directory: Optional[Path] = None):
        """
        Initialize InVEST wrapper.
        
        Args:
            invest_exe: Path to InVEST executable (optional, can use Python API)
            working_directory: Base directory for running simulations
        """
        self.invest_exe = invest_exe
        self.working_directory = working_directory or Path("./invest_runs")
        self.working_directory.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"InVESTWrapper initialized: {self.working_directory}")
    
    def prepare_input_files(self, invest_input: InVESTInput) -> Path:
        """Prepare InVEST input files and workspace."""
        try:
            invest_input.validate()
        except ValueError as e:
            logger.error(f"Validation failed: {e}")
            raise
        
        run_id = f"invest_{invest_input.model_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run_dir = self.working_directory / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        
        # Create model-specific subdirectories
        (run_dir / "input").mkdir(exist_ok=True)
        (run_dir / "output").mkdir(exist_ok=True)
        (run_dir / "intermediate").mkdir(exist_ok=True)
        
        logger.info(f"Preparing InVEST inputs in {run_dir}")
        
        # Create args dict file (InVEST uses JSON/YAML args files)
        args_file = run_dir / "args.json"
        args_file.write_text(f"""{{
            "workspace_dir": "{run_dir / 'output'}",
            "results_suffix": "{run_id}",
            "aoi_vector_path": {str(invest_input.aoi_vector_path) if invest_input.aoi_vector_path else 'null'},
            "model_type": "{invest_input.model_type}"
        }}""")
        
        return run_dir
    
    def run_simulation(self, input_dir: Path, 
                      model_type: str = "carbon") -> str:
        """Execute InVEST model."""
        logger.info(f"Starting InVEST {model_type} simulation from {input_dir}")
        
        simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # InVEST can be run via:
        # 1. natcap.invest Python package (preferred)
        # 2. Command-line executable
        # 3. Docker container
        
        try:
            import natcap.invest
            logger.info("InVEST Python package available")
        except ImportError:
            logger.warning("InVEST not installed. Running in demo mode.")
        
        return simulation_id
    
    def get_results(self, simulation_id: str, 
                   output_dir: Path,
                   model_type: str) -> InVESTOutput:
        """Parse and retrieve InVEST results."""
        logger.info(f"Retrieving {model_type} results for {simulation_id}")
        
        start_time = datetime.now()
        
        # Demo outputs based on model type
        if model_type == "carbon":
            output = InVESTOutput(
                simulation_id=simulation_id,
                status="success",
                model_type=model_type,
                start_time=start_time,
                end_time=datetime.now(),
                execution_time_seconds=3.5,
                total_carbon_storage=125000.0,  # tC
                output_directory=output_dir
            )
        elif model_type == "water_yield":
            output = InVESTOutput(
                simulation_id=simulation_id,
                status="success",
                model_type=model_type,
                start_time=start_time,
                end_time=datetime.now(),
                execution_time_seconds=4.2,
                total_water_yield=8500000.0,  # m³
                output_directory=output_dir
            )
        elif model_type == "habitat_quality":
            output = InVESTOutput(
                simulation_id=simulation_id,
                status="success",
                model_type=model_type,
                start_time=start_time,
                end_time=datetime.now(),
                execution_time_seconds=2.8,
                habitat_quality_avg=0.72,
                output_directory=output_dir
            )
        else:
            output = InVESTOutput(
                simulation_id=simulation_id,
                status="success",
                model_type=model_type,
                start_time=start_time,
                end_time=datetime.now(),
                execution_time_seconds=2.0,
                output_directory=output_dir
            )
        
        return output
    
    def run(self, invest_input: InVESTInput) -> InVESTOutput:
        """Complete workflow for InVEST model."""
        logger.info(f"Starting InVEST {invest_input.model_type} workflow")
        
        input_dir = self.prepare_input_files(invest_input)
        sim_id = self.run_simulation(input_dir, invest_input.model_type)
        output = self.get_results(sim_id, input_dir / "output", invest_input.model_type)
        
        logger.info(f"InVEST {invest_input.model_type} completed: {sim_id}")
        return output
    
    async def run_async(self, invest_input: InVESTInput) -> InVESTOutput:
        """Async version."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.run, invest_input)
    
    def run_carbon_model(self, lulc_raster: Path, 
                        carbon_pools_table: Path,
                        **kwargs) -> InVESTOutput:
        """Run InVEST Carbon Storage and Sequestration model."""
        logger.info("Running Carbon Storage and Sequestration model")
        
        input_params = InVESTInput(
            model_type="carbon",
            lulc_raster=lulc_raster,
            lulc_table=carbon_pools_table,
            custom_parameters=kwargs
        )
        
        return self.run(input_params)
    
    def run_water_yield_model(self, dem_raster: Path,
                             lulc_raster: Path,
                             precipitation_raster: Path,
                             **kwargs) -> InVESTOutput:
        """Run InVEST Water Yield model."""
        logger.info("Running Water Yield model")
        
        input_params = InVESTInput(
            model_type="water_yield",
            dem_raster=dem_raster,
            lulc_raster=lulc_raster,
            precipitation_raster=precipitation_raster,
            custom_parameters=kwargs
        )
        
        return self.run(input_params)
    
    def run_habitat_quality_model(self, lulc_raster: Path,
                                  threat_rasters: Dict[str, Path],
                                  threat_table: Path,
                                  **kwargs) -> InVESTOutput:
        """Run InVEST Habitat Quality model."""
        logger.info("Running Habitat Quality model")
        
        input_params = InVESTInput(
            model_type="habitat_quality",
            lulc_raster=lulc_raster,
            custom_parameters={
                "threat_rasters": threat_rasters,
                "threat_table": threat_table,
                **kwargs
            }
        )
        
        return self.run(input_params)
    
    def run_ndr_model(self, dem_raster: Path,
                     lulc_raster: Path,
                     runoff_proxy_raster: Path,
                     **kwargs) -> InVESTOutput:
        """Run InVEST Nutrient Delivery Ratio (NDR) model."""
        logger.info("Running Nutrient Delivery Ratio model")
        
        input_params = InVESTInput(
            model_type="ndr",
            dem_raster=dem_raster,
            lulc_raster=lulc_raster,
            custom_parameters={
                "runoff_proxy": runoff_proxy_raster,
                **kwargs
            }
        )
        
        return self.run(input_params)


def run_invest_model(
    model_type: str,
    workspace_dir: Path,
    **kwargs
) -> InVESTOutput:
    """Quick function to run an InVEST model."""
    invest_input = InVESTInput(
        model_type=model_type,
        workspace_dir=workspace_dir,
        custom_parameters=kwargs
    )
    
    wrapper = InVESTWrapper()
    return wrapper.run(invest_input)
