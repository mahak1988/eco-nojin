"""Cost–benefit analysis (CBA) — pure Python NPV/BCR."""

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
class CBASimpleSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "cba"

    @property
    def name(self) -> str:
        return "CBA cost-benefit"

    @property
    def category(self) -> str:
        return "economics"

    @property
    def description(self) -> str:
        return "NPV, BCR, simple payback from annual cost/benefit streams."

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="capex", label="Initial investment", type="float", default=100000.0, min_value=0.0, unit="currency", required=True),
            SimulationParameter(name="annual_benefit", label="Annual benefit", type="float", default=25000.0, min_value=0.0, required=True),
            SimulationParameter(name="annual_cost", label="Annual O&M cost", type="float", default=5000.0, min_value=0.0, required=True),
            SimulationParameter(name="years", label="Horizon", type="int", default=15, min_value=1, max_value=50, required=True),
            SimulationParameter(name="discount_rate", label="Discount rate", type="float", default=0.08, min_value=0.0, max_value=0.5, required=True),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        t0 = time.time()
        err = self.validate(parameters)
        if err:
            return SimulationResult(simulator_id=self.id, simulator_name=self.name, status=SimulationStatus.FAILED, parameters=parameters, error="; ".join(err))
        capex = float(parameters["capex"])
        benefit = float(parameters["annual_benefit"])
        cost = float(parameters["annual_cost"])
        years = int(parameters["years"])
        r = float(parameters["discount_rate"])
        npv = -capex
        pv_b = 0.0
        pv_c = 0.0
        cash = []
        payback = None
        cum = -capex
        for y in range(1, years + 1):
            net = benefit - cost
            disc = (1 + r) ** y
            npv += net / disc
            pv_b += benefit / disc
            pv_c += cost / disc
            cum += net
            cash.append(round(cum, 2))
            if payback is None and cum >= 0:
                payback = y
        bcr = pv_b / max(capex + pv_c, 1e-9)
        outputs = {
            "series": [{"key": "cumulative_cash", "label": "Cumulative cash", "values": cash, "kind": "line"}],
            "metrics": {
                "npv": round(npv, 2),
                "bcr": round(bcr, 4),
                "payback_years": float(payback or years),
                "pv_benefits": round(pv_b, 2),
                "pv_costs": round(capex + pv_c, 2),
            },
        }
        return SimulationResult(
            simulator_id=self.id,
            simulator_name=self.name,
            status=SimulationStatus.COMPLETED,
            parameters=parameters,
            outputs=outputs,
            metrics=outputs["metrics"],
            charts={"cumulative_cash": cash},
            execution_time_ms=(time.time() - t0) * 1000,
        )
