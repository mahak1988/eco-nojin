"""Localized names/descriptions for simulators (en source + fa + ar).

API returns English by default; pass lang=fa|ar|en (or Accept-Language) to localize.
"""

from __future__ import annotations

from typing import Any

# id -> {en, fa, ar} for name and description
SIM_I18N: dict[str, dict[str, dict[str, str]]] = {
    "climate": {
        "name": {
            "en": "Climate Model",
            "fa": "مدل اقلیمی",
            "ar": "نموذج المناخ",
        },
        "description": {
            "en": "Temperature, precipitation, extremes and NDVI from CO2 and climate sensitivity.",
            "fa": "دما، بارش، رویدادهای شدید و NDVI بر اساس CO₂ و حساسیت اقلیمی.",
            "ar": "الحرارة والهطول والأحداث المتطرفة وNDVI من CO2 والحساسية المناخية.",
        },
    },
    "urban": {
        "name": {"en": "Urban Climate", "fa": "اقلیم شهری", "ar": "مناخ حضري"},
        "description": {
            "en": "Urban heat island and city-scale climate indicators.",
            "fa": "جزیره گرمایی شهری و شاخص‌های اقلیمی در مقیاس شهر.",
            "ar": "جزيرة الحرارة الحضرية ومؤشرات المناخ على مستوى المدينة.",
        },
    },
    "aquacrop": {
        "name": {"en": "AquaCrop", "fa": "آکواکراپ", "ar": "أكواكروب"},
        "description": {
            "en": "FAO crop-water productivity model (process approximation).",
            "fa": "مدل بهره‌وری آب-محصول فائو (تقریب فرایندی).",
            "ar": "نموذج إنتاجية المياه-المحاصيل لمنظمة الفاو (تقريب عملي).",
        },
    },
    "rothc": {
        "name": {"en": "RothC", "fa": "راث‌سی (کربن خاک)", "ar": "روث سي (كربون التربة)"},
        "description": {
            "en": "Soil organic carbon turnover (RothC-26.3 style).",
            "fa": "چرخه کربن آلی خاک (سبک RothC-26.3).",
            "ar": "دورة كربون التربة العضوي (أسلوب RothC-26.3).",
        },
    },
    "swat": {
        "name": {"en": "SWAT+", "fa": "سوات+", "ar": "سوات+"},
        "description": {
            "en": "Basin hydrology and sediment proxy (not official SWAT binary).",
            "fa": "هیدرولوژی حوضه و رسوب (پروکسی؛ نه باینری رسمی SWAT).",
            "ar": "هيدرولوجيا الحوض والرواسب (تقريبي وليس ثنائي SWAT الرسمي).",
        },
    },
    "dssat": {
        "name": {"en": "DSSAT", "fa": "دی‌اس‌سات", "ar": "دي إس إس إيه تي"},
        "description": {
            "en": "Crop growth decision support (simplified).",
            "fa": "پشتیبانی تصمیم رشد محصول (ساده‌شده).",
            "ar": "دعم قرار نمو المحاصيل (مبسط).",
        },
    },
    "apsim": {
        "name": {"en": "APSIM", "fa": "اِی‌پی‌سیم", "ar": "أبيسيم"},
        "description": {
            "en": "Agricultural production systems simulation (simplified).",
            "fa": "شبیه‌سازی سامانه‌های تولید کشاورزی (ساده‌شده).",
            "ar": "محاكاة أنظمة الإنتاج الزراعي (مبسطة).",
        },
    },
    "wofost": {
        "name": {"en": "WOFOST", "fa": "ووفوست", "ar": "ووفوست"},
        "description": {
            "en": "World Food Studies crop model (simplified).",
            "fa": "مدل محصول مطالعات غذای جهان (ساده‌شده).",
            "ar": "نموذج محاصيل دراسات الغذاء العالمية (مبسط).",
        },
    },
}

CATEGORY_I18N: dict[str, dict[str, str]] = {
    "agriculture": {"en": "Agriculture", "fa": "کشاورزی", "ar": "زراعة"},
    "hydrology": {"en": "Hydrology", "fa": "هیدرولوژی", "ar": "هيدرولوجيا"},
    "carbon": {"en": "Carbon", "fa": "کربن", "ar": "كربون"},
    "climate": {"en": "Climate", "fa": "اقلیم", "ar": "مناخ"},
    "energy": {"en": "Energy", "fa": "انرژی", "ar": "طاقة"},
    "economics": {"en": "Economics", "fa": "اقتصاد", "ar": "اقتصاد"},
    "soil": {"en": "Soil", "fa": "خاک", "ar": "تربة"},
    "water_quality": {"en": "Water quality", "fa": "کیفیت آب", "ar": "جودة المياه"},
    "biodiversity": {"en": "Biodiversity", "fa": "تنوع زیستی", "ar": "تنوع بيولوجي"},
    "ecosystem_services": {
        "en": "Ecosystem services",
        "fa": "خدمات اکوسیستم",
        "ar": "خدمات النظام البيئي",
    },
    "urban": {"en": "Urban", "fa": "شهری", "ar": "حضري"},
    "other": {"en": "Other", "fa": "سایر", "ar": "أخرى"},
}


def normalize_lang(raw: str | None) -> str:
    if not raw:
        return "en"
    code = raw.strip().lower()[:2]
    if code in ("fa", "ar", "en"):
        return code
    return "en"


def localize_sim_meta(meta: dict[str, Any], lang: str) -> dict[str, Any]:
    """Return a copy of simulator metadata with localized name/description/category_label."""
    lang = normalize_lang(lang)
    out = dict(meta)
    sid = str(out.get("id") or "")
    pack = SIM_I18N.get(sid)
    if pack:
        if "name" in pack:
            out["name"] = pack["name"].get(lang) or pack["name"].get("en") or out.get("name")
        if "description" in pack:
            out["description"] = (
                pack["description"].get(lang)
                or pack["description"].get("en")
                or out.get("description")
            )
    cat = str(out.get("category") or "other")
    cat_pack = CATEGORY_I18N.get(cat) or CATEGORY_I18N["other"]
    out["category_label"] = cat_pack.get(lang) or cat_pack["en"]
    out["lang"] = lang
    return out


def localize_sim_list(items: list[dict[str, Any]], lang: str) -> list[dict[str, Any]]:
    return [localize_sim_meta(m, lang) for m in items]
