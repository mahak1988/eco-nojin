"""
HOMER (Hybrid Renewable Energy)
=================
Solar PV + wind generation against demand; renewable fraction and unmet load.
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
class HOMERSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "homer"

    @property
    def name(self) -> str:
        return "HOMER (Hybrid Renewable Energy)"

    @property
    def category(self) -> str:
        return "energy"

    @property
    def description(self) -> str:
        return "Solar PV + wind generation against demand; renewable fraction and unmet load."

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="solar_kw", label="Solar Capacity (kW)", type="float", default=100.0, min_value=0.0, max_value=10000.0, unit="kW", description="Installed PV capacity"),
            SimulationParameter(name="wind_kw", label="Wind Capacity (kW)", type="float", default=50.0, min_value=0.0, max_value=10000.0, unit="kW", description="Installed wind capacity"),
            SimulationParameter(name="irradiance", label="Solar Irradiance (kWh/m2/day)", type="float", default=5.0, min_value=1.0, max_value=8.0, unit="kWh/m2/day", description="Average daily solar resource"),
            SimulationParameter(name="wind_speed", label="Avg Wind Speed (m/s)", type="float", default=6.0, min_value=0.0, max_value=25.0, unit="m/s", description="Mean hub-height wind speed"),
            SimulationParameter(name="demand_kw", label="Peak Demand (kW)", type="float", default=80.0, min_value=1.0, max_value=10000.0, unit="kW", description="Peak electrical demand"),
            SimulationParameter(name="days", label="Simulation Days", type="int", default=30, min_value=1, max_value=365, unit="day", description="Number of days to simulate"),
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
        solar_kw = params.get("solar_kw", 100.0)
        wind_kw = params.get("wind_kw", 50.0)
        irr = params.get("irradiance", 5.0)
        v = params.get("wind_speed", 6.0)
        demand = params.get("demand_kw", 80.0)
        n = int(params.get("days", 30))
        seed = int(params.get("seed", 1))
        gen, solar_g, wind_g, dem, unmet = [], [], [], [], []
        for t in range(n):
            solar_day = solar_kw * irr * 0.75 * (1 + 0.1 * _noise(t, seed))
            v_eff = max(0.0, v + _noise(t + 50, seed) * 2)
            wind_factor = min(1.0, (v_eff / 12) ** 3) if v_eff < 12 else 1.0
            wind_day = wind_kw * 24 * 0.35 * wind_factor
            total_gen = solar_day + wind_day
            daily_demand = demand * 24 * (0.6 + 0.2 * math.sin(2 * math.pi * t / 365) + 0.1 * _noise(t + 90, seed))
            gen.append(round(total_gen, 1)); solar_g.append(round(solar_day, 1))
            wind_g.append(round(wind_day, 1)); dem.append(round(daily_demand, 1))
            unmet.append(round(max(0.0, daily_demand - total_gen), 1))
        tg, td = sum(gen), sum(dem)
        return {
            "series": [
                {"key": "generation", "label": "Generation (kWh/day)", "color": "#16a34a", "values": gen, "kind": "line", "fill": True},
                {"key": "demand", "label": "Demand (kWh/day)", "color": "#dc2626", "values": dem, "kind": "line"},
                {"key": "solar", "label": "Solar (kWh/day)", "color": "#f59e0b", "values": solar_g, "kind": "line"},
                {"key": "wind", "label": "Wind (kWh/day)", "color": "#0284c7", "values": wind_g, "kind": "line"},
            ],
            "metrics": {
                "total_generation_kwh": round(tg, 0),
                "total_demand_kwh": round(td, 0),
                "renewable_fraction": round(min(1.5, tg / max(1.0, td)), 3),
                "unmet_demand_kwh": round(sum(unmet), 0),
                "capacity_factor": round(tg / max(1.0, (solar_kw + wind_kw) * 24 * n), 3),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
