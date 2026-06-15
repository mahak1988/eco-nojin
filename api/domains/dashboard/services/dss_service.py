"""Decision Support System (DSS) Service

این سرویس منطق تصمیم‌گیری و تولید توصیه‌های مدیریتی را پیاده‌سازی می‌کند.
"""
from typing import Dict, List, Optional
from datetime import datetime
from .models.dashboard_models import KPI, KPI_Category, AlertNotification, DashboardType
import uuid


class DSSService:
    """سامانه تصمیم‌یار برای تولید توصیه‌های مدیریتی"""
    
    def __init__(self):
        self.alerts = []
    
    def evaluate_water_stress(
        self,
        wue: float,  # Water Use Efficiency (kg/m3)
        groundwater_level_m: float,
        precipitation_anomaly_percent: float
    ) -> Dict:
        """ارزیابی تنش آبی و تولید توصیه"""
        recommendations = []
        severity = "info"
        
        # ارزیابی WUE
        if wue < 0.5:
            recommendations.append("بهره‌وری آب بسیار پایین است. اصلاح سیستم آبیاری ضروری است.")
            severity = "critical"
        elif wue < 1.0:
            recommendations.append("بهرهوری آب قابل بهبود است. استفاده از آبیاری قطره‌ای توصیه می‌شود.")
            severity = "warning"
        
        # ارزیابی سطح آب زیرزمینی
        if groundwater_level_m < 5:
            recommendations.append("سطح آب زیرزمینی بحرانی است. کاهش برداشت فوری نیاز است.")
            severity = "critical"
        elif groundwater_level_m < 15:
            recommendations.append("سطح آب زیرزمینی در حال کاهش است. پایش دقیق‌تر توصیه می‌شود.")
            if severity != "critical":
                severity = "warning"
        
        # ارزیابی بارش
        if precipitation_anomaly_percent < -30:
            recommendations.append("خشکسالی شدید. فعال‌سازی برنامه‌های اضطراری.")
            severity = "critical"
        elif precipitation_anomaly_percent < -15:
            recommendations.append("کاهش بارش. آماده‌باش برای مدیریت منابع آب.")
            if severity != "critical":
                severity = "warning"
        
        return {
            "assessment": "WATER_STRESS",
            "severity": severity,
            "recommendations": recommendations,
            "indicators": {
                "wue": wue,
                "groundwater_level_m": groundwater_level_m,
                "precipitation_anomaly_percent": precipitation_anomaly_percent
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def evaluate_soil_health(
        self,
        soc_percent: float,  # Soil Organic Carbon
        erosion_rate_t_ha_year: float,
        salinity_ds_m: float
    ) -> Dict:
        """ارزیابی سلامت خاک و تولید توصیه"""
        recommendations = []
        severity = "info"
        
        # ارزی SOC
        if soc_percent < 1.0:
            recommendations.append("کربن آلی خاک بسیار پایین است. افزودن کود آلی و بقایای گیاهی ضروری است.")
            severity = "critical"
        elif soc_percent < 2.0:
            recommendations.append("کربن آلی خاک قابل بهبود است. کشاورزی حفاظتی توصیه می‌شود.")
            severity = "warning"
        
        # ارزیابی فرسایش
        if erosion_rate_t_ha_year > 20:
            recommendations.append("فرسایش شدید. اقدامات فوری کنترل فرسایش نیاز است.")
            severity = "critical"
        elif erosion_rate_t_ha_year > 10:
            recommendations.append("فرسایش متوسط. پوشش گیاهی و تراس‌بندی توصیه می‌شود.")
            if severity != "critical":
                severity = "warning"
        
        # ارزیابی شوری
        if salinity_ds_m > 8:
            recommendations.append("شوری بسیار بالا. اصلاح خاک و زهکشی ضروری است.")
            severity = "critical"
        elif salinity_ds_m > 4:
            recommendations.append("شوری متوسط. استفاده از گونه‌های مقاوم به شوری.")
            if severity != "critical":
                severity = "warning"
        
        return {
            "assessment": "SOIL_HEALTH",
            "severity": severity,
            "recommendations": recommendations,
            "indicators": {
                "soc_percent": soc_percent,
                "erosion_rate_t_ha_year": erosion_rate_t_ha_year,
                "salinity_ds_m": salinity_ds_m
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def evaluate_livelihood_resilience(
        self,
        income_diversity_index: float,  # Simpson's Index
        food_security_score: float,  # 0-100
        poverty_rate_percent: float
    ) -> Dict:
        """ارزیابی تاب‌آوری معیشت و تولید توصیه"""
        recommendations = []
        severity = "info"
        
        # ارزیابی تنوع درآمد
        if income_diversity_index < 0.3:
            recommendations.append("تنوع درآمد بسیار پایین. توسعه مشاغل مکمل ضروری است.")
            severity = "critical"
        elif income_diversity_index < 0.5:
            recommendations.append("تنوع درآمد قابل بهبود. توسعه زنجیره‌های ارزش محلی.")
            severity = "warning"
        
        # ارزیابی امنیت غذایی
        if food_security_score < 50:
            recommendations.append("ناامنی غذایی شدید. مداخلات فوری نیاز است.")
            severity = "critical"
        elif food_security_score < 70:
            recommendations.append("ناامنی غذایی متوسط. تقویت تولید محلی.")
            if severity != "critical":
                severity = "warning"
        
        # ارزیابی فقر
        if poverty_rate_percent > 40:
            recommendations.append("نرخ فقر بالا. برنامه‌های توانمندسازی اقتصادی.")
            severity = "critical"
        elif poverty_rate_percent > 20:
            recommendations.append("نرخ فقر متوسط. حمایت از مشاغل خرد.")
            if severity != "critical":
                severity = "warning"
        
        return {
            "assessment": "LIVELIHOOD_RESILIENCE",
            "severity": severity,
            "recommendations": recommendations,
            "indicators": {
                "income_diversity_index": income_diversity_index,
                "food_security_score": food_security_score,
                "poverty_rate_percent": poverty_rate_percent
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def evaluate_carbon_balance(
        self,
        net_carbon_balance_tCO2e: float,
        soc_sequestration_tCO2: float,
        emissions_tCO2e: float
    ) -> Dict:
        """ارزیابی تراز کربن و تولید توصیه"""
        recommendations = []
        severity = "info"
        
        if net_carbon_balance_tCO2e < 0:
            recommendations.append("انتشار خالص کربن. افزایش ترسیب و کاهش انتشار ضروری است.")
            severity = "critical"
        elif net_carbon_balance_tCO2e < 100:
            recommendations.append("تراز کربن مثبت اما پایین. تقویت اقدامات ترسیب کربن.")
            severity = "warning"
        else:
            recommendations.append("تراز کربن مطلوب. ادامه اقدامات فعلی.")
        
        return {
            "assessment": "CARBON_BALANCE",
            "severity": severity,
            "recommendations": recommendations,
            "indicators": {
                "net_carbon_balance_tCO2e": net_carbon_balance_tCO2e,
                "soc_sequestration_tCO2": soc_sequestration_tCO2,
                "emissions_tCO2e": emissions_tCO2e
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def generate_comprehensive_recommendation(
        self,
        watershed_id: str,
        water_assessment: Dict,
        soil_assessment: Dict,
        livelihood_assessment: Dict,
        carbon_assessment: Dict
    ) -> Dict:
        """تولید توصیه جامع مدیریتی"""
        all_recommendations = []
        overall_severity = "info"
        
        # جمع‌آوری تمام توصیه‌ها
        for assessment in [water_assessment, soil_assessment, livelihood_assessment, carbon_assessment]:
            all_recommendations.extend(assessment.get("recommendations", []))
            if assessment.get("severity") == "critical":
                overall_severity = "critical"
            elif assessment.get("severity") == "warning" and overall_severity != "critical":
                overall_severity = "warning"
        
        # اولویت‌بندی توصیه‌ها
        priority_recommendations = all_recommendations[:5]  # 5 توصیه اولویت‌دار
        
        return {
            "watershed_id": watershed_id,
            "overall_severity": overall_severity,
            "priority_recommendations": priority_recommendations,
            "total_recommendations": len(all_recommendations),
            "assessments": {
                "water": water_assessment,
                "soil": soil_assessment,
                "livelihood": livelihood_assessment,
                "carbon": carbon_assessment
            },
            "generated_at": datetime.utcnow().isoformat()
        }
