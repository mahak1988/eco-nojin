"""TEEB Wrapper for Eco Nozhin - Full Implementation"""

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
class TEEBSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "teeb"

    @property
    def name(self) -> str:
        return "TEEB Ecosystem Services Valuation Model"

    @property
    def category(self) -> str:
        return "economics"

    @property
    def description(self) -> str:
        return "The Economics of Ecosystems and Biodiversity for valuing ecosystem services. Current skeleton implementation."

    @property
    def version(self) -> str:
        return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(
                name="ecosystem_type",
                label="Ecosystem Type",
                type="select",
                options=[
                    "forest",
                    "wetland",
                    "grassland",
                    "marine_coastal",
                    "agricultural",
                    "urban_green",
                ],
                default="forest",
                description="Type of ecosystem to value",
                required=True,
            ),
            SimulationParameter(
                name="area_ha",
                label="Area",
                type="float",
                default=100.0,
                min_value=0.1,
                max_value=100000.0,
                unit="ha",
                description="Area of ecosystem",
                required=True,
            ),
            SimulationParameter(
                name="protection_status",
                label="Protection Status",
                type="select",
                options=["protected", "partially_protected", "unprotected"],
                default="unprotected",
                description="Current protection status",
                required=True,
            ),
            SimulationParameter(
                name="development_pressure",
                label="Development Pressure",
                type="float",
                default=0.3,
                min_value=0.0,
                max_value=1.0,
                description="Level of development pressure (0-1)",
                required=True,
            ),
            SimulationParameter(
                name="climate_risk",
                label="Climate Risk",
                type="float",
                default=0.2,
                min_value=0.0,
                max_value=1.0,
                description="Level of climate risk (0-1)",
                required=True,
            ),
            SimulationParameter(
                name="valuation_year",
                label="Valuation Year",
                type="int",
                default=2024,
                min_value=2000,
                max_value=2100,
                description="Year for economic valuation",
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
            # This is a skeleton - in the real implementation, we would run the TEEB valuation
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
        Skeleton implementation - this will be replaced with real TEEB model
        Based on TEEB methodology for ecosystem service valuation
        """
        ecosystem_type = params.get("ecosystem_type", "forest")
        area_ha = params.get("area_ha", 100.0)
        protection_status = params.get("protection_status", "unprotected")
        development_pressure = params.get("development_pressure", 0.3)
        climate_risk = params.get("climate_risk", 0.2)
        valuation_year = params.get("valuation_year", 2024)

        # TEEB valuation parameters by ecosystem type
        # Values in USD/hectare/year based on TEEB literature
        base_values = {
            "forest": {
                "carbon_storage": 150,
                "biodiversity": 300,
                "water_regulation": 200,
                "timber": 100,
                "recreation": 50,
            },
            "wetland": {
                "water_purification": 400,
                "flood_control": 300,
                "biodiversity": 250,
                "fisheries": 150,
                "recreation": 75,
            },
            "grassland": {
                "carbon_storage": 80,
                "biodiversity": 150,
                "grazing": 200,
                "recreation": 30,
                "pollination": 100,
            },
            "marine_coastal": {
                "fisheries": 500,
                "storm_protection": 400,
                "carbon_storage": 200,
                "tourism": 300,
                "biodiversity": 150,
            },
            "agricultural": {
                "pollination": 150,
                "soil_fertility": 100,
                "water_retention": 80,
                "pest_control": 120,
                "biodiversity": 50,
            },
            "urban_green": {
                "air_purification": 100,
                "temperature_regulation": 80,
                "recreation": 200,
                "biodiversity": 150,
                "mental_health": 300,
            },
        }

        # Protection status multipliers
        protection_multipliers = {"protected": 1.2, "partially_protected": 1.0, "unprotected": 0.8}

        # Get base values for ecosystem type
        ecosystem_values = base_values.get(ecosystem_type, base_values["forest"])

        # Calculate service values with adjustments
        service_values = {}
        total_value = 0

        for service, base_value in ecosystem_values.items():
            # Adjust for protection status
            adjusted_value = base_value * protection_multipliers.get(protection_status, 1.0)

            # Reduce value based on development pressure and climate risk
            risk_factor = 1.0 - (development_pressure * 0.3 + climate_risk * 0.2)
            risk_factor = max(0.1, risk_factor)  # Don't reduce below 10%

            final_value = adjusted_value * risk_factor
            service_values[f"{service}_value_usd_ha"] = round(final_value, 2)
            total_value += final_value

        # Calculate total ecosystem value
        total_ecosystem_value = total_value * area_ha

        # Calculate value loss under different scenarios
        current_threat_level = (development_pressure + climate_risk) / 2
        potential_loss = (
            total_ecosystem_value * current_threat_level * 0.3
        )  # 30% potential loss at full threat

        # Generate time series showing value over time under different scenarios
        years = 20
        baseline_values = []
        protected_values = []
        degraded_values = []

        for year in range(years):
            # Baseline scenario: gradual decline due to threats
            baseline_decline = total_ecosystem_value * (0.99**year)  # 1% decline per year
            baseline_values.append(round(baseline_decline, 2))

            # Protected scenario: slight improvement with protection
            protected_improvement = total_ecosystem_value * (
                1.005**year
            )  # 0.5% improvement per year
            protected_values.append(round(protected_improvement, 2))

            # Degraded scenario: rapid decline without protection
            degraded_decline = total_ecosystem_value * (0.95**year)  # 5% decline per year
            degraded_values.append(round(degraded_decline, 2))

        return {
            "series": [
                {
                    "key": "baseline_value",
                    "label": "Baseline Ecosystem Value ($)",
                    "color": "#10b981",
                    "values": baseline_values,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "protected_value",
                    "label": "With Protection ($)",
                    "color": "#22c55e",
                    "values": protected_values,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "degraded_value",
                    "label": "Without Protection ($)",
                    "color": "#ef4444",
                    "values": degraded_values,
                    "kind": "line",
                    "fill": True,
                },
            ],
            "metrics": {
                "ecosystem_type": ecosystem_type,
                "area_ha": area_ha,
                "protection_status": protection_status,
                "total_ecosystem_value_usd": round(total_ecosystem_value, 2),
                "annual_value_per_ha_usd": round(total_value, 2),
                "potential_loss_usd": round(potential_loss, 2),
                "development_pressure_applied": development_pressure,
                "climate_risk_applied": climate_risk,
                "protection_value_increase_pct": round(
                    (protection_multipliers.get(protection_status, 1.0) - 1.0) * 100, 1
                ),
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


# Try to import from the wrapper, but provide a fallback to skeleton implementation
try:
    from .valuation_model import ValuationModel
    from .wrapper import TEEBOutput, TEEBWrapper
except ImportError:
    logger.warning("TEEB wrapper not available, using skeleton implementation")

    # Provide skeleton classes to prevent import errors
    class TEEBWrapper:
        pass

    class TEEBOutput:
        pass

    class ValuationModel:
        pass


__all__ = ["TEEBOutput", "TEEBSimulator", "TEEBWrapper", "ValuationModel"]
