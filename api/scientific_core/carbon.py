# api/scientific_core/carbon.py
"""
مدل‌های کربن خاک
مرجع:
  - RothC (Coleman & Jenkinson, 1996, 2005)
  - Century Model (Parton et al., 1987)
  - IPCC 2019 Refinement
  - ICBM (Andrén & Kätterer, 1997)
"""
import math
from typing import Dict, List


class RothC:
    """
    مدل Rothamsted Carbon (RothC-26.3)
    مرجع: Coleman & Jenkinson (1996)
    
    پنج حوض کربن:
    - DPM: Decomposable Plant Material (تجزیه‌پذیر سریع)
    - RPM: Resistant Plant Material (تجزیه‌پذیر کند)
    - BIO: Microbial Biomass
    - HUM: Humified Organic Matter
    - IOM: Inert Organic Matter
    """
    
    # نسبت‌های تجزیه
    DPM_RPM_RATIO = {
        "forest": 0.67,
        "grassland": 1.44,
        "arable_no_fym": 1.67,
        "arable_with_fym": 0.67,
    }
    
    @classmethod
    def simulate_year(cls, initial_soc: float, carbon_input_t_ha: float,
                      clay_percent: float, mean_temp_c: float,
                      annual_rain_mm: float, years: int = 100) -> Dict:
        """
        شبیه‌سازی ساده‌شده RothC
        """
        # ضرایب نرخ تجزیه (سال⁻¹)
        k_dpm = 10.0
        k_rpm = 0.3
        k_bio = 0.66
        k_hum = 0.02
        
        # محاسبه PE/P ratio (تعدیل‌کننده اقلیمی)
        if annual_rain_mm > 0:
            pe_ratio = 0.75 * (annual_rain_mm / 1000) ** (-0.3)
        else:
            pe_ratio = 1.0
        
        # محاسبه ضریب رس
        clay_factor = 1.0 + (0.015 * clay_percent)
        
        # مقدار IOM (ماده آلی غیرفعال)
        iom = 0.049 * (initial_soc ** 1.139)
        active_soc = initial_soc - iom
        
        # تقسیم اولیه
        dpm_ratio = cls.DPM_RPM_RATIO["arable_no_fym"]
        dpm = active_soc * 0.59 * (dpm_ratio / (dpm_ratio + 1))
        rpm = active_soc * 0.59 * (1 / (dpm_ratio + 1))
        bio = active_soc * 0.02
        hum = active_soc * 0.39
        
        yearly = []
        for year in range(1, years + 1):
            # تعدیل اقلیمی سالانه
            temp_factor = 0.5 + 0.02 * mean_temp_c
            temp_factor = max(0.3, min(1.5, temp_factor))
            
            rate_mod = temp_factor * pe_ratio
            
            # تجزیه سالانه
            dpm_dec = dpm * (1 - math.exp(-k_dpm * rate_mod))
            rpm_dec = rpm * (1 - math.exp(-k_rpm * rate_mod))
            bio_dec = bio * (1 - math.exp(-k_bio * rate_mod))
            hum_dec = hum * (1 - math.exp(-k_hum * rate_mod))
            
            # ورودی جدید
            dpm_in = carbon_input_t_ha * (dpm_ratio / (dpm_ratio + 1))
            rpm_in = carbon_input_t_ha * (1 / (dpm_ratio + 1))
            
            # به‌روزرسانی حوض‌ها
            dpm = dpm - dpm_dec + dpm_in
            rpm = rpm - rpm_dec + rpm_in
            
            # تقسیم تجزیه‌شده
            total_dec = dpm_dec + rpm_dec + bio_dec + hum_dec
            bio_gain = 0.55 * total_dec
            hum_gain = 0.45 * total_dec * clay_factor
            
            bio = bio - bio_dec + bio_gain
            hum = hum - hum_dec + hum_gain
            
            # SOC کل
            total_soc = dpm + rpm + bio + hum + iom
            
            yearly.append({
                "year": year,
                "soc_t_ha": round(total_soc, 3),
                "dpm": round(dpm, 3),
                "rpm": round(rpm, 3),
                "bio": round(bio, 3),
                "hum": round(hum, 3),
                "iom": round(iom, 3),
                "annual_change_t_ha": round(total_soc - (yearly[-1]["soc_t_ha"] if yearly else initial_soc), 3),
            })
        
        final_soc = yearly[-1]["soc_t_ha"]
        return {
            "initial_soc": initial_soc,
            "final_soc": round(final_soc, 3),
            "soc_change_t_ha": round(final_soc - initial_soc, 3),
            "soc_change_percent": round((final_soc - initial_soc) / initial_soc * 100, 2),
            "yearly": yearly,
        }


class IPCC_Tier1:
    """
    مدل IPCC Tier 1 برای تغییرات کربن خاک
    مرجع: IPCC 2019 Refinement, Chapter 6
    فرمول: ΔC = (SOC0 - L) × (1 - e^(-1/L)) × A
    """
    
    # فاکتورهای کاربری اراضی (FLU)
    F_LU = {
        "cropland_continued": 0.80,
        "cropland_converted_from_forest": 0.69,
        "cropland_converted_from_grassland": 0.85,
        "paddy_rice": 0.78,
        "perennial": 1.00,
        "set_aside_less_20y": 0.90,
        "set_aside_more_20y": 1.00,
        "improved_grassland": 1.04,
        "native_grassland": 1.00,
    }
    
    # فاکتورهای مدیریت (FMG)
    F_MG = {
        "full_tillage": 1.00,
        "reduced_tillage": 1.06,
        "no_till": 1.10,
        "intensive": 0.95,
    }
    
    # فاکتورهای ورودی (FI)
    F_I = {
        "low": 0.95,
        "medium": 1.00,
        "high": 1.37,
        "high_with_manure": 1.60,
    }
    
    @classmethod
    def calculate(cls, area_ha: float, soc_reference: float,
                  f_lu: str, f_mg: str, f_i: str, 
                  time_period: int = 20) -> Dict:
        """
        محاسبه تغییرات کربن خاک
        
        Args:
            area_ha: مساحت (هکتار)
            soc_reference: SOC مرجع (t C/ha)
            f_lu, f_mg, f_i: کلیدهای فاکتورها
            time_period: دوره زمانی (سال)
        """
        flu = cls.F_LU.get(f_lu, 1.0)
        fmg = cls.F_MG.get(f_mg, 1.0)
        fi = cls.F_I.get(f_i, 1.0)
        
        # SOC جدید
        soc_new = soc_reference * flu * fmg * fi
        
        # تغییر سالانه
        default_time = 20
        delta_c_annual = (soc_new - soc_reference) / default_time
        
        # تغییر کل
        delta_c_total = delta_c_annual * min(time_period, default_time)
        
        # تبدیل به CO2e (× 3.67)
        co2e_annual = delta_c_annual * 3.67 * area_ha
        co2e_total = delta_c_total * 3.67 * area_ha
        
        return {
            "area_ha": area_ha,
            "soc_reference_t_ha": soc_reference,
            "soc_new_t_ha": round(soc_new, 3),
            "factors": {"F_LU": flu, "F_MG": fmg, "F_I": fi},
            "delta_c_annual_t_ha": round(delta_c_annual, 3),
            "delta_c_total_t_ha": round(delta_c_total, 3),
            "co2e_annual_ton": round(co2e_annual, 2),
            "co2e_total_ton": round(co2e_total, 2),
            "sequestration_or_loss": "sequestration" if delta_c_annual > 0 else "loss",
        }


class ICBM:
    """
    Introductory Carbon Balance Model
    مرجع: Andrén & Kätterer (1997)
    مدل دو حوضی ساده
    """
    
    @classmethod
    def simulate(cls, initial_c: float, annual_input: float,
                 k_young: float, k_old: float, 
                 connection_factor: float, years: int = 50) -> Dict:
        """
        Args:
            initial_c: کربن اولیه (t/ha)
            annual_input: ورودی سالانه (t/ha/yr)
            k_young: نرخ تجزیه حوض جوان
            k_old: نرخ تجزیه حوض قدیمی
            connection_factor: ضریب اتصال بین حوض‌ها
        """
        # تقسیم اولیه
        young = initial_c * 0.3
        old = initial_c * 0.7
        
        yearly = []
        for year in range(1, years + 1):
            # تجزیه
            young_dec = young * k_young
            old_dec = old * k_old
            
            # ورودی
            young_in = annual_input * 0.7
            old_in = annual_input * 0.3
            
            # انتقال بین حوض‌ها
            transfer = young_dec * connection_factor
            
            # به‌روزرسانی
            young = young - young_dec + young_in
            old = old - old_dec + old_in + transfer
            
            total = young + old
            yearly.append({
                "year": year,
                "total_c": round(total, 3),
                "young_pool": round(young, 3),
                "old_pool": round(old, 3),
                "annual_change": round(total - (yearly[-1]["total_c"] if yearly else initial_c), 3),
            })
        
        return {
            "initial_c": initial_c,
            "final_c": round(yearly[-1]["total_c"], 3),
            "yearly": yearly,
        }
