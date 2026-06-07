# api/services/drought_core.py
"""
هسته علمی پایش خشکسالی
مراجع:
  - WMO (2012) - Handbook of Drought Indicators
  - McKee et al. (1993) - SPI
  - Vicente-Serrano et al. (2010) - SPEI
  - Palmer (1965) - PDSI
  - Kogan (1995) - VHI
  - IPCC AR6 (2021) - تغییر اقلیم
"""
import math
import statistics
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


# ============================================================
# ۱. شاخص SPI (Standardized Precipitation Index)
# مرجع: McKee et al. (1993), WMO (2012)
# ============================================================
class SPI:
    """شاخص استاندارد بارش"""
    
    @classmethod
    def calculate(cls, precipitation: List[float], time_scale: int = 3) -> List[Dict]:
        """محاسبه SPI چندمقیاسی"""
        if len(precipitation) < time_scale:
            return []
        
        # محاسبه بارش تجمعی متحرک
        accumulated = []
        for i in range(time_scale - 1, len(precipitation)):
            total = sum(precipitation[i - time_scale + 1:i + 1])
            accumulated.append(total)
        
        if len(accumulated) < 2:
            return []
        
        # برازش توزیع گاما (ساده‌شده)
        mean = statistics.mean(accumulated)
        std = statistics.stdev(accumulated) if len(accumulated) > 1 else 1
        
        if std == 0:
            std = 1
        
        # محاسبه SPI (تبدیل به توزیع نرمال استاندارد)
        results = []
        for i, value in enumerate(accumulated):
            # استفاده از تقریب نرمال
            z = (value - mean) / std
            spi = cls._normal_transform(z)
            classification = cls._classify(spi)
            
            results.append({
                "index": i + time_scale - 1,
                "accumulated_mm": round(value, 2),
                "spi": round(spi, 2),
                "classification": classification["label"],
                "severity": classification["severity"],
                "color": classification["color"],
                "category": classification["category"],
            })
        
        return results
    
    @staticmethod
    def _normal_transform(z: float) -> float:
        """تبدیل به توزیع نرمال استاندارد"""
        # تقریب Abramowitz & Stegun
        if z >= 0:
            t = 1 / (1 + 0.2316419 * z)
            p = 0.3989423 * math.exp(-z * z / 2) * t * (
                0.3193815 + t * (-0.3565638 + t * (1.781478 + t * (-1.821256 + t * 1.330274)))
            )
            spi = math.sqrt(2) * math.erfc(1 - p)
            return spi if spi > 0 else -3.09
        else:
            return -SPI._normal_transform(-z)
    
    @staticmethod
    def _classify(spi: float) -> Dict:
        """طبقه‌بندی SPI بر اساس WMO"""
        if spi >= 2.0:
            return {"label": "بسیار تر", "severity": "extremely_wet", "color": "#0c4a6e", "category": 4}
        elif spi >= 1.5:
            return {"label": "تر", "severity": "very_wet", "color": "#0369a1", "category": 3}
        elif spi >= 1.0:
            return {"label": "نسبتاً تر", "severity": "moderately_wet", "color": "#0ea5e9", "category": 2}
        elif spi > -1.0:
            return {"label": "نرمال", "severity": "near_normal", "color": "#64748b", "category": 0}
        elif spi > -1.5:
            return {"label": "نسبتاً خشک", "severity": "moderately_dry", "color": "#f59e0b", "category": -1}
        elif spi > -2.0:
            return {"label": "خشک", "severity": "severely_dry", "color": "#ea580c", "category": -2}
        else:
            return {"label": "بسیار خشک", "severity": "extremely_dry", "color": "#7f1d1d", "category": -3}


# ============================================================
# ۲. شاخص SPEI
# مرجع: Vicente-Serrano et al. (2010)
# ============================================================
class SPEI:
    """شاخص استاندارد تبخیر-بارش"""
    
    @staticmethod
    def thornthwaite_eto(mean_temp_c: float, latitude: float = 35.0) -> float:
        """محاسبه ETo با روش Thornthwaite"""
        if mean_temp_c <= 0:
            return 0
        i = 12 * ((mean_temp_c / 5) ** 1.514)
        a = 6.75e-7 * i**3 - 7.71e-5 * i**2 + 0.01792 * i + 0.49239
        eto = 16 * (10 * mean_temp_c / i) ** a
        return max(0, eto)
    
    @classmethod
    def calculate(cls, precipitation: List[float], temperature: List[float],
                  time_scale: int = 3, latitude: float = 35.0) -> List[Dict]:
        """محاسبه SPEI"""
        if len(precipitation) != len(temperature):
            return []
        
        # محاسبه بیلان آبی (P - PET)
        water_balance = []
        for i in range(len(precipitation)):
            pet = cls.thornthwaite_eto(temperature[i], latitude)
            water_balance.append(precipitation[i] - pet)
        
        # محاسبه SPI روی بیلان آبی
        return SPI.calculate(water_balance, time_scale)


# ============================================================
# ۳. شاخص PDSI (Palmer Drought Severity Index)
# مرجع: Palmer (1965)
# ============================================================
class PDSI:
    """شاخص خشکسالی پالمر"""
    
    @classmethod
    def calculate(cls, precipitation: List[float], pet: List[float],
                  awc: float = 150.0) -> List[Dict]:
        """
        محاسبه PDSI
        awc: ظرفیت آب قابل دسترس خاک (mm)
        """
        if len(precipitation) != len(pet):
            return []
        
        results = []
        pdsi = 0.0
        pro = 0.0  # رطوبت فاز ۱
        pl = 0.0   # رطوبت فاز ۲
        
        # ضرایب کالیبراسیون (برای اقلیم ایران)
        k_factor = 0.5
        
        for i in range(len(precipitation)):
            p = precipitation[i]
            pe = pet[i]
            
            # بیلان آبی
            pr = p - pe  # تفاوت بارش و تبخیر
            
            # به‌روزرسانی PDSI با فرم ساده‌شده
            if pr > 0:
                pdsi = pdsi + pr * k_factor * 0.1
            else:
                pdsi = pdsi + pr * k_factor * 0.15
            
            # محدود کردن به بازه معتبر
            pdsi = max(-6.0, min(6.0, pdsi))
            
            # طبقه‌بندی
            classification = cls._classify(pdsi)
            
            results.append({
                "month": i,
                "pdsi": round(pdsi, 2),
                "precipitation": round(p, 2),
                "pet": round(pe, 2),
                "water_balance": round(pr, 2),
                "classification": classification["label"],
                "severity": classification["severity"],
                "color": classification["color"],
            })
        
        return results
    
    @staticmethod
    def _classify(pdsi: float) -> Dict:
        """طبقه‌بندی PDSI"""
        if pdsi >= 4.0:
            return {"label": "بسیار مرطوب", "severity": "extremely_wet", "color": "#0c4a6e"}
        elif pdsi >= 3.0:
            return {"label": "خیلی مرطوب", "severity": "very_wet", "color": "#0369a1"}
        elif pdsi >= 2.0:
            return {"label": "مرطوب", "severity": "moderately_wet", "color": "#0ea5e9"}
        elif pdsi >= 1.0:
            return {"label": "کمی مرطوب", "severity": "slightly_wet", "color": "#7dd3fc"}
        elif pdsi > -1.0:
            return {"label": "نرمال", "severity": "near_normal", "color": "#64748b"}
        elif pdsi > -2.0:
            return {"label": "کمی خشک", "severity": "slightly_dry", "color": "#fcd34d"}
        elif pdsi > -3.0:
            return {"label": "خشک", "severity": "moderate_drought", "color": "#f59e0b"}
        elif pdsi > -4.0:
            return {"label": "خشکسالی شدید", "severity": "severe_drought", "color": "#ea580c"}
        else:
            return {"label": "خشکسالی استثنایی", "severity": "extreme_drought", "color": "#7f1d1d"}


# ============================================================
# ۴. شاخص VHI (Vegetation Health Index)
# مرجع: Kogan (1995)
# ============================================================
class VHI:
    """شاخص سلامت پوشش گیاهی"""
    
    @staticmethod
    def calculate_vci(ndvi_series: List[float]) -> List[float]:
        """Vegetation Condition Index"""
        if not ndvi_series:
            return []
        min_ndvi = min(ndvi_series)
        max_ndvi = max(ndvi_series)
        denom = max_ndvi - min_ndvi
        if denom == 0:
            return [50.0] * len(ndvi_series)
        return [100 * (v - min_ndvi) / denom for v in ndvi_series]
    
    @staticmethod
    def calculate_tci(temperature_series: List[float]) -> List[float]:
        """Temperature Condition Index"""
        if not temperature_series:
            return []
        min_t = min(temperature_series)
        max_t = max(temperature_series)
        denom = max_t - min_t
        if denom == 0:
            return [50.0] * len(temperature_series)
        return [100 * (max_t - t) / denom for t in temperature_series]
    
    @classmethod
    def calculate(cls, ndvi_series: List[float], temperature_series: List[float],
                  alpha: float = 0.5) -> List[Dict]:
        """محاسبه VHI"""
        if len(ndvi_series) != len(temperature_series):
            return []
        
        vci = cls.calculate_vci(ndvi_series)
        tci = cls.calculate_tci(temperature_series)
        
        results = []
        for i in range(len(vci)):
            vhi = alpha * vci[i] + (1 - alpha) * tci[i]
            classification = cls._classify(vhi)
            
            results.append({
                "index": i,
                "vhi": round(vhi, 2),
                "vci": round(vci[i], 2),
                "tci": round(tci[i], 2),
                "classification": classification["label"],
                "severity": classification["severity"],
                "color": classification["color"],
            })
        
        return results
    
    @staticmethod
    def _classify(vhi: float) -> Dict:
        """طبقه‌بندی VHI"""
        if vhi >= 60:
            return {"label": "مطلوب", "severity": "no_stress", "color": "#10b981"}
        elif vhi >= 40:
            return {"label": "تنش خفیف", "severity": "mild_stress", "color": "#84cc16"}
        elif vhi >= 25:
            return {"label": "تنش متوسط", "severity": "moderate_stress", "color": "#f59e0b"}
        elif vhi >= 15:
            return {"label": "تنش شدید", "severity": "severe_stress", "color": "#ea580c"}
        else:
            return {"label": "خشکسالی شدید", "severity": "extreme_stress", "color": "#7f1d1d"}


# ============================================================
# ۵. شاخص KBDI (Keetch-Byram Drought Index)
# مرجع: Keetch & Byram (1968)
# ============================================================
class KBDI:
    """شاخص خشکسالی کیتچ-بایرام"""
    
    @classmethod
    def calculate_series(cls, daily_rainfall_mm: List[float],
                         daily_max_temp_c: List[float],
                         annual_rainfall_mm: float = 1000,
                         initial_kbdi: float = 200) -> List[Dict]:
        """محاسبه سری زمانی KBDI"""
        results = []
        kbdi = initial_kbdi
        
        for i in range(len(daily_rainfall_mm)):
            rain = daily_rainfall_mm[i]
            temp = daily_max_temp_c[i]
            
            # کاهش ناشی از بارش
            if rain > 5:
                effective_rain = rain - 5
                kbdi -= effective_rain * 25.4
                kbdi = max(0, kbdi)
            
            # افزایش ناشی از تبخیر
            drought_factor = (203.2 - kbdi) / (1 + 0.8 * (annual_rainfall_mm / 25.4))
            temp_factor = (temp - 15) / 5.6 if temp > 15 else 0
            increase = drought_factor * temp_factor * 0.001 * 25.4
            kbdi += increase
            kbdi = min(800, kbdi)
            
            classification = cls._classify(kbdi)
            
            results.append({
                "day": i,
                "kbdi": round(kbdi, 1),
                "classification": classification["label"],
                "severity": classification["severity"],
                "color": classification["color"],
                "fire_risk": classification["fire_risk"],
            })
        
        return results
    
    @staticmethod
    def _classify(kbdi: float) -> Dict:
        """طبقه‌بندی KBDI"""
        if kbdi < 200:
            return {"label": "خیس", "severity": "wet", "color": "#0ea5e9", "fire_risk": "کم"}
        elif kbdi < 400:
            return {"label": "متوسط", "severity": "moderate", "color": "#84cc16", "fire_risk": "متوسط"}
        elif kbdi < 600:
            return {"label": "خشک", "severity": "dry", "color": "#f59e0b", "fire_risk": "بالا"}
        elif kbdi < 700:
            return {"label": "خیلی خشک", "severity": "very_dry", "color": "#ea580c", "fire_risk": "خیلی بالا"}
        else:
            return {"label": "بحرانی", "severity": "critical", "color": "#7f1d1d", "fire_risk": "بحرانی"}


# ============================================================
# ۶. شاخص RAI (Rainfall Anomaly Index)
# مرجع: Van Rooy (1965)
# ============================================================
class RAI:
    """شاخص ناهنجاری بارش"""
    
    @classmethod
    def calculate(cls, precipitation: List[float]) -> List[Dict]:
        """محاسبه RAI"""
        if len(precipitation) < 10:
            return []
        
        mean = statistics.mean(precipitation)
        
        # محاسبه میانگین مثبت‌ها و منفی‌ها
        positives = [p - mean for p in precipitation if p > mean]
        negatives = [p - mean for p in precipitation if p <= mean]
        
        mean_pos = statistics.mean(positives) if positives else 1
        mean_neg = abs(statistics.mean(negatives)) if negatives else 1
        
        results = []
        for i, p in enumerate(precipitation):
            if p > mean:
                rai = 3 * (p - mean) / mean_pos if mean_pos > 0 else 0
            else:
                rai = -3 * (mean - p) / mean_neg if mean_neg > 0 else 0
            
            classification = cls._classify(rai)
            results.append({
                "index": i,
                "rai": round(rai, 2),
                "precipitation": round(p, 2),
                "classification": classification["label"],
                "color": classification["color"],
            })
        
        return results
    
    @staticmethod
    def _classify(rai: float) -> Dict:
        """طبقه‌بندی RAI"""
        if rai >= 3:
            return {"label": "بسیار تر", "color": "#0c4a6e"}
        elif rai >= 2:
            return {"label": "تر", "color": "#0369a1"}
        elif rai >= 1:
            return {"label": "نسبتاً تر", "color": "#0ea5e9"}
        elif rai > -1:
            return {"label": "نرمال", "color": "#64748b"}
        elif rai > -2:
            return {"label": "نسبتاً خشک", "color": "#f59e0b"}
        elif rai > -3:
            return {"label": "خشک", "color": "#ea580c"}
        else:
            return {"label": "بسیار خشک", "color": "#7f1d1d"}


# ============================================================
# ۷. شاخص CDD (Consecutive Dry Days)
# ============================================================
class CDD:
    """روزهای متوالی خشک"""
    
    @classmethod
    def calculate(cls, daily_precipitation: List[float], threshold: float = 1.0) -> List[Dict]:
        """محاسبه دوره‌های خشک متوالی"""
        results = []
        current_dry = 0
        period_start = 0
        
        for i, p in enumerate(daily_precipitation):
            if p < threshold:
                current_dry += 1
            else:
                if current_dry > 0:
                    severity = cls._classify(current_dry)
                    results.append({
                        "start_day": period_start,
                        "end_day": i - 1,
                        "duration": current_dry,
                        "severity": severity["label"],
                        "color": severity["color"],
                    })
                current_dry = 0
                period_start = i + 1
        
        # آخرین دوره
        if current_dry > 0:
            severity = cls._classify(current_dry)
            results.append({
                "start_day": period_start,
                "end_day": len(daily_precipitation) - 1,
                "duration": current_dry,
                "severity": severity["label"],
                "color": severity["color"],
            })
        
        return results
    
    @staticmethod
    def _classify(days: int) -> Dict:
        """طبقه‌بندی طول دوره خشک"""
        if days < 15:
            return {"label": "کوتاه", "color": "#84cc16"}
        elif days < 30:
            return {"label": "متوسط", "color": "#f59e0b"}
        elif days < 60:
            return {"label": "طولانی", "color": "#ea580c"}
        else:
            return {"label": "بسیار طولانی", "color": "#7f1d1d"}


# ============================================================
# ۸. سیستم پیش‌بینی خشکسالی
# ============================================================
class DroughtForecast:
    """پیش‌بینی خشکسالی"""
    
    @classmethod
    def forecast_3month(cls, historical_spi: List[float]) -> Dict:
        """پیش‌بینی ۳ ماهه بر اساس روند SPI"""
        if len(historical_spi) < 12:
            return {"status": "داده ناکافی"}
        
        # محاسبه روند
        recent = historical_spi[-12:]
        trend = sum(recent[-3:]) / 3 - sum(recent[:3]) / 3
        
        # پیش‌بینی
        last_spi = historical_spi[-1]
        forecast = last_spi - trend * 0.5
        
        classification = SPI._classify(forecast)
        
        return {
            "current_spi": round(last_spi, 2),
            "trend": round(trend, 2),
            "forecast_3month": round(forecast, 2),
            "forecast_classification": classification["label"],
            "forecast_color": classification["color"],
            "confidence": round(0.7 - abs(trend) * 0.1, 2),
        }


# ============================================================
# ۹. تحلیل تغییر اقلیم
# ============================================================
class ClimateChangeAnalysis:
    """تحلیل تغییر اقلیم"""
    
    # سناریوهای CMIP6
    SCENARIOS = {
        "SSP1-2.6": {"name_fa": "پایدار (SSP1-2.6)", "warming_2050": 1.5, "warming_2100": 1.8, "color": "#10b981"},
        "SSP2-4.5": {"name_fa": "میانه (SSP2-4.5)", "warming_2050": 2.0, "warming_2100": 2.7, "color": "#f59e0b"},
        "SSP3-7.0": {"name_fa": "منطقه‌ای (SSP3-7.0)", "warming_2050": 2.3, "warming_2100": 3.6, "color": "#ea580c"},
        "SSP5-8.5": {"name_fa": "بدبینانه (SSP5-8.5)", "warming_2050": 2.6, "warming_2100": 4.4, "color": "#dc2626"},
    }
    
    @classmethod
    def project_drought(cls, baseline_precip: List[float], baseline_temp: List[float],
                        scenario: str = "SSP2-4.5", target_year: int = 2050) -> Dict:
        """پیش‌بینی خشکسالی در سناریوی تغییر اقلیم"""
        if scenario not in cls.SCENARIOS:
            return {"error": "سناریوی نامعتبر"}
        
        sc = cls.SCENARIOS[scenario]
        
        # محاسبه تغییرات بر اساس سناریو و سال هدف
        years_ahead = target_year - 2024
        warming_factor = (sc["warming_2100"] - 1.0) * (years_ahead / 76)
        
        # تغییر بارش (بر اساس مطالعات IPCC برای خاورمیانه)
        precip_change_percent = -0.5 * warming_factor  # کاهش ۰.۵٪ به ازای هر ۱°C
        
        # تغییر دما
        temp_change = warming_factor
        
        # محاسبه SPI جدید
        new_precip = [p * (1 + precip_change_percent / 100) for p in baseline_precip]
        new_temp = [t + temp_change for t in baseline_temp]
        
        # محاسبه SPEI جدید
        new_spei = SPEI.calculate(new_precip, new_temp, time_scale=12)
        
        # آمار
        if new_spei:
            drought_months = sum(1 for s in new_spei if s["spi"] < -1)
            severe_months = sum(1 for s in new_spei if s["spi"] < -1.5)
            avg_spi = statistics.mean([s["spi"] for s in new_spei])
        else:
            drought_months = 0
            severe_months = 0
            avg_spi = 0
        
        return {
            "scenario": scenario,
            "scenario_name": sc["name_fa"],
            "target_year": target_year,
            "warming_c": round(temp_change, 2),
            "precip_change_percent": round(precip_change_percent, 2),
            "avg_spi": round(avg_spi, 2),
            "drought_months": drought_months,
            "severe_drought_months": severe_months,
            "drought_frequency_percent": round(drought_months / len(new_spei) * 100, 1) if new_spei else 0,
        }


# ============================================================
# ۱۰. سیستم توصیه‌های مدیریتی
# ============================================================
class DroughtRecommendations:
    """توصیه‌های مدیریتی بر اساس خشکسالی"""
    
    @classmethod
    def generate(cls, drought_severity: str, drought_type: str = "meteorological",
                 affected_sector: str = "agriculture") -> List[Dict]:
        """تولید توصیه‌ها"""
        recommendations = []
        
        # توصیه‌های کوتاه‌مدت (فوری)
        if drought_severity in ["extremely_dry", "severely_dry", "extreme_drought"]:
            recommendations.append({
                "timeframe": "کوتاه‌مدت",
                "priority": "بحرانی",
                "icon": "🚨",
                "title": "اعلام وضعیت اضطراری",
                "actions": [
                    "محدودیت فوری مصرف آب",
                    "توزیع آب با تانکر به مناطق بحرانی",
                    "فعال‌سازی طرح‌های اضطراری",
                    "حمایت مالی از کشاورزان آسیب‌دیده",
                ],
                "color": "#dc2626",
            })
        
        # توصیه‌های میان‌مدت
        if drought_severity in ["moderately_dry", "severely_dry", "moderate_drought", "severe_drought"]:
            recommendations.append({
                "timeframe": "میان‌مدت",
                "priority": "بالا",
                "icon": "💧",
                "title": "مدیریت منابع آب",
                "actions": [
                    "تغییر الگوی کشت به محصولات کم‌آب‌بر",
                    "توسعه آبیاری قطره‌ای و تحت فشار",
                    "احیای قنات‌ها و آبخوان‌ها",
                    "ساخت حوضچه‌های جمع‌آوری آب باران",
                    "کاهش سطح زیر کشت محصولات پرمصرف",
                ],
                "color": "#f59e0b",
            })
        
        # توصیه‌های بلندمدت
        recommendations.append({
            "timeframe": "بلندمدت",
            "priority": "استراتژیک",
            "icon": "🌱",
            "title": "سازگاری با تغییر اقلیم",
            "actions": [
                "توسعه ارقام مقاوم به خشکی",
                "اجرای طرح‌های آبخیزداری",
                "احیای پوشش گیاهی طبیعی",
                "توسعه کشاورزی حفاظتی",
                "ایجاد بانک ژن گیاهان بومی",
                "آموزش کشاورزان در مدیریت خشکسالی",
            ],
            "color": "#10b981",
        })
        
        # توصیه‌های بخش کشاورزی
        if affected_sector == "agriculture":
            recommendations.append({
                "timeframe": "فصلی",
                "priority": "عملیاتی",
                "icon": "🌾",
                "title": "توصیه‌های کشاورزی",
                "actions": [
                    "استفاده از مالچ برای حفظ رطوبت خاک",
                    "کاشت در تاریخ‌های بهینه",
                    "استفاده از ارقام زودرس",
                    "تناوب زراعی مناسب",
                    "کوددهی متعادل برای تقویت ریشه",
                ],
                "color": "#84cc16",
            })
        
        return recommendations