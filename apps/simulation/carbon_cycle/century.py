"""
CENTURY Soil Organic Matter Model — standardized model (Phase 4 upgrade).
Deterministic, returns standard outputs.series + metrics for the frontend.
"""
import math
import hashlib
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator, SimulationParameter, SimulationResult,
    SimulationRegistry, SimulationStatus,
)


def _noise(i: int, seed: int) -> float:
    h = hashlib.sha256(f"{seed}:{i}".encode()).hexdigest()
    return (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1


@SimulationRegistry.register
class CenturySimulator(BaseSimulator):
    @property
    def id(self) -> str: return "century"
    @property
    def name(self) -> str: return "CENTURY Soil Organic Matter Model"
    @property
    def category(self) -> str: return "carbon_cycle"
    @property
    def description(self) -> str: return "Carbon and nutrient dynamics for grassland/forest/crop systems over long time scales."
    @property
    def version(self) -> str: return "2.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="initial_soc", label="Initial SOC (t C/ha)", type="float", default=60.0, min_value=5.0, max_value=300.0, unit="t C/ha", description="Initial soil organic carbon", required=False),
            SimulationParameter(name="annual_input", label="Annual C Input (t C/ha/yr)", type="float", default=4.0, min_value=0.0, max_value=25.0, unit="t C/ha/yr", description="Annual carbon inputs", required=False),
            SimulationParameter(name="temperature", label="Mean Annual Temp (C)", type="float", default=12.0, min_value=-5.0, max_value=35.0, unit="C", description="Mean annual temperature", required=False),
            SimulationParameter(name="years", label="Simulation Years", type="int", default=100, min_value=10, max_value=500, unit="yr", description="Years to simulate", required=False),
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
        soc = params.get("initial_soc", 60.0)
        cin = params.get("annual_input", 4.0); temp = params.get("temperature", 12.0)
        n = int(params.get("years", 100)); seed = int(params.get("seed", 1))
        k = max(0.02, 0.05 * (0.5 + temp / 25))
        soc_s, active_s, passive_s = [round(soc, 2)], [], []
        active = soc * 0.15; passive = soc * 0.85
        for t in range(n):
            active += cin - k * 2 * active + 0.01 * passive
            passive += 0.4 * k * 2 * active - 0.01 * passive
            active = max(0.1, active); passive = max(0.1, passive)
            soc = active + passive
            soc_s.append(round(soc, 2)); active_s.append(round(active, 2)); passive_s.append(round(passive, 2))
        return {
            "series": [
                {"key": "total_soc", "label": "Total SOC (t C/ha)", "color": "#16a34a", "values": soc_s, "kind": "line", "fill": True},
                {"key": "active", "label": "Active Pool (t C/ha)", "color": "#f59e0b", "values": active_s, "kind": "line"},
                {"key": "passive", "label": "Passive Pool (t C/ha)", "color": "#0284c7", "values": passive_s, "kind": "line"},
            ],
            "metrics": {
                "final_soc": round(soc, 2),
                "soc_change": round(soc - params.get("initial_soc", 60.0), 2),
                "equilibrium_soc": round(cin / max(0.01, k), 2),
                "sequestration_rate": round((soc - params.get("initial_soc", 60.0)) / n, 3),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
