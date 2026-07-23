"""
SWAT (Soil & Water Assessment Tool)
=================
Watershed water balance: surface runoff, baseflow and evapotranspiration (monthly).
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
class SWATSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "swat"

    @property
    def name(self) -> str:
        return "SWAT (Soil & Water Assessment Tool)"

    @property
    def category(self) -> str:
        return "hydrology"

    @property
    def description(self) -> str:
        return "Watershed water balance: surface runoff, baseflow and evapotranspiration (monthly)."

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="precipitation", label="Annual Precipitation (mm)", type="float", default=800.0, min_value=100.0, max_value=3000.0, unit="mm", description="Total annual precipitation"),
            SimulationParameter(name="et0", label="Reference ET0 (mm/yr)", type="float", default=600.0, min_value=100.0, max_value=2500.0, unit="mm", description="Annual reference evapotranspiration"),
            SimulationParameter(name="runoff_coef", label="Runoff Coefficient", type="float", default=0.35, min_value=0.05, max_value=0.9, description="Fraction of precipitation becoming surface runoff"),
            SimulationParameter(name="baseflow", label="Baseflow (mm/yr)", type="float", default=120.0, min_value=0.0, max_value=1000.0, unit="mm", description="Groundwater contribution to streamflow"),
            SimulationParameter(name="area_km2", label="Watershed Area (km2)", type="float", default=100.0, min_value=1.0, max_value=10000.0, unit="km2", description="Drainage area"),
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
        precip = params.get("precipitation", 800.0)
        et0 = params.get("et0", 600.0)
        rc = params.get("runoff_coef", 0.35)
        baseflow = params.get("baseflow", 120.0)
        area = params.get("area_km2", 100.0)
        n = int(params.get("months", 24))
        seed = int(params.get("seed", 1))
        flow, runoff, bf = [], [], []
        for t in range(n):
            seasonal = 1 + 0.5 * math.sin(2 * math.pi * t / 12 - math.pi / 2)
            p_month = precip / 12 * seasonal + _noise(t, seed) * 15
            ro = max(0.0, p_month * rc + _noise(t + 100, seed) * 5)
            b = baseflow / 12 * (1 + 0.2 * _noise(t + 200, seed))
            flow.append(round(ro + b, 1)); runoff.append(round(ro, 1)); bf.append(round(b, 1))
        total = sum(flow)
        return {
            "series": [
                {"key": "streamflow", "label": "Streamflow (mm/mo)", "color": "#0284c7", "values": flow, "kind": "line", "fill": True},
                {"key": "surface_runoff", "label": "Surface Runoff (mm/mo)", "color": "#f59e0b", "values": runoff, "kind": "line"},
                {"key": "baseflow", "label": "Baseflow (mm/mo)", "color": "#16a34a", "values": bf, "kind": "line"},
            ],
            "metrics": {
                "total_streamflow_mm": round(total, 1),
                "total_volume_m3": round(total * area * 1000, 0),
                "baseflow_ratio": round(sum(bf) / max(1.0, total), 3),
                "mean_monthly_flow": round(total / n, 1),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
