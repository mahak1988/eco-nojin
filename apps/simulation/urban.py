"""
Urban Growth & Land Use Simulator — standardized model (Phase 4 upgrade).
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
class UrbanSimulator(BaseSimulator):
    @property
    def id(self) -> str: return "urban"
    @property
    def name(self) -> str: return "Urban Growth & Land Use Simulator"
    @property
    def category(self) -> str: return "urban"
    @property
    def description(self) -> str: return "Simulates urban expansion, land use change and population dynamics (cellular-automata style)."
    @property
    def version(self) -> str: return "2.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="initial_population", label="Initial Population", type="float", default=100000.0, min_value=1000.0, max_value=20000000.0, description="Starting population", required=False),
            SimulationParameter(name="growth_rate", label="Annual Growth Rate (%)", type="float", default=2.0, min_value=-2.0, max_value=8.0, unit="%", description="Population growth rate", required=False),
            SimulationParameter(name="urban_area_km2", label="Initial Urban Area (km2)", type="float", default=50.0, min_value=1.0, max_value=5000.0, unit="km2", description="Initial built-up area", required=False),
            SimulationParameter(name="years", label="Simulation Years", type="int", default=30, min_value=5, max_value=100, unit="yr", description="Years to simulate", required=False),
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
        pop = params.get("initial_population", 100000.0)
        gr = params.get("growth_rate", 2.0) / 100.0
        area = params.get("urban_area_km2", 50.0)
        n = int(params.get("years", 30)); seed = int(params.get("seed", 1))
        pop_s, area_s, density_s = [round(pop, 0)], [round(area, 2)], []
        for t in range(n):
            pop *= (1 + gr * (1 + 0.1 * _noise(t, seed)))
            area *= (1 + gr * 0.7 * (1 + 0.1 * _noise(t + 50, seed)))
            pop_s.append(round(pop, 0)); area_s.append(round(area, 2))
            density_s.append(round(pop / max(1, area), 0))
        return {
            "series": [
                {"key": "population", "label": "Population", "color": "#7c3aed", "values": pop_s, "kind": "line", "fill": True},
                {"key": "urban_area", "label": "Urban Area (km2)", "color": "#dc2626", "values": area_s, "kind": "line"},
                {"key": "density", "label": "Density (pop/km2)", "color": "#0284c7", "values": density_s, "kind": "line"},
            ],
            "metrics": {
                "final_population": round(pop, 0),
                "final_urban_area_km2": round(area, 2),
                "population_growth_pct": round((pop / params.get("initial_population", 100000.0) - 1) * 100, 1),
                "final_density": round(pop / max(1, area), 0),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
