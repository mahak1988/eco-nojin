"""Drought Service with real business logic."""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
from .repositories.drought_repository import DroughtRepository
from .models.drought_models import DroughtIndex


class DroughtService:
    def __init__(self, repository: DroughtRepository):
        self.repo = repository
    
    def calculate_spei(self, precipitation: List[float], pet: List[float]) -> float:
        """محاسبه واقعی شاخص SPEI"""
        if len(precipitation) != len(pet) or len(precipitation) == 0:
            return 0.0
        
        # محاسبه تفاوت بارش و تبخیر-تعرق
        differences = [p - e for p, e in zip(precipitation, pet)]
        avg_diff = sum(differences) / len(differences)
        
        # نرمال‌سازی (ساده‌سازی شده)
        std_diff = (sum((d - avg_diff) ** 2 for d in differences) / len(differences)) ** 0.5
        if std_diff == 0:
            return 0.0
        
        spei = avg_diff / std_diff
        return round(spei, 2)
    
    def classify_drought_severity(self, spei: float) -> str:
        """طبقه‌بندی شدت خشکسالی بر اساس SPEI"""
        if spei >= 2.0:
            return "EXTREMELY_WET"
        elif spei >= 1.5:
            return "VERY_WET"
        elif spei >= 1.0:
            return "MODERATELY_WET"
        elif spei >= -1.0:
            return "NORMAL"
        elif spei >= -1.5:
            return "MODERATE_DROUGHT"
        elif spei >= -2.0:
            return "SEVERE_DROUGHT"
        else:
            return "EXTREME_DROUGHT"
    
    def get_early_warning(self, lat: float, lon: float) -> dict:
        """سیستم هشدار زودهنگام خشکسالی"""
        # دریافت داده‌های اخیر
        end_date = datetime.utcnow()
        start_date = datetime(end_date.year, end_date.month - 3, end_date.day)
        
        indices = self.repo.get_drought_index(lat, lon, start_date, end_date)
        
        if not indices:
            return {
                "status": "NO_DATA",
                "message": "داده کافی برای تحلیل موجود نیست",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # محاسبه میانگین شاخص‌ها
        avg_value = sum(idx.value for idx in indices) / len(indices)
        severity = self.classify_drought_severity(avg_value)
        
        # تولید توصیه
        recommendations = {
            "EXTREME_DROUGHT": "اعلام وضعیت بحرانی، محدودیت فوری مصرف آب، فعال‌سازی برنامه‌های اضطراری",
            "SEVERE_DROUGHT": "کاهش ۳۰٪ مصرف آب، تغییر الگوی کشت، حمایت از کشاورزان",
            "MODERATE_DROUGHT": "بهینه‌سازی آبیاری، پایش دقیق منابع آب",
            "NORMAL": "شرایط عادی، ادامه پایش",
            "MODERATELY_WET": "شرایط مطلوب، ذخیره آب",
            "VERY_WET": "آمادگی برای سیلاب، مدیریت رواناب",
            "EXTREMELY_WET": "هشدار سیلاب، تخلیه مناطق پرخطر"
        }
        
        return {
            "region": {"lat": lat, "lon": lon},
            "severity": severity,
            "spei_value": round(avg_value, 2),
            "data_points": len(indices),
            "recommendation": recommendations.get(severity, "نامشخص"),
            "timestamp": datetime.utcnow().isoformat()
        }
