# api/scientific_core/drought.py
"""
شاخص‌های خشکسالی استاندارد جهانی
مرجع:
  - WMO (2012) - Standardized Precipitation Index
  - Vicente-Serrano et al. (2010) - SPEI
  - Palmer (1965) - PDSI
  - Kogan (1995) - VHI
"""
import math
import statistics
from typing import Dict, List, Tuple


class SPI:
    """
    Standardized Precipitation Index
    مرجع: McKee et al. (1993), WMO (2012)
    
    تفسیر:
      SPI ≥ 2.0: بسیار تر
      1.5 ≤ SPI < 2.0: تر
      1.0 ≤ SPI < 1.5: نسبتاً تر
      -1.0 < SPI < 1.0: نرمال
      -1.5 < SPI ≤ -1.0: نسبتاً خشک
      -2.0 < SPI ≤ -1.5: خشک
      SPI ≤ -2.0: بسیار خشک
    """
    
    @classmethod
    def calculate(cls, precipitation_series: List[float], 
                  time_scale: int = 3) -> List[Dict]:
        """
        محاسبه SPI برای یک سری زمانی بارش
        """
        if len(precipitation_series) < time_scale:
            return []
        
        # محاسبه بارش تجمعی متحرک
        accumulated = []
        for i in range(time_scale - 1, len(precipitation_series)):
            total = sum(precipitation_series[i - time_scale + 1:i + 1])
            accumulated.append(total)
        
        # محاسبه میانگین و انحراف معیار
        mean = statistics.mean(accumulated)
        std = statistics.stdev(accumulated) if len(accumulated) > 1 else 1
        
        if std == 0:
            std = 1
        
        # محاسبه SPI
        results = []
        for i, value in enumerate(accumulated):
            spi = (value - mean) / std
            classification = cls._classify(spi)
            
            results.append({
                "index": i + time_scale - 1,
                "accumulated_mm": round(value, 2),
                "spi": round(spi, 2),
                "classification": classification["label"],
                "severity": classification["severity"],
                "color": classification["color"],
            })
        
        return results
    
    @staticmethod
    def _classify(spi: float) -> Dict:
        """طبقه‌بندی SPI"""
        if spi >= 2.0:
            return {"label": "بسیار تر", "severity": "extremely_wet", "color": "#0c4a6e"}
        elif spi >= 1.5:
            return {"label": "تر", "severity": "very_wet", "color": "#0369a1"}
        elif spi >= 1.0:
            return {"label": "نسبتاً تر", "severity": "moderately_wet", "color": "#0ea5e9"}
        elif spi > -1.0:
            return {"label": "نرمال", "severity": "near_normal", "color": "#64748b"}
        elif spi > -1.5:
            return {"label": "نسبتاً خشک", "severity": "moderately_dry", "color": "#f59e0b"}
        elif spi > -2.0:
            return {"label": "خشک", "severity": "severely_dry", "color": "#ea580c"}
        else:
            return {"label": "بسیار خشک", "severity": "extremely_dry", "color": "#7f1d1d"}


class SPEI:
    """
    Standardized Precipitation Evapotranspiration Index
    مرجع: Vicente-Serrano et al. (2010)
    """
    
    @staticmethod
    def thornthwaite_eto(mean_temp_c: float, latitude: float) -> float:
        """
        محاسبه ETo با روش Thornthwaite
        """
        if mean_temp_c <= 0:
            return 0
        
        # شاخص حرارتی سالانه
        i = 12 * ((mean_temp_c / 5) ** 1.514)
        
        # ضریب a
        a = (6.75e-7 * i**3 - 7.71e-5 * i**2 + 0.01792 * i + 0.49239)
        
        # ETo ماهانه (mm)
        eto = 16 * (10 * mean_temp_c / i) ** a
        
        return max(0, eto)
    
    @classmethod
    def calculate(cls, precipitation: List[float], 
                  temperature: List[float],
                  latitude: float = 35.0,
                  time_scale: int = 3) -> List[Dict]:
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


class VHI:
    """
    Vegetation Health Index
    مرجع: Kogan (1995)
    VHI = α × VCI + (1-α) × TCI
    """
    
    @staticmethod
    def calculate_vci(ndvi_series: List[float]) -> List[float]:
        """Vegetation Condition Index"""
        min_ndvi = min(ndvi_series)
        max_ndvi = max(ndvi_series)
        denom = max_ndvi - min_ndvi
        if denom == 0:
            return [50.0] * len(ndvi_series)
        return [100 * (v - min_ndvi) / denom for v in ndvi_series]
    
    @staticmethod
    def calculate_tci(temperature_series: List[float]) -> List[float]:
        """Temperature Condition Index"""
        min_t = min(temperature_series)
        max_t = max(temperature_series)
        denom = max_t - min_t
        if denom == 0:
            return [50.0] * len(temperature_series)
        return [100 * (max_t - t) / denom for t in temperature_series]
    
    @classmethod
    def calculate(cls, ndvi_series: List[float], 
                  temperature_series: List[float],
                  alpha: float = 0.5) -> List[Dict]:
        """محاسبه VHI"""
        if len(ndvi_series) != len(temperature_series):
            return []
        
        vci = cls.calculate_vci(ndvi_series)
        tci = cls.calculate_tci(temperature_series)
        
        results = []
        for i in range(len(vci)):
            vhi = alpha * vci[i] + (1 - alpha) * tci[i]
            
            # طبقه‌بندی
            if vhi >= 60:
                severity = "مطلوب"
                color = "#10b981"
            elif vhi >= 40:
                severity = "تنش خفیف"
                color = "#84cc16"
            elif vhi >= 25:
                severity = "تنش متوسط"
                color = "#f59e0b"
            elif vhi >= 15:
                severity = "تنش شدید"
                color = "#ea580c"
            else:
                severity = "خشکسالی شدید"
                color = "#7f1d1d"
            
            results.append({
                "index": i,
                "vhi": round(vhi, 2),
                "vci": round(vci[i], 2),
                "tci": round(tci[i], 2),
                "severity": severity,
                "color": color,
            })
        
        return results


class KBDI:
    """
    Keetch-Byram Drought Index
    مرجع: Keetch & Byram (1968)
    کاربرد: پتانسیل آتش‌سوزی جنگل
    """
    
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
            
            # طبقه‌بندی
            if kbdi < 200:
                severity = "خیس"
                color = "#0ea5e9"
            elif kbdi < 400:
                severity = "متوسط"
                color = "#84cc16"
            elif kbdi < 600:
                severity = "خشک"
                color = "#f59e0b"
            elif kbdi < 700:
                severity = "خیلی خشک"
                color = "#ea580c"
            else:
                severity = "بحرانی"
                color = "#7f1d1d"
            
            results.append({
                "day": i,
                "kbdi": round(kbdi, 1),
                "severity": severity,
                "color": color,
            })
        
        return results
