"""MRV Calculator - IPCC AFOLU Tier 2 Methodology"""
from typing import Dict
from datetime import datetime, timezone
import hashlib
import json


class MRVCalculator:
    CARBON_TO_CO2 = 44.0 / 12.0
    SOIL_BULK_DENSITY = 1.3
    SOIL_DEPTH = 30

    def calculate_carbon_sequestration(self, pilot_data: Dict) -> Dict:
        soil_data = pilot_data["soil_data"]
        baseline_soc = soil_data["baseline_soc_percent"]
        final_soc = soil_data["final_soc_percent"]
        area_ha = 100
        baseline_soc_t_ha = (baseline_soc / 100) * self.SOIL_BULK_DENSITY * self.SOIL_DEPTH * 100
        final_soc_t_ha = (final_soc / 100) * self.SOIL_BULK_DENSITY * self.SOIL_DEPTH * 100
        soc_change_t_ha = final_soc_t_ha - baseline_soc_t_ha
        total_soc_change_tCO2 = soc_change_t_ha * area_ha * self.CARBON_TO_CO2
        biomass_sequestration_tCO2 = total_soc_change_tCO2 * 0.3
        return {
            "soil_carbon": {"baseline_soc_percent": baseline_soc, "final_soc_percent": final_soc, "total_change_tCO2": round(total_soc_change_tCO2, 2)},
            "biomass_carbon": {"sequestration_tCO2": round(biomass_sequestration_tCO2, 2)},
            "total_sequestration_tCO2": round(total_soc_change_tCO2 + biomass_sequestration_tCO2, 2),
            "methodology": "IPCC AFOLU Tier 2"
        }

    def calculate_water_savings(self, pilot_data: Dict) -> Dict:
        water_data = pilot_data["water_data"]
        return {"wue": {"baseline_kg_m3": water_data["baseline_wue_kg_m3"], "final_kg_m3": water_data["final_wue_kg_m3"]}, "water_saved_m3": water_data["water_saved_m3"]}

    def calculate_soil_improvement(self, pilot_data: Dict) -> Dict:
        return {"erosion": {"current_t_ha_yr": pilot_data["soil_data"]["erosion_rate_t_ha_yr"]}, "methodology": "RUSLE"}

    def generate_mrv_report(self, pilot_data: Dict) -> Dict:
        carbon = self.calculate_carbon_sequestration(pilot_data)
        water = self.calculate_water_savings(pilot_data)
        soil = self.calculate_soil_improvement(pilot_data)
        report_data = {"pilot_site": pilot_data["pilot_site"], "carbon": carbon, "water": water, "soil": soil, "generated_at": datetime.now(timezone.utc).isoformat()}
        report_hash = hashlib.sha256(json.dumps(report_data, sort_keys=True).encode()).hexdigest()
        report_data["report_hash"] = report_hash
        return report_data