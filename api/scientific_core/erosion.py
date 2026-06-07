# api/scientific_core/erosion.py
"""
مدل‌های فرسایش خاک
مرجع:
  - RUSLE (Renard et al., 1997) - USDA Agriculture Handbook 703
  - MUSLE (Williams, 1975)
  - USLE (Wischmeier & Smith, 1978)
  - RWEQ (Fryrear et al., 1998) - فرسایش بادی
"""
import math
from typing import Dict, List


class RUSLE:
    """
    Revised Universal Soil Loss Equation
    مرجع: Renard et al. (1997)
    فرمول: A = R × K × LS × C × P
    
    A: نرخ فرسایش (t/ha/yr)
    R: عامل فرسندگی بارش (MJ·mm/ha·h·yr)
    K: عامل فرسایش‌پذیری خاک (t·h/MJ·mm)
    LS: عامل طول-شیب (بدون واحد)
    C: عامل پوشش و مدیریت (بدون واحد)
    P: عامل حفاظت (بدون واحد)
    """
    
    # مقادیر K پیش‌فرض بر اساس بافت خاک
    K_DEFAULTS = {
        "sand": 0.05,
        "loamy_sand": 0.10,
        "sandy_loam": 0.20,
        "loam": 0.30,
        "silt_loam": 0.40,
        "silty_clay_loam": 0.35,
        "clay_loam": 0.25,
        "sandy_clay": 0.15,
        "clay": 0.10,
    }
    
    # مقادیر C بر اساس کاربری اراضی
    C_DEFAULTS = {
        "forest": 0.001,
        "grass_permanent": 0.01,
        "pasture_good": 0.02,
        "pasture_degraded": 0.10,
        "cropland_conventional": 0.40,
        "cropland_contour": 0.25,
        "cropland_contour_terrace": 0.15,
        "cropland_no_till": 0.10,
        "cropland_no_till_cover": 0.05,
        "orchard": 0.15,
        "urban": 0.05,
        "bare_soil": 1.00,
    }
    
    # مقادیر P بر اساس روش حفاظتی
    P_DEFAULTS = {
        "no_practice": 1.00,
        "contour_farming": 0.60,
        "contour_stripcropping": 0.50,
        "terrace": 0.30,
        "contour_terrace": 0.20,
        "grass_waterway": 0.40,
    }
    
    @classmethod
    def calculate_r(cls, monthly_rainfall_mm: List[float]) -> float:
        """
        محاسبه عامل R (فرسندگی بارش)
        روش: Wischmeier & Smith (1978)
        R = Σ(0.276 × P × EI30)
        """
        # روش ساده‌شده بر اساس بارش ماهانه
        r = 0
        for p in monthly_rainfall_mm:
            if p > 0:
                # فرمول تجربی
                r += 0.276 * p * (10 + 0.5 * p)
        return r
    
    @classmethod
    def calculate_k(cls, soil_texture: str, organic_matter: float = 2.0,
                    structure: int = 2, permeability: int = 3) -> float:
        """
        محاسبه عامل K (فرسایش‌پذیری خاک)
        روش: Wischmeier et al. (1971)
        """
        if soil_texture in cls.K_DEFAULTS:
            return cls.K_DEFAULTS[soil_texture]
        return 0.30
    
    @classmethod
    def calculate_ls(cls, slope_length_m: float, slope_percent: float,
                     rill_ratio: float = 0.5) -> float:
        """
        محاسبه عامل LS (طول-شیب)
        روش: McCool et al. (1997)
        LS = (L/22.13)^m × (65.41 × sin²β + 4.56 × sinβ + 0.065)
        """
        if slope_length_m <= 0 or slope_percent <= 0:
            return 1.0
        
        # تبدیل شیب درصد به زاویه
        slope_rad = math.atan(slope_percent / 100)
        sin_beta = math.sin(slope_rad)
        
        # محاسبه m بر اساس نسبت rill/interrill
        if slope_percent < 1:
            m = 0.2
        elif slope_percent < 3:
            m = 0.3
        elif slope_percent < 5:
            m = 0.4
        else:
            m = 0.5
        
        # فاکتور L
        l_factor = (slope_length_m / 22.13) ** m
        
        # فاکتور S
        s_factor = 65.41 * sin_beta**2 + 4.56 * sin_beta + 0.065
        
        return l_factor * s_factor
    
    @classmethod
    def calculate(cls, r: float, k: float = None, ls: float = None,
                  c: float = None, p: float = None,
                  soil_texture: str = "loam",
                  land_use: str = "cropland_conventional",
                  conservation: str = "no_practice",
                  slope_length_m: float = 50,
                  slope_percent: float = 5) -> Dict:
        """محاسبه کامل RUSLE"""
        if k is None:
            k = cls.calculate_k(soil_texture)
        if ls is None:
            ls = cls.calculate_ls(slope_length_m, slope_percent)
        if c is None:
            c = cls.C_DEFAULTS.get(land_use, 0.30)
        if p is None:
            p = cls.P_DEFAULTS.get(conservation, 1.0)
        
        # محاسبه فرسایش
        a = r * k * ls * c * p
        
        # تفسیر شدت
        if a < 5:
            severity = "بسیار کم"
            color = "#10b981"
        elif a < 10:
            severity = "کم"
            color = "#84cc16"
        elif a < 15:
            severity = "متوسط"
            color = "#f59e0b"
        elif a < 25:
            severity = "زیاد"
            color: "#f97316"
            severity = "زیاد"
            color = "#f97316"
        elif a < 40:
            severity = "خیلی زیاد"
            color = "#ef4444"
        else:
            severity = "بحرانی"
            color = "#7f1d1d"
        
        return {
            "erosion_t_ha_yr": round(a, 2),
            "factors": {
                "R": round(r, 2),
                "K": round(k, 3),
                "LS": round(ls, 2),
                "C": round(c, 3),
                "P": round(p, 2),
            },
            "severity": severity,
            "color": color,
            "tolerable_loss_t_ha_yr": 5.0,  # T value
            "above_tolerance": a > 5.0,
        }


class MUSLE:
    """
    Modified Universal Soil Loss Equation
    مرجع: Williams (1975)
    کاربرد: فرسایش برای یک رویداد بارش
    فرمول: Y = 11.8 × (Q × qp × A)^0.56 × K × LS × C × P
    """
    
    @classmethod
    def calculate(cls, runoff_m3: float, peak_discharge_m3s: float,
                  area_ha: float, k: float = 0.30, ls: float = 1.0,
                  c: float = 0.30, p: float = 1.0) -> Dict:
        """محاسبه فرسایش رویداد"""
        term = runoff_m3 * peak_discharge_m3s * area_ha
        if term <= 0:
            return {"sediment_ton": 0}
        
        y = 11.8 * (term ** 0.56) * k * ls * c * p
        
        return {
            "sediment_ton": round(y, 2),
            "runoff_m3": runoff_m3,
            "peak_m3s": peak_discharge_m3s,
            "area_ha": area_ha,
        }


class WindErosion:
    """
    مدل‌های فرسایش بادی
    مرجع: RWEQ (Fryrear et al., 1998)
    """
    
    @classmethod
    def rweq_simplified(cls, wind_speed_ms: float, 
                        soil_roughness_cm: float = 2.0,
                        vegetation_cover_percent: float = 20.0,
                        soil_moisture_percent: float = 10.0) -> Dict:
        """
        فرسایش بادی ساده‌شده
        """
        # فاکتور اقلیمی (WF)
        wf = (wind_speed_ms ** 3) * 0.01
        
        # فاکتور پوشش گیاهی (VC)
        vc = math.exp(-0.05 * vegetation_cover_percent)
        
        # فاکتور زبری خاک (SC)
        sc = 1 / (1 + 0.01 * soil_roughness_cm)
        
        # فاکتور رطوبت (MC)
        mc = 1 - max(0, (soil_moisture_percent - 5) / 20)
        
        # پتانسیل فرسایش
        erosion_potential = wf * vc * sc * mc
        
        # تفسیر
        if erosion_potential < 1:
            severity = "کم"
        elif erosion_potential < 5:
            severity = "متوسط"
        elif erosion_potential < 15:
            severity = "زیاد"
        else:
            severity = "بحرانی"
        
        return {
            "potential_t_ha_yr": round(erosion_potential, 2),
            "factors": {
                "wind_factor": round(wf, 2),
                "vegetation_factor": round(vc, 3),
                "roughness_factor": round(sc, 3),
                "moisture_factor": round(mc, 3),
            },
            "severity": severity,
        }
