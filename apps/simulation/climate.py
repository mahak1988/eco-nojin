"""
Climate Scenario Simulator
==========================
Temperature, precipitation, extreme events and NDVI from CO2, climate
sensitivity and an IPCC-style pathway. Deterministic (seeded noise) so
server charts never jump on re-render.

Physics (simplified, educational, NOT a GCM):
    equilibrium warming ~ sensitivity * log2(CO2 / 280)
    transient progression ~ year / horizon
    precipitation reacts to warming; extremes scale with anomaly.
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

SCENARIO_OPTIONS = ["baseline", "rcp26", "rcp45", "rcp85", "ssp126", "ssp245", "ssp585"]
SCENARIO_FORCING = {
    "baseline": 0.0, "rcp26": 0.45, "rcp45": 0.85, "rcp85": 1.6,
    "ssp126": 0.45, "ssp245": 0.85, "ssp585": 1.6,
}


def _noise(i: int, seed: int) -> float:
    h = hashlib.sha256(f"{seed}:{i}".encode()).hexdigest()
    return (int(h[:8], 16) / 0xFFFFFFFF) * 2 - 1


@SimulationRegistry.register
class ClimateSimulator(BaseSimulator):
    @property
    def id(self) -> str: return "climate"
    @property
    def name(self) -> str: return "Climate Scenario Simulator"
    @property
    def category(self) -> str: return "climate"
    @property
    def description(self) -> str:
        return "Simulates temperature, precipitation, extreme events and NDVI from CO2, sensitivity and an IPCC pathway."
    @property
    def version(self) -> str: return "2.1.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="scenario", label="Pathway", type="select",
                                default="rcp45", options=SCENARIO_OPTIONS,
                                description="IPCC pathway", required=True),
            SimulationParameter(name="co2_ppm", label="CO2 (ppm)", type="float",
                                default=420.0, unit="ppm", min_value=150.0, max_value=1200.0,
                                description="Atmospheric CO2 concentration", required=True),
            SimulationParameter(name="climate_sensitivity", label="Climate sensitivity (K)", type="float",
                                default=3.0, unit="K", min_value=1.0, max_value=6.0,
                                description="Warming per CO2 doubling", required=True),
            SimulationParameter(name="years", label="Horizon (years)", type="int",
                                default=50, unit="yr", min_value=1.0, max_value=120.0,
                                description="Simulation horizon", required=True),
            SimulationParameter(name="base_temp_c", label="Base temperature (C)", type="float",
                                default=15.0, unit="C", min_value=-10.0, max_value=40.0,
                                description="Baseline mean temperature", required=False),
            SimulationParameter(name="base_precip_mm", label="Base precipitation (mm/yr)", type="float",
                                default=600.0, unit="mm", min_value=0.0, max_value=3000.0,
                                description="Baseline annual precipitation", required=False),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                                    status=SimulationStatus.FAILED, parameters=parameters,
                                    error="; ".join(errors))
        try:
            outputs = await self._run_simulation(parameters)
            elapsed = (time.time() - start) * 1000
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                                    status=SimulationStatus.COMPLETED, parameters=parameters,
                                    outputs=outputs, metrics=self._calculate_metrics(outputs),
                                    charts=self._generate_charts(outputs), execution_time_ms=elapsed)
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SimulationResult(simulator_id=self.id, simulator_name=self.name,
                                    status=SimulationStatus.FAILED, parameters=parameters,
                                    error=str(e), execution_time_ms=elapsed)

    async def _run_simulation(self, params: dict[str, Any]) -> dict:
        # Accept backend keys and the lighter client keys (co2 / sensitivity).
        try:
            co2 = float(params.get("co2_ppm", params.get("co2", 420)))
            sens = float(params.get("climate_sensitivity", params.get("sensitivity", 3.0)))
            years = int(float(params.get("years", 50)))
            base_temp = float(params.get("base_temp_c", params.get("base_temp", 15.0)))
            base_precip = float(params.get("base_precip_mm", params.get("base_precip", 600.0)))
            seed = int(float(params.get("seed", 1)))
        except (TypeError, ValueError) as e:
            raise ValueError(f"Invalid numeric parameter: {e}")
        scenario = str(params.get("scenario", "rcp45")).lower()
        if scenario not in SCENARIO_FORCING:
            scenario = "rcp45"

        scen_mult = SCENARIO_FORCING[scenario]
        n = max(12, min(years, 120))
        base_ndvi, base_extreme = 0.62, 4.0

        temp_v, precip_v, extreme_v, ndvi_v = [], [], [], []
        for t in range(n):
            prog = (t + 1) / n
            noise_t = _noise(t, seed)
            eq = sens * math.log2(max(co2, 150) / 280.0)
            anomaly = eq * prog * (0.6 + 0.4 * scen_mult) + math.sin(2 * math.pi * t / 12) * 0.12 + noise_t * 0.12
            temp_v.append(round(base_temp + anomaly, 2))
            precip = base_precip * (1 - 1.8 * anomaly * 0.01 * prog) * (1 + 0.25 * math.sin(2 * math.pi * t / 12 + 1)) + noise_t * 8
            precip_v.append(round(max(0.0, precip), 1))
            extreme_v.append(max(0, round(base_extreme + 2.5 * max(0.0, anomaly) * prog + max(0.0, noise_t) * 1.5)))
            ndvi = base_ndvi - 0.025 * anomaly * prog + 0.0002 * (precip - base_precip) + noise_t * 0.015
            ndvi_v.append(round(max(0.05, min(0.95, ndvi)), 3))

        series = [
            {"key": "temp_anomaly", "label": "Temperature (C)", "color": "#dc2626", "values": temp_v, "kind": "line", "fill": True},
            {"key": "precipitation", "label": "Precipitation (mm)", "color": "#0284c7", "values": precip_v, "kind": "line", "fill": True},
            {"key": "extreme_events", "label": "Extreme events / yr", "color": "#f59e0b", "values": extreme_v, "kind": "bars"},
            {"key": "ndvi", "label": "NDVI", "color": "#16a34a", "values": ndvi_v, "kind": "line"},
        ]
        metrics = {
            "mean_temp": round(sum(temp_v) / n, 2),
            "temp_change": round(temp_v[-1] - base_temp, 2),
            "precip_change_pct": round((sum(precip_v) / n - base_precip) / base_precip * 100, 1),
            "total_extreme": int(sum(extreme_v)),
            "ndvi_change": round(ndvi_v[-1] - base_ndvi, 3),
        }
        return {"series": series, "metrics": metrics, "scenario": scenario, "co2": co2, "years": n}

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
