# api/scientific_core/hydrology.py
"""
مدل‌های هیدرولوژی استاندارد جهانی
مرجع: 
  - USDA NRCS (SCS-CN)
  - Chow et al. (1988) - Applied Hydrology
  - Viessman & Lewis (2003)
  - HEC-HMS Technical Reference
"""
import math
from typing import Dict, List, Optional


class SCS_CN:
    """
    مدل SCS Curve Number (USDA NRCS)
    مرجع: Soil Conservation Service (1972, 1985)
    فرمول: Q = (P - Ia)^2 / (P - Ia + S)
           Ia = 0.2S
           S = 25400/CN - 254
    """
    
    # CN پیش‌فرض بر اساس کاربری اراضی و نوع هیدرولوژیک خاک
    CN_TABLE = {
        # (کاربری, گروه هیدرولوژیک): CN
        ("forest_good", "A"): 36, ("forest_good", "B"): 60, 
        ("forest_good", "C"): 73, ("forest_good", "D"): 79,
        ("forest_fair", "A"): 60, ("forest_fair", "B"): 73,
        ("forest_fair", "C"): 79, ("forest_fair", "D"): 83,
        ("grass_good", "A"): 49, ("grass_good", "B"): 69,
        ("grass_good", "C"): 79, ("grass_good", "D"): 84,
        ("grass_fair", "A"): 68, ("grass_fair", "B"): 79,
        ("grass_fair", "C"): 86, ("grass_fair", "D"): 89,
        ("cultivated", "A"): 72, ("cultivated", "B"): 81,
        ("cultivated", "C"): 88, ("cultivated", "D"): 91,
        ("impervious", "A"): 98, ("impervious", "B"): 98,
        ("impervious", "C"): 98, ("impervious", "D"): 98,
        ("wetland", "A"): 96, ("wetland", "B"): 96,
        ("wetland", "C"): 96, ("wetland", "D"): 97,
    }
    
    @classmethod
    def calculate(cls, rainfall_mm: float, cn: float, 
                  initial_moisture: str = "AMC_II") -> Dict:
        """
        محاسبه رواناب مستقیم
        
        Args:
            rainfall_mm: بارش (mm)
            cn: ضریب رواناب (Curve Number)
            initial_moisture: شرایط رطوبت اولیه (AMC_I, AMC_II, AMC_III)
        """
        # تنظیم CN بر اساس AMC
        if initial_moisture == "AMC_I":  # خشک
            cn_adj = 4.2 * cn / (10 - 0.058 * cn) if cn > 0 else cn
        elif initial_moisture == "AMC_III":  # اشباع
            cn_adj = 23 * cn / (10 + 0.13 * cn) if cn > 0 else cn
        else:  # AMC_II - متوسط
            cn_adj = cn
        
        # محاسبه S (max retention)
        s = (25400 / cn_adj) - 254 if cn_adj > 0 else 0
        
        # تلفات اولیه
        ia = 0.2 * s
        
        # رواناب
        if rainfall_mm <= ia:
            q = 0
        else:
            q = ((rainfall_mm - ia) ** 2) / (rainfall_mm - ia + s)
        
        # نفوذ
        infiltration = rainfall_mm - q - ia if rainfall_mm > ia else 0
        
        return {
            "curve_number": round(cn_adj, 1),
            "s_mm": round(s, 2),
            "ia_mm": round(ia, 2),
            "rainfall_mm": round(rainfall_mm, 2),
            "runoff_mm": round(q, 2),
            "infiltration_mm": round(infiltration, 2),
            "runoff_coefficient": round(q / rainfall_mm, 3) if rainfall_mm > 0 else 0,
        }
    
    @classmethod
    def get_cn(cls, land_use: str, hydrologic_group: str) -> int:
        """دریافت CN از جدول"""
        return cls.CN_TABLE.get((land_use, hydrologic_group), 75)


class RationalMethod:
    """
    روش عقلایی برای محاسبه دبی پیک
    مرجع: Chow et al. (1988)
    فرمول: Q = C × I × A
    """
    
    # ضرایب رواناب C بر اساس کاربری
    RUNOFF_COEFFICIENTS = {
        "impervious": 0.90,
        "business": 0.85,
        "residential_dense": 0.70,
        "residential_single": 0.55,
        "parks": 0.25,
        "forests": 0.20,
        "cultivated": 0.40,
        "grass_sandy_flat": 0.20,
        "grass_heavy_soil": 0.45,
    }
    
    @classmethod
    def calculate(cls, c: float, intensity_mm_hr: float, 
                  area_hectares: float) -> Dict:
        """
        محاسبه دبی پیک
        
        Q = C × I × A / 360 (m³/s)
        """
        q_m3s = (c * intensity_mm_hr * area_hectares) / 360
        
        return {
            "runoff_coefficient": c,
            "intensity_mm_hr": intensity_mm_hr,
            "area_hectares": area_hectares,
            "peak_discharge_m3s": round(q_m3s, 3),
            "peak_discharge_lps": round(q_m3s * 1000, 1),
        }


class InfiltrationModels:
    """مدل‌های نفوذ"""
    
    @staticmethod
    def horton(f0: float, fc: float, k: float, t: float) -> float:
        """
        مدل نفوذ هورتون
        مرجع: Horton (1940)
        f(t) = fc + (f0 - fc) × e^(-kt)
        """
        return fc + (f0 - fc) * math.exp(-k * t)
    
    @staticmethod
    def philip(s: float, a: float, t: float) -> float:
        """
        مدل نفوذ فیلیپ
        مرجع: Philip (1957)
        f(t) = 0.5 × S × t^(-0.5) + A
        """
        if t <= 0: return s
        return 0.5 * s / math.sqrt(t) + a
    
    @staticmethod
    def kostiakov(k: float, a: float, t: float) -> float:
        """
        مدل نفوذ کستیاکوف
        مرجع: Kostiakov (1932)
        f(t) = k × t^(-a)
        """
        if t <= 0: return 0
        return k * (t ** -a)
    
    @staticmethod
    def green_ampt(k_sat: float, psi_f: float, delta_theta: float, 
                   f: float) -> float:
        """
        مدل نفوذ Green-Ampt
        مرجع: Green & Ampt (1911)
        f = Ks × (1 + (ψ_f × Δθ) / F)
        """
        if f <= 0: return k_sat
        return k_sat * (1 + (psi_f * delta_theta) / f)


class Muskingum:
    """
    مدل مسیریابی مسکینگام
    مرجع: McCarthy (1938)
    O2 = C1 × I2 + C2 × I1 + C3 × O1
    """
    
    @classmethod
    def calculate(cls, inflow: List[float], k: float, x: float, 
                  dt: float) -> List[float]:
        """
        Args:
            inflow: سری زمانی ورودی
            k: ضریب ذخیره (ساعت)
            x: ضریب وزن (0 تا 0.5)
            dt: گام زمانی (ساعت)
        """
        denom = 2 * k * (1 - x) + dt
        if denom == 0: return inflow
        
        c1 = (dt - 2 * k * x) / denom
        c2 = (dt + 2 * k * x) / denom
        c3 = (2 * k * (1 - x) - dt) / denom
        
        outflow = [inflow[0]]
        for i in range(1, len(inflow)):
            o = c1 * inflow[i] + c2 * inflow[i-1] + c3 * outflow[-1]
            outflow.append(max(0, o))
        
        return {
            "outflow": [round(o, 3) for o in outflow],
            "coefficients": {"C1": round(c1, 3), "C2": round(c2, 3), "C3": round(c3, 3)},
            "peak_attenuation": round(max(inflow) - max(outflow), 3),
            "peak_lag_hours": round((outflow.index(max(outflow)) - inflow.index(max(inflow))) * dt, 1),
        }


class TimeOfConcentration:
    """زمان تمرکز حوضه آبریز"""
    
    @staticmethod
    def kirpich(length_m: float, slope_m_m: float) -> float:
        """
        فرمول کرپیچ (1940)
        tc = 0.0195 × L^0.77 × S^(-0.385)
        """
        if slope_m_m <= 0: return 0
        return 0.0195 * (length_m ** 0.77) * (slope_m_m ** -0.385)
    
    @staticmethod
    def scs(length_m: float, cn: float, slope_percent: float) -> float:
        """
        فرمول SCS
        tc = (L^0.8 × (1000/CN - 9)^0.7) / (1140 × S^0.5)
        """
        if slope_percent <= 0: return 0
        s = math.sqrt(slope_percent / 100)
        return (length_m ** 0.8 * ((1000/cn - 9) ** 0.7)) / (1140 * s)
    
    @staticmethod
    def ventura(length_km: float, slope_m_m: float) -> float:
        """
        فرمول ونتورا
        tc = L / (10 × sqrt(S))
        """
        if slope_m_m <= 0: return 0
        return length_km / (10 * math.sqrt(slope_m_m))
