"""
WEAP Water Evaluation and Planning System — Integrated water resources planning.
This is a skeleton implementation that will be replaced with real WEAP model when available.

Current status: skeleton
Has real Python model?: No native Python library, requires WEAP executable integration
Implementation needed: Wrapper to WEAP executable or API call
"""

import logging
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
class WEAPSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "weap"

    @property
    def name(self) -> str:
        return "WEAP Water Resources Planner"

    @property
    def category(self) -> str:
        return "hydrology"

    @property
    def description(self) -> str:
        return "Water Evaluation and Planning System for integrated water resources planning. Current skeleton implementation."

    @property
    def version(self) -> str:
        return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(
                name="watershed_area",
                label="Watershed Area",
                type="float",
                default=1000.0,
                min_value=1.0,
                max_value=1000000.0,
                unit="km²",
                description="Total watershed area",
                required=True,
            ),
            SimulationParameter(
                name="climate_scenario",
                label="Climate Scenario",
                type="select",
                options=["historical", "wet_future", "dry_future", "variable"],
                default="historical",
                description="Climate scenario to simulate",
                required=True,
            ),
            SimulationParameter(
                name="demand_category",
                label="Demand Category",
                type="select",
                options=["agriculture", "municipal", "industrial", "environmental", "mixed"],
                default="mixed",
                description="Primary water demand category",
                required=True,
            ),
            SimulationParameter(
                name="supply_infrastructure",
                label="Supply Infrastructure",
                type="select",
                options=["natural", "developed", "managed", "stress_tested"],
                default="developed",
                description="Level of supply infrastructure",
                required=True,
            ),
            SimulationParameter(
                name="population_growth",
                label="Population Growth",
                type="float",
                default=0.02,
                min_value=0.0,
                max_value=0.05,
                description="Annual population growth rate",
                required=True,
            ),
            SimulationParameter(
                name="economic_growth",
                label="Economic Growth",
                type="float",
                default=0.03,
                min_value=0.0,
                max_value=0.1,
                description="Annual economic growth rate",
                required=True,
            ),
            SimulationParameter(
                name="conservation_effort",
                label="Conservation Effort",
                type="float",
                default=0.1,
                min_value=0.0,
                max_value=0.5,
                description="Fraction of demand reduced through conservation",
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
            # This is a skeleton - in the real implementation, we would run the WEAP model
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
        Skeleton implementation - this will be replaced with real WEAP model
        Based on WEAP principles: integrated water resources planning and management
        """
        watershed_area = params.get("watershed_area", 1000.0)
        climate_scenario = params.get("climate_scenario", "historical")
        demand_category = params.get("demand_category", "mixed")
        supply_infrastructure = params.get("supply_infrastructure", "developed")
        pop_growth = params.get("population_growth", 0.02)
        econ_growth = params.get("economic_growth", 0.03)
        conservation_effort = params.get("conservation_effort", 0.1)

        # Define base values
        base_precip = 800  # mm/year
        base_evap = 1200  # mm/year
        base_pop = 100000  # Population
        base_demand = 500  # MCM/year per demand category

        # Climate scenario adjustments
        climate_multipliers = {
            "historical": 1.0,
            "wet_future": 1.2,
            "dry_future": 0.8,
            "variable": 1.0,  # Will vary annually
        }
        climate_multiplier = climate_multipliers[climate_scenario]

        # Demand category multipliers
        demand_multipliers = {
            "agriculture": 3.0,
            "municipal": 1.0,
            "industrial": 1.5,
            "environmental": 0.5,
            "mixed": 1.5,
        }
        demand_multiplier = demand_multipliers[demand_category]

        # Supply infrastructure multipliers
        infrastructure_multipliers = {
            "natural": 0.7,
            "developed": 1.0,
            "managed": 1.2,
            "stress_tested": 0.8,
        }
        infrastructure_multiplier = infrastructure_multipliers[supply_infrastructure]

        # Calculate base supply from watershed
        # Precipitation over watershed area
        base_supply = (
            base_precip * climate_multiplier * watershed_area * 1000
        ) / 1e6  # Convert to MCM

        # Simulate over time (25 years)
        n_years = 25
        years = list(range(2025, 2025 + n_years))

        # Initialize arrays
        supplies = []
        demands = []
        deficits = []
        storages = []

        # Starting storage (reservoir capacity)
        current_storage = base_supply * 0.5  # 50% of annual supply
        max_storage = base_supply * 1.2  # 120% of annual supply

        for year in range(n_years):
            # Calculate population and economic growth
            current_pop = base_pop * ((1 + pop_growth) ** year)
            economic_factor = (1 + econ_growth) ** year

            # Calculate water demand
            # Municipal demand: 150 L/person/day
            municipal_demand = (current_pop * 150 * 365) / 1e6  # Convert to MCM
            # Other demands scaled by economic growth
            other_demand = base_demand * demand_multiplier * economic_factor
            total_demand = municipal_demand + other_demand

            # Apply conservation measures
            total_demand = total_demand * (1 - conservation_effort)

            # Calculate available supply
            # Climate varies annually in variable scenario
            if climate_scenario == "variable":
                import random

                annual_multiplier = climate_multiplier * (0.8 + random.random() * 0.4)  # 0.8 to 1.2
                annual_supply = (base_precip * annual_multiplier * watershed_area * 1000) / 1e6
            else:
                annual_supply = base_supply * infrastructure_multiplier

            # Calculate storage changes
            inflow = annual_supply
            outflow = min(
                total_demand, current_storage + inflow
            )  # Can't release more than available
            current_storage = current_storage + inflow - outflow

            # Constrain storage to reservoir limits
            current_storage = max(0, min(max_storage, current_storage))

            # Calculate shortage
            shortage = max(0, total_demand - (current_storage + inflow))

            # Store values
            supplies.append(round(annual_supply, 2))
            demands.append(round(total_demand, 2))
            deficits.append(round(shortage, 2))
            storages.append(round(current_storage, 2))

        # Calculate reliability metrics
        total_supplied = sum(supplies) - sum(deficits)
        total_demand_sum = sum(demands)
        reliability = (total_supplied / total_demand_sum) if total_demand_sum > 0 else 0

        # Calculate shortage metrics
        avg_shortage = sum(deficits) / len(deficits) if deficits else 0
        max_shortage = max(deficits) if deficits else 0
        shortage_frequency = sum(1 for s in deficits if s > 0) / len(deficits)

        # Calculate system sustainability
        if reliability > 0.95:
            sustainability = "High"
        elif reliability > 0.85:
            sustainability = "Medium"
        else:
            sustainability = "Low"

        # Calculate vulnerability (severity of worst-case shortage)
        vulnerability = max_shortage / max(demands) if demands else 0

        # Economic impact calculation
        economic_impact = sum(deficits) * 5000  # $5000 per MCM shortage

        # Environmental flow satisfaction
        environmental_flow_requirement = base_supply * 0.3  # 30% for environment
        env_flow_satisfied = sum(
            1 for i in range(len(supplies)) if supplies[i] > environmental_flow_requirement
        ) / len(supplies)

        return {
            "series": [
                {
                    "key": "supply",
                    "label": "Water Supply (MCM)",
                    "color": "#3b82f6",
                    "values": supplies,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "demand",
                    "label": "Water Demand (MCM)",
                    "color": "#ef4444",
                    "values": demands,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "storage",
                    "label": "System Storage (MCM)",
                    "color": "#8b5cf6",
                    "values": storages,
                    "kind": "area",
                    "fill": True,
                },
                {
                    "key": "deficit",
                    "label": "Water Deficit (MCM)",
                    "color": "#f97316",
                    "values": deficits,
                    "kind": "column",
                    "fill": True,
                },
            ],
            "metrics": {
                "watershed_area_km2": watershed_area,
                "climate_scenario": climate_scenario,
                "demand_category": demand_category,
                "supply_infrastructure": supply_infrastructure,
                "population_growth_rate": pop_growth,
                "economic_growth_rate": econ_growth,
                "conservation_effort_fraction": conservation_effort,
                "base_supply_mcm": round(base_supply, 2),
                "simulation_years": n_years,
                "average_annual_supply_mcm": round(sum(supplies) / len(supplies), 2),
                "average_annual_demand_mcm": round(sum(demands) / len(demands), 2),
                "average_annual_deficit_mcm": round(avg_shortage, 2),
                "maximum_annual_deficit_mcm": round(max_shortage, 2),
                "system_reliability_fraction": round(reliability, 3),
                "shortage_frequency_fraction": round(shortage_frequency, 3),
                "system_sustainability": sustainability,
                "system_vulnerability": round(vulnerability, 3),
                "estimated_economic_impact_usd": round(economic_impact, 2),
                "environmental_flow_satisfaction_fraction": round(env_flow_satisfied, 3),
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
