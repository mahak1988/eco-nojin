# api/services/soil_water_calculator.py
"""
محاسبات هیدرولیک خاک و نیاز آبیاری
"""
from typing import Dict, List
from dataclasses import dataclass


@dataclass
class SoilWaterParams:
    soil_texture: str
    bulk_density: float
    field_capacity: float
    wilting_point: float
    root_depth_cm: float
    current_moisture: float
    etc_daily: float


class SoilWaterCalculator:
    """محاسبه‌گر دینامیک آب در خاک"""
    
    SOIL_DEFAULTS = {
        "sandy": {"fc": 10.0, "wp": 5.0, "bulk_density": 1.5, "k_sat": 10.0},
        "loam": {"fc": 25.0, "wp": 12.0, "bulk_density": 1.3, "k_sat": 2.5},
        "clay": {"fc": 35.0, "wp": 20.0, "bulk_density": 1.2, "k_sat": 0.5},
    }

    @classmethod
    def get_soil_defaults(cls, texture: str) -> Dict:
        return cls.SOIL_DEFAULTS.get(texture, cls.SOIL_DEFAULTS["loam"])

    @classmethod
    def calculate_available_water(cls, params: SoilWaterParams) -> Dict:
        """محاسبه آب قابل دسترس برای گیاه"""
        try:
            # آب کل قابل دسترس (mm)
            taw = (params.field_capacity - params.wilting_point) * params.root_depth_cm / 10.0
            
            # آب به راحتی قابل دسترس
            raw = taw * 0.5
            
            # آب فعلی موجود
            current_water = (params.current_moisture - params.wilting_point) * params.root_depth_cm / 10.0
            current_water = max(0.0, current_water)
            
            # کسری آب
            deficit = taw - current_water
            
            # روزهای باقی‌مانده تا تنش
            days_to_stress = current_water / params.etc_daily if params.etc_daily > 0 else 999.0
            
            # نیاز آبیاری
            irrigation_need = max(0.0, deficit)
            
            # وضعیت رطوبت
            status = cls._get_moisture_status(params.current_moisture, params.field_capacity, params.wilting_point)
            
            return {
                "total_available_water_mm": round(taw, 2),
                "readily_available_water_mm": round(raw, 2),
                "current_water_mm": round(current_water, 2),
                "water_deficit_mm": round(deficit, 2),
                "days_to_stress": round(days_to_stress, 1),
                "net_irrigation_need_mm": round(irrigation_need, 2),
                "moisture_status": status
            }
        except Exception as e:
            return {
                "total_available_water_mm": 0,
                "readily_available_water_mm": 0,
                "current_water_mm": 0,
                "water_deficit_mm": 0,
                "days_to_stress": 0,
                "net_irrigation_need_mm": 0,
                "moisture_status": f"خطا: {str(e)}"
            }

    @classmethod
    def _get_moisture_status(cls, current: float, fc: float, wp: float) -> str:
        if current >= fc:
            return "اشباع / در خطر آب‌گرفتگی"
        elif current >= (fc + wp) / 2:
            return "مطلوب"
        elif current >= wp:
            return "تنش آبی خفیف"
        else:
            return "تنش آبی شدید / پژمردگی"

    @classmethod
    def generate_moisture_profile(cls, params: SoilWaterParams) -> List[Dict]:
        """تولید پروفایل رطوبت در اعماق مختلف"""
        profile = []
        depths = [10, 20, 30, 40, 50, 60, 80, 100]
        
        for depth in depths:
            depth_factor = 1 - (depth / 150.0)
            simulated = params.current_moisture * depth_factor + (params.field_capacity * (1 - depth_factor)) * 0.3
            
            profile.append({
                "depth_cm": depth,
                "moisture_percent": round(simulated, 1),
                "field_capacity": params.field_capacity,
                "wilting_point": params.wilting_point,
                "status": "مطلوب" if simulated > params.wilting_point else "تنش"
            })
        
        return profile
