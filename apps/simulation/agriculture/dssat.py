"""
DSSAT (Crop Growth & Yield)
=================
Thermal-time (GDD) crop growth with water and nitrogen limitation; logistic biomass.
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
class DSSATSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "dssat"

    @property
    def name(self) -> str:
        return "DSSAT (Crop Growth & Yield)"

    @property
    def category(self) -> str:
        return "agriculture"

    @property
    def description(self) -> str:
        return "Thermal-time (GDD) crop growth with water and nitrogen limitation; logistic biomass."

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="crop", label="Crop", type="select", options=["wheat", "maize", "rice"], default="wheat", description="Crop type"),
            SimulationParameter(name="gdd_required", label="GDD Required (C.day)", type="float", default=1500.0, min_value=500.0, max_value=3000.0, unit="C.day", description="Growing degree days to maturity"),
            SimulationParameter(name="base_temp", label="Base Temperature (C)", type="float", default=5.0, min_value=0.0, max_value=15.0, unit="C", description="Base temperature for growth"),
            SimulationParameter(name="mean_temp", label="Mean Growing Temp (C)", type="float", default=22.0, min_value=5.0, max_value=40.0, unit="C", description="Mean temperature during season"),
            SimulationParameter(name="water_factor", label="Water Availability Factor", type="float", default=0.85, min_value=0.1, max_value=1.0, description="Water stress factor (1=no stress)"),
            SimulationParameter(name="nitrogen_factor", label="Nitrogen Availability Factor", type="float", default=0.9, min_value=0.1, max_value=1.0, description="Nitrogen stress factor (1=no stress)"),
            SimulationParameter(name="potential_yield", label="Potential Yield (t/ha)", type="float", default=10.0, min_value=1.0, max_value=20.0, unit="t/ha", description="Non-stressed potential yield"),
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
        gdd_req = params.get("gdd_required", 1500.0); base_t = params.get("base_temp", 5.0)
        mean_t = params.get("mean_temp", 22.0); wf = params.get("water_factor", 0.85)
        nf = params.get("nitrogen_factor", 0.9); pot_yield = params.get("potential_yield", 10.0)
        seed = int(params.get("seed", 1))
        daily_gdd = max(0.0, mean_t - base_t)
        n = min(int(gdd_req / max(0.1, daily_gdd)), 200)
        stress = min(wf, nf)
        biomass, lai = [], []
        cum = 0.0
        for t in range(n):
            cum += daily_gdd * (1 + 0.1 * _noise(t, seed))
            progress = min(1.0, cum / gdd_req)
            biomass.append(round(pot_yield * stress * 8 * (1 / (1 + math.exp(-8 * (progress - 0.5)))), 2))
            lai.append(round(6 * stress * (1 / (1 + math.exp(-10 * (progress - 0.4)))), 2))
        final_yield = pot_yield * stress * (1 - 0.1 * max(0.0, 1 - wf))
        return {
            "series": [
                {"key": "biomass", "label": "Biomass (t/ha)", "color": "#16a34a", "values": biomass, "kind": "line", "fill": True},
                {"key": "lai", "label": "Leaf Area Index", "color": "#0284c7", "values": lai, "kind": "line"},
            ],
            "metrics": {
                "yield_t_ha": round(final_yield, 2),
                "days_to_maturity": n,
                "total_gdd": round(cum, 0),
                "stress_factor": round(stress, 3),
                "yield_gap_pct": round((1 - final_yield / pot_yield) * 100, 1),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
