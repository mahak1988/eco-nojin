#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
💧 تکمیل ماژول آب خاک
- تحلیل هوشمند دینامیک رطوبت
- توصیه‌های تخصصی بر اساس بافت خاک
- شاخص‌های پیشرفته (CWSI, WUE, IE)
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


# ============================================================
# فایل 1: بهبود بک‌اند - تحلیل پیشرفته
# ============================================================
def enhance_backend():
    print("\n🧬 بهبود بک‌اند با تحلیل پیشرفته...")
    
    content = '''# api/services/soil_water_core.py
"""
هسته علمی ماژول آب خاک - نسخه پیشرفته
با تحلیل هوشمند و توصیه‌های تخصصی
"""
import math
from typing import Dict, List
from dataclasses import dataclass


# ============================================================
# پایگاه داده خاک (USDA Rosetta)
# ============================================================
SOIL_DATABASE = {
    "sand": {
        "name_fa": "شن", "name_en": "Sand",
        "theta_r": 0.045, "theta_s": 0.430,
        "alpha_vg": 0.145, "n_vg": 2.68,
        "k_sat": 8.25, "bulk_density": 1.55,
        "field_capacity": 0.10, "wilting_point": 0.05,
        "color": "#f59e0b",
        "irrigation_advice": {
            "frequency": "هر ۱-۲ روز",
            "depth": "کم (۱۰-۱۵ میلی‌متر)",
            "method": "قطره‌ای یا بارانی با شدت کم",
            "risk": "خطر شستشوی مواد مغذی و تبخیر بالا"
        }
    },
    "loamy_sand": {
        "name_fa": "شن لومی", "name_en": "Loamy Sand",
        "theta_r": 0.057, "theta_s": 0.410,
        "alpha_vg": 0.124, "n_vg": 2.28,
        "k_sat": 4.50, "bulk_density": 1.50,
        "field_capacity": 0.14, "wilting_point": 0.07,
        "color": "#eab308",
        "irrigation_advice": {
            "frequency": "هر ۲-۳ روز",
            "depth": "کم تا متوسط (۱۵-۲۰ میلی‌متر)",
            "method": "قطره‌ای ترجیحاً",
            "risk": "زهکشی نسبتاً سریع"
        }
    },
    "sandy_loam": {
        "name_fa": "لومی شنی", "name_en": "Sandy Loam",
        "theta_r": 0.065, "theta_s": 0.410,
        "alpha_vg": 0.075, "n_vg": 1.89,
        "k_sat": 2.50, "bulk_density": 1.45,
        "field_capacity": 0.20, "wilting_point": 0.10,
        "color": "#d97706",
        "irrigation_advice": {
            "frequency": "هر ۳-۴ روز",
            "depth": "متوسط (۲۰-۳۰ میلی‌متر)",
            "method": "قطره‌ای یا بارانی",
            "risk": "متعادل - مدیریت آسان"
        }
    },
    "loam": {
        "name_fa": "لوم", "name_en": "Loam",
        "theta_r": 0.078, "theta_s": 0.430,
        "alpha_vg": 0.036, "n_vg": 1.56,
        "k_sat": 1.20, "bulk_density": 1.35,
        "field_capacity": 0.27, "wilting_point": 0.13,
        "color": "#84cc16",
        "irrigation_advice": {
            "frequency": "هر ۴-۶ روز",
            "depth": "متوسط تا عمیق (۲۵-۴۰ میلی‌متر)",
            "method": "هر روش آبیاری مناسب است",
            "risk": "ایده‌آل برای اکثر محصولات"
        }
    },
    "silty_loam": {
        "name_fa": "لومی سیلتی", "name_en": "Silty Loam",
        "theta_r": 0.067, "theta_s": 0.450,
        "alpha_vg": 0.028, "n_vg": 1.45,
        "k_sat": 0.80, "bulk_density": 1.30,
        "field_capacity": 0.32, "wilting_point": 0.14,
        "color": "#22c55e",
        "irrigation_advice": {
            "frequency": "هر ۵-۷ روز",
            "depth": "عمیق (۳۰-۴۵ میلی‌متر)",
            "method": "جویی یا قطره‌ای",
            "risk": "خطر آب‌گرفتگی در آبیاری سنگین"
        }
    },
    "sandy_clay_loam": {
        "name_fa": "لومی رسی شنی", "name_en": "Sandy Clay Loam",
        "theta_r": 0.100, "theta_s": 0.390,
        "alpha_vg": 0.059, "n_vg": 1.51,
        "k_sat": 0.60, "bulk_density": 1.35,
        "field_capacity": 0.25, "wilting_point": 0.14,
        "color": "#14b8a6",
        "irrigation_advice": {
            "frequency": "هر ۵-۷ روز",
            "depth": "متوسط (۲۵-۳۵ میلی‌متر)",
            "method": "قطره‌ای ترجیحاً",
            "risk": "خطر تشکیل پوسته سطحی"
        }
    },
    "clay_loam": {
        "name_fa": "لومی رسی", "name_en": "Clay Loam",
        "theta_r": 0.095, "theta_s": 0.410,
        "alpha_vg": 0.019, "n_vg": 1.31,
        "k_sat": 0.35, "bulk_density": 1.30,
        "field_capacity": 0.32, "wilting_point": 0.20,
        "color": "#06b6d4",
        "irrigation_advice": {
            "frequency": "هر ۷-۱۰ روز",
            "depth": "عمیق (۳۵-۵۰ میلی‌متر)",
            "method": "جویی یا قطره‌ای با فاصله زیاد",
            "risk": "خطر آب‌گرفتگی و کمبود اکسیژن ریشه"
        }
    },
    "silty_clay_loam": {
        "name_fa": "لومی رسی سیلتی", "name_en": "Silty Clay Loam",
        "theta_r": 0.089, "theta_s": 0.430,
        "alpha_vg": 0.016, "n_vg": 1.26,
        "k_sat": 0.25, "bulk_density": 1.25,
        "field_capacity": 0.35, "wilting_point": 0.21,
        "color": "#3b82f6",
        "irrigation_advice": {
            "frequency": "هر ۷-۱۰ روز",
            "depth": "عمیق (۳۵-۵۰ میلی‌متر)",
            "method": "جویی با شیب مناسب",
            "risk": "خطر بسیار بالای آب‌گرفتگی"
        }
    },
    "sandy_clay": {
        "name_fa": "رسی شنی", "name_en": "Sandy Clay",
        "theta_r": 0.100, "theta_s": 0.380,
        "alpha_vg": 0.027, "n_vg": 1.23,
        "k_sat": 0.30, "bulk_density": 1.35,
        "field_capacity": 0.30, "wilting_point": 0.20,
        "color": "#8b5cf6",
        "irrigation_advice": {
            "frequency": "هر ۶-۸ روز",
            "depth": "متوسط (۲۵-۳۵ میلی‌متر)",
            "method": "قطره‌ای",
            "risk": "ترک خوردن در خشکی"
        }
    },
    "silty_clay": {
        "name_fa": "رسی سیلتی", "name_en": "Silty Clay",
        "theta_r": 0.089, "theta_s": 0.400,
        "alpha_vg": 0.013, "n_vg": 1.17,
        "k_sat": 0.18, "bulk_density": 1.25,
        "field_capacity": 0.37, "wilting_point": 0.24,
        "color": "#a855f7",
        "irrigation_advice": {
            "frequency": "هر ۱۰-۱۴ روز",
            "depth": "عمیق (۴۰-۶۰ میلی‌متر)",
            "method": "فقط قطره‌ای یا زیرسطحی",
            "risk": "خطر بسیار بالای غرقابی"
        }
    },
    "clay": {
        "name_fa": "رس", "name_en": "Clay",
        "theta_r": 0.068, "theta_s": 0.380,
        "alpha_vg": 0.010, "n_vg": 1.15,
        "k_sat": 0.12, "bulk_density": 1.20,
        "field_capacity": 0.38, "wilting_point": 0.25,
        "color": "#ec4899",
        "irrigation_advice": {
            "frequency": "هر ۱۰-۱۴ روز",
            "depth": "عمیق (۴۰-۶۰ میلی‌متر)",
            "method": "قطره‌ای با دبی کم",
            "risk": "خطر بحرانی آب‌گرفتگی و شوری"
        }
    },
}


# ============================================================
# پایگاه داده محصولات (FAO-56)
# ============================================================
CROPS_DATABASE = {
    "wheat": {"name_fa": "گندم", "kc_init": 0.30, "kc_mid": 1.15, "kc_end": 0.30, "stages_days": [30, 50, 40, 30], "root_depth_cm": 80, "ky": 1.10},
    "barley": {"name_fa": "جو", "kc_init": 0.30, "kc_mid": 1.15, "kc_end": 0.25, "stages_days": [25, 45, 40, 30], "root_depth_cm": 70, "ky": 0.90},
    "maize": {"name_fa": "ذرت", "kc_init": 0.30, "kc_mid": 1.20, "kc_end": 0.50, "stages_days": [25, 55, 40, 30], "root_depth_cm": 100, "ky": 1.25},
    "rice": {"name_fa": "برنج", "kc_init": 1.05, "kc_mid": 1.20, "kc_end": 0.90, "stages_days": [30, 60, 40, 30], "root_depth_cm": 50, "ky": 1.10},
    "soybean": {"name_fa": "سویا", "kc_init": 0.30, "kc_mid": 1.15, "kc_end": 0.35, "stages_days": [30, 45, 40, 25], "root_depth_cm": 70, "ky": 1.10},
    "cotton": {"name_fa": "پنبه", "kc_init": 0.35, "kc_mid": 1.15, "kc_end": 0.30, "stages_days": [40, 60, 50, 30], "root_depth_cm": 120, "ky": 0.85},
    "tomato": {"name_fa": "گوجه", "kc_init": 0.35, "kc_mid": 1.15, "kc_end": 0.70, "stages_days": [30, 40, 50, 30], "root_depth_cm": 80, "ky": 1.10},
    "potato": {"name_fa": "سیب‌زمینی", "kc_init": 0.35, "kc_mid": 1.15, "kc_end": 0.45, "stages_days": [30, 45, 40, 25], "root_depth_cm": 60, "ky": 1.15},
    "alfalfa": {"name_fa": "یونجه", "kc_init": 0.30, "kc_mid": 1.20, "kc_end": 0.75, "stages_days": [20, 40, 30, 20], "root_depth_cm": 150, "ky": 1.10},
    "pistachio": {"name_fa": "پسته", "kc_init": 0.30, "kc_mid": 0.85, "kc_end": 0.55, "stages_days": [60, 90, 90, 60], "root_depth_cm": 180, "ky": 0.80},
}


# ============================================================
# محاسبه Kc در هر مرحله
# ============================================================
def calculate_kc(crop_key: str, day: int) -> float:
    """محاسبه ضریب محصول در روز مشخص"""
    crop = CROPS_DATABASE.get(crop_key)
    if not crop:
        return 0.8
    
    stages = crop["stages_days"]
    total = sum(stages)
    
    if day <= stages[0]:
        return crop["kc_init"]
    elif day <= stages[0] + stages[1]:
        progress = (day - stages[0]) / stages[1]
        return crop["kc_init"] + progress * (crop["kc_mid"] - crop["kc_init"])
    elif day <= stages[0] + stages[1] + stages[2]:
        return crop["kc_mid"]
    else:
        progress = min(1.0, (day - sum(stages[:3])) / stages[3])
        return crop["kc_mid"] + progress * (crop["kc_end"] - crop["kc_mid"])


def get_growth_stage(crop_key: str, day: int) -> str:
    """تعیین مرحله رشد"""
    crop = CROPS_DATABASE.get(crop_key)
    if not crop:
        return "نامشخص"
    
    stages = crop["stages_days"]
    if day <= stages[0]:
        return "اولیه"
    elif day <= stages[0] + stages[1]:
        return "توسعه"
    elif day <= stages[0] + stages[1] + stages[2]:
        return "میانی"
    else:
        return "پایانی"


# ============================================================
# شبیه‌سازی بیلان آبی پیشرفته
# ============================================================
def simulate_water_balance(params: Dict) -> Dict:
    """
    شبیه‌سازی پیشرفته بیلان آبی با تحلیل هوشمند
    """
    soil = SOIL_DATABASE.get(params["soil_type"], SOIL_DATABASE["loam"])
    crop = CROPS_DATABASE.get(params.get("crop", "wheat"), CROPS_DATABASE["wheat"])
    
    # پارامترهای خاک
    theta_fc = soil["field_capacity"]
    theta_wp = soil["wilting_point"]
    theta_s = soil["theta_s"]
    root_depth = params.get("root_depth_cm", crop["root_depth_cm"])
    
    # ظرفیت‌ها (mm)
    taw = (theta_fc - theta_wp) * root_depth
    raw = taw * 0.5
    
    # وضعیت اولیه
    theta_init = params.get("initial_moisture_percent", 20) / 100
    sw_current = (theta_init - theta_wp) * root_depth
    sw_current = max(0, min(taw, sw_current))
    
    days = params.get("days", 30)
    crop_key = params.get("crop", "wheat")
    
    # تولید داده‌های هواشناسی نمونه
    weather = _generate_sample_weather(days)
    
    # شبیه‌سازی روز به روز
    daily_results = []
    stress_days = 0
    optimal_days = 0
    saturation_days = 0
    total_etc = 0
    total_eto = 0
    total_rainfall = 0
    total_irrigation = 0
    total_dp = 0
    total_runoff = 0
    
    for day in range(1, days + 1):
        w = weather[day - 1]
        
        # محاسبه ETc
        eto = w.get("eto", 5.0)
        kc = calculate_kc(crop_key, day)
        etc = eto * kc
        
        # ضریب تنش آب (Ks) - FAO-56
        if sw_current > raw:
            ks = 1.0
        else:
            ks = max(0, (sw_current - 0.5 * raw) / (0.5 * raw)) if raw > 0 else 0
        
        etc_actual = etc * ks
        
        # بارش و آبیاری
        rain = w.get("rainfall", 0)
        irr = 0  # بدون آبیاری خودکار
        
        # رواناب
        runoff = max(0, rain - soil["k_sat"] * 0.5) if rain > soil["k_sat"] else 0
        effective_rain = rain - runoff
        
        # بیلان آبی
        sw_current = sw_current + effective_rain + irr - etc_actual
        
        # نشت عمیق
        dp = 0
        if sw_current > taw:
            dp = sw_current - taw
            sw_current = taw
        
        if sw_current < 0:
            sw_current = 0
            stress_days += 1
        
        # محاسبه وضعیت
        theta_current = theta_wp + (sw_current / root_depth)
        
        if theta_current >= theta_fc:
            status = "اشباع"
            saturation_days += 1
        elif theta_current >= (theta_fc + theta_wp) / 2:
            status = "مطلوب"
            optimal_days += 1
        elif theta_current >= theta_wp:
            status = "تنش خفیف"
        else:
            status = "تنش شدید"
            stress_days += 1
        
        # مرحله رشد
        stage = get_growth_stage(crop_key, day)
        
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
            "stage": stage,
        })
        
        total_etc += etc_actual
        total_eto += eto
        total_rainfall += rain
        total_dp += dp
        total_runoff += runoff
    
    # ============================================================
    # تحلیل پیشرفته
    # ============================================================
    
    # شاخص تنش آبی محصول (CWSI)
    cwsi = stress_days / days if days > 0 else 0
    
    # کارایی استفاده از آب (WUE) - فرض عملکرد 5 t/ha
    yield_t_ha = 5.0 * (1 - cwsi * crop["ky"])
    wue = yield_t_ha / (total_etc / 1000) if total_etc > 0 else 0  # kg/m³
    
    # نسبت بارش به ETc
    rain_efficiency = (total_rainfall / total_etc * 100) if total_etc > 0 else 0
    
    # میانگین و انحراف معیار رطوبت
    moisture_values = [d["soil_water_percent"] for d in daily_results]
    avg_moisture = sum(moisture_values) / len(moisture_values)
    moisture_std = (sum((x - avg_moisture)**2 for x in moisture_values) / len(moisture_values))**0.5
    
    # روزهای بحرانی
    critical_days = [d["day"] for d in daily_results if d["status"] in ["تنش شدید", "اشباع"]]
    
    # تحلیل روند
    first_half = sum(moisture_values[:len(moisture_values)//2]) / (len(moisture_values)//2)
    second_half = sum(moisture_values[len(moisture_values)//2:]) / (len(moisture_values) - len(moisture_values)//2)
    trend = "کاهشی" if second_half < first_half - 5 else "افزایشی" if second_half > first_half + 5 else "پایدار"
    
    # ============================================================
    # توصیه‌های هوشمند
    # ============================================================
    recommendations = _generate_recommendations(
        soil=soil,
        soil_type=params["soil_type"],
        crop=crop,
        crop_key=crop_key,
        stress_days=stress_days,
        saturation_days=saturation_days,
        optimal_days=optimal_days,
        days=days,
        cwsi=cwsi,
        total_etc=total_etc,
        total_rainfall=total_rainfall,
        avg_moisture=avg_moisture,
        moisture_std=moisture_std,
        k_sat=soil["k_sat"],
        trend=trend,
    )
    
    return {
        "soil_info": {
            "type": params["soil_type"],
            "name_fa": soil["name_fa"],
            "name_en": soil["name_en"],
            "field_capacity": round(theta_fc * 100, 1),
            "wilting_point": round(theta_wp * 100, 1),
            "saturation": round(theta_s * 100, 1),
            "available_water": round((theta_fc - theta_wp) * 100, 1),
            "k_sat_cm_per_day": soil["k_sat"],
            "color": soil["color"],
        },
        "crop_info": {
            "key": crop_key,
            "name_fa": crop["name_fa"],
            "ky_factor": crop["ky"],
            "root_depth_cm": crop["root_depth_cm"],
        },
        "capacity": {
            "taw_mm": round(taw, 2),
            "raw_mm": round(raw, 2),
            "root_depth_cm": root_depth,
        },
        "summary": {
            "total_eto_mm": round(total_eto, 2),
            "total_etc_mm": round(total_etc, 2),
            "total_rainfall_mm": round(total_rainfall, 2),
            "total_deep_percolation_mm": round(total_dp, 2),
            "total_runoff_mm": round(total_runoff, 2),
            "stress_days": stress_days,
            "optimal_days": optimal_days,
            "saturation_days": saturation_days,
            "stress_percent": round((stress_days / days) * 100, 1),
            "optimal_percent": round((optimal_days / days) * 100, 1),
        },
        "advanced_analysis": {
            "cwsi": round(cwsi, 3),
            "cwsi_interpretation": _interpret_cwsi(cwsi),
            "wue_kg_per_m3": round(wue, 2),
            "estimated_yield_t_ha": round(yield_t_ha, 2),
            "rain_efficiency_percent": round(rain_efficiency, 1),
            "avg_moisture_percent": round(avg_moisture, 1),
            "moisture_std": round(moisture_std, 1),
            "moisture_trend": trend,
            "critical_days": critical_days[:10],  # 10 روز اول بحرانی
        },
        "recommendations": recommendations,
        "daily": daily_results,
    }


def _interpret_cwsi(cwsi: float) -> str:
    """تفسیر شاخص CWSI"""
    if cwsi < 0.1:
        return "بدون تنش - عالی"
    elif cwsi < 0.2:
        return "تنش خفیف - قابل قبول"
    elif cwsi < 0.35:
        return "تنش متوسط - نیاز به بهبود"
    elif cwsi < 0.5:
        return "تنش شدید - کاهش عملکرد"
    else:
        return "تنش بحرانی - خسارت جدی"


def _generate_recommendations(soil, soil_type, crop, crop_key, 
                              stress_days, saturation_days, optimal_days,
                              days, cwsi, total_etc, total_rainfall,
                              avg_moisture, moisture_std, k_sat, trend) -> List[Dict]:
    """تولید توصیه‌های هوشمند"""
    recommendations = []
    
    # 1. توصیه بر اساس هدایت هیدرولیکی
    if k_sat > 5:
        recommendations.append({
            "category": "آبیاری",
            "priority": "high",
            "icon": "💧",
            "title": "خاک با زهکشی بسیار سریع",
            "description": f"هدایت هیدرولیکی {k_sat} cm/day نشان‌دهنده زهکشی سریع است.",
            "advice": soil["irrigation_advice"]["frequency"] + " با حجم " + soil["irrigation_advice"]["depth"],
            "risk": soil["irrigation_advice"]["risk"],
            "color": "#f59e0b"
        })
    elif k_sat > 2:
        recommendations.append({
            "category": "آبیاری",
            "priority": "medium",
            "icon": "💧",
            "title": "خاک با زهکشی متوسط",
            "description": f"هدایت هیدرولیکی {k_sat} cm/day - شرایط متعادل.",
            "advice": soil["irrigation_advice"]["frequency"] + " با حجم " + soil["irrigation_advice"]["depth"],
            "risk": soil["irrigation_advice"]["risk"],
            "color": "#84cc16"
        })
    elif k_sat > 0.5:
        recommendations.append({
            "category": "آبیاری",
            "priority": "medium",
            "icon": "💧",
            "title": "خاک با زهکشی کند",
            "description": f"هدایت هیدرولیکی {k_sat} cm/day - احتیاط در آبیاری.",
            "advice": soil["irrigation_advice"]["frequency"] + " با حجم " + soil["irrigation_advice"]["depth"],
            "risk": soil["irrigation_advice"]["risk"],
            "color": "#3b82f6"
        })
    else:
        recommendations.append({
            "category": "آبیاری",
            "priority": "high",
            "icon": "⚠️",
            "title": "خاک با زهکشی بسیار کند",
            "description": f"هدایت هیدرولیکی {k_sat} cm/day - خطر بالای آب‌گرفتگی!",
            "advice": soil["irrigation_advice"]["frequency"] + " با حجم " + soil["irrigation_advice"]["depth"],
            "risk": soil["irrigation_advice"]["risk"],
            "color": "#ef4444"
        })
    
    # 2. توصیه بر اساس تنش آبی
    if stress_days > 0:
        severity = "بحرانی" if stress_days > days * 0.3 else "جدی" if stress_days > days * 0.15 else "خفیف"
        recommendations.append({
            "category": "تنش آبی",
            "priority": "high" if stress_days > days * 0.15 else "medium",
            "icon": "🌵",
            "title": f"تنش آبی {severity}",
            "description": f"در {stress_days} روز از {days} روز ({round(stress_days/days*100)}٪)، گیاه دچار تنش آبی شده است.",
            "advice": f"افزایش فرکانس آبیاری یا استفاده از مالچ برای حفظ رطوبت. کاهش تبخیر با پوشش گیاهی.",
            "risk": f"کاهش عملکرد تا {round(cwsi * crop['ky'] * 100)}٪ با ضریب حساسیت Ky={crop['ky']}",
            "color": "#ef4444"
        })
    else:
        recommendations.append({
            "category": "تنش آبی",
            "priority": "low",
            "icon": "✅",
            "title": "بدون تنش آبی",
            "description": "رطوبت خاک در تمام دوره در محدوده مطلوب بوده است.",
            "advice": "ادامه پایش منظم و حفظ برنامه آبیاری فعلی.",
            "risk": "بدون ریسک",
            "color": "#10b981"
        })
    
    # 3. توصیه بر اساس اشباع
    if saturation_days > 0:
        recommendations.append({
            "category": "زهکشی",
            "priority": "high",
            "icon": "🌊",
            "title": "خطر آب‌گرفتگی",
            "description": f"در {saturation_days} روز، خاک در حالت اشباع بوده است.",
            "advice": "ایجاد زهکش مناسب، کاهش حجم آبیاری، یا انتخاب محصول مقاوم‌تر به غرقابی.",
            "risk": "کمبود اکسیژن ریشه، بیماری‌های قارچی، کاهش جذب مواد مغذی",
            "color": "#3b82f6"
        })
    
    # 4. توصیه بر اساس کارایی بارش
    rain_eff = (total_rainfall / total_etc * 100) if total_etc > 0 else 0
    if rain_eff < 50:
        recommendations.append({
            "category": "بارش",
            "priority": "medium",
            "icon": "🌧️",
            "title": "کمبود بارش مؤثر",
            "description": f"بارش فقط {round(rain_eff)}٪ از نیاز آبی محصول را تأمین کرده است.",
            "advice": "استفاده از سیستم‌های جمع‌آوری آب باران، افزایش آبیاری تکمیلی، یا انتخاب محصول کم‌آب‌بر.",
            "risk": "وابستگی بالا به آبیاری تکمیلی",
            "color": "#f59e0b"
        })
    elif rain_eff > 100:
        recommendations.append({
            "category": "بارش",
            "priority": "low",
            "icon": "☔",
            "title": "بارش کافی",
            "description": f"بارش {round(rain_eff)}٪ از نیاز آبی را تأمین کرده است.",
            "advice": "مدیریت رواناب و استفاده از آب اضافی برای شستشوی نمک.",
            "risk": "خطر شستشوی مواد مغذی",
            "color": "#10b981"
        })
    
    # 5. توصیه بر اساس نوسان رطوبت
    if moisture_std > 20:
        recommendations.append({
            "category": "پایداری",
            "priority": "medium",
            "icon": "📊",
            "title": "نوسان زیاد رطوبت",
            "description": f"انحراف معیار رطوبت {round(moisture_std, 1)}٪ - نوسانات شدید.",
            "advice": "آبیاری‌های منظم‌تر با حجم کمتر، استفاده از سنسور رطوبت برای زمان‌بندی دقیق.",
            "risk": "استرس گیاه ناشی از تغییرات ناگهانی رطوبت",
            "color": "#a855f7"
        })
    
    # 6. توصیه بر اساس روند
    if trend == "کاهشی":
        recommendations.append({
            "category": "روند",
            "priority": "high",
            "icon": "📉",
            "title": "روند کاهشی رطوبت",
            "description": "رطوبت خاک در نیمه دوم دوره کاهش یافته است.",
            "advice": "افزایش تدریجی حجم آبیاری یا کاهش فاصله بین آبیاری‌ها.",
            "risk": "تنش آبی در اواخر فصل رشد",
            "color": "#ef4444"
        })
    
    # 7. توصیه محصول-محور
    recommendations.append({
        "category": "محصول",
        "priority": "info",
        "icon": "🌾",
        "title": f"ویژگی‌های {crop['name_fa']}",
        "description": f"ضریب حساسیت به کم‌آبی (Ky): {crop['ky']} - عمق ریشه: {crop['root_depth_cm']} cm",
        "advice": f"مراحل حساس به تنش: میانی (بیشترین نیاز آبی). Kc حداکثر: {crop['kc_mid']}",
        "risk": f"کاهش {crop['ky']*10}٪ عملکرد به ازای هر ۱۰٪ تنش آبی",
        "color": "#84cc16"
    })
    
    return recommendations


def _generate_sample_weather(days: int) -> List[Dict]:
    """تولید داده‌های هواشناسی نمونه با الگوی واقع‌گرایانه"""
    import random
    weather = []
    for i in range(days):
        season_factor = 1 + 0.3 * math.sin(2 * math.pi * i / 365)
        eto = 4.0 + 2.0 * season_factor + random.uniform(-0.5, 0.5)
        
        rainfall = 0
        if random.random() < 0.2:
            rainfall = random.uniform(2, 15)
        
        weather.append({
            "eto": round(max(0, eto), 2),
            "rainfall": round(rainfall, 2),
        })
    return weather
'''
    
    write_file(API_DIR / "services" / "soil_water_core.py", content)


# ============================================================
# فایل 2: Router بهبودیافته
# ============================================================
def enhance_router():
    print("\n🔌 بهبود Router...")
    
    content = '''# api/modules/soil_water/router.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict

from api.services.soil_water_core import (
    simulate_water_balance, SOIL_DATABASE, CROPS_DATABASE,
    calculate_kc, get_growth_stage
)

router = APIRouter(prefix="/soil-water", tags=["Soil Water"])


class WaterBalanceRequest(BaseModel):
    soil_type: str = Field("loam")
    crop: str = Field("wheat")
    root_depth_cm: float = Field(50, ge=10, le=300)
    initial_moisture_percent: float = Field(20, ge=0, le=50)
    days: int = Field(30, ge=7, le=365)


@router.get("/soils")
async def list_soils():
    """لیست تمام خاک‌ها با توصیه‌های آبیاری"""
    return {
        key: {
            "name_fa": v["name_fa"],
            "name_en": v["name_en"],
            "field_capacity": v["field_capacity"],
            "wilting_point": v["wilting_point"],
            "k_sat": v["k_sat"],
            "color": v["color"],
            "irrigation_advice": v.get("irrigation_advice", {}),
        }
        for key, v in SOIL_DATABASE.items()
    }


@router.get("/crops")
async def list_crops():
    """لیست تمام محصولات"""
    return {
        key: {
            "name_fa": v["name_fa"],
            "kc_init": v["kc_init"],
            "kc_mid": v["kc_mid"],
            "kc_end": v["kc_end"],
            "ky": v["ky"],
            "root_depth_cm": v["root_depth_cm"],
            "total_days": sum(v["stages_days"]),
        }
        for key, v in CROPS_DATABASE.items()
    }


@router.post("/water-balance")
async def calculate_water_balance(request: WaterBalanceRequest):
    """شبیه‌سازی پیشرفته بیلان آبی با تحلیل هوشمند"""
    if request.soil_type not in SOIL_DATABASE:
        raise HTTPException(400, f"نوع خاک نامعتبر: {request.soil_type}")
    
    params = {
        "soil_type": request.soil_type,
        "crop": request.crop,
        "root_depth_cm": request.root_depth_cm,
        "initial_moisture_percent": request.initial_moisture_percent,
        "days": request.days,
    }
    
    return simulate_water_balance(params)


@router.get("/crops/{crop_key}/kc/{day}")
async def get_kc_at_day(crop_key: str, day: int):
    """ضریب Kc در روز مشخص"""
    if crop_key not in CROPS_DATABASE:
        raise HTTPException(404, "محصول یافت نشد")
    
    kc = calculate_kc(crop_key, day)
    stage = get_growth_stage(crop_key, day)
    crop = CROPS_DATABASE[crop_key]
    
    return {
        "crop": crop_key,
        "crop_name_fa": crop["name_fa"],
        "day": day,
        "kc": round(kc, 3),
        "stage": stage,
        "ky": crop["ky"],
    }
'''
    
    write_file(API_DIR / "modules" / "soil_water" / "router.py", content)


# ============================================================
# فایل 3: داشبورد پیشرفته فرانت‌اند
# ============================================================
def enhance_dashboard():
    print("\n📊 ایجاد داشبورد پیشرفته...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  ArrowRight, Droplets, Calculator, AlertTriangle, CheckCircle,
  TrendingUp, Sprout, Info, Loader2, Database, FlaskConical,
  BarChart3, LineChart as LineChartIcon, Activity, Zap, Target,
  Gauge, Leaf, CloudRain, Sun, Thermometer, Award
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
const ReferenceArea = dynamic(() => import("recharts").then(m => m.ReferenceArea), { ssr: false });

const API_BASE = "http://localhost:8000/api/v1/soil-water";

export default function SoilWaterPage() {
  const [isCalculating, setIsCalculating] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [soils, setSoils] = useState<any>({});
  const [crops, setCrops] = useState<any>({});
  const [error, setError] = useState("");

  const [formData, setFormData] = useState({
    soil_type: "loam",
    crop: "wheat",
    root_depth_cm: 50,
    initial_moisture_percent: 22,
    days: 30,
  });

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

  const handleCalculate = async () => {
    setIsCalculating(true);
    setError("");
    setResult(null);

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

      setResult(await res.json());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setIsCalculating(false);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high": return "border-red-500/50 bg-red-500/5";
      case "medium": return "border-amber-500/50 bg-amber-500/5";
      case "low": return "border-emerald-500/50 bg-emerald-500/5";
      default: return "border-sky-500/50 bg-sky-500/5";
    }
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
                  تحلیل هوشمند رطوبت خاک با توصیه‌های تخصصی بر اساس ویژگی‌های فیزیکی خاک و نیاز محصول
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mt-4">
              {["FAO-56", "van Genuchten", "USDA Rosetta", "CWSI", "WUE"].map(s => (
                <span key={s} className="px-3 py-1 bg-sky-500/10 border border-sky-500/30 rounded-full text-xs text-sky-300">
                  {s}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          
          {/* Input Form */}
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 h-fit sticky top-4">
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
                {soils[formData.soil_type] && (
                  <div className="mt-2 p-2 bg-slate-800/50 rounded text-xs text-slate-400">
                    <div className="flex justify-between">
                      <span>FC:</span>
                      <span className="text-sky-400">{(soils[formData.soil_type].field_capacity * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>WP:</span>
                      <span className="text-amber-400">{(soils[formData.soil_type].wilting_point * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Ks:</span>
                      <span className="text-emerald-400">{soils[formData.soil_type].k_sat} cm/day</span>
                    </div>
                  </div>
                )}
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
                      {crop.name_fa} (Kc={crop.kc_mid}, Ky={crop.ky})
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
                onClick={handleCalculate}
                disabled={isCalculating}
                className="w-full py-3 bg-gradient-to-l from-sky-500 to-blue-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-sky-500/30 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {isCalculating ? (
                  <><Loader2 className="h-5 w-5 animate-spin" /> در حال محاسبه...</>
                ) : (
                  <><Zap className="h-5 w-5" /> شروع تحلیل هوشمند</>
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
            {!result ? (
              <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-12 text-center h-full flex flex-col items-center justify-center">
                <FlaskConical className="h-16 w-16 text-slate-600 mb-4" />
                <h3 className="text-xl font-bold text-white mb-2">پارامترها را وارد کنید</h3>
                <p className="text-slate-400">پس از محاسبه، تحلیل کامل با توصیه‌های تخصصی نمایش داده می‌شود</p>
              </div>
            ) : (
              <>
                {/* Summary Cards - 8 کارت */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Leaf className="h-4 w-4" style={{ color: result.soil_info.color }} />
                      <p className="text-xs text-slate-400">نوع خاک</p>
                    </div>
                    <p className="text-lg font-black text-white">{result.soil_info.name_fa}</p>
                    <p className="text-xs text-slate-500">AWC: {result.soil_info.available_water}%</p>
                  </div>
                  
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Droplets className="h-4 w-4 text-sky-400" />
                      <p className="text-xs text-slate-400">TAW</p>
                    </div>
                    <p className="text-2xl font-black text-sky-400">{result.capacity.taw_mm}</p>
                    <p className="text-xs text-slate-500">mm (آب قابل دسترس)</p>
                  </div>
                  
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Sun className="h-4 w-4 text-amber-400" />
                      <p className="text-xs text-slate-400">ETc کل</p>
                    </div>
                    <p className="text-2xl font-black text-amber-400">{result.summary.total_etc_mm}</p>
                    <p className="text-xs text-slate-500">mm تبخیر و تعرق</p>
                  </div>
                  
                  <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Target className="h-4 w-4" style={{ color: result.summary.stress_days > 0 ? "#ef4444" : "#10b981" }} />
                      <p className="text-xs text-slate-400">روزهای تنش</p>
                    </div>
                    <p className={`text-2xl font-black ${result.summary.stress_days > 0 ? "text-red-400" : "text-emerald-400"}`}>
                      {result.summary.stress_days}
                    </p>
                    <p className="text-xs text-slate-500">از {formData.days} روز</p>
                  </div>
                </div>

                {/* Advanced Analysis Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-500/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Gauge className="h-4 w-4 text-purple-400" />
                      <p className="text-xs text-purple-300">CWSI</p>
                    </div>
                    <p className="text-xl font-black text-purple-300">{result.advanced_analysis.cwsi}</p>
                    <p className="text-xs text-purple-400/70 truncate">{result.advanced_analysis.cwsi_interpretation}</p>
                  </div>
                  
                  <div className="bg-gradient-to-br from-emerald-900/30 to-emerald-800/20 border border-emerald-500/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <Award className="h-4 w-4 text-emerald-400" />
                      <p className="text-xs text-emerald-300">WUE</p>
                    </div>
                    <p className="text-xl font-black text-emerald-300">{result.advanced_analysis.wue_kg_per_m3}</p>
                    <p className="text-xs text-emerald-400/70">kg/m³ کارایی آب</p>
                  </div>
                  
                  <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-500/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <CloudRain className="h-4 w-4 text-blue-400" />
                      <p className="text-xs text-blue-300">کارایی بارش</p>
                    </div>
                    <p className="text-xl font-black text-blue-300">{result.advanced_analysis.rain_efficiency_percent}%</p>
                    <p className="text-xs text-blue-400/70">نسبت بارش به ETc</p>
                  </div>
                  
                  <div className="bg-gradient-to-br from-amber-900/30 to-amber-800/20 border border-amber-500/30 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <TrendingUp className="h-4 w-4 text-amber-400" />
                      <p className="text-xs text-amber-300">روند</p>
                    </div>
                    <p className="text-xl font-black text-amber-300">{result.advanced_analysis.moisture_trend}</p>
                    <p className="text-xs text-amber-400/70">σ = {result.advanced_analysis.moisture_std}%</p>
                  </div>
                </div>

                {/* Main Chart - Soil Water Dynamics */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Activity className="h-5 w-5 text-sky-400" />
                    دینامیک رطوبت خاک در طول زمان
                  </h3>
                  <div className="h-80">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={result.daily}>
                        <defs>
                          <linearGradient id="swGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.6}/>
                            <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="day" stroke="#64748b" fontSize={11} label={{ value: "روز", position: "insideBottom", offset: -5, fill: "#64748b" }} />
                        <YAxis stroke="#64748b" fontSize={11} label={{ value: "درصد", angle: -90, position: "insideLeft", fill: "#64748b" }} />
                        <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                        <Legend />
                        
                        {/* ناحیه مطلوب */}
                        <ReferenceArea y1={50} y2={100} fill="#10b981" fillOpacity={0.05} label={{ value: "محدوده مطلوب", position: "insideTopRight", fill: "#10b981" }} />
                        
                        {/* خطوط FC و WP */}
                        <ReferenceLine y={100} stroke="#10b981" strokeDasharray="5 5" label={{ value: "FC", fill: "#10b981", position: "right" }} />
                        <ReferenceLine y={0} stroke="#ef4444" strokeDasharray="5 5" label={{ value: "WP", fill: "#ef4444", position: "right" }} />
                        
                        <Area type="monotone" dataKey="soil_water_percent" stroke="#0ea5e9" strokeWidth={2} fill="url(#swGrad)" name="رطوبت خاک (%)" />
                        <Line type="monotone" dataKey="ks" stroke="#f59e0b" strokeWidth={2} dot={false} name="ضریب تنش Ks" />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-4 grid grid-cols-3 gap-2 text-xs">
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-3 rounded bg-emerald-500/20 border border-emerald-500" />
                      <span className="text-slate-400">محدوده مطلوب (بین FC و WP)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-0.5 bg-emerald-500" />
                      <span className="text-slate-400">ظرفیت زراعی (FC)</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-3 h-0.5 bg-red-500" />
                      <span className="text-slate-400">نقطه پژمردگی (WP)</span>
                    </div>
                  </div>
                </div>

                {/* Kc & ETc Chart */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Sprout className="h-5 w-5 text-emerald-400" />
                    ضریب محصول (Kc) و تبخیر و تعرق
                  </h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={result.daily}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                        <YAxis yAxisId="left" stroke="#10b981" fontSize={11} label={{ value: "Kc", angle: -90, position: "insideLeft", fill: "#10b981" }} />
                        <YAxis yAxisId="right" orientation="right" stroke="#f59e0b" fontSize={11} label={{ value: "mm", angle: 90, position: "insideRight", fill: "#f59e0b" }} />
                        <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                        <Legend />
                        <Line yAxisId="left" type="monotone" dataKey="kc" stroke="#10b981" strokeWidth={3} dot={false} name="ضریب محصول Kc" />
                        <Bar yAxisId="right" dataKey="eto_mm" fill="#f59e0b" opacity={0.4} name="ETo (mm)" />
                        <Line yAxisId="right" type="monotone" dataKey="etc_mm" stroke="#ef4444" strokeWidth={2} dot={false} name="ETc (mm)" />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="mt-3 p-3 bg-slate-800/50 rounded-lg text-xs text-slate-400">
                    <strong className="text-slate-200">تفسیر:</strong> منحنی سبز (Kc) مراحل رشد محصول را نشان می‌دهد. 
                    اوج Kc در مرحله میانی ({result.crop_info.name_fa}: Kc={crops[formData.crop]?.kc_mid}) است.
                  </div>
                </div>

                {/* Water Balance Chart */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <BarChart3 className="h-5 w-5 text-blue-400" />
                    بیلان آبی روزانه
                  </h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={result.daily}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis dataKey="day" stroke="#64748b" fontSize={11} />
                        <YAxis stroke="#64748b" fontSize={11} />
                        <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                        <Legend />
                        <Bar dataKey="rainfall_mm" fill="#3b82f6" name="بارش" />
                        <Bar dataKey="etc_actual_mm" fill="#ef4444" name="ETc واقعی" />
                        <Line type="monotone" dataKey="deep_percolation_mm" stroke="#8b5cf6" strokeWidth={2} dot={false} name="نشت عمیق" />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Smart Recommendations */}
                <div className="bg-gradient-to-br from-sky-900/30 to-blue-900/30 border border-sky-500/30 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Sprout className="h-5 w-5 text-sky-400" />
                    توصیه‌های هوشمند مدیریتی
                  </h3>
                  <div className="space-y-3">
                    {result.recommendations.map((rec: any, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.1 }}
                        className={`p-4 rounded-xl border-2 ${getPriorityColor(rec.priority)}`}
                      >
                        <div className="flex items-start gap-3">
                          <div className="text-3xl">{rec.icon}</div>
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-bold text-white">{rec.title}</h4>
                              <span className={`text-xs px-2 py-0.5 rounded-full ${
                                rec.priority === "high" ? "bg-red-500/20 text-red-300" :
                                rec.priority === "medium" ? "bg-amber-500/20 text-amber-300" :
                                "bg-emerald-500/20 text-emerald-300"
                              }`}>
                                {rec.priority === "high" ? "اولویت بالا" : rec.priority === "medium" ? "متوسط" : "اطلاعات"}
                              </span>
                              <span className="text-xs text-slate-500">[{rec.category}]</span>
                            </div>
                            <p className="text-sm text-slate-300 mb-2">{rec.description}</p>
                            <div className="bg-slate-900/50 rounded-lg p-2 mb-2">
                              <p className="text-xs text-sky-300">
                                <strong>💡 توصیه:</strong> {rec.advice}
                              </p>
                            </div>
                            <p className="text-xs text-slate-400">
                              <strong>⚠️ ریسک:</strong> {rec.risk}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>

                {/* Soil Hydraulic Analysis */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Database className="h-5 w-5 text-purple-400" />
                    تحلیل هدایت هیدرولیکی
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-slate-800/50 rounded-xl">
                      <p className="text-xs text-slate-400 mb-1">هدایت اشباع (Ks)</p>
                      <p className="text-2xl font-black text-white">{result.soil_info.k_sat_cm_per_day}</p>
                      <p className="text-xs text-slate-500">cm/day</p>
                      <div className="mt-2 h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full rounded-full"
                          style={{
                            width: `${Math.min(100, result.soil_info.k_sat_cm_per_day * 10)}%`,
                            background: result.soil_info.k_sat_cm_per_day > 5 ? "#f59e0b" :
                                       result.soil_info.k_sat_cm_per_day > 1 ? "#10b981" : "#3b82f6"
                          }}
                        />
                      </div>
                    </div>
                    <div className="p-4 bg-slate-800/50 rounded-xl">
                      <p className="text-xs text-slate-400 mb-1">کلاس زهکشی</p>
                      <p className="text-lg font-bold text-white">
                        {result.soil_info.k_sat_cm_per_day > 5 ? "سریع" :
                         result.soil_info.k_sat_cm_per_day > 1 ? "متعادل" : "کند"}
                      </p>
                      <p className="text-xs text-slate-500 mt-2">
                        {result.soil_info.k_sat_cm_per_day > 5 ? "آبیاری مکرر با حجم کم" :
                         result.soil_info.k_sat_cm_per_day > 1 ? "آبیاری متعادل" : "آبیاری با فاصله زیاد"}
                      </p>
                    </div>
                    <div className="p-4 bg-slate-800/50 rounded-xl">
                      <p className="text-xs text-slate-400 mb-1">توصیه روش آبیاری</p>
                      <p className="text-sm font-bold text-white mb-1">
                        {result.soil_info.k_sat_cm_per_day > 5 ? "قطره‌ای" :
                         result.soil_info.k_sat_cm_per_day > 1 ? "بارانی یا قطره‌ای" : "جویی یا زیرسطحی"}
                      </p>
                      <p className="text-xs text-slate-500">
                        {soils[formData.soil_type]?.irrigation_advice?.frequency}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Summary Statistics */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Info className="h-5 w-5 text-sky-400" />
                    خلاصه آماری دوره
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-slate-400">روزهای مطلوب</p>
                      <p className="text-xl font-bold text-emerald-400">{result.summary.optimal_days}</p>
                      <p className="text-xs text-slate-500">{result.summary.optimal_percent}%</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-slate-400">روزهای تنش</p>
                      <p className="text-xl font-bold text-red-400">{result.summary.stress_days}</p>
                      <p className="text-xs text-slate-500">{result.summary.stress_percent}%</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-slate-400">روزهای اشباع</p>
                      <p className="text-xl font-bold text-blue-400">{result.summary.saturation_days}</p>
                      <p className="text-xs text-slate-500">{((result.summary.saturation_days / formData.days) * 100).toFixed(1)}%</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-slate-400">نشت عمیق</p>
                      <p className="text-xl font-bold text-purple-400">{result.summary.total_deep_percolation_mm}</p>
                      <p className="text-xs text-slate-500">mm</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-slate-400">ETo کل</p>
                      <p className="text-xl font-bold text-amber-400">{result.summary.total_eto_mm}</p>
                      <p className="text-xs text-slate-500">mm</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-slate-400">بارش کل</p>
                      <p className="text-xl font-bold text-blue-400">{result.summary.total_rainfall_mm}</p>
                      <p className="text-xs text-slate-500">mm</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-slate-400">رواناب</p>
                      <p className="text-xl font-bold text-slate-400">{result.summary.total_runoff_mm}</p>
                      <p className="text-xs text-slate-500">mm</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="text-xs text-slate-400">عملکرد تخمینی</p>
                      <p className="text-xl font-bold text-emerald-400">{result.advanced_analysis.estimated_yield_t_ha}</p>
                      <p className="text-xs text-slate-500">t/ha</p>
                    </div>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "soil-water" / "page.tsx", content)


# ============================================================
# Main
# ============================================================
def main():
    print("💧 تکمیل ماژول آب خاک با تحلیل هوشمند")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    enhance_backend()
    enhance_router()
    enhance_dashboard()
    
    print("\n" + "=" * 70)
    print("✅ تکمیل شد!")
    print("\n🎯 بهبودهای اعمال شده:")
    print("   📊 ۸ کارت آماری (به جای ۴)")
    print("   📈 نمودار با خطوط FC/WP و ناحیه مطلوب")
    print("   🌾 نمودار Kc با مراحل رشد")
    print("   💧 نمودار بیلان آبی روزانه")
    print("   🧠 توصیه‌های هوشمند بر اساس:")
    print("      • هدایت هیدرولیکی خاک")
    print("      • تعداد روزهای تنش")
    print("      • کارایی بارش")
    print("      • نوسان رطوبت")
    print("      • روند رطوبت")
    print("      • ویژگی‌های محصول")
    print("   🎯 شاخص‌های پیشرفته:")
    print("      • CWSI (Crop Water Stress Index)")
    print("      • WUE (Water Use Efficiency)")
    print("      • عملکرد تخمینی")
    print("      • کارایی بارش")
    print("   💧 تحلیل هدایت هیدرولیکی:")
    print("      • کلاس زهکشی")
    print("      • توصیه روش آبیاری")
    print("      • فرکانس آبیاری")
    print("")
    print("🚀 گام بعدی:")
    print("   1. ری‌استارت سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   2. پاک‌سازی کش فرانت‌اند:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   3. اجرا:")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   4. مشاهده: http://localhost:3001/soil-water")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())