"""
SWAT (Soil & Water Assessment Tool)
=================
Watershed water balance: surface runoff, baseflow and evapotranspiration (monthly).
"""

import logging

logger = logging.getLogger(__name__)
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



@SimulationRegistry.register
class SWATSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        """Handle id."""
        return "swat"

    @property
    def name(self) -> str:
        """Handle name."""
        return "SWAT (Soil & Water Assessment Tool)"

    @property
    def category(self) -> str:
        """Handle category."""
        return "hydrology"

    @property
    def description(self) -> str:
        """Handle description."""
        return "Watershed water balance: surface runoff, baseflow and evapotranspiration (monthly)."

    @property
    def version(self) -> str:
        """Handle version."""
        return "1.0.0"

    def get_parameters(self) -> list[SimulationParameter]:
        """Handle get_parameters."""
        return self._get_parameters()

    def _get_parameters(self) -> list[SimulationParameter]:
        """Handle _get_parameters."""
        return [
            SimulationParameter(name="lat", label="Latitude", type="float", default=35.7, min_value=-90.0, max_value=90.0, description="Watershed latitude (triggers NASA climate fetch)", required=False),
            SimulationParameter(name="lon", label="Longitude", type="float", default=51.4, min_value=-180.0, max_value=180.0, description="Watershed longitude", required=False),
            SimulationParameter(name="start_date", label="Start Date", type="string", default="2023-01-01", description="Simulation start date (YYYY-MM-DD)", required=False),
            SimulationParameter(name="end_date", label="End Date", type="string", default="2023-12-31", description="Simulation end date (YYYY-MM-DD)", required=False),
            SimulationParameter(name="land_use", label="Land Use", type="select", options=["forest", "pasture", "row_crop", "urban"], default="pasture", description="Dominant land cover"),
            SimulationParameter(name="soil_group", label="Hydrologic Soil Group", type="select", options=["A", "B", "C", "D"], default="B", description="A=High infiltration, D=Low infiltration"),
            SimulationParameter(name="area_km2", label="Watershed Area (km2)", type="float", default=100.0, min_value=1.0, max_value=10000.0, unit="km2", description="Drainage area"),
            SimulationParameter(name="precipitation", label="Annual Precipitation (mm) [Fallback]", type="float", default=800.0, min_value=100.0, max_value=3000.0, unit="mm", description="Used if no lat/lon provided"),
            SimulationParameter(name="et0", label="Reference ET0 (mm/yr) [Fallback]", type="float", default=600.0, min_value=100.0, max_value=2500.0, unit="mm", description="Used if no lat/lon provided"),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        """Handle run (parameters)."""
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
        """
        Conceptual SWAT Engine: SCS-CN (Curve Number) Method for Surface Runoff.
        Uses daily NASA precipitation or falls back to annual averages.
        """
        lat = params.get("lat")
        lon = params.get("lon")
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        land_use = params.get("land_use", "pasture")
        soil_group = params.get("soil_group", "B")
        area_km2 = float(params.get("area_km2", 100.0))
        
        # Simplified SCS-CN Lookup Table (Public Domain USDA-NRCS)
        cn_table = {
            "forest": {"A": 55, "B": 70, "C": 79, "D": 83},
            "pasture": {"A": 68, "B": 79, "C": 86, "D": 89},
            "row_crop": {"A": 72, "B": 81, "C": 88, "D": 91},
            "urban": {"A": 77, "B": 85, "C": 90, "D": 92}
        }
        cn = cn_table.get(land_use, cn_table["pasture"]).get(soil_group, 79)
        
        # SCS-CN Equations
        s_mm = 25.4 * ((1000.0 / cn) - 10.0)  # Potential maximum retention
        ia_mm = 0.2 * s_mm                      # Initial abstraction
        
        total_precip = 0.0
        total_runoff = 0.0
        daily_runoff_series = []
        days_simulated = 0
        
        # Try to fetch real NASA data
        if lat is not None and lon is not None and start_date and end_date:
            try:
                from apps.simulation.data import service
                from datetime import datetime
                start_dt = datetime.strptime(str(start_date), "%Y-%m-%d").date()
                end_dt = datetime.strptime(str(end_date), "%Y-%m-%d").date()
                
                climate_series = await service.get_climate_series(float(lat), float(lon), start_dt, end_dt, source="nasa")
                
                if climate_series:
                    for day_data in climate_series.values():
                        p = float(day_data.get('precipitation_mm', 0.0))
                        total_precip += p
                        days_simulated += 1
                        
                        if p > ia_mm:
                            q = ((p - ia_mm) ** 2) / (p - ia_mm + s_mm)
                        else:
                            q = 0.0
                            
                        total_runoff += q
                        daily_runoff_series.append(round(q, 2))
            except Exception as e:
                import logging
                logging.getLogger(__name__).warning(f"NASA fetch failed for SWAT, falling back: {e}")
        
        # Fallback to manual parameters if NASA fetch failed or no coords provided
        if days_simulated == 0:
            total_precip = float(params.get("precipitation", 800.0))
            # Assume 365 days for annual fallback, distribute evenly for conceptual demo
            days_simulated = 365
            p_daily = total_precip / 365.0
            if p_daily > ia_mm:
                q_daily = ((p_daily - ia_mm) ** 2) / (p_daily - ia_mm + s_mm)
            else:
                q_daily = 0.0
            total_runoff = q_daily * 365.0
            daily_runoff_series = [round(q_daily, 2)] * 365

        # Baseflow estimation (conceptual: ~20% of total precip minus runoff, bounded)
        total_et0 = float(params.get("et0", 600.0)) # Fallback or could be summed from NASA
        conceptual_baseflow = max(0.0, (total_precip - total_runoff) * 0.2)
        
        # Convert runoff depth (mm) to volume (m3) for the watershed area
        # 1 mm over 1 km2 = 1000 m3
        runoff_volume_m3 = total_runoff * area_km2 * 1000.0

        return {
            "metrics": {
                "total_precip_mm": round(total_precip, 2),
                "total_runoff_mm": round(total_runoff, 2),
                "runoff_volume_m3": round(runoff_volume_m3, 2),
                "conceptual_baseflow_mm": round(conceptual_baseflow, 2),
                "curve_number": cn,
                "potential_retention_s_mm": round(s_mm, 2),
                "days_simulated": days_simulated
            },
            "charts": [
                {
                    "key": "daily_runoff", 
                    "label": "Daily Surface Runoff (mm)", 
                    "color": "#0ea5e9", 
                    "values": daily_runoff_series[-30:], # Show last 30 days for chart readability
                    "kind": "bar"
                }
            ]
        }


    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        """Handle _calculate_metrics (outputs)."""
        return {k: float(v) for k, v in outputs.get("metrics", {}).items() if isinstance(v, (int, float))}

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        """Handle _generate_charts (outputs)."""
        return {s["key"]: s["values"] for s in outputs.get("series", [])}
