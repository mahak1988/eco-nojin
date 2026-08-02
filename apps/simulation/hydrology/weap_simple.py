"""WEAP-simple regional water balance — pure Python proxy (not SEI WEAP software)."""

from __future__ import annotations

import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator,
    SimulationParameter,
    SimulationResult,
    SimulationRegistry,
    SimulationStatus,
)


@SimulationRegistry.register
class WEAPSimpleSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "weap-simple"

    @property
    def name(self) -> str:
        return "WEAP-simple water balance"

    @property
    def category(self) -> str:
        return "hydrology"

    @property
    def description(self) -> str:
        return "Monthly supply–demand balance proxy. Not SEI WEAP."

    @property
    def version(self) -> str:
        return "1.0.0-proxy"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="annual_inflow_mcm", label="Annual inflow", type="float", default=120.0, min_value=1.0, max_value=10000.0, unit="MCM", required=True),
            SimulationParameter(name="annual_demand_mcm", label="Annual demand", type="float", default=100.0, min_value=1.0, max_value=10000.0, unit="MCM", required=True),
            SimulationParameter(name="reservoir_storage_mcm", label="Storage", type="float", default=50.0, min_value=0.0, max_value=5000.0, unit="MCM", required=True),
            SimulationParameter(name="loss_fraction", label="System loss", type="float", default=0.15, min_value=0.0, max_value=0.5, required=True),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        t0 = time.time()
        err = self.validate(parameters)
        if err:
            return SimulationResult(simulator_id=self.id, simulator_name=self.name, status=SimulationStatus.FAILED, parameters=parameters, error="; ".join(err))
        inflow = float(parameters["annual_inflow_mcm"])
        demand = float(parameters["annual_demand_mcm"])
        storage = float(parameters["reservoir_storage_mcm"])
        loss = float(parameters["loss_fraction"])
        monthly_in = inflow / 12
        monthly_dem = demand / 12
        s = storage
        unmet = []
        stor = []
        for _ in range(12):
            available = s + monthly_in * (1 - loss)
            delivered = min(monthly_dem, available)
            short = max(0.0, monthly_dem - delivered)
            s = max(0.0, available - delivered)
            unmet.append(round(short, 3))
            stor.append(round(s, 3))
        reliability = 1.0 - (sum(1 for u in unmet if u > 1e-6) / 12)
        outputs = {
            "series": [
                {"key": "unmet_demand", "label": "Unmet (MCM)", "values": unmet, "kind": "bar"},
                {"key": "storage", "label": "Storage (MCM)", "values": stor, "kind": "line"},
            ],
            "metrics": {
                "annual_unmet_mcm": round(sum(unmet), 3),
                "end_storage_mcm": stor[-1],
                "supply_reliability": round(reliability, 3),
                "stress_index": round(demand / max(inflow, 1e-6), 3),
                "engine": "weap_simple_proxy",
            },
            "disclaimer": "Educational water balance — not SEI WEAP.",
        }
        return SimulationResult(
            simulator_id=self.id,
            simulator_name=self.name,
            status=SimulationStatus.COMPLETED,
            parameters=parameters,
            outputs=outputs,
            metrics={k: float(v) for k, v in outputs["metrics"].items() if isinstance(v, (int, float))},
            charts={x["key"]: x["values"] for x in outputs["series"]},
            execution_time_ms=(time.time() - t0) * 1000,
        )
