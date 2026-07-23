"""
Generic Crop Growth Model — standardized model (Phase 4 upgrade).
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
class CropModelSimulator(BaseSimulator):
    @property
    def id(self) -> str: return "crop-model"
    @property
    def name(self) -> str: return "Generic Crop Growth Model"
    @property
    def category(self) -> str: return "agriculture"
    @property
    def description(self) -> str: return "Simplified crop growth: light interception, radiation use efficiency, and harvest index."
    @property
    def version(self) -> str: return "2.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="potential_yield", label="Potential Yield (t/ha)", type="float", default=10.0, min_value=1.0, max_value=25.0, unit="t/ha", description="Non-stressed potential yield", required=False),
            SimulationParameter(name="water_factor", label="Water Factor (0-1)", type="float", default=0.85, min_value=0.1, max_value=1.0, description="Water availability factor", required=False),
            SimulationParameter(name="nutrient_factor", label="Nutrient Factor (0-1)", type="float", default=0.9, min_value=0.1, max_value=1.0, description="Nutrient availability factor", required=False),
            SimulationParameter(name="cycle_days", label="Crop Cycle (days)", type="int", default=120, min_value=60, max_value=250, unit="day", description="Growing season length", required=False),
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
        pot = params.get("potential_yield", 10.0)
        wf = params.get("water_factor", 0.85); nf = params.get("nutrient_factor", 0.9)
        n = int(params.get("cycle_days", 120)); seed = int(params.get("seed", 1))
        stress = min(wf, nf)
        biomass, yield_s = [], []
        for t in range(n):
            progress = t / n
            bm = pot * stress * 8 * (1 / (1 + math.exp(-8 * (progress - 0.5))))
            biomass.append(round(bm, 2))
            yield_s.append(round(bm * 0.45, 2))
        final_yield = pot * stress * 0.95
        return {
            "series": [
                {"key": "biomass", "label": "Biomass (t/ha)", "color": "#16a34a", "values": biomass, "kind": "line", "fill": True},
                {"key": "yield", "label": "Grain Yield (t/ha)", "color": "#f59e0b", "values": yield_s, "kind": "line"},
            ],
            "metrics": {
                "yield_t_ha": round(final_yield, 2),
                "biomass_t_ha": round(pot * stress * 8, 2),
                "stress_factor": round(stress, 3),
                "yield_gap_pct": round((1 - final_yield / pot) * 100, 1),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
