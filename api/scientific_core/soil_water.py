# api/scientific_core/soil_water.py
"""
مدل‌های آب خاک
مرجع:
  - van Genuchten (1980)
  - Brooks & Corey (1964)
  - Campbell (1974)
  - FAO-56
"""
import math
from typing import Dict, List


class VanGenuchten:
    """
    مدل van Genuchten-Mualem
    مرجع: van Genuchten, M.T. (1980). Soil Sci. Soc. Am. J. 44:892-898
    """
    
    @staticmethod
    def theta_from_psi(psi_cm: float, theta_r: float, theta_s: float,
                       alpha: float, n: float) -> float:
        """رطوبت از مکش"""
        if psi_cm >= 0:
            return theta_s
        m = 1 - 1/n
        se = (1 + (alpha * abs(psi_cm))**n) ** (-m)
        return theta_r + (theta_s - theta_r) * se
    
    @staticmethod
    def psi_from_theta(theta: float, theta_r: float, theta_s: float,
                       alpha: float, n: float) -> float:
        """مکش از رطوبت"""
        if theta >= theta_s:
            return 0
        if theta <= theta_r:
            return float("inf")
        m = 1 - 1/n
        se = (theta - theta_r) / (theta_s - theta_r)
        return -(1/alpha) * (se**(-1/m) - 1)**(1/n)
    
    @staticmethod
    def hydraulic_conductivity(theta: float, theta_r: float, theta_s: float,
                               alpha: float, n: float, k_sat: float) -> float:
        """هدایت هیدرولیکی غیراشباع (Mualem, 1976)"""
        m = 1 - 1/n
        se = max(0.001, min(0.999, (theta - theta_r) / (theta_s - theta_r)))
        term = 1 - (1 - se**(1/m))**m
        return k_sat * (se**0.5) * (term**2)


class BrooksCorey:
    """
    مدل Brooks-Corey
    مرجع: Brooks & Corey (1964)
    """
    
    @staticmethod
    def theta_from_psi(psi_cm: float, theta_s: float, 
                       psi_air_entry_cm: float, lambda_bc: float) -> float:
        """رطوبت از مکش"""
        if psi_cm >= 0:
            return theta_s
        if abs(psi_cm) <= psi_air_entry_cm:
            return theta_s
        return theta_s * (psi_air_entry_cm / abs(psi_cm)) ** lambda_bc
    
    @staticmethod
    def hydraulic_conductivity(theta: float, theta_s: float,
                               k_sat: float, psi_air_entry_cm: float,
                               lambda_bc: float, psi_cm: float) -> float:
        """هدایت هیدرولیکی"""
        if theta >= theta_s:
            return k_sat
        se = theta / theta_s
        return k_sat * se ** (3 + 2/lambda_bc)


class Campbell:
    """
    مدل Campbell
    مرجع: Campbell (1974)
    """
    
    @staticmethod
    def psi_from_theta(theta: float, theta_s: float, 
                       psi_air_entry: float, b: float) -> float:
        """مکش از رطوبت"""
        if theta >= theta_s:
            return psi_air_entry
        se = theta / theta_s
        return psi_air_entry * se ** (-b)


class FAO56WaterBalance:
    """
    بیلان آبی FAO-56
    مرجع: Allen et al. (1998), Chapter 8
    """
    
    @staticmethod
    def daily_balance(sw_prev: float, rainfall: float, irrigation: float,
                      etc: float, cn: float = 75, root_depth_mm: float = 500,
                      fc_mm: float = 150, wp_mm: float = 75) -> Dict:
        """
        بیلان آبی روزانه
        
        Args:
            sw_prev: آب خاک قبلی (mm)
            rainfall: بارش (mm)
            irrigation: آبیاری (mm)
            etc: تبخیر و تعرق محصول (mm)
            cn: Curve Number برای رواناب
            root_depth_mm: عمق ریشه (mm)
            fc_mm: ظرفیت زراعی (mm)
            wp_mm: نقطه پژمردگی (mm)
        """
        # محاسبه رواناب
        s = (25400 / cn) - 254 if cn > 0 else 0
        ia = 0.2 * s
        if rainfall > ia:
            runoff = ((rainfall - ia) ** 2) / (rainfall - ia + s)
        else:
            runoff = 0
        
        # بارش مؤثر
        effective_rain = rainfall - runoff
        
        # بیلان
        sw_new = sw_prev + effective_rain + irrigation - etc
        
        # نشت عمیق
        dp = 0
        if sw_new > fc_mm:
            dp = sw_new - fc_mm
            sw_new = fc_mm
        
        # حداقل
        if sw_new < 0:
            sw_new = 0
        
        # وضعیت
        taw = fc_mm - wp_mm
        raw = taw * 0.5
        
        if sw_new > fc_mm:
            status = "اشباع"
        elif sw_new > (fc_mm + wp_mm) / 2:
            status = "مطلوب"
        elif sw_new > wp_mm:
            status = "تنش خفیف"
        else:
            status = "تنش شدید"
        
        return {
            "soil_water_mm": round(sw_new, 2),
            "soil_water_percent": round((sw_new / taw) * 100, 1),
            "effective_rain_mm": round(effective_rain, 2),
            "runoff_mm": round(runoff, 2),
            "deep_percolation_mm": round(dp, 2),
            "status": status,
        }
