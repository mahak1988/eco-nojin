"""
AquaCrop (FAO Crop Water Productivity Model) — Full daily simulation.
"""
import math
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator, SimulationParameter, SimulationResult,
    SimulationRegistry, SimulationStatus,
)

CROPS = {
    "wheat": dict(label="Wheat", cycle=150, tbase=0, tmax=30, kc_ini=0.40, kc_max=1.10, p_up=0.65, p_lo=0.20, hi=0.45, wp=33.7, root_ini=0.30, root_max=1.30),
    "maize": dict(label="Maize", cycle=140, tbase=8, tmax=42, kc_ini=0.35, kc_max=1.20, p_up=0.70, p_lo=0.30, hi=0.50, wp=33.7, root_ini=0.30, root_max=1.70),
    "rice": dict(label="Rice", cycle=130, tbase=10, tmax=40, kc_ini=1.05, kc_max=1.20, p_up=0.20, p_lo=0.00, hi=0.45, wp=19.0, root_ini=0.20, root_max=0.80),
}

@SimulationRegistry.register
class AquaCropSimulator(BaseSimulator):
    @property
    def id(self) -> str: return "aquacrop"
    @property
    def name(self) -> str: return "AquaCrop (FAO Crop Water Productivity Model)"
    @property
    def category(self) -> str: return "agriculture"
    @property
    def description(self) -> str: return "FAO AquaCrop daily simulation: soil water balance, Kc/Ks stress, biomass via water productivity."
    @property
    def version(self) -> str: return "2.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(name="crop", label="Crop Type", type="select", options=list(CROPS.keys()), default="wheat", description="Crop to simulate", required=True),
            SimulationParameter(name="planting_date", label="Planting Date", type="string", default="2024-03-15", description="Planting date (YYYY-MM-DD)", required=True),
            SimulationParameter(name="latitude", label="Latitude", type="float", default=35.7, min_value=-90.0, max_value=90.0, unit="deg", description="Latitude", required=False),
            SimulationParameter(name="longitude", label="Longitude", type="float", default=51.4, min_value=-180.0, max_value=180.0, unit="deg", description="Longitude", required=False),
            SimulationParameter(name="use_real_climate", label="Use Real Climate", type="select", options=["yes", "no"], default="no", description="Fetch real climate", required=False),
            SimulationParameter(name="field_capacity", label="Field Capacity", type="float", default=30.0, min_value=10.0, max_value=50.0, unit="%", description="Soil field capacity", required=False),
            SimulationParameter(name="wilting_point", label="Wilting Point", type="float", default=14.0, min_value=3.0, max_value=30.0, unit="%", description="Soil wilting point", required=False),
            SimulationParameter(name="soil_depth", label="Soil Depth", type="float", default=1.2, min_value=0.3, max_value=3.0, unit="m", description="Effective soil depth", required=False),
            SimulationParameter(name="total_irrigation", label="Total Irrigation", type="float", default=250.0, min_value=0.0, max_value=2000.0, unit="mm", description="Total irrigation applied", required=False),
            SimulationParameter(name="co2_ppm", label="Atmospheric CO2", type="float", default=420.0, min_value=280.0, max_value=1000.0, unit="ppm", description="CO2 concentration", required=False),
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
        crop_key = params.get("crop", "wheat")
        crop = CROPS.get(crop_key, CROPS["wheat"])
        n_days = crop["cycle"]
        
        fc = params.get("field_capacity", 30.0) / 100.0
        wp = params.get("wilting_point", 14.0) / 100.0
        soil_depth = params.get("soil_depth", 1.2)
        total_irr = params.get("total_irrigation", 250.0)
        co2 = params.get("co2_ppm", 420.0)
        co2_factor = 1.0 + 0.00035 * (co2 - 300)
        co2_factor = max(0.9, min(1.25, co2_factor))

        root = crop["root_ini"]
        sw = fc * root * 1000
        irr_per_day = total_irr / n_days
        biomass = 0.0
        sw_series, biomass_series = [], []
        total_et, total_transp = 0.0, 0.0

        for i in range(n_days):
            tmean = 15.0 + 10.0 * math.sin(math.pi * i / n_days)
            et0 = 5.0 * (0.6 + 0.6 * math.sin(math.pi * i / n_days))
            rain = (params.get("fallback_precip", 250.0) / n_days) * (1 + 0.5 * math.sin(math.pi * i / n_days))
            
            kc = crop["kc_ini"] + (crop["kc_max"] - crop["kc_ini"]) * (i / n_days)
            etc = kc * et0
            
            taw = (fc - wp) * root * 1000
            sw_max = fc * root * 1000
            sw = sw + rain + irr_per_day - etc
            drainage = max(0.0, sw - sw_max); sw -= drainage
            sw = max(0.0, sw)
            
            depletion = sw_max - sw
            frac = depletion / taw if taw > 0 else 1.0
            if frac <= crop["p_lo"]: ks = 1.0
            elif frac >= crop["p_up"]: ks = max(0.05, 1 - (frac - crop["p_up"]) / (1 - crop["p_up"]))
            else: ks = 1.0
            
            transp = ks * etc
            total_et += etc; total_transp += transp
            biomass += crop["wp"] * transp * co2_factor
            
            sw_series.append(round(sw, 1))
            biomass_series.append(round(biomass / 100, 2))

        biomass_t_ha = biomass / 100.0
        hi = crop["hi"]
        yield_t_ha = hi * biomass_t_ha
        wue = (yield_t_ha * 1000) / max(1.0, total_transp)

        return {
            "series": [
                {"key": "soil_water", "label": "Soil Water (mm)", "color": "#0284c7", "values": sw_series, "kind": "line", "fill": True},
                {"key": "biomass", "label": "Biomass (t/ha)", "color": "#16a34a", "values": biomass_series, "kind": "line", "fill": True},
            ],
            "metrics": {
                "yield_t_ha": round(yield_t_ha, 2),
                "biomass_t_ha": round(biomass_t_ha, 2),
                "water_use_efficiency_kg_m3": round(wue, 2),
                "total_et_mm": round(total_et, 1),
                "total_transpiration_mm": round(total_transp, 1),
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
