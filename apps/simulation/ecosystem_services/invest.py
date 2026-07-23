"""
InVEST (Ecosystem Services)
=================
Three ecosystem services (carbon storage, water yield, habitat quality) across a land-conversion gradient.
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
class InVESTSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "invest"

    @property
    def name(self) -> str:
        return "InVEST (Ecosystem Services)"

    @property
    def category(self) -> str:
        return "ecosystem_services"

    @property
    def description(self) -> str:
        return "Three ecosystem services (carbon storage, water yield, habitat quality) across a land-conversion gradient."

    @property
    def version(self) -> str:
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="forest_area", label="Forest Area (ha)", type="float", default=5000.0, min_value=0.0, max_value=100000.0, unit="ha", description="Forest area"),
            SimulationParameter(name="agri_area", label="Agricultural Area (ha)", type="float", default=3000.0, min_value=0.0, max_value=100000.0, unit="ha", description="Agricultural area"),
            SimulationParameter(name="carbon_density_forest", label="Forest C Density (t C/ha)", type="float", default=150.0, min_value=10.0, max_value=400.0, unit="t C/ha", description="Carbon density in forest"),
            SimulationParameter(name="precipitation", label="Precipitation (mm/yr)", type="float", default=800.0, min_value=100.0, max_value=3000.0, unit="mm", description="Annual precipitation"),
            SimulationParameter(name="aet_forest", label="Forest AET (mm/yr)", type="float", default=500.0, min_value=50.0, max_value=2000.0, unit="mm", description="Actual evapotranspiration in forest"),
            SimulationParameter(name="habitat_quality_forest", label="Forest Habitat Quality", type="float", default=0.9, min_value=0.0, max_value=1.0, description="Habitat quality index for forest"),
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
        forest = params.get("forest_area", 5000.0); agri = params.get("agri_area", 3000.0)
        c_forest = params.get("carbon_density_forest", 150.0); precip = params.get("precipitation", 800.0)
        aet_f = params.get("aet_forest", 500.0); hq_f = params.get("habitat_quality_forest", 0.9)
        c_agri = c_forest * 0.25; aet_agri = aet_f * 0.7; hq_agri = hq_f * 0.4
        total_area = forest + agri
        total_carbon = forest * c_forest + agri * c_agri
        total_wy = max(0.0, precip - aet_f) * forest / 10000 + max(0.0, precip - aet_agri) * agri / 10000
        habitat_index = (forest * hq_f + agri * hq_agri) / max(1.0, total_area)
        n = 11
        carbon_s, water_s, habitat_s = [], [], []
        for i in range(n):
            frac = i / (n - 1)
            f_now = forest * (1 - frac); a_now = agri + forest * frac
            carbon_s.append(round((f_now * c_forest + a_now * c_agri) / 1000, 1))
            water_s.append(round((max(0.0, precip - aet_f) * f_now + max(0.0, precip - aet_agri) * a_now) / 10000, 1))
            habitat_s.append(round((f_now * hq_f + a_now * hq_agri) / max(1.0, f_now + a_now), 3))
        return {
            "series": [
                {"key": "carbon", "label": "Carbon Storage (kt C)", "color": "#16a34a", "values": carbon_s, "kind": "line", "fill": True},
                {"key": "water_yield", "label": "Water Yield (MCM)", "color": "#0284c7", "values": water_s, "kind": "line"},
                {"key": "habitat", "label": "Habitat Quality Index", "color": "#f59e0b", "values": habitat_s, "kind": "line"},
            ],
            "metrics": {
                "total_carbon_t": round(total_carbon, 0),
                "total_water_yield_mcm": round(total_wy, 1),
                "habitat_quality_index": round(habitat_index, 3),
                "carbon_per_ha": round(total_carbon / max(1.0, total_area), 1),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
