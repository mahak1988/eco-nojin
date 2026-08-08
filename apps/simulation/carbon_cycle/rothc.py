"""
RothC (Soil Organic Carbon Turnover)
=================
Soil organic carbon dynamics with temperature/moisture/clay-dependent decomposition.
"""

import logging

logger = logging.getLogger(__name__)
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator,
    SimulationParameter,
    SimulationRegistry,
    SimulationResult,
    SimulationStatus,
)


@SimulationRegistry.register
class RothCSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        """Handle id."""
        return "rothc"

    @property
    def name(self) -> str:
        """Handle name."""
        return "RothC (Soil Organic Carbon Turnover)"

    @property
    def category(self) -> str:
        """Handle category."""
        return "carbon_cycle"

    @property
    def description(self) -> str:
        """Handle description."""
        return (
            "Soil organic carbon dynamics with temperature/moisture/clay-dependent decomposition."
        )

    @property
    def version(self) -> str:
        """Handle version."""
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        """Handle get_parameters."""
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        """Handle _get_parameters."""
        return [
            SimulationParameter(
                name="lat",
                label="Latitude",
                type="float",
                default=35.7,
                min_value=-90.0,
                max_value=90.0,
                description="Field latitude (triggers NASA climate fetch)",
            ),
            SimulationParameter(
                name="lon",
                label="Longitude",
                type="float",
                default=51.4,
                min_value=-180.0,
                max_value=180.0,
                description="Field longitude",
            ),
            SimulationParameter(
                name="start_date",
                label="Start Date",
                type="string",
                default="2020-01-01",
                description="Simulation start date (YYYY-MM-DD)",
            ),
            SimulationParameter(
                name="end_date",
                label="End Date",
                type="string",
                default="2024-12-31",
                description="Simulation end date (YYYY-MM-DD)",
            ),
            SimulationParameter(
                name="initial_soc",
                label="Initial SOC (t C/ha)",
                type="float",
                default=50.0,
                min_value=5.0,
                max_value=300.0,
                unit="t C/ha",
                description="Initial soil organic carbon",
            ),
            SimulationParameter(
                name="carbon_input",
                label="Annual C Input (t C/ha/yr)",
                type="float",
                default=3.0,
                min_value=0.0,
                max_value=20.0,
                unit="t C/ha/yr",
                description="Annual carbon inputs (residues, manure)",
            ),
            SimulationParameter(
                name="clay",
                label="Clay Content (%)",
                type="float",
                default=25.0,
                min_value=5.0,
                max_value=70.0,
                unit="%",
                description="Soil clay percentage",
            ),
            SimulationParameter(
                name="temperature",
                label="Mean Annual Temp (C) [Fallback]",
                type="float",
                default=15.0,
                min_value=-5.0,
                max_value=35.0,
                unit="C",
                description="Mean annual temperature (used if no lat/lon)",
            ),
            SimulationParameter(
                name="moisture",
                label="Moisture Factor [Fallback]",
                type="float",
                default=0.8,
                min_value=0.1,
                max_value=1.5,
                description="Soil moisture rate modifier (used if no lat/lon)",
            ),
            SimulationParameter(
                name="years",
                label="Simulation Years [Fallback]",
                type="int",
                default=5,
                min_value=1,
                max_value=200,
                unit="yr",
                description="Number of years to simulate (used if no dates)",
            ),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        """Handle run (parameters) with optional NASA POWER climate integration."""
        start = time.time()

        # 1. Enrich parameters with NASA climate data if lat/lon are provided
        lat = parameters.get("lat")
        lon = parameters.get("lon")
        start_date = parameters.get("start_date")
        end_date = parameters.get("end_date")

        if lat is not None and lon is not None and start_date and end_date:
            try:
                from datetime import datetime

                from apps.simulation.data import service

                start_dt = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                end_dt = datetime.strptime(str(end_date), "%Y-%m-%d").date()

                # Fetch real climate data
                climate_series = await service.get_climate_series(
                    float(lat), float(lon), start_dt, end_dt, source="nasa"
                )

                if climate_series:
                    # Calculate averages from daily data
                    temps = [
                        (float(d.get("temp_max_c", 15)) + float(d.get("temp_min_c", 15))) / 2.0
                        for d in climate_series.values()
                    ]
                    precs = [float(d.get("precipitation_mm", 0)) for d in climate_series.values()]
                    et0s = [float(d.get("et0_mm", 3)) for d in climate_series.values()]

                    mean_temp = sum(temps) / len(temps) if temps else 15.0

                    # Moisture factor: ratio of total precip to total ET0, clamped to [0.1, 1.5]
                    total_precip = sum(precs)
                    total_et0 = sum(et0s) if sum(et0s) > 0 else 1.0
                    moisture_ratio = total_precip / total_et0
                    mean_moisture = max(0.1, min(1.5, moisture_ratio))

                    # Calculate years from date range
                    years = max(1, (end_dt - start_dt).days // 365)

                    # Update parameters for the simulation
                    parameters["temperature"] = mean_temp
                    parameters["moisture"] = mean_moisture
                    parameters["years"] = years

            except Exception as e:
                # If NASA fetch fails, we fall back to provided parameters or defaults
                import logging

                logging.getLogger(__name__).warning(
                    f"NASA climate fetch failed, falling back to defaults: {e}"
                )

        # 2. Proceed with standard validation and simulation
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
            outputs = await self._run_simulation(parameters)
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

    async def _run_simulation(self, params: dict[str, Any]) -> dict:
        """
        Conceptual RothC Engine: 2-Pool Soil Organic Carbon Model.
        Uses scientific rate modifiers for Temperature, Moisture, and Clay protection.
        """
        # Extract parameters with safe defaults
        initial_soc = float(params.get("initial_soc", 50.0))
        c_input = float(params.get("carbon_input", 3.0))
        clay = float(params.get("clay", 25.0))
        temp = float(params.get("temperature", 15.0))
        moist = float(params.get("moisture", 0.8))
        years = int(params.get("years", 50))

        # RothC Conceptual Rate Modifiers (Public Domain Principles)
        # 1. Temperature modifier (f_temp): peaks around 25-30C, drops at extremes
        f_temp = max(0.1, min(2.0, 0.5 + (temp / 30.0)))

        # 2. Moisture modifier (f_moist): optimal around 0.8-1.0, drops if too dry/wet
        f_moist = max(0.1, min(1.0, moist))

        # 3. Clay protection factor (f_clay): higher clay = slower decomposition (physical protection)
        f_clay = 1.0 / (1.0 + 0.015 * clay)

        # Base decomposition rate for active pool (per year)
        k_base = 0.15

        # Actual decomposition rate
        k_actual = k_base * f_temp * f_moist * f_clay

        # Conceptual 2-Pool Split: Assume a portion of initial SOC is inert/stable based on clay
        inert_fraction = min(0.6, clay / 100.0)
        inert_soc = initial_soc * inert_fraction
        active_soc = initial_soc - inert_soc

        soc_series = [round(initial_soc, 2)]
        sequestered_series = [0.0]
        current_sequestered = 0.0

        for t in range(years):
            # Annual carbon balance for active pool
            decomposition = k_actual * active_soc
            net_change = c_input - decomposition

            active_soc = max(0.0, active_soc + net_change)
            current_sequestered += net_change

            total_soc = active_soc + inert_soc
            soc_series.append(round(total_soc, 2))
            sequestered_series.append(round(current_sequestered, 2))

        final_soc = soc_series[-1]
        total_seq = sequestered_series[-1]

        # Calculate equilibrium SOC (where input = decomposition)
        equilibrium_soc = inert_soc + (c_input / k_actual) if k_actual > 0 else initial_soc

        return {
            "series": [
                {
                    "key": "soc",
                    "label": "Soil Organic Carbon (t C/ha)",
                    "color": "#16a34a",
                    "values": soc_series,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "sequestered",
                    "label": "Cumulative C Sequestered (t C/ha)",
                    "color": "#0284c7",
                    "values": sequestered_series,
                    "kind": "line",
                },
            ],
            "metrics": {
                "final_soc": round(final_soc, 2),
                "soc_change": round(final_soc - initial_soc, 2),
                "total_sequestered": round(total_seq, 2),
                "equilibrium_soc": round(equilibrium_soc, 2),
                "decomposition_rate_k": round(k_actual, 4),
                "years_simulated": years,
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        """Handle _calculate_metrics (outputs)."""
        return {
            "final_soc_t_ha": float(outputs["metrics"].get("final_soc", 0)),
            "total_sequestered_t_ha": float(outputs["metrics"].get("total_sequestered", 0)),
            "equilibrium_soc_t_ha": float(outputs["metrics"].get("equilibrium_soc", 0)),
            "decomposition_rate": float(outputs["metrics"].get("decomposition_rate_k", 0)),
        }

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        """Handle _generate_charts (outputs)."""
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
