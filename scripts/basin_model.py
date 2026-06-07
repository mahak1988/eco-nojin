"""
Basin Hydrology Model Interface
================================
Abstract base class for distributed hydrological models.
Supports wflow, GR4J, and other open-source models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import xarray as xr


@dataclass
class BasinConfig:
    """Configuration for basin hydrology model"""

    basin_id: str
    dem_path: str  # DEM file path
    soil_path: str  # Soil properties file
    landcover_path: str  # Land cover file
    climate_source: str  # 'era5', 'chirps', etc.
    start_date: str
    end_date: str
    timestep: str = "1D"  # '1H', '1D', '1M'

    # Model parameters
    model_type: str = "wflow"  # 'wflow', 'gr4j', 'hbv'
    calibration_params: Optional[Dict] = None


@dataclass
class HydrologyOutput:
    """Standardized output from hydrology model"""

    basin_id: str
    model_type: str
    start_date: str
    end_date: str

    # Time series outputs
    discharge: np.ndarray  # m³/s
    evapotranspiration: np.ndarray  # mm/day
    soil_moisture: np.ndarray  # mm
    snow_storage: Optional[np.ndarray] = None

    # Spatial outputs (if distributed)
    spatial_outputs: Optional[Dict[str, xr.DataArray]] = None

    # Metrics
    metrics: Dict[str, float] = None  # NSE, PBIAS, RMSE, etc.


class BasinModel(ABC):
    """Abstract base class for basin hydrology models"""

    @abstractmethod
    def setup(self, config: BasinConfig) -> None:
        """Prepare model with input data and parameters"""
        pass

    @abstractmethod
    def run(self) -> HydrologyOutput:
        """Execute model simulation"""
        pass

    @abstractmethod
    def calibrate(
        self, observed_discharge: np.ndarray, param_bounds: Dict[str, tuple], metric: str = "NSE"
    ) -> Dict[str, float]:
        """Calibrate model parameters against observations"""
        pass

    @abstractmethod
    def get_spatial_output(self, variable: str) -> xr.DataArray:
        """Get spatial output for a specific variable"""
        pass


class WflowModel(BasinModel):
    """
    Implementation of wflow distributed hydrological model.

    wflow is an open-source, Python-based distributed hydrological model
    that simulates water balance components at catchment scale.

    References:
    - https://deltares.github.io/wflow/
    - https://github.com/Deltares/wflow
    """

    def __init__(self):
        self.config: Optional[BasinConfig] = None
        self.model = None  # wflow model instance
        self.results: Optional[HydrologyOutput] = None

    def setup(self, config: BasinConfig) -> None:
        """Setup wflow model using HydroMT for automated configuration"""
        self.config = config

        try:
            from hydromt.data_catalog import DataCatalog
            from hydromt_wflow import WflowModel as HydroMTWflow

            # Initialize data catalog with open data sources
            data_catalog = DataCatalog(data_libs=["artifact_data"])

            # Build model from static and dynamic data
            self.model = HydroMTWflow(
                root=config.dem_path.replace("/dem.nc", ""),
                mode="w",
                data_libs=["wflow", "artifact_data"],
            )

            # Setup model geometry from DEM
            self.model.setup_basemaps(
                basin_idx=config.basin_id,
                hydrography_fn="merit_hydro",
                basin_index_fn="merit_hydro_index",
            )

            # Add static maps (soil, landcover)
            self.model.setup_soilmaps(soilgrids_fn="soilgrids")
            self.model.setup_landuse(landuse_fn="globcover")

            # Add climate forcing
            self.model.setup_precip_forcing(precip_fn=config.climate_source)
            self.model.setup_temp_forcing(temp_fn="era5")

            # Set model parameters
            if config.calibration_params:
                self.model.set_config(config.calibration_params)

        except ImportError:
            print_warning("wflow/hydromt not installed. Using fallback GR4J model.")
            # Fallback to simpler GR4J implementation
            self._setup_gr4j_fallback(config)

    def _setup_gr4j_fallback(self, config: BasinConfig) -> None:
        """Fallback setup using GR4J conceptual model"""
        from .gr4j_model import GR4JModel

        self.model = GR4JModel(x1=300, x2=0.5, x3=20, x4=1.5)  # Default GR4J parameters
        self.config = config

    def run(self) -> HydrologyOutput:
        """Run the hydrology simulation"""
        if self.model is None:
            raise RuntimeError("Model not setup. Call setup() first.")

        # Run wflow or fallback GR4J
        if hasattr(self.model, "run_model"):
            # wflow execution
            self.model.run_model()
            results = self.model.results
        else:
            # GR4J fallback
            results = self.model.run(
                precip=self._load_precip(),
                pet=self._load_pet(),
                start_date=self.config.start_date,
                end_date=self.config.end_date,
            )

        return HydrologyOutput(
            basin_id=self.config.basin_id,
            model_type=self.config.model_type,
            start_date=self.config.start_date,
            end_date=self.config.end_date,
            discharge=results.get("discharge", np.array([])),
            evapotranspiration=results.get("et", np.array([])),
            soil_moisture=results.get("soil_moisture", np.array([])),
            metrics=results.get("metrics", {}),
        )

    def calibrate(self, observed_discharge, param_bounds, metric="NSE"):
        """Calibrate model using scipy optimization"""
        from scipy.optimize import differential_evolution

        def objective(params):
            # Update model parameters
            self.model.update_parameters(dict(zip(param_bounds.keys(), params)))

            # Run model
            output = self.run()

            # Calculate metric
            if metric == "NSE":
                return -self._calculate_nse(output.discharge, observed_discharge)
            elif metric == "RMSE":
                return self._calculate_rmse(output.discharge, observed_discharge)
            else:
                return -self._calculate_nse(output.discharge, observed_discharge)

        # Run optimization
        bounds = list(param_bounds.values())
        result = differential_evolution(objective, bounds, maxiter=100)

        return dict(zip(param_bounds.keys(), result.x))

    def _calculate_nse(self, simulated, observed):
        """Calculate Nash-Sutcliffe Efficiency"""
        obs_mean = np.mean(observed)
        return 1 - np.sum((simulated - observed) ** 2) / np.sum((observed - obs_mean) ** 2)

    def _calculate_rmse(self, simulated, observed):
        """Calculate Root Mean Square Error"""
        return np.sqrt(np.mean((simulated - observed) ** 2))

    def _load_precip(self):
        """Load precipitation data from configured source"""
        # Implementation depends on climate_source
        pass

    def _load_pet(self):
        """Load potential evapotranspiration"""
        pass

    def get_spatial_output(self, variable: str):
        """Get spatial output raster"""
        if self.model and hasattr(self.model, "results"):
            return self.model.results.get(variable)
        return None
