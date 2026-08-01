"""
APSIM (Agricultural Production Systems Simulator) Simulator
=================
APSIM is a modular modelling framework for agricultural systems. Simulates crop growth, soil water, nitrogen, and management practices.
"""

import logging

logger = logging.getLogger(__name__)
import random
import math
from datetime import datetime, UTC
from typing import Any

from apps.simulation.base import (
    BaseSimulator,
    SimulationParameter,
    SimulationResult,
    SimulationRegistry,
    SimulationStatus,
)


@SimulationRegistry.register
class APSIMSimulator(BaseSimulator):
    """APSIM (Agricultural Production Systems Simulator) implementation."""

    @property
    def id(self) -> str: return "apsim"
    @property
    def name(self) -> str: return "APSIM Agricultural Production Systems Simulator"
    @property
    def category(self) -> str: return "agriculture"
    @property
    def description(self) -> str: return "Agricultural Production Systems Simulator for farming systems analysis. Current skeleton implementation."
    @property
    def version(self) -> str: return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="crop_type", label="Crop Type", type="select", 
                              options=["wheat", "barley", "canola", "sorghum", "maize", "fallow"], 
                              default="wheat", description="Type of crop to simulate", required=True),
            SimulationParameter(name="region", label="Region", type="select", 
                              options=["temperate", "subtropical", "mediterranean", "tropical"], 
                              default="temperate", description="Climate region", required=True),
            SimulationParameter(name="soil_type", label="Soil Type", type="select", 
                              options=["clay", "loamy_clay", "sandy_loam", "sandy", "light_clay"], 
                              default="loamy_clay", description="Soil classification", required=True),
            SimulationParameter(name="nitrogen_rate", label="Nitrogen Rate", type="float", 
                              default=80.0, min_value=0.0, max_value=300.0, unit="kg/ha", 
                              description="Applied nitrogen fertilizer rate", required=True),
            SimulationParameter(name="phosphorus_rate", label="Phosphorus Rate", type="float", 
                              default=20.0, min_value=0.0, max_value=100.0, unit="kg/ha", 
                              description="Applied phosphorus fertilizer rate", required=True),
            SimulationParameter(name="simulation_start", label="Start Date", type="string", 
                              default="2024-01-01", description="Simulation start date (YYYY-MM-DD)", required=True),
            SimulationParameter(name="simulation_end", label="End Date", type="string", 
                              default="2024-12-31", description="Simulation end date (YYYY-MM-DD)", required=True),
        ]
    def _get_parameters(self) -> list[SimulationParameter]:
        return self.get_parameters()

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.FAILED, parameters=parameters, error="; ".join(errors))
        
        try:
            # This is a skeleton - in the real implementation, we would call the APSIM model
            outputs = self._run_skeleton_simulation(parameters)
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
    
    def _run_skeleton_simulation(self, params: dict[str, Any]) -> dict:
        """
        Skeleton implementation - this will be replaced with real APSIM model
        """
        crop_type = params.get("crop_type", "wheat")
        region = params.get("region", "temperate")
        soil_type = params.get("soil_type", "loamy_clay")
        n_rate = params.get("nitrogen_rate", 80.0)
        p_rate = params.get("phosphorus_rate", 20.0)
        
        # Crop-specific parameters based on APSIM concepts
        crop_params = {
            "wheat": {"base_temp": 0, "opt_temp": 15, "max_temp": 30, "max_yield": 8.0},
            "barley": {"base_temp": 0, "opt_temp": 15, "max_temp": 30, "max_yield": 7.0},
            "canola": {"base_temp": 2, "opt_temp": 18, "max_temp": 32, "max_yield": 4.0},
            "sorghum": {"base_temp": 10, "opt_temp": 28, "max_temp": 40, "max_yield": 8.0},
            "maize": {"base_temp": 8, "opt_temp": 28, "max_temp": 40, "max_yield": 12.0},
            "fallow": {"base_temp": 0, "opt_temp": 15, "max_temp": 30, "max_yield": 0.0}
        }
        
        crop_info = crop_params.get(crop_type, crop_params["wheat"])
        max_yield = crop_info["max_yield"]
        
        # Region-specific modifiers
        region_modifiers = {
            "temperate": 1.0,
            "subtropical": 1.1,
            "mediterranean": 0.9,
            "tropical": 0.8
        }
        
        # Soil-specific modifiers
        soil_modifiers = {
            "clay": 0.9,
            "loamy_clay": 1.0,
            "sandy_loam": 0.8,
            "sandy": 0.7,
            "light_clay": 0.95
        }
        
        # Calculate yield based on inputs
        base_yield = max_yield * region_modifiers.get(region, 1.0) * soil_modifiers.get(soil_type, 1.0)
        
        # Apply fertilizer effects (non-linear response)
        n_effect = 1.0 + (n_rate / 200.0) * 0.3  # Up to 30% increase with N
        n_effect = min(1.3, n_effect)  # Cap at 30%
        
        p_effect = 1.0 + (p_rate / 100.0) * 0.2  # Up to 20% increase with P
        p_effect = min(1.2, p_effect)  # Cap at 20%
        
        final_yield = base_yield * n_effect * p_effect
        
        # Generate some time series data representing crop growth
        daily_biomass = []
        daily_nitrogen = []
        biomass = 0.0
        nitrogen_uptake = 0.0
        
        # Simulate 200 days of growth for the crop
        for day in range(200):
            if crop_type != "fallow":
                # Simulate daily growth with logistic curve
                growth_factor = 1 / (1 + math.exp(-0.1 * (day - 100)))  # Peak around day 100
                daily_growth = max_yield * growth_factor / 200
                biomass += daily_growth
                
                # Nitrogen uptake follows biomass but with delay
                if day > 30:
                    nitrogen_uptake += daily_growth * 0.02  # 2% N content
            
            daily_biomass.append(round(biomass, 2))
            daily_nitrogen.append(round(nitrogen_uptake, 2))
        
        return {
            "series": [
                {"key": "biomass", "label": "Biomass (t/ha)", "color": "#16a34a", 
                 "values": daily_biomass, "kind": "line", "fill": True},
                {"key": "nitrogen_uptake", "label": "N Uptake (kg/ha)", "color": "#3b82f6", 
                 "values": daily_nitrogen, "kind": "line", "fill": False},
            ],
            "metrics": {
                "predicted_yield_t_ha": round(final_yield, 2),
                "nitrogen_recovery_pct": round((nitrogen_uptake / max(n_rate, 1)) * 100, 1) if crop_type != "fallow" else 0,
                "crop_type": crop_type,
                "region": region,
                "soil_type": soil_type,
                "applied_n_kg_ha": n_rate,
                "applied_p_kg_ha": p_rate,
                "water_use_efficiency": round(final_yield / 500 * 1000, 2),  # Assuming 500mm water
            },
        }
        
    async def _run_simulation(self, params: dict[str, Any]) -> dict:
        return self._run_skeleton_simulation(params)

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
