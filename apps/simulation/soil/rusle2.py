"""
RUSLE2 (Revised Universal Soil Loss Equation)
=================
Annual soil erosion A = R*K*LS*C*P with monthly distribution and tolerance check.
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
class RUSLE2Simulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "rusle2"

    @property
    def name(self) -> str:
        return "RUSLE2 (Revised Universal Soil Loss Equation)"

    @property
    def category(self) -> str:
        return "soil"

    @property
    def description(self) -> str:
        return "Annual soil erosion A = R*K*LS*C*P with monthly distribution and tolerance check."

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="R", label="Rainfall Erosivity (R)", type="float", default=150.0, min_value=10.0, max_value=1000.0, unit="MJ.mm/ha.h.yr", description="Rainfall-runoff erosivity factor"),
            SimulationParameter(name="K", label="Soil Erodibility (K)", type="float", default=0.32, min_value=0.0, max_value=0.7, description="Soil erodibility factor"),
            SimulationParameter(name="LS", label="Slope Length-Steepness (LS)", type="float", default=1.5, min_value=0.0, max_value=15.0, description="Topographic factor"),
            SimulationParameter(name="C", label="Cover Management (C)", type="float", default=0.2, min_value=0.0, max_value=1.0, description="Cover-management factor"),
            SimulationParameter(name="P", label="Support Practice (P)", type="float", default=0.8, min_value=0.0, max_value=1.0, description="Support practice factor"),
            SimulationParameter(name="tolerance", label="Soil Loss Tolerance (T)", type="float", default=11.0, min_value=1.0, max_value=20.0, unit="t/ha/yr", description="Maximum sustainable soil loss"),
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
        R = params.get("R", 150.0); K = params.get("K", 0.32); LS = params.get("LS", 1.5)
        C = params.get("C", 0.2); P = params.get("P", 0.8); T = params.get("tolerance", 11.0)
        seed = int(params.get("seed", 1))
        A = R * K * LS * C * P
        n = 12
        monthly = []
        for t in range(n):
            seasonal = 1 + 0.8 * math.sin(2 * math.pi * t / 12 - math.pi / 3)
            monthly.append(max(0.0, A / 12 * seasonal * (1 + 0.1 * _noise(t, seed))))
        scale = A / max(0.01, sum(monthly))
        monthly = [round(m * scale, 2) for m in monthly]
        sustainability = "sustainable" if A <= T else ("moderate risk" if A <= 2 * T else "high risk")
        return {
            "series": [
                {"key": "monthly_erosion", "label": "Monthly Soil Loss (t/ha)", "color": "#a16207", "values": monthly, "kind": "bars"},
            ],
            "metrics": {
                "annual_soil_loss_t_ha": round(A, 2),
                "tolerance_t_ha": round(T, 2),
                "loss_to_tolerance_ratio": round(A / max(0.01, T), 2),
                "sustainability_index": round(max(0.0, 1 - A / (2 * T)), 3),
            },
            "sustainability": sustainability,
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
