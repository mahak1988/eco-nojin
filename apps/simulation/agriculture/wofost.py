"""
WOFOST (World Food Studies) — standardized model (Phase 4 upgrade).
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
class WOFOSTSimulator(BaseSimulator):
    @property
    def id(self) -> str: return "wofost"
    @property
    def name(self) -> str: return "WOFOST (World Food Studies)"
    @property
    def category(self) -> str: return "agriculture"
    @property
    def description(self) -> str: return "Crop growth and production for food security: radiation-driven biomass with water limitation."
    @property
    def version(self) -> str: return "2.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="crop", label="Crop", type="select", options=["wheat", "maize", "rice", "barley"], default="wheat", description="Crop type", required=False),
            SimulationParameter(name="radiation", label="Season Radiation (kJ/m2/day)", type="float", default=15000.0, min_value=5000.0, max_value=30000.0, unit="kJ/m2/day", description="Mean daily global radiation", required=False),
            SimulationParameter(name="water_availability", label="Water Availability (0-1)", type="float", default=0.8, min_value=0.1, max_value=1.0, description="Fraction of crop water requirement met", required=False),
            SimulationParameter(name="cycle_days", label="Crop Cycle (days)", type="int", default=140, min_value=60, max_value=250, unit="day", description="Growing season length", required=False),
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
        rad = params.get("radiation", 15000.0)
        water = params.get("water_availability", 0.8)
        n = int(params.get("cycle_days", 140)); seed = int(params.get("seed", 1))
        rue = 2.2  # radiation use efficiency g/MJ
        biomass, lai = [], []
        cum = 0.0
        for t in range(n):
            progress = t / n
            par = rad * 0.5 * (0.5 + 0.5 * math.sin(math.pi * progress))  # PAR
            lai_t = 6 * water * (1 / (1 + math.exp(-10 * (progress - 0.35))))
            light_int = 1 - math.exp(-0.6 * lai_t)
            cum += rue * (par / 1000) * light_int * water
            biomass.append(round(cum / 100, 2)); lai.append(round(lai_t, 2))
        yield_t = cum * 0.45 / 100  # harvest index
        return {
            "series": [
                {"key": "biomass", "label": "Biomass (t/ha)", "color": "#16a34a", "values": biomass, "kind": "line", "fill": True},
                {"key": "lai", "label": "Leaf Area Index", "color": "#0284c7", "values": lai, "kind": "line"},
            ],
            "metrics": {
                "yield_t_ha": round(yield_t, 2),
                "total_biomass_t_ha": round(cum / 100, 2),
                "max_lai": round(max(lai), 2),
                "radiation_use_efficiency": round(cum / max(1, rad * n / 1000), 2),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
