"""
DSSAT Decision Support System for Agrotechnology Transfer — Cropping systems simulation.
This is a skeleton implementation that will be replaced with real DSSAT model when available.

Current status: skeleton
Has real Python model?: No native Python library, requires DSSAT executable integration
Implementation needed: Wrapper to DSSAT executable or API call
"""
import logging
import math
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator, SimulationParameter, SimulationResult,
    SimulationRegistry, SimulationStatus,
)

logger = logging.getLogger(__name__)

@SimulationRegistry.register
class DSSATSimulator(BaseSimulator):
    @property
    def id(self) -> str: return "dssat"
    @property
    def name(self) -> str: return "DSSAT Cropping Systems Simulator"
    @property
    def category(self) -> str: return "agriculture"
    @property
    def description(self) -> str: return "Decision Support System for Agrotechnology Transfer for cropping systems simulation. Current skeleton implementation."
    @property
    def version(self) -> str: return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="lat", label="Latitude", type="float", default=35.7, min_value=-90.0, max_value=90.0, description="Field latitude (triggers NASA climate fetch for leaching estimation)", required=False),
            SimulationParameter(name="lon", label="Longitude", type="float", default=51.4, min_value=-180.0, max_value=180.0, description="Field longitude", required=False),
            SimulationParameter(name="start_date", label="Start Date", type="string", default="2024-05-01", description="Season start date (YYYY-MM-DD)", required=False),
            SimulationParameter(name="end_date", label="End Date", type="string", default="2024-10-01", description="Season end date (YYYY-MM-DD)", required=False),
            SimulationParameter(name="crop", label="Crop", type="select", 
                              options=["maize", "wheat", "rice", "soybean", "cotton", "sunflower"], 
                              default="maize", description="Crop to simulate", required=True),
            SimulationParameter(name="variety", label="Variety", type="string", 
                              default="generic", description="Crop variety/cultivar", required=False),
            SimulationParameter(name="planting_density", label="Planting Density", type="float", 
                              default=6.0, min_value=1.0, max_value=20.0, unit="plants/m²", 
                              description="Planting density", required=False),
            SimulationParameter(name="nitrogen_application", label="N Application", type="float", 
                              default=120.0, min_value=0.0, max_value=300.0, unit="kg/ha", 
                              description="Total nitrogen applied", required=True),
            SimulationParameter(name="irrigation_strategy", label="Irrigation Strategy", type="select", 
                              options=["rainfed", "deficit", "full", "scheduled"], 
                              default="rainfed", description="Irrigation strategy", required=True),
            SimulationParameter(name="soil_ph", label="Soil pH", type="float", 
                              default=6.5, min_value=4.0, max_value=8.5, 
                              description="Soil pH (affects N availability)", required=True),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.FAILED, parameters=parameters, error="; ".join(errors))
        
        try:
            # This is a skeleton - in the real implementation, we would call the DSSAT model
            outputs = await self._run_simulation(parameters)
            elapsed = (time.time() - start) * 1000
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.COMPLETED, parameters=parameters, outputs=outputs,
                metrics=self._calculate_metrics(outputs), charts=self._generate_charts(outputs),
                execution_time_ms=elapsed)
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.FAILED, parameters=parameters, error=str(e),
                execution_time_ms=elapsed)

    async def _run_simulation(self, params: dict[str, Any]) -> dict:
        """
        Conceptual DSSAT Engine: Nitrogen Balance and Yield Response.
        Estimates N stress, yield reduction, and N leaching based on pH, irrigation, and climate.
        """
        crop = params.get("crop", "maize")
        n_app = float(params.get("nitrogen_application", 120.0))
        soil_ph = float(params.get("soil_ph", 6.5))
        irrigation = params.get("irrigation_strategy", "rainfed")
        lat = params.get("lat")
        lon = params.get("lon")
        start_date = params.get("start_date")
        end_date = params.get("end_date")

        # Crop-specific parameters (Optimal N, Max Yield, N stress sensitivity)
        crop_db = {
            "maize": {"optimal_n": 150.0, "max_yield": 10.0, "n_sensitivity": 0.8},
            "wheat": {"optimal_n": 120.0, "max_yield": 8.0, "n_sensitivity": 0.7},
            "rice": {"optimal_n": 100.0, "max_yield": 7.0, "n_sensitivity": 0.6},
            "soybean": {"optimal_n": 40.0, "max_yield": 4.0, "n_sensitivity": 0.3},
            "cotton": {"optimal_n": 130.0, "max_yield": 3.5, "n_sensitivity": 0.7},
            "sunflower": {"optimal_n": 90.0, "max_yield": 3.5, "n_sensitivity": 0.6}
        }
        crop_info = crop_db.get(crop, crop_db["maize"])

        # 1. Calculate N Efficiency Factor
        # pH factor: optimal between 6.0 and 7.0
        if 6.0 <= soil_ph <= 7.0:
            ph_factor = 1.0
        else:
            ph_factor = max(0.5, 1.0 - 0.15 * abs(soil_ph - 6.5))
            
        # Irrigation factor
        irr_factors = {"full": 1.0, "scheduled": 0.9, "deficit": 0.7, "rainfed": 0.6}
        irr_factor = irr_factors.get(irrigation, 0.6)
        
        n_efficiency = ph_factor * irr_factor
        effective_n = n_app * n_efficiency

        # 2. Calculate N Stress and Yield
        n_deficit = max(0.0, crop_info["optimal_n"] - effective_n)
        n_stress = min(1.0, (n_deficit / crop_info["optimal_n"]) * crop_info["n_sensitivity"])
        actual_yield = crop_info["max_yield"] * (1.0 - n_stress)

        # 3. Estimate N Leaching (requires precipitation data)
        total_precip = 0.0
        if lat is not None and lon is not None and start_date and end_date:
            try:
                from apps.simulation.data import service
                from datetime import datetime
                start_dt = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                end_dt = datetime.strptime(str(end_date), "%Y-%m-%d").date()
                climate_series = await service.get_climate_series(float(lat), float(lon), start_dt, end_dt, source="nasa")
                if climate_series:
                    total_precip = sum(float(d.get('precipitation_mm', 0)) for d in climate_series.values())
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"NASA fetch failed for DSSAT leaching: {e}")
        
        # Leaching proxy: excess water * unutilized N fraction
        water_excess = max(0.0, total_precip - 300.0) # Assume ~300mm crop water use
        leaching_risk = min(1.0, water_excess / 200.0) if total_precip > 0 else 0.1
        n_unutilized = max(0.0, n_app * (1.0 - (effective_n / crop_info["optimal_n"])))
        n_leached = max(0.0, n_unutilized * leaching_risk * 0.5) # 0.5 is a conservative leaching coefficient

        # 4. Generate conceptual chart data
        yield_curve = [0.0, actual_yield * 0.2, actual_yield * 0.5, actual_yield * 0.8, actual_yield]
        n_uptake_curve = [0.0, effective_n * 0.3, effective_n * 0.7, effective_n * 0.9, effective_n]

        return {
            "metrics": {
                "actual_yield_t_ha": round(actual_yield, 2),
                "potential_yield_t_ha": crop_info["max_yield"],
                "n_stress_factor": round(n_stress, 2),
                "n_efficiency": round(n_efficiency, 2),
                "n_leached_kg_ha": round(n_leached, 2),
                "total_precip_mm": round(total_precip, 2)
            },
            "charts": [
                {"key": "yield_accumulation", "label": "Yield Accumulation (t/ha)", "color": "#16a34a", "values": yield_curve, "kind": "line", "fill": True},
                {"key": "n_uptake", "label": "N Uptake (kg/ha)", "color": "#0284c7", "values": n_uptake_curve, "kind": "line"}
            ]
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return outputs.get("charts", [])
