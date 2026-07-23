"""
WEAP (Water Evaluation And Planning)
=================
Monthly water supply-demand balance with priority allocation (domestic > industrial > agricultural).
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
class WEAPSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "weap"

    @property
    def name(self) -> str:
        return "WEAP (Water Evaluation And Planning)"

    @property
    def category(self) -> str:
        return "hydrology"

    @property
    def description(self) -> str:
        return "Monthly water supply-demand balance with priority allocation (domestic > industrial > agricultural)."

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="supply", label="Water Supply (MCM/yr)", type="float", default=500.0, min_value=10.0, max_value=10000.0, unit="MCM", description="Total annual water supply"),
            SimulationParameter(name="demand_agri", label="Agricultural Demand (MCM/yr)", type="float", default=300.0, min_value=0.0, max_value=10000.0, unit="MCM", description="Annual agricultural demand"),
            SimulationParameter(name="demand_domestic", label="Domestic Demand (MCM/yr)", type="float", default=100.0, min_value=0.0, max_value=5000.0, unit="MCM", description="Annual domestic demand"),
            SimulationParameter(name="demand_industrial", label="Industrial Demand (MCM/yr)", type="float", default=80.0, min_value=0.0, max_value=5000.0, unit="MCM", description="Annual industrial demand"),
            SimulationParameter(name="reservoir_cap", label="Reservoir Capacity (MCM)", type="float", default=200.0, min_value=0.0, max_value=10000.0, unit="MCM", description="Storage capacity"),
            SimulationParameter(name="months", label="Simulation Months", type="int", default=24, min_value=6, max_value=120, unit="mo", description="Number of months to simulate"),
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
        supply = params.get("supply", 500.0); d_agri = params.get("demand_agri", 300.0)
        d_dom = params.get("demand_domestic", 100.0); d_ind = params.get("demand_industrial", 80.0)
        res_cap = params.get("reservoir_cap", 200.0); n = int(params.get("months", 24))
        seed = int(params.get("seed", 1))
        storage = res_cap * 0.5
        unmet_total, supply_s, demand_s = [], [], []
        reliable = 0
        for t in range(n):
            seasonal = 1 + 0.4 * math.sin(2 * math.pi * t / 12 - math.pi / 2)
            inflow = supply / 12 * seasonal * (1 + 0.1 * _noise(t, seed))
            dom = d_dom / 12; ind = d_ind / 12; agri = d_agri / 12 * (2 - seasonal)
            available = storage + inflow
            a_dom = min(dom, available); available -= a_dom
            a_ind = min(ind, available); available -= a_ind
            a_agri = min(agri, available); available -= a_agri
            storage = min(res_cap, available)
            total_unmet = (dom - a_dom) + (ind - a_ind) + (agri - a_agri)
            unmet_total.append(round(total_unmet, 2))
            supply_s.append(round(inflow, 1)); demand_s.append(round(dom + ind + agri, 1))
            if total_unmet < 0.01 * (dom + ind + agri):
                reliable += 1
        return {
            "series": [
                {"key": "supply", "label": "Supply (MCM/mo)", "color": "#0284c7", "values": supply_s, "kind": "line", "fill": True},
                {"key": "demand", "label": "Demand (MCM/mo)", "color": "#dc2626", "values": demand_s, "kind": "line"},
                {"key": "unmet", "label": "Unmet Demand (MCM/mo)", "color": "#f59e0b", "values": unmet_total, "kind": "bars"},
            ],
            "metrics": {
                "reliability_pct": round(reliable / n * 100, 1),
                "total_unmet_mcm": round(sum(unmet_total), 1),
                "final_storage_mcm": round(storage, 1),
                "demand_to_supply_ratio": round((d_agri + d_dom + d_ind) / max(1.0, supply), 3),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
