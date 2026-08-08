"""
WOFOST Crop Growth Simulation Model — Crop production quantification.
This is a skeleton implementation that will be replaced with real WOFOST model when available.

Current status: skeleton
Has real Python model?: Yes, PCSE/WOFOST library
Implementation needed: Integration with PCSE library
"""

import logging
import math
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator,
    SimulationParameter,
    SimulationRegistry,
    SimulationResult,
    SimulationStatus,
)

logger = logging.getLogger(__name__)


@SimulationRegistry.register
class WOFOSTSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "wofost"

    @property
    def name(self) -> str:
        return "WOFOST Crop Growth Simulation Model"

    @property
    def category(self) -> str:
        return "agriculture"

    @property
    def description(self) -> str:
        return "WOFOST model for crop growth simulation and production quantification. Current skeleton implementation."

    @property
    def version(self) -> str:
        return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(
                name="crop",
                label="Crop Type",
                type="select",
                options=["wheat", "maize", "potato", "sugarbeet", "grass"],
                default="wheat",
                description="Type of crop to simulate",
                required=True,
            ),
            SimulationParameter(
                name="planting_date",
                label="Planting Date",
                type="string",
                default="2024-04-01",
                description="Planting date (YYYY-MM-DD)",
                required=True,
            ),
            SimulationParameter(
                name="latitude",
                label="Latitude",
                type="float",
                default=52.1,
                min_value=-90.0,
                max_value=90.0,
                unit="deg",
                description="Latitude of location",
                required=True,
            ),
            SimulationParameter(
                name="longitude",
                label="Longitude",
                type="float",
                default=5.18,
                min_value=-180.0,
                max_value=180.0,
                unit="deg",
                description="Longitude of location",
                required=True,
            ),
            SimulationParameter(
                name="soil_type",
                label="Soil Type",
                type="select",
                options=["clay", "loam", "sand", "peat"],
                default="loam",
                description="Soil type",
                required=True,
            ),
            SimulationParameter(
                name="irrigation",
                label="Irrigation Level",
                type="select",
                options=["rainfed", "limited", "full"],
                default="rainfed",
                description="Irrigation level",
                required=True,
            ),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.FAILED,
                parameters=parameters,
                error="; ".join(errors),
            )

        try:
            # This is a skeleton - in the real implementation, we would call the WOFOST model
            outputs = self._run_skeleton_simulation(parameters)
            elapsed = (time.time() - start) * 1000
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.COMPLETED,
                parameters=parameters,
                outputs=outputs,
                metrics=self._calculate_metrics(outputs),
                charts=self._generate_charts(outputs),
                execution_time_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.FAILED,
                parameters=parameters,
                error=str(e),
                execution_time_ms=elapsed,
            )

    def _run_skeleton_simulation(self, params: dict[str, Any]) -> dict:
        """
        Skeleton implementation - this will be replaced with real WOFOST model
        """
        crop = params.get("crop", "wheat")
        planting_date = params.get("planting_date", "2024-04-01")
        latitude = params.get("latitude", 52.1)
        irrigation = params.get("irrigation", "rainfed")

        # Crop-specific parameters based on WOFOST concepts
        crop_params = {
            "wheat": {"duration": 150, "max_yield": 10.0, "opt_temp": 18},
            "maize": {"duration": 120, "max_yield": 15.0, "opt_temp": 25},
            "potato": {"duration": 110, "max_yield": 40.0, "opt_temp": 18},
            "sugarbeet": {"duration": 160, "max_yield": 80.0, "opt_temp": 18},
            "grass": {"duration": 365, "max_yield": 15.0, "opt_temp": 15},
        }

        crop_info = crop_params.get(crop, crop_params["wheat"])
        growing_days = crop_info["duration"]

        # Calculate yield based on crop type, latitude, and irrigation
        base_yield = crop_info["max_yield"]

        # Latitude effect on temperature and day length
        lat_effect = max(0.5, min(1.2, 1.0 - abs(latitude - 52.1) * 0.01))

        # Irrigation effect
        irr_effect = {"rainfed": 0.7, "limited": 0.9, "full": 1.0}[irrigation]

        # Calculate approximate daily growth
        daily_values = []
        lai_values = []
        biomass = 0.0

        for day in range(growing_days):
            # Simulate daily growth with sigmoid curve (typical for crop models)
            progress = day / growing_days
            # Sigmoid-like growth curve
            growth_factor = 1 / (1 + math.exp(-12 * (progress - 0.5)))
            daily_growth = base_yield * growth_factor / growing_days
            biomass += daily_growth

            # Leaf Area Index (LAI) follows biomass but peaks earlier
            lai = min(biomass * 0.3, 5.0)  # Peak LAI around 5.0
            if day > growing_days * 0.7:  # After peak, LAI decreases
                lai *= (growing_days - day) / (growing_days * 0.3)

            daily_values.append(round(biomass, 2))
            lai_values.append(round(min(lai, 6.0), 2))

        final_yield = biomass * lat_effect * irr_effect

        return {
            "series": [
                {
                    "key": "biomass",
                    "label": "Biomass (t/ha)",
                    "color": "#16a34a",
                    "values": daily_values,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "lai",
                    "label": "Leaf Area Index",
                    "color": "#22c55e",
                    "values": lai_values,
                    "kind": "line",
                    "fill": False,
                },
            ],
            "metrics": {
                "predicted_yield_t_ha": round(final_yield, 2),
                "max_biomass_t_ha": round(max(daily_values), 2),
                "crop_duration_days": growing_days,
                "latitude_factor": round(lat_effect, 2),
                "irrigation_factor": round(irr_effect, 2),
                "growth_efficiency": round(final_yield / crop_info["max_yield"], 2),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {
            k: float(v)
            for k, v in outputs.get("metrics", {}).items()
            if isinstance(v, (int, float))
        }

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
