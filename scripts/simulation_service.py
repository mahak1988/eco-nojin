from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from typing import Any, Dict, Literal, Optional, Tuple

from scripts.models.soil_carbon.aquacrop import AquaCropModel
from scripts.models.soil_carbon.rothc import RothCModel
from scripts.models.hydrology.swat_plus import SWATPlusModel


IrrigationMethod = Literal["drip", "sprinkler", "flood"]


@dataclass(frozen=True)
class FarmerSimulationInput:
    fid: str
    crop_type: str
    planting_date: str
    expected_harvest: str
    irrigation_method: IrrigationMethod = "drip"

    # Minimal optional inputs (extend later)
    temp_avg_c: float = 20.0
    precip_mm: float = 300.0
    field_capacity: float = 0.3
    clay_pct: float = 25.0
    soc_percent: float = 1.2

    # management
    residue_return: bool = True
    years: int = 10


class SimulationService:
    """
    Simulation orchestration service.

    Performance upgrades in this step:
    - model output caching (pure-input memoization) to avoid repeated computations.
    - lightweight structure to allow async/worker migration later.
    """

    def __init__(
        self,
        aquacrop_model: Optional[AquaCropModel] = None,
        rothc_model: Optional[RothCModel] = None,
        swat_model: Optional[SWATPlusModel] = None,
    ):
        self.aquacrop = aquacrop_model or AquaCropModel()
        self.rothc = rothc_model or RothCModel()
        self.swat = swat_model or SWATPlusModel()

    @lru_cache(maxsize=256)
    def _run_aquacrop_cached(
        self,
        temp_avg_c: float,
        precip_mm: float,
        field_capacity: float,
        crop_type: str,
    ) -> Dict[str, Any]:
        weather = {"temp_avg_c": temp_avg_c, "precip_mm": precip_mm}
        soil_for_aquacrop = {"field_capacity": field_capacity}
        crop_for_aquacrop = {"crop_type": crop_type, "growing_days": 120}
        return self.aquacrop.run(
            weather=weather, soil=soil_for_aquacrop, crop=crop_for_aquacrop
        )

    @lru_cache(maxsize=256)
    def _run_rothc_cached(
        self,
        temp_avg_c: float,
        precip_mm: float,
        clay_pct: float,
        soc_percent: float,
        residue_return: bool,
        years: int,
    ) -> Dict[str, Any]:
        climate = {"temp_avg_c": temp_avg_c, "precip_mm": precip_mm}
        soil_for_rothc = {"clay_pct": clay_pct, "soc_percent": soc_percent}
        management = {"residue_return": residue_return}
        return self.rothc.run(
            climate=climate,
            soil=soil_for_rothc,
            management=management,
            years=years,
        )

    @lru_cache(maxsize=128)
    def _run_swat_cached(
        self,
        basin_area_ha: float,
        precip_mm: float,
        et_mm: float,
        curve_number: float,
        c_factor: float,
    ) -> Dict[str, Any]:
        basin_config = {"id": "pilot", "area_ha": basin_area_ha, "outlet": {}}
        climate_data = {"annual_precip_mm": precip_mm, "annual_et_mm": et_mm, "temp_avg_c": 18}
        land_use = {"curve_number": curve_number, "c_factor": c_factor}
        return self.swat.run(basin_config, climate_data, land_use)

    def simulate(self, inp: FarmerSimulationInput) -> Dict[str, Any]:
        # Map irrigation to a simple multiplier (kept for API compatibility)
        irr_mult = {"drip": 0.8, "sprinkler": 1.0, "flood": 0.95}.get(
            inp.irrigation_method, 1.0
        )

        # Run models using cached pure-input computation
        yield_result = self._run_aquacrop_cached(
            temp_avg_c=inp.temp_avg_c,
            precip_mm=inp.precip_mm,
            field_capacity=inp.field_capacity,
            crop_type=inp.crop_type.lower(),
        )

        estimated_yield_kg_ha = round(yield_result["yield_kg_ha"] * irr_mult, 1)
        water_need_total_mm = round(
            min(1000.0, inp.precip_mm * (0.35 if inp.irrigation_method == "drip" else 0.5)),
            1,
        )

        soc_result = self._run_rothc_cached(
            temp_avg_c=inp.temp_avg_c,
            precip_mm=inp.precip_mm,
            clay_pct=inp.clay_pct,
            soc_percent=inp.soc_percent,
            residue_return=inp.residue_return,
            years=inp.years,
        )

        # Hydrology (SWAT+ wrapper) - still uses conservative approximations;
        # next steps will replace these with real basin_config/climate/land_use inputs.
        swat_result = self._run_swat_cached(
            basin_area_ha=inp.field_capacity * 1000 + 1000,
            precip_mm=inp.precip_mm,
            et_mm=max(50.0, inp.precip_mm * 0.7),
            curve_number=78.0,
            c_factor=0.3 if inp.crop_type.lower() in ["wheat", "barley", "corn"] else 0.25,
        )

        recommendations = [
            "Monitor soil moisture",
            "Apply fertilizer at planting",
            "Use residue management to improve SOC stability",
            "Consider runoff/sediment mitigation for the basin",
        ]

        return {
            "success": True,
            "model_outputs": {"aquacrop": yield_result, "rothc": soc_result, "swat_plus": swat_result},
            "estimated_yield_kg_ha": estimated_yield_kg_ha,
            "water_need_total_mm": water_need_total_mm,
            "soc_change_t_ha": soc_result.get("soc_change_t_ha"),
            "hydrology_outputs": {
                "streamflow_m3_s": swat_result.get("streamflow_m3_s"),
                "runoff_mm": swat_result.get("water_balance", {}).get("runoff_mm"),
                "sediment_load_tons": swat_result.get("sediment_load_tons"),
            },
            "recommendations": recommendations,
        }

