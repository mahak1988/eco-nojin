"""
Cost-Benefit Analysis Model — standardized model (Phase 4 upgrade).
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
class CBASimulator(BaseSimulator):
    @property
    def id(self) -> str: return "cba"
    @property
    def name(self) -> str: return "Cost-Benefit Analysis Model"
    @property
    def category(self) -> str: return "economics"
    @property
    def description(self) -> str: return "Economic feasibility: costs vs. benefits over time with NPV and IRR."
    @property
    def version(self) -> str: return "2.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="initial_investment", label="Initial Investment (M USD)", type="float", default=10.0, min_value=0.1, max_value=1000.0, unit="M USD", description="Upfront investment cost", required=False),
            SimulationParameter(name="annual_benefit", label="Annual Benefit (M USD/yr)", type="float", default=2.5, min_value=0.0, max_value=500.0, unit="M USD/yr", description="Mean annual benefit", required=False),
            SimulationParameter(name="annual_cost", label="Annual O&M Cost (M USD/yr)", type="float", default=0.5, min_value=0.0, max_value=200.0, unit="M USD/yr", description="Annual operation & maintenance cost", required=False),
            SimulationParameter(name="discount_rate", label="Discount Rate (%)", type="float", default=5.0, min_value=0.0, max_value=20.0, unit="%", description="Discount rate for NPV", required=False),
            SimulationParameter(name="years", label="Project Horizon (years)", type="int", default=25, min_value=5, max_value=60, unit="yr", description="Analysis period", required=False),
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
        inv = params.get("initial_investment", 10.0)
        benefit = params.get("annual_benefit", 2.5); om = params.get("annual_cost", 0.5)
        dr = params.get("discount_rate", 5.0) / 100.0
        n = int(params.get("years", 25)); seed = int(params.get("seed", 1))
        cum_cash, cum_disc = [-inv], [-inv]
        npv = -inv
        for t in range(1, n + 1):
            net = (benefit * (1 + 0.05 * _noise(t, seed))) - om
            cum_cash.append(round(cum_cash[-1] + net, 2))
            disc = net / ((1 + dr) ** t)
            npv += disc
            cum_disc.append(round(cum_disc[-1] + disc, 2))
        # simple IRR estimate (bisection)
        lo, hi = -0.5, 1.0
        for _ in range(50):
            mid = (lo + hi) / 2
            v = -inv + sum(((benefit - om) / ((1 + mid) ** t)) for t in range(1, n + 1))
            if v > 0: lo = mid
            else: hi = mid
        irr = (lo + hi) / 2
        return {
            "series": [
                {"key": "cumulative_cash", "label": "Cumulative Cash Flow (M USD)", "color": "#16a34a", "values": cum_cash, "kind": "line", "fill": True},
                {"key": "cumulative_discounted", "label": "Cumulative Discounted (M USD)", "color": "#0284c7", "values": cum_disc, "kind": "line"},
            ],
            "metrics": {
                "npv_m_usd": round(npv, 2),
                "irr_pct": round(irr * 100, 2),
                "payback_years": round(inv / max(0.01, benefit - om), 1),
                "benefit_cost_ratio": round((benefit / max(0.01, om + inv / n)), 2),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
