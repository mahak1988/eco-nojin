# api/services/soil_water_core.py
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
