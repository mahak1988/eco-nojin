"""Launch Dashboard Service"""
from typing import Dict
from datetime import datetime, timezone


class LaunchDashboardService:
    """داشبورد ویژه مراسم راه‌اندازی"""

    def get_global_overview(self) -> Dict:
        """نمای کلی جهانی"""
        return {
            "total_pilots": 12,
            "countries": 9,
            "continents": 4,
            "climate_zones": [
                "Mountain dryland", "Saline semi-arid", "Humid forest",
                "Snow mountain", "Semi-arid desert", "Hyper-arid",
                "Semi-arid coastal", "Mountain", "Semi-arid hot",
                "Desert", "Hyper-arid", "Cold steppe"
            ],
            "total_beneficiaries_target": 6955,
            "total_area_hectares": 26000,
            "carbon_target_tCO2e": 500000,
            "launch_date": datetime.now(timezone.utc).isoformat()
        }

    def get_real_time_metrics(self) -> Dict:
        """معیارهای بلادرنگ"""
        return {
            "sensors_online": 0,
            "data_points_collected": 0,
            "community_members_registered": 0,
            "mrv_cycles_completed": 0,
            "pes_payments_issued": 0,
            "carbon_sequestered_tCO2e": 0.0,
            "water_saved_m3": 0.0,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }

    def get_pilot_map_data(self) -> Dict:
        """داده‌های نقشه پایلوت‌ها"""
        pilots = [
            {"id": "dishmok", "name": "Dishmok", "country": "Iran", "lat": 30.9, "lon": 51.4},
            {"id": "behbahan", "name": "Behbahan", "country": "Iran", "lat": 30.6, "lon": 50.2},
            {"id": "rodbar_talesh", "name": "Rodbar/Talesh", "country": "Iran", "lat": 37.0, "lon": 49.5},
            {"id": "snow_mountain", "name": "Snow Mountain", "country": "Iran", "lat": 30.7, "lon": 51.6},
            {"id": "ouarzazate", "name": "Ouarzazate", "country": "Morocco", "lat": 30.92, "lon": -6.90},
            {"id": "wadi_rum", "name": "Wadi Rum", "country": "Jordan", "lat": 29.58, "lon": 35.42},
            {"id": "sahel_senegal", "name": "Sahel", "country": "Senegal", "lat": 15.62, "lon": -16.22},
            {"id": "ethiopian_highlands", "name": "Highlands", "country": "Ethiopia", "lat": 11.60, "lon": 37.38},
            {"id": "rajasthan", "name": "Rajasthan", "country": "India", "lat": 26.92, "lon": 70.90},
            {"id": "outback_australia", "name": "Outback", "country": "Australia", "lat": -23.70, "lon": 133.88},
            {"id": "atacama_chile", "name": "Atacama", "country": "Chile", "lat": -24.50, "lon": -69.25},
            {"id": "mongolian_steppe", "name": "Steppe", "country": "Mongolia", "lat": 45.75, "lon": 106.25}
        ]

        return {
            "pilots": pilots,
            "total": len(pilots)
        }