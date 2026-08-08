"""
AquaCrop Conceptual Engine (FAO-56 Based)
=========================================
A robust, copyright-free implementation of crop water productivity and yield response.
Based on FAO Irrigation and Drainage Paper 56 (Public Domain).
Optimized for arid, semi-arid, and mountainous regions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

# ==========================================
# 1. Crop Database (Public Domain Parameters)
# ==========================================
CROP_DATABASE = {
    "wheat_rainfed": {
        "name_fa": "گندم دیم",
        "ky": 1.15,
        "root_max_m": 1.0,
        "t_base": 0.0,
        "season_days": 150,
    },
    "wheat_irrigated": {
        "name_fa": "گندم آبی",
        "ky": 1.15,
        "root_max_m": 1.0,
        "t_base": 0.0,
        "season_days": 150,
    },
    "maize": {"name_fa": "ذرت", "ky": 1.25, "root_max_m": 1.2, "t_base": 10.0, "season_days": 120},
    "barley": {"name_fa": "جو", "ky": 1.0, "root_max_m": 1.0, "t_base": 0.0, "season_days": 120},
    "saffron": {
        "name_fa": "زعفران",
        "ky": 0.85,
        "root_max_m": 0.4,
        "t_base": 5.0,
        "season_days": 200,
    },
    "pistachio": {
        "name_fa": "پسته",
        "ky": 0.80,
        "root_max_m": 2.0,
        "t_base": 7.0,
        "season_days": 365,
    },
}


@dataclass
class SoilProfile:
    fc_mm: float = 200.0
    wp_mm: float = 100.0
    depletion_fraction: float = 0.55


@dataclass
class Management:
    irrigation_events: dict[int, float] = field(default_factory=dict)


@dataclass
class AquaCropResult:
    crop_id: str
    total_yield_t_ha: float
    potential_yield_t_ha: float
    total_water_use_mm: float
    irrigation_applied_mm: float
    avg_water_stress: float
    daily_records: list[dict[str, Any]]
    status: str = "success"
    message: str = ""


def run_aquacrop_conceptual(
    crop_id: str,
    climate_data: list[dict[str, float]],
    soil: SoilProfile = SoilProfile(),
    management: Management = Management(),
    potential_yield_t_ha: float = 8.0,
) -> AquaCropResult:
    if crop_id not in CROP_DATABASE:
        crop_id = "wheat_rainfed"

    crop = CROP_DATABASE[crop_id]
    taw = soil.fc_mm - soil.wp_mm
    threshold_depletion = taw * soil.depletion_fraction

    current_soil_water = soil.fc_mm
    total_et_a, total_et_c, total_irrigation, stress_sum = 0.0, 0.0, 0.0, 0.0
    daily_records = []
    season_len = len(climate_data)

    for day_idx, day_data in enumerate(climate_data):
        day = day_idx + 1
        tmax = day_data.get("tmax", 25.0)
        tmin = day_data.get("tmin", 10.0)
        precip = day_data.get("precip", 0.0)
        et0 = day_data.get("et0", 3.0)
        irrigation = management.irrigation_events.get(day, 0.0)

        # Frost Stress Check
        if tmin < crop["t_base"]:
            kc, frost_stress = 0.0, True
        else:
            frost_stress = False
            progress = day / season_len
            if progress < 0.25:
                kc = 0.3 + (0.85 * (progress / 0.25))
            elif progress < 0.75:
                kc = 1.15
            else:
                kc = 1.15 - (0.85 * ((progress - 0.75) / 0.25))
            kc = max(0.1, min(1.2, kc))

        etc = kc * et0
        total_irrigation += irrigation

        depletion = soil.fc_mm - current_soil_water
        ks = (
            (taw - depletion) / (taw - threshold_depletion)
            if depletion > threshold_depletion
            else 1.0
        )
        ks = max(0.0, min(1.0, ks))
        if frost_stress:
            ks = 0.0

        eta = ks * etc
        current_soil_water = current_soil_water + precip + irrigation - eta

        current_soil_water = min(current_soil_water, soil.fc_mm)

        total_et_a += eta
        total_et_c += etc
        stress_sum += 1.0 - ks

        daily_records.append(
            {
                "day": day,
                "tmax": tmax,
                "tmin": tmin,
                "precip": precip,
                "et0": et0,
                "kc": round(kc, 2),
                "ks": round(ks, 2),
                "eta_mm": round(eta, 2),
            }
        )

    # Yield Calculation (FAO-56)
    if total_et_c > 0:
        et_ratio = total_et_a / total_et_c
        yield_reduction = crop["ky"] * (1.0 - et_ratio)
        actual_yield = max(0.0, potential_yield_t_ha * (1.0 - yield_reduction))
    else:
        actual_yield = 0.0

    avg_stress = stress_sum / season_len if season_len > 0 else 0.0

    return AquaCropResult(
        crop_id=crop_id,
        total_yield_t_ha=round(actual_yield, 2),
        potential_yield_t_ha=potential_yield_t_ha,
        total_water_use_mm=round(total_et_a, 2),
        irrigation_applied_mm=round(total_irrigation, 2),
        avg_water_stress=round(avg_stress, 2),
        daily_records=daily_records,
        status="success",
        message=f"Simulation completed for {crop['name_fa']}. Yield: {actual_yield:.2f} t/ha",
    )


# ==========================================
# 4. Simulation Registry Integration (The Bridge)
# ==========================================
try:
    from datetime import datetime

    from apps.simulation.base import (
        BaseSimulator,
        SimulationParameter,
        SimulationRegistry,
        SimulationResult,
    )
    from apps.simulation.data import service

    @SimulationRegistry.register
    class AquaCropSimulator(BaseSimulator):
        @property
        def id(self) -> str:
            return "aquacrop"

        @property
        def name(self) -> str:
            return "AquaCrop (FAO-56 Conceptual)"

        @property
        def category(self) -> str:
            return "agriculture"

        @property
        def description(self) -> str:
            return "Conceptual crop yield simulation based on FAO-56 water balance, optimized for arid regions."

        @property
        def version(self) -> str:
            return "2.0.0"

        def get_parameters(self) -> list[SimulationParameter]:
            return [
                SimulationParameter(id="lat", name="Latitude", type="float", default=35.7),
                SimulationParameter(id="lon", name="Longitude", type="float", default=51.4),
                SimulationParameter(
                    id="start_date", name="Start Date", type="string", default="2023-06-01"
                ),
                SimulationParameter(
                    id="end_date", name="End Date", type="string", default="2023-06-10"
                ),
                SimulationParameter(
                    id="crop_id", name="Crop Type", type="string", default="wheat_rainfed"
                ),
                SimulationParameter(
                    id="potential_yield_t_ha",
                    name="Potential Yield (t/ha)",
                    type="float",
                    default=4.0,
                ),
            ]

        async def run(self, params: dict) -> AquaCropResult:
            # 1. Extract parameters with safe defaults
            lat = float(params.get("lat", 35.7))
            lon = float(params.get("lon", 51.4))
            crop_id = str(params.get("crop_id", "wheat_rainfed"))
            potential_yield = float(params.get("potential_yield_t_ha", 4.0))

            # Parse dates
            start_str = str(params.get("start_date", "2023-06-01"))
            end_str = str(params.get("end_date", "2023-06-10"))
            try:
                start_dt = datetime.strptime(start_str, "%Y-%m-%d").date()
                end_dt = datetime.strptime(end_str, "%Y-%m-%d").date()
            except ValueError:
                return AquaCropResult(
                    status="error",
                    metrics={},
                    advisory={"error": "Invalid date format. Use YYYY-MM-DD."},
                )

            # 2. Fetch real climate data from NASA POWER (using the service we fixed!)
            try:
                climate_series = await service.get_climate_series(
                    lat, lon, start_dt, end_dt, source="nasa"
                )
            except Exception as e:
                return AquaCropResult(
                    status="error",
                    metrics={},
                    advisory={"error": f"Failed to fetch climate data: {e!s}"},
                )

            if not climate_series:
                return AquaCropResult(
                    status="error",
                    metrics={},
                    advisory={"error": "No climate data returned for the specified period."},
                )

            # 3. Format data for the conceptual engine
            climate_data = []
            for date_str, day_data in climate_series.items():
                climate_data.append(
                    {
                        "tmax": float(day_data.get("temp_max_c", 25.0)),
                        "tmin": float(day_data.get("temp_min_c", 10.0)),
                        "precip": float(day_data.get("precipitation_mm", 0.0)),
                        "et0": float(day_data.get("et0_mm", 3.0)),  # The ET0 we added!
                    }
                )

            # 4. Run the conceptual engine
            result = run_aquacrop_conceptual(
                crop_id=crop_id, climate_data=climate_data, potential_yield_t_ha=potential_yield
            )

            # 5. Map to standard SimulationResult for the Run database
            # Return standard SimulationResult for the Run database
            return SimulationResult(
                simulator_id="aquacrop",
                simulator_name="AquaCrop (FAO-56 Conceptual)",
                status="success",
                metrics={
                    "total_yield_t_ha": result.total_yield_t_ha,
                    "potential_yield_t_ha": result.potential_yield_t_ha,
                    "total_water_use_mm": result.total_water_use_mm,
                    "irrigation_applied_mm": result.irrigation_applied_mm,
                    "avg_water_stress": result.avg_water_stress,
                },
                outputs={
                    "message": result.message,
                    "crop_name_fa": CROP_DATABASE.get(crop_id, {}).get("name_fa", "Unknown"),
                    # Store only first 3 days of daily records to keep DB payload light
                    "daily_sample": result.daily_records[:3],
                },
            )

except ImportError as e:
    import logging

    logging.getLogger(__name__).warning(f"AquaCrop Simulator registration skipped: {e}")
