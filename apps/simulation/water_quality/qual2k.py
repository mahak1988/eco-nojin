"""
QUAL2K River Water Quality Model — Stream water quality simulation.
This is a skeleton implementation that will be replaced with real QUAL2K model when available.

Current status: skeleton
Has real Python model?: No native Python library, requires QUAL2K executable integration
Implementation needed: Wrapper to QUAL2K executable or subprocess call
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
class QUAL2KSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "qual2k"

    @property
    def name(self) -> str:
        return "QUAL2K River Water Quality Model"

    @property
    def category(self) -> str:
        return "water_quality"

    @property
    def description(self) -> str:
        return "QUAL2K model for stream water quality simulation. Current skeleton implementation."

    @property
    def version(self) -> str:
        return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(
                name="stream_length",
                label="Stream Length",
                type="float",
                default=10000.0,
                min_value=100.0,
                max_value=1000000.0,
                unit="m",
                description="Length of stream segment",
                required=True,
            ),
            SimulationParameter(
                name="average_flow",
                label="Average Flow",
                type="float",
                default=1.0,
                min_value=0.001,
                max_value=1000.0,
                unit="m³/s",
                description="Average stream flow rate",
                required=True,
            ),
            SimulationParameter(
                name="temperature",
                label="Water Temperature",
                type="float",
                default=20.0,
                min_value=0.0,
                max_value=40.0,
                unit="°C",
                description="Average water temperature",
                required=True,
            ),
            SimulationParameter(
                name="dissolved_oxygen",
                label="Dissolved Oxygen",
                type="float",
                default=8.0,
                min_value=0.0,
                max_value=15.0,
                unit="mg/L",
                description="Initial dissolved oxygen concentration",
                required=True,
            ),
            SimulationParameter(
                name="bod",
                label="Biochemical Oxygen Demand",
                type="float",
                default=5.0,
                min_value=0.0,
                max_value=100.0,
                unit="mg/L",
                description="Biochemical oxygen demand",
                required=True,
            ),
            SimulationParameter(
                name="nitrogen_concentration",
                label="Nitrogen Concentration",
                type="float",
                default=2.0,
                min_value=0.0,
                max_value=20.0,
                unit="mg/L",
                description="Total nitrogen concentration",
                required=True,
            ),
            SimulationParameter(
                name="phosphorus_concentration",
                label="Phosphorus Concentration",
                type="float",
                default=0.1,
                min_value=0.0,
                max_value=5.0,
                unit="mg/L",
                description="Total phosphorus concentration",
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
            # This is a skeleton - in the real implementation, we would run the QUAL2K model
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
        Skeleton implementation - this will be replaced with real QUAL2K model
        Based on QUAL2K principles: oxygen balance, nutrient cycling, algal growth
        """
        stream_length = params.get("stream_length", 10000.0)
        avg_flow = params.get("average_flow", 1.0)
        temp = params.get("temperature", 20.0)
        do_init = params.get("dissolved_oxygen", 8.0)
        bod_init = params.get("bod", 5.0)
        n_conc = params.get("nitrogen_concentration", 2.0)
        p_conc = params.get("phosphorus_concentration", 0.1)

        # Calculate oxygen saturation based on temperature (Weiss equation)
        log_do_sat = (
            -139.34410
            + (1.575701e05 / (temp + 273.15))
            - (6.642308e07 / (temp + 273.15) ** 2)
            + (1.243800e10 / (temp + 273.15) ** 3)
            - (8.621949e11 / (temp + 273.15) ** 4)
        )
        do_sat = math.exp(log_do_sat)

        # Calculate deoxygenation coefficient based on temperature
        k_d = 0.1  # Base deoxygenation rate (day^-1)
        k_d_temp = k_d * (1.047 ** (temp - 20))  # Temperature correction

        # Calculate reaeration coefficient (O'Connor-Dobbins)
        k_r = 3.93 * (avg_flow**0.5) / (0.026**0.5)  # Based on flow velocity
        k_r_temp = k_r * (1.024 ** (temp - 20))  # Temperature correction

        # Calculate algal growth rate based on nutrients
        # Phosphorus limitation
        p_limit = p_conc / (p_conc + 0.02)  # Half-saturation constant for P
        # Nitrogen limitation
        n_limit = n_conc / (n_conc + 0.3)  # Half-saturation constant for N
        growth_factor = min(p_limit, n_limit)

        # Calculate algal growth rate
        mu_max = 2.0 * growth_factor  # Maximum growth rate (day^-1) corrected for nutrients
        mu = mu_max * (do_sat / (do_sat + 2))  # Light limitation effect

        # Simulate along stream distance
        n_segments = min(100, int(stream_length / 100))  # Max 100 segments
        dx = stream_length / n_segments / avg_flow  # Time step based on flow

        # Initialize concentrations
        do_profile = [do_init]
        bod_profile = [bod_init]
        n_profile = [n_conc]
        p_profile = [p_conc]

        current_do = do_init
        current_bod = bod_init
        current_n = n_conc
        current_p = p_conc

        # Simulate water quality changes along the stream
        for seg in range(n_segments):
            # Calculate changes based on QUAL2K principles
            # Deoxygenation due to BOD
            deoxygenation = k_d_temp * current_bod

            # Reaeration
            reaeration = k_r_temp * (do_sat - current_do)

            # Algal oxygen production
            algae_prod = mu * 0.5  # Simplified algae production

            # Net oxygen change
            do_change = reaeration + algae_prod - deoxygenation
            current_do = max(0.1, current_do + do_change * dx)  # Prevent negative DO

            # BOD decay
            bod_decay = k_d_temp * current_bod
            current_bod = max(0.01, current_bod - bod_decay * dx)  # Prevent negative BOD

            # Nutrient uptake by algae
            n_uptake = mu * current_n * 0.1  # Simplified uptake
            p_uptake = mu * current_p * 0.1  # Simplified uptake

            current_n = max(0.01, current_n - n_uptake * dx)
            current_p = max(0.001, current_p - p_uptake * dx)

            # Store profiles
            do_profile.append(round(current_do, 2))
            bod_profile.append(round(current_bod, 2))
            n_profile.append(round(current_n, 2))
            p_profile.append(round(current_p, 2))

        # Calculate trophic state based on phosphorus
        if p_conc < 0.01:
            trophic_state = "Oligotrophic"
            trophic_index = 30
        elif p_conc < 0.03:
            trophic_state = "Mesotrophic"
            trophic_index = 50
        elif p_conc < 0.1:
            trophic_state = "Eutrophic"
            trophic_index = 65
        else:
            trophic_state = "Hypereutrophic"
            trophic_index = 80

        # Calculate pollution indices
        pollution_score = (bod_init / 10) + (n_conc / 5) + (p_conc / 0.2) + ((do_sat - do_init) / 2)
        pollution_category = (
            "Good"
            if pollution_score < 2
            else "Fair"
            if pollution_score < 4
            else "Poor"
            if pollution_score < 6
            else "Very Poor"
        )

        return {
            "series": [
                {
                    "key": "dissolved_oxygen",
                    "label": "Dissolved Oxygen (mg/L)",
                    "color": "#3b82f6",
                    "values": do_profile,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "bod",
                    "label": "BOD (mg/L)",
                    "color": "#ef4444",
                    "values": bod_profile,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "nitrogen",
                    "label": "Nitrogen (mg/L)",
                    "color": "#f59e0b",
                    "values": n_profile,
                    "kind": "line",
                    "fill": False,
                },
                {
                    "key": "phosphorus",
                    "label": "Phosphorus (mg/L)",
                    "color": "#8b5cf6",
                    "values": p_profile,
                    "kind": "line",
                    "fill": False,
                },
            ],
            "metrics": {
                "stream_length_m": stream_length,
                "average_flow_cms": avg_flow,
                "temperature_celsius": temp,
                "initial_dissolved_oxygen": do_init,
                "initial_bod": bod_init,
                "initial_nitrogen_concentration": n_conc,
                "initial_phosphorus_concentration": p_conc,
                "dissolved_oxygen_saturation": round(do_sat, 2),
                "deoxygenation_coefficient": round(k_d_temp, 3),
                "reaeration_coefficient": round(k_r_temp, 3),
                "trophic_state": trophic_state,
                "trophic_index": trophic_index,
                "pollution_category": pollution_category,
                "pollution_score": round(pollution_score, 2),
                "minimum_dissolved_oxygen": round(min(do_profile), 2),
                "maximum_bod": round(max(bod_profile), 2),
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
