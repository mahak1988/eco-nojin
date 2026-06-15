"""IoT Data Simulator - Realistic Sensor Data Generation"""
from typing import Dict, List
from datetime import datetime, timezone, timedelta
import random


class IoTDataSimulator:
    """شبیه‌ساز داده‌های IoT برای پایلوت‌ها"""

    def __init__(self):
        self.pilots = {
            "dishmok": {"climate": "Mountain dryland", "baseline_soc": 1.2, "baseline_wue": 0.8},
            "behbahan": {"climate": "Saline semi-arid", "baseline_soc": 0.9, "baseline_wue": 1.1},
            "rodbar_talesh": {"climate": "Humid forest", "baseline_soc": 2.1, "baseline_wue": 1.5},
            "snow_mountain": {"climate": "Snow mountain", "baseline_soc": 1.8, "baseline_wue": 1.2},
            "ouarzazate": {"climate": "Semi-arid desert", "baseline_soc": 0.6, "baseline_wue": 0.5},
            "wadi_rum": {"climate": "Hyper-arid", "baseline_soc": 0.4, "baseline_wue": 0.3},
            "sahel_senegal": {"climate": "Semi-arid coastal", "baseline_soc": 0.8, "baseline_wue": 0.7},
            "ethiopian_highlands": {"climate": "Mountain", "baseline_soc": 1.5, "baseline_wue": 1.0},
            "rajasthan": {"climate": "Semi-arid hot", "baseline_soc": 0.7, "baseline_wue": 0.6},
            "outback_australia": {"climate": "Desert", "baseline_soc": 0.5, "baseline_wue": 0.4},
            "atacama_chile": {"climate": "Hyper-arid", "baseline_soc": 0.3, "baseline_wue": 0.2},
            "mongolian_steppe": {"climate": "Cold steppe", "baseline_soc": 1.3, "baseline_wue": 0.9}
        }

    def simulate_sensor_readings(self, pilot_site: str, days: int = 90) -> Dict:
        """شبیه‌سازی قرائت‌های حسگر برای یک دوره ۹۰ روزه"""
        if pilot_site not in self.pilots:
            return {"error": "Invalid pilot site"}

        pilot_data = self.pilots[pilot_site]
        baseline_soc = pilot_data["baseline_soc"]
        baseline_wue = pilot_data["baseline_wue"]

        improvement_factor = 1.0 + (random.uniform(0.05, 0.15))

        soil_moisture_readings = []
        soc_readings = []
        for day in range(days):
            base_moisture = 15.0 + (day / days) * 5.0
            moisture = base_moisture + random.uniform(-3, 3)
            soil_moisture_readings.append({
                "day": day, "value": round(moisture, 2), "unit": "percent"
            })
            if day % 30 == 0:
                soc = baseline_soc * (1 + (day / days) * 0.1)
                soc += random.uniform(-0.05, 0.05)
                soc_readings.append({"day": day, "value": round(soc, 3), "unit": "percent"})

        water_level_readings = []
        for day in range(days):
            base_level = -10.0 + (day / days) * 2.0
            level = base_level + random.uniform(-0.5, 0.5)
            water_level_readings.append({"day": day, "value": round(level, 2), "unit": "meters"})

        final_wue = baseline_wue * improvement_factor
        final_erosion = 15.0 * (1 / improvement_factor)

        return {
            "pilot_site": pilot_site, "period_days": days,
            "soil_data": {
                "moisture_readings": soil_moisture_readings, "soc_readings": soc_readings,
                "baseline_soc_percent": baseline_soc,
                "final_soc_percent": round(baseline_soc * improvement_factor, 3),
                "erosion_rate_t_ha_yr": round(final_erosion, 2)
            },
            "water_data": {
                "level_readings": water_level_readings,
                "baseline_wue_kg_m3": baseline_wue,
                "final_wue_kg_m3": round(final_wue, 2),
                "water_saved_m3": round(random.uniform(800, 1500), 0)
            },
            "generated_at": datetime.now(timezone.utc).isoformat()
        }