"""
RothC (Soil Organic Carbon Turnover)
=================
Soil organic carbon dynamics with temperature/moisture/clay-dependent decomposition.
"""

import math
import hashlib
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator,
    SimulationParameter,
    SimulationResult,
    SimulationRegistry,
    SimulationStatus,
)


def _noise(i: int, seed: int) -> float:
    h = hashlib.sha256(f"{seed}:{i}".encode()).hexdigest()
    return (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1


@SimulationRegistry.register
class RothCSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "rothc"

    @property
    def name(self) -> str:
        return "RothC (Soil Organic Carbon Turnover)"

    @property
    def category(self) -> str:
        return "carbon_cycle"

    @property
    def description(self) -> str:
        return "Soil organic carbon dynamics with temperature/moisture/clay-dependent decomposition."

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="initial_soc", label="Initial SOC (t C/ha)", type="float", default=50.0, min_value=5.0, max_value=300.0, unit="t C/ha", description="Initial soil organic carbon"),
            SimulationParameter(name="carbon_input", label="Annual C Input (t C/ha/yr)", type="float", default=3.0, min_value=0.0, max_value=20.0, unit="t C/ha/yr", description="Annual carbon inputs (residues, manure)"),
            SimulationParameter(name="clay", label="Clay Content (%)", type="float", default=25.0, min_value=5.0, max_value=70.0, unit="%", description="Soil clay percentage"),
            SimulationParameter(name="temperature", label="Mean Annual Temp (C)", type="float", default=15.0, min_value=-5.0, max_value=35.0, unit="C", description="Mean annual temperature"),
            SimulationParameter(name="moisture", label="Moisture Factor", type="float", default=0.8, min_value=0.1, max_value=1.5, description="Soil moisture rate modifier"),
            SimulationParameter(name="years", label="Simulation Years", type="int", default=50, min_value=5, max_value=200, unit="yr", description="Number of years to simulate"),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                status=SimulationStatus.FAILED, parameters=parameters, error="; ".join(errors))
        try:
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
        soc = params.get("initial_soc", 50.0)
        cin = params.get("carbon_input", 3.0); clay = params.get("clay", 25.0)
        temp = params.get("temperature", 15.0); moist = params.get("moisture", 0.8)
        n = int(params.get("years", 50)); seed = int(params.get("seed", 1))
        k = max(0.05, min(2.0, 1.44 * moist * (0.5 + temp / 30) / (0.8 + clay / 100)))
        soc_series, seq = [round(soc, 2)], []
        cum = 0.0
        for t in range(n):
            net = cin - k * soc + _noise(t, seed) * 0.1
            soc = max(1.0, soc + net); cum += net
            soc_series.append(round(soc, 2)); seq.append(round(cum, 2))
        return {
            "series": [
                {"key": "soc", "label": "Soil Organic Carbon (t C/ha)", "color": "#16a34a", "values": soc_series, "kind": "line", "fill": True},
                {"key": "sequestered", "label": "Cumulative C Sequestered (t C/ha)", "color": "#0284c7", "values": seq, "kind": "line"},
            ],
            "metrics": {
                "final_soc": round(soc, 2),
                "soc_change": round(soc - params.get("initial_soc", 50.0), 2),
                "total_sequestered": round(cum, 2),
                "equilibrium_soc": round(cin / max(0.01, k), 2),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
