"""Soil & Water Service with real RUSLE calculation."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from .repositories.soil_water_repository import SoilWaterRepository
from .models.soil_water_models import SoilAnalysis, ErosionRisk


class SoilWaterService:
    def __init__(self, repository: SoilWaterRepository):
        self.repo = repository
    
    def calculate_rusle(
        self,
        r_factor: float,  # بارش و رواناب
        k_factor: float,  # فرسایش‌پذیری خاک
        ls_factor: float,  # طول و شیب
        c_factor: float,  # پوشش و مدیریت
        p_factor: float   # اقدامات حفاظتی
    ) -> float:
        """محاسبه واقعی مدل RUSLE برای فرسایش خاک"""
        # RUSLE: A = R * K * LS * C * P
        erosion = r_factor * k_factor * ls_factor * c_factor * p_factor
        return round(erosion, 2)
    
    def classify_erosion_risk(self, rusle_value: float) -> str:
        """طبقه‌بندی ریسک فرسایش"""
        if rusle_value < 5:
            return "LOW"
        elif rusle_value < 15:
            return "MODERATE"
        elif rusle_value < 30:
            return "HIGH"
        else:
            return "VERY_HIGH"
    
    def analyze_soil_health(
        self,
        lat: float,
        lon: float,
        organic_matter: float,
        moisture: float,
        ph: float
    ) -> dict:
        """تحلیل سلامت خاک"""
        # امتیازدهی به پارامترها
        om_score = min(organic_matter / 5.0, 1.0) * 100  # 5% ایده‌آل
        moisture_score = min(moisture / 30.0, 1.0) * 100  # 30% ایده‌آل
        ph_score = 100 - abs(ph - 6.5) * 20  # 6.5 ایده‌آل
        ph_score = max(0, min(100, ph_score))
        
        # میانگین وزن‌دار
        health_score = (om_score * 0.4 + moisture_score * 0.3 + ph_score * 0.3)
        
        if health_score >= 80:
            status = "EXCELLENT"
            recommendations = ["حفظ وضعیت فعلی", "پایش دوره‌ای"]
        elif health_score >= 60:
            status = "GOOD"
            recommendations = ["افزایش ماده آلی", "بهینه‌سازی آبیاری"]
        elif health_score >= 40:
            status = "FAIR"
            recommendations = ["اصلاح ساختار خاک", "تناوب زراعی", "کود آلی"]
        else:
            status = "POOR"
            recommendations = ["اصلاح فوری", "توقف کشت موقت", "احیای خاک"]
        
        return {
            "location": {"lat": lat, "lon": lon},
            "health_score": round(health_score, 1),
            "health_status": status,
            "parameters": {
                "organic_matter": organic_matter,
                "moisture": moisture,
                "ph": ph
            },
            "recommendations": recommendations,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_erosion_assessment(
        self,
        lat: float,
        lon: float,
        r: float,
        k: float,
        ls: float,
        c: float,
        p: float
    ) -> dict:
        """ارزیابی فرسایش با RUSLE"""
        rusle_value = self.calculate_rusle(r, k, ls, c, p)
        risk_level = self.classify_erosion_risk(rusle_value)
        
        recommendations = {
            "LOW": ["ادامه مدیریت فعلی", "پایش سالانه"],
            "MODERATE": ["کشاورزی حفاظتی", "تناوب زراعی", "پوشش گیاهی"],
            "HIGH": ["تراس‌بندی", "بادشکن", "توقف شخم"],
            "VERY_HIGH": ["اقدامات فوری", "توقف فعالیت", "احیای فوری"]
        }
        
        return {
            "location": {"lat": lat, "lon": lon},
            "rusle_value": rusle_value,
            "risk_level": risk_level,
            "factors": {
                "R": r,
                "K": k,
                "LS": ls,
                "C": c,
                "P": p
            },
            "recommendations": recommendations.get(risk_level, []),
            "timestamp": datetime.utcnow().isoformat()
        }
