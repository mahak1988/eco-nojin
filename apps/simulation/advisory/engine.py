"""
EcoNojin Advisory Engine — Scientifically grounded, rule-based recommendations.
Generates analysis, recommendations, and actionable scenarios based on simulation metrics.
"""
from typing import Any, Dict, List

def generate_advisory(simulator_id: str, metrics: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main entry point for generating advisory content.
    """
    analysis = ""
    recommendations = []
    scenarios = []
    references = []

    if simulator_id == "aquacrop":
        yield_val = metrics.get("yield_t_ha", 0)
        wue = metrics.get("water_use_efficiency_kg_m3", 0)
        
        analysis = f"عملکرد شبیه‌سازی‌شده {yield_val:.2f} تن در هکتار است. "
        if yield_val < 3.0:
            analysis += "این مقدار نشان‌دهندهٔ تنش شدید (آبی یا غذایی) در طول دوره رشد است."
            recommendations.append({
                "level": "warning",
                "icon": "droplet",
                "text": "تنش آبی شناسایی شد. توصیه می‌شود آبیاری تکمیلی در مراحل حساس (گلدهی و پر شدن دانه) اعمال شود.",
                "source": "FAO AquaCrop Paper 66, §Water Stress"
            })
        else:
            analysis += "عملکرد در محدودهٔ مطلوب قرار دارد."
            recommendations.append({
                "level": "success",
                "icon": "check-circle",
                "text": "مدیریت آبیاری فعلی کارآمد است. برای بهینه‌سازی بیشتر، می‌توانید سناریوی کاهش ۱۰٪ آب را بررسی کنید.",
                "source": "FAO Water Productivity Guidelines"
            })

        if wue > 0 and wue < 1.0:
            recommendations.append({
                "level": "warning",
                "icon": "trending-down",
                "text": "بهره‌وری آب (WUE) پایین است. بررسی نشت سیستم آبیاری یا استفاده از روش‌های قطره‌ای توصیه می‌شود.",
                "source": "FAO Irrigation and Drainage Paper"
            })

        scenarios = [
            {
                "id": "deficit_irrigation",
                "name": "آبیاری تکمیلی بهینه",
                "desc": "اعمال ۵۰ میلی‌متر آبیاری اضافی در مرحله گلدهی",
                "params": {"total_irrigation": parameters.get("total_irrigation", 250) + 50}
            },
            {
                "id": "drip_efficiency",
                "name": "ارتقاء به آبیاری قطره‌ای",
                "desc": "کاهش تلفات تبخیر و افزایش بهره‌وری آب",
                "params": {"total_irrigation": parameters.get("total_irrigation", 250) * 0.8} # 20% savings
            }
        ]
        references = ["Steduto P. et al. (2009). AquaCrop — The FAO Crop Model to Simulate Yield Response to Water. FAO Irrigation & Drainage Paper 66."]

    elif simulator_id == "cba":
        npv = metrics.get("npv_m_usd", 0)
        irr = metrics.get("irr_pct", 0)
        
        analysis = f"ارزش خالص فعلی (NPV) پروژه برابر با {npv:.2f} و نرخ بازده داخلی (IRR) برابر {irr:.1f}٪ است. "
        if npv > 0 and irr > 8.0:
            analysis += "پروژه از نظر اقتصادی کاملاً توجیه‌پذیر و سودآور است."
            recommendations.append({
                "level": "success",
                "icon": "trending-up",
                "text": "شاخص‌های مالی مثبت هستند. اجرای پروژه با شرایط فعلی توصیه می‌شود.",
                "source": "Principles of Corporate Finance (Brealey, Myers, Allen)"
            })
        else:
            analysis += "پروژه در مرز توجیه‌پذیری قرار دارد یا زیان‌ده است."
            recommendations.append({
                "level": "warning",
                "icon": "alert-triangle",
                "text": "NPV منفی یا پایین است. پیشنهاد می‌شود هزینه‌های سرمایه‌گذاری اولیه را کاهش دهید یا به دنبال تسهیلات با نرخ بهره پایین‌تر باشید.",
                "source": "World Bank Project Appraisal Guidelines"
            })
            
        scenarios = [
            {
                "id": "cost_reduction",
                "name": "کاهش ۲۰٪ هزینه‌های اجرایی",
                "desc": "بررسی حساسیت پروژه به بهینه‌سازی هزینه‌ها",
                "params": {"annual_cost": parameters.get("annual_cost", 500) * 0.8}
            },
            {
                "id": "subsidy",
                "name": "اعمال یارانه دولتی",
                "desc": "کاهش نرخ تنزیل مؤثر به دلیل تسهیلات",
                "params": {"discount_rate": 3.0}
            }
        ]
        references = ["Boardman A.E. et al. (2017). Cost-Benefit Analysis: Concepts and Practice. Cambridge University Press."]

    elif simulator_id == "rusle2":
        soil_loss = metrics.get("soil_loss_t_ha", 0)
        analysis = f"میزان فرسایش خاک شبیه‌سازی‌شده {soil_loss:.2f} تن در هکتار در سال است. "
        if soil_loss > 10.0: # Tolerable soil loss is often around 10 t/ha/yr
            analysis += "این مقدار بیش از حد مجاز فرسایش (T-value) است و نیاز به مداخله فوری دارد."
            recommendations.append({
                "level": "warning",
                "icon": "alert-octagon",
                "text": "فرسایش خاک شدید است. اجرای عملیات حفاظتی مانند کشت نواری، تراس‌بندی یا افزایش پوشش گیاهی اکیداً توصیه می‌شود.",
                "source": "USDA Agriculture Handbook 703 (RUSLE2)"
            })
        else:
            analysis += "میزان فرسایش در محدودهٔ قابل قبول و پایدار قرار دارد."
            recommendations.append({
                "level": "success",
                "icon": "shield",
                "text": "مدیریت فعلی خاک مؤثر است. حفظ پوشش گیاهی و عدم شخم عمیق را ادامه دهید.",
                "source": "USDA NRCS Conservation Practice Standards"
            })
            
        scenarios = [
            {
                "id": "contour_farming",
                "name": "کشت روی خطوط تراز (Contour)",
                "desc": "کاهش عامل حفاظتی P",
                "params": {"P": parameters.get("P", 1.0) * 0.5}
            },
            {
                "id": "cover_crop",
                "name": "کاشت گیاه پوششی",
                "desc": "کاهش عامل پوشش C",
                "params": {"C": parameters.get("C", 0.5) * 0.6}
            }
        ]
        references = ["Renard K.G. et al. (1997). Predicting Soil Erosion by Water: A Guide to Conservation Planning with RUSLE. USDA."]

    else:
        # Fallback for other simulators (DSSAT, SWAT, etc.)
        analysis = "تحلیل تخصصی متنی برای این شبیه‌ساز در حال توسعه است. لطفاً به خروجی‌های عددی، نمودارها و بخش اعتبارسنجی توجه کنید."
        recommendations = [{
            "level": "info",
            "icon": "info",
            "text": "قوانین توصیهٔ مستند برای این ماژول به‌زودی بر اساس مقالات مرجع اضافه خواهد شد.",
            "source": "EcoNojin Development Roadmap"
        }]
        scenarios = []
        references = []

    return {
        "simulator_id": simulator_id,
        "analysis": analysis,
        "recommendations": recommendations,
        "scenarios": scenarios,
        "references": references
    }
