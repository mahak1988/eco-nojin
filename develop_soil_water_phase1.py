#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💧 فاز ۱: هسته علمی ماژول آب خاک
بر اساس FAO-56 و van Genuchten-Mualem
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ========== 1. هسته علمی (Scientific Core) ==========
def create_scientific_core():
    print("\n🧬 ایجاد هسته علمی Soil Water...")
    
    content = '''# api/services/soil_water_core.py
"""
هسته علمی ماژول آب خاک
بر اساس استانداردهای:
- FAO-56 (Allen et al., 1998)
- van Genuchten-Mualem (1980)
- USDA Rosetta Database
"""
import math
from typing import Dict, List, Tuple
from dataclasses import dataclass, field


# ============================================================
# پایگاه داده خاک (بر اساس USDA Rosetta و FAO)
# ============================================================
SOIL_DATABASE = {
    "sand": {
        "name_fa": "شن",
        "name_en": "Sand",
        "theta_r": 0.045,  # رطوبت باقیمانده
        "theta_s": 0.430,  # رطوبت اشباع
        "alpha_vg": 0.145, # پارامتر van Genuchten (1/cm)
        "n_vg": 2.68,      # پارامتر van Genuchten
        "k_sat": 8.25,     # هدایت هیدرولیکی اشباع (cm/day)
        "bulk_density": 1.55,  # چگالی ظاهری (g/cm³)
        "field_capacity": 0.10,  # ظرفیت زراعی (حجمی)
        "wilting_point": 0.05,   # نقطه پژمردگی (حجمی)
        "color": "#f59e0b"
    },
    "loamy_sand": {
        "name_fa": "شن لومی",
        "name_en": "Loamy Sand",
        "theta_r": 0.057, "theta_s": 0.410,
        "alpha_vg": 0.124, "n_vg": 2.28, "k_sat": 4.50,
        "bulk_density": 1.50, "field_capacity": 0.14, "wilting_point": 0.07,
        "color": "#eab308"
    },
    "sandy_loam": {
        "name_fa": "لومی شنی",
        "name_en": "Sandy Loam",
        "theta_r": 0.065, "theta_s": 0.410,
        "alpha_vg": 0.075, "n_vg": 1.89, "k_sat": 2.50,
        "bulk_density": 1.45, "field_capacity": 0.20, "wilting_point": 0.10,
        "color": "#d97706"
    },
    "loam": {
        "name_fa": "لوم",
        "name_en": "Loam",
        "theta_r": 0.078, "theta_s": 0.430,
        "alpha_vg": 0.036, "n_vg": 1.56, "k_sat": 1.20,
        "bulk_density": 1.35, "field_capacity": 0.27, "wilting_point": 0.13,
        "color": "#84cc16"
    },
    "silty_loam": {
        "name_fa": "لومی سیلتی",
        "name_en": "Silty Loam",
        "theta_r": 0.067, "theta_s": 0.450,
        "alpha_vg": 0.028, "n_vg": 1.45, "k_sat": 0.80,
        "bulk_density": 1.30, "field_capacity": 0.32, "wilting_point": 0.14,
        "color": "#22c55e"
    },
    "sandy_clay_loam": {
        "name_fa": "لومی رسی شنی",
        "name_en": "Sandy Clay Loam",
        "theta_r": 0.100, "theta_s": 0.390,
        "alpha_vg": 0.059, "n_vg": 1.51, "k_sat": 0.60,
        "bulk_density": 1.35, "field_capacity": 0.25, "wilting_point": 0.14,
        "color": "#14b8a6"
    },
    "clay_loam": {
        "name_fa": "لومی رسی",
        "name_en": "Clay Loam",
        "theta_r": 0.095, "theta_s": 0.410,
        "alpha_vg": 0.019, "n_vg": 1.31, "k_sat": 0.35,
        "bulk_density": 1.30, "field_capacity": 0.32, "wilting_point": 0.20,
        "color": "#06b6d4"
    },
    "silty_clay_loam": {
        "name_fa": "لومی رسی سیلتی",
        "name_en": "Silty Clay Loam",
        "theta_r": 0.089, "theta_s": 0.430,
        "alpha_vg": 0.016, "n_vg": 1.26, "k_sat": 0.25,
        "bulk_density": 1.25, "field_capacity": 0.35, "wilting_point": 0.21,
        "color": "#3b82f6"
    },
    "sandy_clay": {
        "name_fa": "رسی شنی",
        "name_en": "Sandy Clay",
        "theta_r": 0.100, "theta_s": 0.380,
        "alpha_vg": 0.027, "n_vg": 1.23, "k_sat": 0.30,
        "bulk_density": 1.35, "field_capacity": 0.30, "wilting_point": 0.20,
        "color": "#8b5cf6"
    },
    "silty_clay": {
        "name_fa": "رسی سیلتی",
        "name_en": "Silty Clay",
        "theta_r": 0.089, "theta_s": 0.400,
        "alpha_vg": 0.013, "n_vg": 1.17, "k_sat": 0.18,
        "bulk_density": 1.25, "field_capacity": 0.37, "wilting_point": 0.24,
        "color": "#a855f7"
    },
    "clay": {
        "name_fa": "رس",
        "name_en": "Clay",
        "theta_r": 0.068, "theta_s": 0.380,
        "alpha_vg": 0.010, "n_vg": 1.15, "k_sat": 0.12,
        "bulk_density": 1.20, "field_capacity": 0.38, "wilting_point": 0.25,
        "color": "#ec4899"
    },
}


# ============================================================
# مدل van Genuchten-Mualem (1980)
# ============================================================
class VanGenuchtenModel:
    """
    مدل van Genuchten-Mualem برای منحنی مشخصه رطوبت خاک
    مرجع: van Genuchten, M.T. (1980). Soil Sci. Soc. Am. J. 44:892-898
    """
    
    @staticmethod
    def theta_from_psi(psi_cm: float, theta_r: float, theta_s: float, 
                       alpha: float, n: float) -> float:
        """محاسبه رطوبت از مکش (معکوس منحنی مشخصه)"""
        if psi_cm >= 0:
            return theta_s  # اشباع
        m = 1 - 1/n
        se = (1 + (alpha * abs(psi_cm))**n) ** (-m)
        return theta_r + (theta_s - theta_r) * se
    
    @staticmethod
    def psi_from_theta(theta: float, theta_r: float, theta_s: float,
                       alpha: float, n: float) -> float:
        """محاسبه مکش از رطوبت (منحنی مشخصه)"""
        if theta >= theta_s:
            return 0
        if theta <= theta_r:
            return float("inf")
        m = 1 - 1/n
        se = (theta - theta_r) / (theta_s - theta_r)
        psi = -(1/alpha) * (se**(-1/m) - 1)**(1/n)
        return psi
    
    @staticmethod
    def hydraulic_conductivity(theta: float, theta_r: float, theta_s: float,
                               alpha: float, n: float, k_sat: float) -> float:
        """
        هدایت هیدرولیکی غیراشباع (Mualem, 1976)
        K(θ) = Ks × Se^0.5 × [1 - (1 - Se^(1/m))^m]^2
        """
        m = 1 - 1/n
        se = max(0.001, min(0.999, (theta - theta_r) / (theta_s - theta_r)))
        term = 1 - (1 - se**(1/m))**m
        k = k_sat * (se**0.5) * (term**2)
        return k
    
    @classmethod
    def generate_swcc(cls, soil_key: str, n_points: int = 100) -> List[Dict]:
        """تولید منحنی مشخصه رطوبت خاک (SWCC)"""
        soil = SOIL_DATABASE.get(soil_key, SOIL_DATABASE["loam"])
        curve = []
        
        # بازه مکش: از 0 تا 15000 cm (معادل -1500 kPa)
        psi_values = [10**(i/20) for i in range(0, 85)]  # 1 تا ~30000 cm
        
        for psi in psi_values:
            theta = cls.theta_from_psi(
                -psi, soil["theta_r"], soil["theta_s"],
                soil["alpha_vg"], soil["n_vg"]
            )
            k = cls.hydraulic_conductivity(
                theta, soil["theta_r"], soil["theta_s"],
                soil["alpha_vg"], soil["n_vg"], soil["k_sat"]
            )
            curve.append({
                "psi_cm": round(psi, 2),
                "psi_kpa": round(psi * 0.0981, 2),  # 1 cm ≈ 0.0981 kPa
                "theta": round(theta, 4),
                "theta_percent": round(theta * 100, 2),
                "se": round((theta - soil["theta_r"]) / (soil["theta_s"] - soil["theta_r"]), 3),
                "k_cm_per_day": round(k, 4),
            })
        
        return curve


# ============================================================
# مدل FAO-56 (Allen et al., 1998)
# ============================================================
class FAO56Model:
    """
    مدل FAO-56 برای محاسبه تبخیر و تعرق و نیاز آبیاری
    """
    
    # ضرایب Kc برای محصولات اصلی (مرحله میانی)
    KC_DATABASE = {
        "wheat": {"name_fa": "گندم", "kc_init": 0.30, "kc_mid": 1.15, "kc_end": 0.30, "days": [30, 50, 40, 30]},
        "maize": {"name_fa": "ذرت", "kc_init": 0.30, "kc_mid": 1.20, "kc_end": 0.50, "days": [25, 55, 40, 30]},
        "rice": {"name_fa": "برنج", "kc_init": 1.05, "kc_mid": 1.20, "kc_end": 0.90, "days": [30, 60, 40, 30]},
        "cotton": {"name_fa": "پنبه", "kc_init": 0.35, "kc_mid": 1.15, "kc_end": 0.30, "days": [40, 60, 50, 30]},
        "soybean": {"name_fa": "سویا", "kc_init": 0.30, "kc_mid": 1.15, "kc_end": 0.35, "days": [30, 45, 40, 25]},
        "barley": {"name_fa": "جو", "kc_init": 0.30, "kc_mid": 1.15, "kc_end": 0.25, "days": [25, 45, 40, 30]},
        "sugarbeet": {"name_fa": "چغندر", "kc_init": 0.35, "kc_mid": 1.10, "kc_end": 0.65, "days": [40, 60, 60, 30]},
        "potato": {"name_fa": "سیب‌زمینی", "kc_init": 0.35, "kc_mid": 1.15, "kc_end": 0.45, "days": [30, 45, 40, 25]},
        "tomato": {"name_fa": "گوجه", "kc_init": 0.35, "kc_mid": 1.15, "kc_end": 0.70, "days": [30, 40, 50, 30]},
        "alfalfa": {"name_fa": "یونجه", "kc_init": 0.30, "kc_mid": 1.20, "kc_end": 0.75, "days": [20, 40, 30, 20]},
    }
    
    @classmethod
    def calculate_kc(cls, crop: str, growth_day: int) -> float:
        """محاسبه ضریب محصول در روز مشخص از رشد"""
        if crop not in cls.KC_DATABASE:
            return 0.8  # پیش‌فرض
        
        c = cls.KC_DATABASE[crop]
        stages = c["days"]
        total = sum(stages)
        
        if growth_day <= stages[0]:
            return c["kc_init"]
        elif growth_day <= stages[0] + stages[1]:
            # مرحله توسعه: خطی از Kc_init تا Kc_mid
            progress = (growth_day - stages[0]) / stages[1]
            return c["kc_init"] + progress * (c["kc_mid"] - c["kc_init"])
        elif growth_day <= stages[0] + stages[1] + stages[2]:
            return c["kc_mid"]
        else:
            # مرحله پایانی: خطی از Kc_mid تا Kc_end
            progress = (growth_day - sum(stages[:3])) / stages[3]
            progress = min(1.0, progress)
            return c["kc_mid"] + progress * (c["kc_end"] - c["kc_mid"])
    
    @staticmethod
    def calculate_eto_simplified(t_min: float, t_max: float, 
                                  rh_mean: float, wind_speed: float,
                                  solar_radiation: float) -> float:
        """
        محاسبه ETo با روش Hargreaves (ساده‌شده)
        مرجع: Hargreaves & Samani (1985)
        """
        t_mean = (t_min + t_max) / 2
        ra = 15.0  # تابش خارج از جو (MJ/m²/day) - ساده‌شده
        
        eto = 0.0023 * (t_mean + 17.8) * (t_max - t_min)**0.5 * ra * 0.408
        return max(0, eto)
    
    @classmethod
    def calculate_etc(cls, eto: float, crop: str, growth_day: int) -> float:
        """محاسبه تبخیر و تعرق محصول"""
        kc = cls.calculate_kc(crop, growth_day)
        return eto * kc


# ============================================================
# مدل بیلان آبی روزانه (FAO-56 Chapter 8)
# ============================================================
class SoilWaterBalance:
    """
    بیلان آبی خاک:
    SW_t = SW_{t-1} + P + I + CR - ET - RO - DP
    
    مرجع: FAO-56 Chapter 8
    """
    
    @staticmethod
    def simulate(params: Dict) -> Dict:
        """
        شبیه‌سازی بیلان آبی روزانه
        
        params:
            soil_type: نوع خاک
            root_depth_cm: عمق ریشه
            initial_moisture_percent: رطوبت اولیه (%)
            crop: نوع محصول
            days: تعداد روزهای شبیه‌سازی
            weather: لیست داده‌های هواشناسی روزانه
            irrigation_schedule: برنامه آبیاری (اختیاری)
        """
        soil = SOIL_DATABASE.get(params["soil_type"], SOIL_DATABASE["loam"])
        
        # پارامترهای خاک
        theta_fc = soil["field_capacity"]
        theta_wp = soil["wilting_point"]
        theta_s = soil["theta_s"]
        root_depth = params.get("root_depth_cm", 50)
        
        # ظرفیت‌ها (mm)
        taw = (theta_fc - theta_wp) * root_depth  # آب کل قابل دسترس
        raw = taw * 0.5  # آب به راحتی قابل دسترس (پیش‌فرض 50%)
        
        # وضعیت اولیه
        theta_init = params.get("initial_moisture_percent", 20) / 100
        sw_current = (theta_init - theta_wp) * root_depth
        sw_current = max(0, min(taw, sw_current))
        
        days = params.get("days", 30)
        weather = params.get("weather", [])
        irrigation = params.get("irrigation_schedule", [])
        crop = params.get("crop", "wheat")
        
        # اگر هواشناسی ارائه نشده، داده‌های نمونه تولید کن
        if not weather:
            weather = SoilWaterBalance._generate_sample_weather(days)
        
        # شبیه‌سازی روز به روز
        daily_results = []
        stress_days = 0
        total_etc = 0
        total_irrigation = 0
        total_rainfall = 0
        total_dp = 0
        
        for day in range(1, days + 1):
            w = weather[day - 1] if day - 1 < len(weather) else weather[-1]
            
            # محاسبه ETc
            eto = w.get("eto", 5.0)
            kc = FAO56Model.calculate_kc(crop, day)
            etc = eto * kc
            
            # ضریب تنش آب (Ks)
            if sw_current > raw:
                ks = 1.0
            else:
                ks = max(0, (sw_current - 0.5 * raw) / (0.5 * raw)) if raw > 0 else 0
            
            # ETc واقعی (با تنش)
            etc_actual = etc * ks
            
            # بارش و آبیاری
            rain = w.get("rainfall", 0)
            irr = irrigation[day - 1] if day - 1 < len(irrigation) else 0
            
            # رواناب (ساده‌شده)
            runoff = max(0, rain - soil["k_sat"] * 0.5) if rain > soil["k_sat"] else 0
            effective_rain = rain - runoff
            
            # بیلان آبی
            sw_before = sw_current
            sw_current = sw_current + effective_rain + irr - etc_actual
            
            # نشت عمیق (اگر از ظرفیت اشباع بیشتر شود)
            dp = 0
            if sw_current > taw:
                dp = sw_current - taw
                sw_current = taw
            
            # حداقل صفر
            if sw_current < 0:
                sw_current = 0
                stress_days += 1
            
            # درصد رطوبت حجمی
            theta_current = theta_wp + (sw_current / root_depth)
            
            # وضعیت
            if theta_current >= theta_fc:
                status = "اشباع"
            elif theta_current >= (theta_fc + theta_wp) / 2:
                status = "مطلوب"
            elif theta_current >= theta_wp:
                status = "تنش خفیف"
            else:
                status = "تنش شدید"
            
            daily_results.append({
                "day": day,
                "eto_mm": round(eto, 2),
                "kc": round(kc, 2),
                "etc_mm": round(etc, 2),
                "etc_actual_mm": round(etc_actual, 2),
                "ks": round(ks, 2),
                "rainfall_mm": round(rain, 2),
                "irrigation_mm": round(irr, 2),
                "runoff_mm": round(runoff, 2),
                "deep_percolation_mm": round(dp, 2),
                "soil_water_mm": round(sw_current, 2),
                "soil_water_percent": round((sw_current / taw) * 100, 1),
                "theta_percent": round(theta_current * 100, 2),
                "status": status,
            })
            
            total_etc += etc_actual
            total_irrigation += irr
            total_rainfall += rain
            total_dp += dp
        
        return {
            "soil_info": {
                "type": params["soil_type"],
                "name_fa": soil["name_fa"],
                "field_capacity": round(theta_fc * 100, 1),
                "wilting_point": round(theta_wp * 100, 1),
                "saturation": round(theta_s * 100, 1),
                "k_sat_cm_per_day": soil["k_sat"],
            },
            "capacity": {
                "taw_mm": round(taw, 2),
                "raw_mm": round(raw, 2),
                "root_depth_cm": root_depth,
            },
            "summary": {
                "total_etc_mm": round(total_etc, 2),
                "total_irrigation_mm": round(total_irrigation, 2),
                "total_rainfall_mm": round(total_rainfall, 2),
                "total_deep_percolation_mm": round(total_dp, 2),
                "stress_days": stress_days,
                "stress_percent": round((stress_days / days) * 100, 1),
            },
            "daily": daily_results,
        }
    
    @staticmethod
    def _generate_sample_weather(days: int) -> List[Dict]:
        """تولید داده‌های هواشناسی نمونه (برای دمو)"""
        import random
        weather = []
        for i in range(days):
            # الگوی فصلی ساده
            season_factor = 1 + 0.3 * math.sin(2 * math.pi * i / 365)
            eto = 4.0 + 2.0 * season_factor + random.uniform(-0.5, 0.5)
            
            # بارش تصادفی (۲۰٪ روزها بارانی)
            rainfall = 0
            if random.random() < 0.2:
                rainfall = random.uniform(2, 15)
            
            weather.append({
                "eto": round(max(0, eto), 2),
                "rainfall": round(rainfall, 2),
            })
        return weather


# ============================================================
# توابع کمکی
# ============================================================
def get_all_soils() -> Dict:
    """دریافت لیست تمام خاک‌ها"""
    return {k: {
        "name_fa": v["name_fa"],
        "name_en": v["name_en"],
        "field_capacity": v["field_capacity"],
        "wilting_point": v["wilting_point"],
        "k_sat": v["k_sat"],
        "color": v["color"],
    } for k, v in SOIL_DATABASE.items()}


def get_all_crops() -> Dict:
    """دریافت لیست تمام محصولات"""
    return {k: {
        "name_fa": v["name_fa"],
        "kc_init": v["kc_init"],
        "kc_mid": v["kc_mid"],
        "kc_end": v["kc_end"],
        "total_days": sum(v["days"]),
    } for k, v in FAO56Model.KC_DATABASE.items()}
'''
    
    write_file(API_DIR / "services" / "soil_water_core.py", content)


# ========== 2. Router بک‌اند ==========
def create_router():
    print("\n🔌 ایجاد Soil Water Router...")
    
    content = '''# api/modules/soil_water/router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import sys
from pathlib import Path

# اضافه کردن ریشه پروژه به path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from api.services.soil_water_core import (
    VanGenuchtenModel, FAO56Model, SoilWaterBalance,
    SOIL_DATABASE, get_all_soils, get_all_crops
)

router = APIRouter(prefix="/soil-water", tags=["Soil Water"])


# ============ Models ============
class SWCCRequest(BaseModel):
    soil_type: str = Field("loam", description="نوع خاک")
    n_points: int = Field(100, ge=20, le=500)


class WaterBalanceRequest(BaseModel):
    soil_type: str = Field("loam")
    root_depth_cm: float = Field(50, ge=10, le=300)
    initial_moisture_percent: float = Field(20, ge=0, le=50)
    crop: str = Field("wheat")
    days: int = Field(30, ge=7, le=365)
    irrigation_schedule: Optional[List[float]] = None


class KcRequest(BaseModel):
    crop: str
    growth_day: int = Field(..., ge=1, le=365)


# ============ Endpoints ============
@router.get("/soils")
async def list_soils():
    """لیست تمام انواع خاک با پارامترهای استاندارد"""
    return get_all_soils()


@router.get("/crops")
async def list_crops():
    """لیست تمام محصولات با ضرایب Kc"""
    return get_all_crops()


@router.post("/swcc")
async def calculate_swcc(request: SWCCRequest):
    """محاسبه منحنی مشخصه رطوبت خاک (SWCC) با مدل van Genuchten"""
    if request.soil_type not in SOIL_DATABASE:
        raise HTTPException(400, f"نوع خاک نامعتبر: {request.soil_type}")
    
    curve = VanGenuchtenModel.generate_swcc(request.soil_type, request.n_points)
    soil = SOIL_DATABASE[request.soil_type]
    
    return {
        "soil_type": request.soil_type,
        "soil_name_fa": soil["name_fa"],
        "parameters": {
            "theta_r": soil["theta_r"],
            "theta_s": soil["theta_s"],
            "alpha_vg": soil["alpha_vg"],
            "n_vg": soil["n_vg"],
            "k_sat": soil["k_sat"],
        },
        "curve": curve,
    }


@router.post("/kc")
async def calculate_kc(request: KcRequest):
    """محاسبه ضریب محصول (Kc) در روز مشخص"""
    kc = FAO56Model.calculate_kc(request.crop, request.growth_day)
    crop_data = FAO56Model.KC_DATABASE.get(request.crop, {})
    
    return {
        "crop": request.crop,
        "crop_name_fa": crop_data.get("name_fa", "نامشخص"),
        "growth_day": request.growth_day,
        "kc": round(kc, 3),
        "stages_days": crop_data.get("days", []),
    }


@router.post("/water-balance")
async def calculate_water_balance(request: WaterBalanceRequest):
    """شبیه‌سازی بیلان آبی روزانه"""
    if request.soil_type not in SOIL_DATABASE:
        raise HTTPException(400, f"نوع خاک نامعتبر: {request.soil_type}")
    
    params = {
        "soil_type": request.soil_type,
        "root_depth_cm": request.root_depth_cm,
        "initial_moisture_percent": request.initial_moisture_percent,
        "crop": request.crop,
        "days": request.days,
        "irrigation_schedule": request.irrigation_schedule or [],
    }
    
    result = SoilWaterBalance.simulate(params)
    return result


@router.get("/compare-soils")
async def compare_soils():
    """مقایسه پارامترهای هیدرولیک تمام خاک‌ها"""
    comparison = []
    for key, soil in SOIL_DATABASE.items():
        comparison.append({
            "key": key,
            "name_fa": soil["name_fa"],
            "name_en": soil["name_en"],
            "field_capacity_percent": round(soil["field_capacity"] * 100, 1),
            "wilting_point_percent": round(soil["wilting_point"] * 100, 1),
            "available_water_percent": round((soil["field_capacity"] - soil["wilting_point"]) * 100, 1),
            "k_sat_cm_per_day": soil["k_sat"],
            "color": soil["color"],
        })
    return comparison
'''
    
    write_file(API_DIR / "modules" / "soil_water" / "router.py", content)


# ========== 3. داشبورد فرانت‌اند پیشرفته ==========
def create_dashboard():
    print("\n📊 ایجاد داشبورد پیشرفته آب خاک...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Droplets, Calculator, AlertTriangle, CheckCircle,
  TrendingUp, Sprout, Info, Loader2, Database, FlaskConical,
  BarChart3, LineChart as LineChartIcon, Activity
} from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(m => m.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(m => m.Area), { ssr: false });
const ComposedChart = dynamic(() => import("recharts").then(m => m.ComposedChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });
const ReferenceLine = dynamic(() => import("recharts").then(m => m.ReferenceLine), { ssr: false });

const API_BASE = "http://localhost:8000/api/v1/soil-water";

export default function SoilWaterPage() {
  const [activeTab, setActiveTab] = useState<"balance" | "swcc" | "compare">("balance");
  const [isCalculating, setIsCalculating] = useState(false);
  const [balanceResult, setBalanceResult] = useState<any>(null);
  const [swccResult, setSwccResult] = useState<any>(null);
  const [soils, setSoils] = useState<any>({});
  const [crops, setCrops] = useState<any>({});
  const [error, setError] = useState("");

  // Form state
  const [formData, setFormData] = useState({
    soil_type: "loam",
    root_depth_cm: 50,
    initial_moisture_percent: 22,
    crop: "wheat",
    days: 30,
  });

  const [swccSoil, setSwccSoil] = useState("loam");

  useEffect(() => {
    loadReferenceData();
  }, []);

  const loadReferenceData = async () => {
    try {
      const [soilsRes, cropsRes] = await Promise.all([
        fetch(`${API_BASE}/soils`),
        fetch(`${API_BASE}/crops`),
      ]);
      if (soilsRes.ok) setSoils(await soilsRes.json());
      if (cropsRes.ok) setCrops(await cropsRes.json());
    } catch (e) {
      console.error("Failed to load reference data");
    }
  };

  const handleCalculateBalance = async () => {
    setIsCalculating(true);
    setError("");
    setBalanceResult(null);

    try {
      const res = await fetch(`${API_BASE}/water-balance`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData),
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "خطا در محاسبه");
      }

      setBalanceResult(await res.json());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsCalculating(false);
    }
  };

  const handleCalculateSWCC = async () => {
    setIsCalculating(true);
    setError("");
    setSwccResult(null);

    try {
      const res = await fetch(`${API_BASE}/swcc`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ soil_type: swccSoil, n_points: 80 }),
      });

      if (!res.ok) throw new Error("خطا در محاسبه");
      setSwccResult(await res.json());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsCalculating(false);
    }
  };

  const getStatusColor = (status: string) => {
    if (status.includes("اشباع")) return "text-blue-400 bg-blue-500/20 border-blue-500/30";
    if (status.includes("مطلوب")) return "text-emerald-400 bg-emerald-500/20 border-emerald-500/30";
    if (status.includes("خفیف")) return "text-amber-400 bg-amber-500/20 border-amber-500/30";
    return "text-red-400 bg-red-500/20 border-red-500/30";
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-sky-500 to-blue-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-4">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-sky-500 to-blue-600 shadow-2xl">
                <Droplets className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sky-400 text-sm font-medium mb-1">ماژول تخصصی • FAO-56 & van Genuchten-Mualem</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">آب خاک و دینامیک رطوبت</h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  تحلیل علمی رطوبت خاک با مدل‌های استاندارد جهانی، محاسبه بیلان آبی روزانه، و منحنی مشخصه رطوبت
                </p>
              </div>
            </div>

            {/* Standards badges */}
            <div className="flex flex-wrap gap-2 mt-4">
              {["FAO-56", "van Genuchten", "USDA Rosetta", "Penman-Monteith", "Mualem"].map(s => (
                <span key={s} className="px-3 py-1 bg-sky-500/10 border border-sky-500/30 rounded-full text-xs text-sky-300">
                  {s}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6 flex-wrap">
          {[
            { id: "balance", label: "بیلان آبی روزانه", icon: Activity },
            { id: "swcc", label: "منحنی مشخصه رطوبت", icon: LineChartIcon },
            { id: "compare", label: "مقایسه خاک‌ها", icon: Database },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-sky-600 text-white shadow-lg shadow-sky-500/30"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* ============ WATER BALANCE TAB ============ */}
        {activeTab === "balance" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Input Form */}
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Calculator className="h-5 w-5 text-sky-400" />
                پارامترهای شبیه‌سازی
              </h3>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-bold text-white mb-2">نوع خاک (USDA)</label>
                  <select
                    value={formData.soil_type}
                    onChange={(e) => setFormData({ ...formData, soil_type: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                  >
                    {Object.entries(soils).map(([key, soil]: any) => (
                      <option key={key} value={key}>
                        {soil.name_fa} ({soil.name_en})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">نوع محصول</label>
                  <select
                    value={formData.crop}
                    onChange={(e) => setFormData({ ...formData, crop: e.target.value })}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white text-sm"
                  >
                    {Object.entries(crops).map(([key, crop]: any) => (
                      <option key={key} value={key}>
                        {crop.name_fa} (Kc={crop.kc_mid})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    عمق ریشه: {formData.root_depth_cm} cm
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="200"
                    step="5"
                    value={formData.root_depth_cm}
                    onChange={(e) => setFormData({ ...formData, root_depth_cm: parseInt(e.target.value) })}
                    className="w-full accent-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    رطوبت اولیه: {formData.initial_moisture_percent}%
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="50"
                    step="1"
                    value={formData.initial_moisture_percent}
                    onChange={(e) => setFormData({ ...formData, initial_moisture_percent: parseInt(e.target.value) })}
                    className="w-full accent-sky-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-bold text-white mb-2">
                    مدت شبیه‌سازی: {formData.days} روز
                  </label>
                  <input
                    type="range"
                    min="7"
                    max="180"
                    step="1"
                    value={formData.days}
                    onChange={(e) => setFormData({ ...formData, days: parseInt(e.target.value) })}
                    className="w-full accent-sky-500"
                  />
                </div>

                <button
                  onClick={handleCalculateBalance}
                  disabled={isCalculating}
                  className="w-full py-3 bg-gradient-to-l from-sky-500 to-blue-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-sky-500/30 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                >
                  {isCalculating ? (
                    <><Loader2 className="h-5 w-5 animate-spin" /> در حال محاسبه...</>
                  ) : (
                    <><Droplets className="h-5 w-5" /> شروع شبیه‌سازی بیلان آبی</>
                  )}
                </button>

                {error && (
                  <div className="p-3 bg-red-500/20 border border-red-500/30 rounded-lg text-red-300 text-sm">
                    {error}
                  </div>
                )}
              </div>
            </div>

            {/* Results */}
            <div className="lg:col-span-2 space-y-6">
              {!balanceResult ? (
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-12 text-center h-full flex flex-col items-center justify-center">
                  <FlaskConical className="h-16 w-16 text-slate-600 mb-4" />
                  <h3 className="text-xl font-bold text-white mb-2">پارامترها را وارد کنید</h3>
                  <p className="text-slate-400">پس از محاسبه، نمودارهای بیلان آبی روزانه و تحلیل تنش نمایش داده می‌شود</p>
                </div>
              ) : (
                <>
                  {/* Summary Cards */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                      <p className="text-xs text-slate-400 mb-1">نوع خاک</p>
                      <p className="text-lg font-black text-sky-400">{balanceResult.soil_info.name_fa}</p>
                      <p className="text-xs text-slate-500">FC: {balanceResult.soil_info.field_capacity}%</p>
                    </div>
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                      <p className="text-xs text-slate-400 mb-1">TAW (آب کل قابل دسترس)</p>
                      <p className="text-2xl font-black text-sky-400">{balanceResult.capacity.taw_mm}</p>
                      <p className="text-xs text-slate-500">میلی‌متر</p>
                    </div>
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                      <p className="text-xs text-slate-400 mb-1">ETc کل دوره</p>
                      <p className="text-2xl font-black text-amber-400">{balanceResult.summary.total_etc_mm}</p>
                      <p className="text-xs text-slate-500">میلی‌متر</p>
                    </div>
                    <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                      <p className="text-xs text-slate-400 mb-1">روزهای تنش</p>
                      <p className={`text-2xl font-black ${balanceResult.summary.stress_days > 0 ? "text-red-400" : "text-emerald-400"}`}>
                        {balanceResult.summary.stress_days}
                      </p>
                      <p className="text-xs text-slate-500">از {formData.days} روز</p>
                    </div>
                  </div>

                  {/* Soil Water Chart */}
                  <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-sky-400" />
                      دینامیک رطوبت خاک در طول زمان
                    </h3>
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={balanceResult.daily}>
                          <defs>
                            <linearGradient id="swGrad" x1="0" y1="0" x2="0" y2="1">
                              <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.6}/>
                              <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                            </linearGradient>
                          </defs>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                          <XAxis dataKey="day" stroke="#64748b" fontSize={11} label={{ value: "روز", position: "insideBottom", offset: -5, fill: "#64748b" }} />
                          <YAxis stroke="#64748b" fontSize={11} />
                          <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                          <Legend />
                          <Area type="monotone" dataKey="soil_water_percent" stroke="#0ea5e9" strokeWidth={2} fill="url(#swGrad)" name="رطوبت خاک (%)" />
                          <Line type="monotone" dataKey="etc_actual_mm" stroke="#f59e0b" strokeWidth={2} dot={false} name="ETc واقعی (mm)" />
                          <Bar dataKey="rainfall_mm" fill="#3b82f6" opacity={0.6} name="بارش (mm)" />
                          <Bar dataKey="irrigation_mm" fill="#06b6d4" opacity={0.6} name="آبیاری (mm)" />
                        </ComposedChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Kc & ET Chart */}
                  <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                      <Sprout className="h-5 w-5 text-emerald-400" />
                      ضریب محصول (Kc) و تبخیر و تعرق
                    </h3>
                    <div className="h-64">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={balanceResult.daily}>
                          <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                          <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                          <YAxis yAxisId="left" stroke="#64748b" fontSize={11} />
                          <YAxis yAxisId="right" orientation="right" stroke="#64748b" fontSize={11} />
                          <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                          <Legend />
                          <Line yAxisId="left" type="monotone" dataKey="kc" stroke="#10b981" strokeWidth={2} dot={false} name="ضریب محصول Kc" />
                          <Line yAxisId="right" type="monotone" dataKey="eto_mm" stroke="#f59e0b" strokeWidth={2} dot={false} name="ETo (mm)" />
                          <Line yAxisId="right" type="monotone" dataKey="etc_mm" stroke="#ef4444" strokeWidth={2} dot={false} name="ETc (mm)" />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="bg-gradient-to-br from-sky-900/30 to-blue-900/30 border border-sky-500/30 rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-3 flex items-center gap-2">
                      <Sprout className="h-5 w-5 text-sky-400" />
                      تحلیل و توصیه‌های مدیریتی
                    </h3>
                    <div className="space-y-2 text-sm text-slate-300">
                      {balanceResult.summary.stress_days > 0 ? (
                        <>
                          <div className="flex items-start gap-2 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
                            <AlertTriangle className="h-4 w-4 text-red-400 flex-shrink-0 mt-0.5" />
                            <span>
                              در <strong className="text-red-300">{balanceResult.summary.stress_days} روز</strong> از دوره شبیه‌سازی، 
                              گیاه دچار تنش آبی شده است ({balanceResult.summary.stress_percent}% از زمان).
                            </span>
                          </div>
                          <div className="flex items-start gap-2 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                            <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                            <span>
                              توصیه می‌شود برنامه آبیاری منظم با حجم حداقل <strong className="text-emerald-300">
                              {Math.round(balanceResult.summary.total_etc_mm / formData.days)} میلی‌متر در روز
                              </strong> اعمال شود.
                            </span>
                          </div>
                        </>
                      ) : (
                        <div className="flex items-start gap-2 p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                          <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0 mt-0.5" />
                          <span>رطوبت خاک در تمام دوره در محدوده مطلوب بوده است.</span>
                        </div>
                      )}
                      <div className="flex items-start gap-2 p-3 bg-slate-800/50 rounded-lg">
                        <Info className="h-4 w-4 text-sky-400 flex-shrink-0 mt-0.5" />
                        <span>
                          <strong className="text-slate-200">هدایت هیدرولیکی اشباع:</strong> {balanceResult.soil_info.k_sat_cm_per_day} cm/day
                          {balanceResult.soil_info.k_sat_cm_per_day < 0.5 && " (خاک با زهکشی کند - مراقب آب‌گرفتگی باشید)"}
                          {balanceResult.soil_info.k_sat_cm_per_day > 5 && " (خاک با زهکشی سریع - آبیاری‌های مکرر نیاز است)"}
                        </span>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* ============ SWCC TAB ============ */}
        {activeTab === "swcc" && (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">انتخاب خاک</h3>
              <select
                value={swccSoil}
                onChange={(e) => setSwccSoil(e.target.value)}
                className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-white mb-4"
              >
                {Object.entries(soils).map(([key, soil]: any) => (
                  <option key={key} value={key}>{soil.name_fa}</option>
                ))}
              </select>
              <button
                onClick={handleCalculateSWCC}
                disabled={isCalculating}
                className="w-full py-3 bg-gradient-to-l from-sky-500 to-blue-600 text-white rounded-xl font-bold disabled:opacity-50"
              >
                {isCalculating ? "در حال محاسبه..." : "محاسبه منحنی SWCC"}
              </button>

              {swccResult && (
                <div className="mt-4 space-y-2 text-sm">
                  <p className="text-slate-400">پارامترهای van Genuchten:</p>
                  <div className="bg-slate-800/50 rounded-lg p-3 font-mono text-xs space-y-1">
                    <p>θr = {swccResult.parameters.theta_r}</p>
                    <p>θs = {swccResult.parameters.theta_s}</p>
                    <p>α = {swccResult.parameters.alpha_vg} /cm</p>
                    <p>n = {swccResult.parameters.n_vg}</p>
                    <p>Ks = {swccResult.parameters.k_sat} cm/day</p>
                  </div>
                </div>
              )}
            </div>

            <div className="lg:col-span-2 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
              {!swccResult ? (
                <div className="h-96 flex items-center justify-center text-slate-500">
                  <div className="text-center">
                    <LineChartIcon className="h-16 w-16 mx-auto mb-3 opacity-30" />
                    <p>نوع خاک را انتخاب و منحنی را محاسبه کنید</p>
                  </div>
                </div>
              ) : (
                <>
                  <h3 className="text-lg font-bold text-white mb-4">
                    منحنی مشخصه رطوبت خاک (SWCC) - {swccResult.soil_name_fa}
                  </h3>
                  <div className="h-96">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={swccResult.curve}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis 
                          dataKey="psi_kpa" 
                          type="number" 
                          scale="log" 
                          domain={[0.1, 1500]}
                          stroke="#64748b" 
                          fontSize={11}
                          label={{ value: 'مکش (kPa) - مقیاس لگاریتمی', position: 'insideBottom', offset: -5, fill: '#64748b' }}
                        />
                        <YAxis 
                          stroke="#64748b" 
                          fontSize={11}
                          label={{ value: 'رطوبت حجمی (%)', angle: -90, position: 'insideLeft', fill: '#64748b' }}
                        />
                        <Tooltip 
                          contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }}
                          formatter={(value: any) => [`${value}%`, 'رطوبت']}
                          labelFormatter={(label) => `مکش: ${label} kPa`}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="theta_percent" 
                          stroke="#0ea5e9" 
                          strokeWidth={3} 
                          dot={false}
                          name="رطوبت حجمی"
                        />
                        <ReferenceLine x={33} stroke="#10b981" strokeDasharray="5 5" label={{ value: "FC", fill: "#10b981" }} />
                        <ReferenceLine x={1500} stroke="#ef4444" strokeDasharray="5 5" label={{ value: "WP", fill: "#ef4444" }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-4 flex items-start gap-2 text-xs text-slate-400 bg-slate-800/50 p-3 rounded-lg">
                    <Info className="h-4 w-4 text-sky-400 flex-shrink-0 mt-0.5" />
                    <p>
                      <strong className="text-slate-200">تفسیر:</strong> خط سبز (FC = 33 kPa) ظرفیت زراعی و خط قرمز (WP = 1500 kPa) نقطه پژمردگی است. 
                      ناحیه بین این دو خط، "آب قابل دسترس برای گیاه" (AWC) است.
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>
        )}

        {/* ============ COMPARE TAB ============ */}
        {activeTab === "compare" && (
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">مقایسه پارامترهای هیدرولیک خاک‌ها</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-slate-700">
                    <th className="text-right py-3 px-2 text-slate-300">نوع خاک</th>
                    <th className="text-right py-3 px-2 text-slate-300">FC (%)</th>
                    <th className="text-right py-3 px-2 text-slate-300">WP (%)</th>
                    <th className="text-right py-3 px-2 text-slate-300">AWC (%)</th>
                    <th className="text-right py-3 px-2 text-slate-300">Ks (cm/day)</th>
                    <th className="text-right py-3 px-2 text-slate-300">ویژگی</th>
                  </tr>
                </thead>
                <tbody>
                  {Object.entries(soils).map(([key, soil]: any) => {
                    const awc = (soil.field_capacity - soil.wilting_point) * 100;
                    return (
                      <tr key={key} className="border-b border-slate-800 hover:bg-slate-800/50">
                        <td className="py-3 px-2">
                          <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: soil.color }} />
                            <span className="text-white font-bold">{soil.name_fa}</span>
                          </div>
                        </td>
                        <td className="py-3 px-2 text-slate-300">{(soil.field_capacity * 100).toFixed(1)}</td>
                        <td className="py-3 px-2 text-slate-300">{(soil.wilting_point * 100).toFixed(1)}</td>
                        <td className="py-3 px-2">
                          <span className="font-bold text-sky-400">{awc.toFixed(1)}</span>
                        </td>
                        <td className="py-3 px-2 text-slate-300">{soil.k_sat}</td>
                        <td className="py-3 px-2 text-xs text-slate-400">
                          {soil.k_sat > 5 ? "زهکشی سریع" : soil.k_sat < 0.5 ? "زهکشی کند" : "متعادل"}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "soil-water" / "page.tsx", content)


# ========== Main ==========
def main():
    print("💧 فاز ۱: هسته علمی ماژول آب خاک")
    print("=" * 70)
    print("بر اساس استانداردهای: FAO-56, van Genuchten-Mualem, USDA Rosetta")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    create_scientific_core()
    create_router()
    create_dashboard()
    
    print("\n" + "=" * 70)
    print("✅ فاز ۱ تکمیل شد!")
    print("\n🎯 ویژگی‌های علمی پیاده‌سازی شده:")
    print("   🧬 مدل van Genuchten-Mualem (1980):")
    print("      • منحنی مشخصه رطوبت (SWCC)")
    print("      • هدایت هیدرولیکی غیراشباع K(θ)")
    print("      • ۱۱ نوع خاک USDA با پارامترهای واقعی")
    print("")
    print("   🌾 مدل FAO-56 (Allen et al., 1998):")
    print("      • محاسبه ضریب محصول Kc (۴ مرحله رشد)")
    print("      • ۱۰ محصول اصلی با ضرایب استاندارد")
    print("      • تبخیر و تعرق محصول ETc = ETo × Kc")
    print("")
    print("   💧 مدل بیلان آبی روزانه:")
    print("      • SW_t = SW_{t-1} + P + I + CR - ET - RO - DP")
    print("      • ضریب تنش آب Ks")
    print("      • شبیه‌سازی تا ۳۶۵ روز")
    print("")
    print("   📊 داشبورد پیشرفته:")
    print("      • تب ۱: بیلان آبی روزانه با نمودارهای ترکیبی")
    print("      • تب ۲: منحنی مشخصه رطوبت (SWCC)")
    print("      • تب ۳: مقایسه ۱۱ نوع خاک")
    print("")
    print("🚀 گام بعدی:")
    print("   1. پاک‌سازی کش:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   2. اجرای سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   3. اجرای سرور فرانت‌اند:")
    print("      cd apps\\web")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   4. مشاهده: http://localhost:3001/soil-water")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())