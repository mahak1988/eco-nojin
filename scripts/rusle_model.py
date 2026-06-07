"""
RUSLE Erosion Model with GIS Integration
========================================
Revised Universal Soil Loss Equation implementation using open-source GIS.
Calculates spatial erosion risk using R, K, LS, C, P factors.

Reference: Renard et al. (1997), "Predicting soil erosion by water"
"""

import numpy as np
import xarray as xr

try:
    import rioxarray as rxr

    GIS_AVAILABLE = True
except ImportError:
    GIS_AVAILABLE = False
import warnings
from pathlib import Path
from typing import Dict, Optional, Tuple

# Optional GIS dependencies
try:
    import geopandas as gpd
    from rasterio import features

    GIS_AVAILABLE = True
except ImportError:
    GIS_AVAILABLE = False
    warnings.warn("GIS packages not installed. Using array-based RUSLE only.")


class RUSLEFactors:
    """Calculate individual RUSLE factors from open data"""

    @staticmethod
    def calculate_r_factor(
        precip_data: xr.DataArray, method: str = "arnoldus"  # Monthly precipitation [mm]
    ) -> xr.DataArray:
        """
        Calculate rainfall erosivity factor R [MJ mm / ha h yr].

        Parameters:
        -----------
        precip_data : xr.DataArray
            Monthly precipitation with dimensions (time, lat, lon)
        method : str
            Calculation method: 'arnoldus', 'yu_rosewell', or 'simple'

        Returns:
        --------
        r_factor : xr.DataArray
            R factor map [MJ mm / ha h yr]
        """
        if method == "arnoldus":
            # Arnoldus (1977) method for monthly data
            # R = sum(1.735 * 10^(1.5*log10(Pi^2/P) - 0.8188))
            monthly = precip_data
            annual = monthly.sum(dim="time")

            r_monthly = 1.735 * 10 ** (1.5 * np.log10(monthly**2 / annual) - 0.8188)
            return r_monthly.sum(dim="time").clip(0)

        elif method == "yu_rosewell":
            # Yu & Rosewell (1996) for daily data
            # R = alpha * sum(Pi^1.5) where Pi is daily rainfall
            daily = precip_data
            return (1.5 * (daily**1.5)).sum(dim="time") * 0.394

        else:  # simple
            # Simplified: R = 0.01 * P^1.5 where P is annual precip
            annual = precip_data.sum(dim="time")
            return 0.01 * annual**1.5

    @staticmethod
    def calculate_k_factor(
        soil_data: xr.Dataset, method: str = "erosion_nomograph"  # From SoilGrids
    ) -> xr.DataArray:
        """
        Calculate soil erodibility factor K [t ha h / ha MJ mm].

        Parameters:
        -----------
        soil_data : xr.Dataset
            Soil properties: sand, silt, clay, soc, coarse_fragments
        method : str
            Calculation method

        Returns:
        --------
        k_factor : xr.DataArray
            K factor map
        """
        # Extract soil properties (convert to % if needed)
        sand = soil_data["sand_percent"]  # %
        silt = soil_data["silt_percent"]  # %
        clay = soil_data["clay_percent"]  # %
        soc = soil_data["soc_percent"]  # %

        if method == "erosion_nomograph":
            # Wischmeier & Smith (1978) nomograph equation
            # Simplified for Python implementation

            # Calculate M parameter (% silt + very fine sand) * (100 - % clay)
            m = (silt + sand * 0.1) * (100 - clay)

            # K calculation
            k = (
                2.1e-4 * m**1.14 * (12 - soc)
                + 3.25 * (2 - soil_structure_code)
                + 2.5 * (permeability_code - 3)
            ) / 100

            # Convert to SI units if needed
            return k.clip(0, 0.7)

        else:  # simplified
            # Simplified: K decreases with SOC and clay
            k_base = 0.3
            k_soc = 1 - soc / 10  # SOC reduces erodibility
            k_clay = 1 - clay / 50  # Clay reduces erodibility
            return k_base * k_soc * k_clay

    @staticmethod
    def calculate_ls_factor(
        dem: xr.DataArray,  # Digital elevation model [m]
        resolution_m: float,  # Pixel resolution [m]
        method: str = "desmet_govers",
    ) -> xr.DataArray:
        """
        Calculate slope length-steepness factor LS.

        Parameters:
        -----------
        dem : xr.DataArray
            Digital elevation model
        resolution_m : float
            Spatial resolution [m]
        method : str
            Calculation method

        Returns:
        --------
        ls_factor : xr.DataArray
            LS factor map (dimensionless)
        """
        # Calculate slope in degrees
        dy, dx = np.gradient(dem.values, resolution_m)
        slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
        slope_deg = np.degrees(slope_rad)

        if method == "desmet_govers":
            # Desmet & Govers (1996) for complex terrain

            # Calculate flow accumulation (simplified)
            flow_dir = _calculate_flow_direction(dem)
            flow_acc = _calculate_flow_accumulation(flow_dir)

            # Slope length lambda
            lambda_val = flow_acc * resolution_m

            # Exponent m based on slope
            beta = (np.sin(slope_rad) / 0.0896) / (3 * np.sin(slope_rad) ** 0.8 + 0.56)
            m = beta / (1 + beta)

            # LS calculation
            ls = (lambda_val / 22.13) ** m * (
                65.41 * np.sin(slope_rad) ** 2 + 4.56 * np.sin(slope_rad) + 0.065
            )

            return xr.DataArray(ls, coords=dem.coords, dims=dem.dims)

        else:  # mccool
            # McCool et al. (1993) for rangeland
            slope_percent = np.tan(slope_rad) * 100

            # S factor (steepness)
            if slope_percent < 9:
                s = 10.8 * np.sin(slope_rad) + 0.03
            else:
                s = 16.8 * np.sin(slope_rad) - 0.50

            # L factor (length) - simplified
            l = (22.13 / resolution_m) ** 0.4

            return xr.DataArray(l * s, coords=dem.coords, dims=dem.dims)

    @staticmethod
    def calculate_c_factor(
        landcover: xr.DataArray,
        ndvi: Optional[xr.DataArray] = None,
        crop_type: Optional[str] = None,
    ) -> xr.DataArray:
        """
        Calculate cover-management factor C.

        Parameters:
        -----------
        landcover : xr.DataArray
            Land cover classification
        ndvi : xr.DataArray, optional
            NDVI for dynamic C factor
        crop_type : str, optional
            Specific crop for agricultural C factor

        Returns:
        --------
        c_factor : xr.DataArray
            C factor map (0-1, lower = better protection)
        """
        # Default C values by land cover class
        c_defaults = {
            "forest": 0.01,
            "grassland": 0.05,
            "cropland": 0.3,
            "bare_soil": 0.8,
            "urban": 0.01,
            "water": 0.0,
        }

        if ndvi is not None:
            # Dynamic C factor based on NDVI
            # C = exp(-alpha * NDVI / (beta - NDVI))
            alpha, beta = 2.0, 1.0
            c_dynamic = np.exp(-alpha * ndvi / (beta - ndvi + 1e-6))
            return c_dynamic.clip(0.01, 1.0)

        elif crop_type:
            # Crop-specific C factor
            crop_c = {
                "wheat": 0.35,
                "maize": 0.30,
                "alfalfa": 0.05,
                "fallow": 0.80,
                "cover_crop": 0.10,
            }
            return xr.full_like(landcover, crop_c.get(crop_type, 0.3))

        else:
            # Lookup from landcover map
            c_map = xr.full_like(landcover, 0.3, dtype=float)
            for lc_class, c_val in c_defaults.items():
                c_map = c_map.where(landcover != lc_class, c_val)
            return c_map

    @staticmethod
    def calculate_p_factor(
        interventions: xr.DataArray,  # Conservation practice map
        slope: xr.DataArray,  # Slope [degrees]
    ) -> xr.DataArray:
        """
        Calculate support practice factor P.

        Parameters:
        -----------
        interventions : xr.DataArray
            Conservation practice classification
        slope : xr.DataArray
            Slope map [degrees]

        Returns:
        --------
        p_factor : xr.DataArray
            P factor map (0-1, lower = better practices)
        """
        # Default P values by practice
        p_defaults = {
            "none": 1.0,
            "contour": 0.5,
            "terraces": 0.2,
            "strip_cropping": 0.4,
            "grassed_waterway": 0.3,
            "check_dam": 0.1,
        }

        p_map = xr.full_like(interventions, 1.0, dtype=float)
        for practice, p_val in p_defaults.items():
            p_map = p_map.where(interventions != practice, p_val)

        # Slope adjustment for contouring
        slope_adj = xr.where(
            slope < 5, 1.0, xr.where(slope < 10, 0.8, xr.where(slope < 20, 0.6, 0.5))
        )

        return p_map * slope_adj


class RUSLEModel:
    """
    Full RUSLE erosion model: A = R * K * LS * C * P

    Output: Annual soil loss [t/ha/yr]
    """

    def __init__(self):
        self.factors = {}

    def setup(
        self,
        precip: xr.DataArray,
        soil: xr.Dataset,
        dem: xr.DataArray,
        landcover: xr.DataArray,
        interventions: Optional[xr.DataArray] = None,
        resolution_m: float = 30,
    ) -> None:
        """
        Setup RUSLE model with input data.

        All inputs should be spatially aligned rasters.
        """
        # Calculate R factor
        self.factors["R"] = RUSLEFactors.calculate_r_factor(precip)

        # Calculate K factor
        self.factors["K"] = RUSLEFactors.calculate_k_factor(soil)

        # Calculate LS factor
        self.factors["LS"] = RUSLEFactors.calculate_ls_factor(dem, resolution_m)

        # Calculate C factor
        self.factors["C"] = RUSLEFactors.calculate_c_factor(landcover)

        # Calculate P factor
        if interventions is not None:
            slope = np.arctan(np.gradient(dem, resolution_m)[0]) * 180 / np.pi
            slope_xr = xr.DataArray(slope, coords=dem.coords)
            self.factors["P"] = RUSLEFactors.calculate_p_factor(interventions, slope_xr)
        else:
            self.factors["P"] = xr.full_like(landcover, 1.0)

    def run(self) -> xr.DataArray:
        """
        Calculate soil loss using RUSLE equation.

        Returns:
        --------
        soil_loss : xr.DataArray
            Annual soil loss [t/ha/yr]
        """
        # A = R * K * LS * C * P
        soil_loss = (
            self.factors["R"]
            * self.factors["K"]
            * self.factors["LS"]
            * self.factors["C"]
            * self.factors["P"]
        )

        return soil_loss.clip(0)  # No negative erosion

    def get_critical_areas(self, threshold: float = 10.0) -> xr.DataArray:
        """
        Identify areas with erosion above threshold.

        Parameters:
        -----------
        threshold : float
            Erosion threshold [t/ha/yr]

        Returns:
        --------
        critical_mask : xr.DataArray
            Boolean mask of critical erosion areas
        """
        soil_loss = self.run()
        return soil_loss > threshold

    def estimate_project_impact(
        self,
        baseline_interventions: xr.DataArray,
        project_interventions: xr.DataArray,
        area_ha: float,
    ) -> Dict:
        """
        Estimate erosion reduction from conservation project.

        Parameters:
        -----------
        baseline_interventions : xr.DataArray
            Current conservation practices
        project_interventions : xr.DataArray
            Proposed conservation practices
        area_ha : float
            Project area [ha]

        Returns:
        --------
        impact : dict
            Erosion reduction estimates
        """
        # Run baseline
        self.factors["P"] = RUSLEFactors.calculate_p_factor(
            baseline_interventions, self.factors.get("slope", None)
        )
        baseline_loss = self.run()

        # Run project scenario
        self.factors["P"] = RUSLEFactors.calculate_p_factor(
            project_interventions, self.factors.get("slope", None)
        )
        project_loss = self.run()

        # Calculate reduction
        reduction = baseline_loss - project_loss
        total_reduction_t = (reduction * area_ha / reduction.size).sum().item()

        return {
            "baseline_erosion_t_ha_yr": round(baseline_loss.mean().item(), 2),
            "project_erosion_t_ha_yr": round(project_loss.mean().item(), 2),
            "reduction_t_ha_yr": round(reduction.mean().item(), 2),
            "total_reduction_t_yr": round(total_reduction_t, 1),
            "reduction_percentage": round(
                100 * (1 - project_loss.mean() / baseline_loss.mean()), 1
            ),
        }


def _calculate_flow_direction(dem: xr.DataArray) -> np.ndarray:
    """Calculate flow direction using D8 algorithm (simplified)"""
    # Placeholder - in production, use pysheds or richdem
    return np.zeros_like(dem.values)


def _calculate_flow_accumulation(flow_dir: np.ndarray) -> np.ndarray:
    """Calculate flow accumulation (simplified)"""
    # Placeholder - in production, use proper hydrological routing
    return np.ones_like(flow_dir)
