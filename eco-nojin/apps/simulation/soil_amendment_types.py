"""
Soil typology + amendment recommendations.

Covers major problem soils: acidic, calcareous, saline, sodic, sandy,
clay-compacted, organic-poor, waterlogged, gypsiferous, polluted (generic).
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


def classify_soil(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = params or {}
    ph = float(p.get("ph", 7.0))
    ec = float(p.get("ec_ds_m", 1.0))
    esp = float(p.get("esp_pct", 5.0))
    sand = float(p.get("sand_pct", 40))
    clay = float(p.get("clay_pct", 25))
    om = float(p.get("om_pct", 1.5))
    bd = float(p.get("bulk_density_mg_m3", 1.4))
    gyp = float(p.get("gypsum_pct", 0.0))

    tags: list[str] = []
    if ph < 5.5:
        tags.append("acidic")
    elif ph > 8.2:
        tags.append("alkaline")
    elif 7.5 <= ph <= 8.2 and ec < 4:
        tags.append("calcareous_suspect")

    if ec >= 4:
        tags.append("saline")
    if esp >= 15:
        tags.append("sodic")
    if ec >= 4 and esp >= 15:
        tags.append("saline_sodic")

    if sand >= 70:
        tags.append("sandy")
    if clay >= 40:
        tags.append("clayey")
    if bd >= 1.6:
        tags.append("compacted")
    if om < 1.0:
        tags.append("organic_poor")
    if om >= 5:
        tags.append("organic_rich")
    if gyp >= 5:
        tags.append("gypsiferous")

    if not tags:
        tags.append("normal")

    return {
        "model": "soil_classify",
        "tags": tags,
        "inputs": {
            "ph": ph,
            "ec_ds_m": ec,
            "esp_pct": esp,
            "sand_pct": sand,
            "clay_pct": clay,
            "om_pct": om,
            "bulk_density": bd,
        },
        "completed_at": datetime.now(UTC).isoformat(),
    }


_AMENDMENTS: dict[str, dict[str, Any]] = {
    "acidic": {
        "primary": ["lime_caco3", "dolomitic_lime"],
        "secondary": ["organic_matter", "phosphate_rock_careful"],
        "avoid": ["ammonium_only_without_lime"],
        "notes_fa": "آهک بر اساس بافر pH؛ فسفر در pH خیلی پایین تثبیت می‌شود.",
    },
    "alkaline": {
        "primary": ["elemental_sulfur", "acidifying_n_fertilizer"],
        "secondary": ["organic_acids", "compost"],
        "avoid": ["more_lime"],
        "notes_fa": "گوگرد عنصری به‌تدریج pH را کاهش می‌دهد.",
    },
    "calcareous_suspect": {
        "primary": ["band_p_fertilizer", "organic_acids", "fe_chelate_if_chlorosis"],
        "secondary": ["compost", "mulch"],
        "avoid": ["broadcast_high_p_fixation_loss"],
        "notes_fa": "در خاک‌های آهکی فسفر و آهن محدود می‌شوند؛ جایگذاری نواری بهتر است.",
    },
    "saline": {
        "primary": ["leaching_with_good_water", "drainage"],
        "secondary": ["salt_tolerant_crops", "mulch"],
        "avoid": ["poor_quality_irrigation_water"],
        "notes_fa": "کسر آبشویی (LR) و زهکشی ضروری است.",
    },
    "sodic": {
        "primary": ["gypsum_caso4", "leaching_after_gypsum"],
        "secondary": ["organic_matter", "deep_ripping_if_safe"],
        "avoid": ["sodium_based_amendments"],
        "notes_fa": "گچ جایگزین سدیم تبادلی؛ سپس آبشویی.",
    },
    "saline_sodic": {
        "primary": ["gypsum_then_leach", "drainage"],
        "secondary": ["organic_matter"],
        "avoid": ["leach_only_without_ca_source"],
        "notes_fa": "ابتدا منبع کلسیم، بعد آبشویی نمک.",
    },
    "sandy": {
        "primary": ["compost", "biochar_moderate", "split_fertilizer"],
        "secondary": ["cover_crops", "mulch"],
        "avoid": ["single_large_n_dose"],
        "notes_fa": "ظرفیت نگهداری آب و مواد غذایی کم؛ ماده آلی و کود تقسیطی.",
    },
    "clayey": {
        "primary": ["organic_matter", "controlled_traffic", "gypsum_if_structure_poor"],
        "secondary": ["cover_crops_roots"],
        "avoid": ["tillage_when_wet"],
        "notes_fa": "بهبود ساختمان با OM؛ از شخم در رطوبت بالا پرهیز.",
    },
    "compacted": {
        "primary": ["mechanical_loosening", "cover_crops", "reduce_axle_load"],
        "secondary": ["organic_matter"],
        "avoid": ["heavy_traffic_wet"],
        "notes_fa": "شکستن لایه سخت + مدیریت تردد.",
    },
    "organic_poor": {
        "primary": ["compost", "manure", "cover_crops", "residue_retention"],
        "secondary": ["biochar", "reduced_tillage"],
        "avoid": ["residue_burning"],
        "notes_fa": "افزایش ورودی کربن و کاهش تلفات.",
    },
    "organic_rich": {
        "primary": ["drainage_if_wet", "balanced_npk"],
        "secondary": ["monitor_n_mineralization"],
        "avoid": ["excessive_n"],
        "notes_fa": "معدنی‌سازی N بالا ممکن است؛ پایش نیترات.",
    },
    "gypsiferous": {
        "primary": ["careful_irrigation", "organic_matter"],
        "secondary": ["avoid_deep_mixing_if_hardpan"],
        "avoid": ["over_irrigation_dissolution_collapse"],
        "notes_fa": "خطر نشست/فرونشست با انحلال گچ.",
    },
    "normal": {
        "primary": ["maintain_om", "balanced_fertilizer", "cover_crops"],
        "secondary": ["monitor_ph_ec"],
        "avoid": ["neglect_soil_tests"],
        "notes_fa": "حفظ وضعیت با آزمون خاک منظم.",
    },
}


def recommend_amendments(params: dict[str, Any] | None = None) -> dict[str, Any]:
    clf = classify_soil(params)
    plans = []
    for tag in clf["tags"]:
        rec = _AMENDMENTS.get(tag, _AMENDMENTS["normal"])
        plans.append({"soil_type": tag, **rec})

    # Quantitative hooks if possible
    quant: dict[str, Any] = {}
    p = params or {}
    ph = float(p.get("ph", 7))
    if ph < 5.5:
        cec = float(p.get("cec_cmol_kg", 15))
        quant["lime_t_ha_rough"] = round((6.5 - ph) * cec * 0.15, 2)
    esp = float(p.get("esp_pct", 0))
    if esp >= 15:
        cec = float(p.get("cec_cmol_kg", 20))
        depth = float(p.get("depth_cm", 30))
        bd = float(p.get("bulk_density_mg_m3", 1.4))
        quant["gypsum_t_ha_rough"] = round(
            (esp - 10) / 100.0 * cec * depth * bd * 0.086, 2
        )
    ec = float(p.get("ec_ds_m", 0))
    if ec >= 4:
        quant["leaching_fraction_hint"] = round(
            min(0.5, max(0.05, float(p.get("ec_water_ds_m", 1.0)) / max(0.1, 5 * ec - 1))),
            3,
        )

    return {
        "model": "soil_amendment_plan",
        "classification": clf,
        "plans": plans,
        "quantitative": quant,
        "completed_at": datetime.now(UTC).isoformat(),
    }


def list_soil_types() -> dict[str, Any]:
    return {
        "types": list(_AMENDMENTS.keys()),
        "count": len(_AMENDMENTS),
        "description_fa": "طبقه‌بندی و بسته اصلاح برای انواع خاک مشکل‌دار و عادی",
    }
