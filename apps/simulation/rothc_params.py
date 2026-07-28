"""
RothC-26.3 precise parameter catalog, presets, and validation.

Units: t C ha⁻¹ for pools; rates year⁻¹ at standard conditions.
Ref: Coleman & Jenkinson (RothC-26.3); Falloon et al. IOM estimate.
"""

from __future__ import annotations

from typing import Any, Optional

# ── Rate constants at standard conditions (1/year) ───────────────────────────
K_DPM = 10.0
K_RPM = 0.3
K_BIO = 0.66
K_HUM = 0.02

# Partition of BIO+HUM from decomposed C that stays in soil
BIO_FRAC_OF_BH = 0.46
HUM_FRAC_OF_BH = 0.54

# Input quality ratios (DPM:RPM)
DPM_RPM_CROPS = 1.44
DPM_RPM_FYM = 1.0
DPM_RPM_GRASS = 0.67
DPM_RPM_WOOD = 0.25

PARAM_CATALOG: list[dict[str, Any]] = [
    {
        "name": "years",
        "type": "int",
        "unit": "year",
        "default": 15,
        "min": 1,
        "max": 100,
        "group": "simulation",
        "label_fa": "افق شبیه‌سازی",
        "label_en": "Simulation horizon",
        "help_fa": "تعداد سال‌های گام سالانه. برای تعادل استخرها معمولاً ۱۵–۵۰ سال.",
        "help_en": "Annual steps; 15–50 y typical for pool equilibration.",
    },
    {
        "name": "soc_t_ha",
        "type": "float",
        "unit": "t C/ha",
        "default": 40.0,
        "min": 5.0,
        "max": 200.0,
        "group": "initial_pools",
        "label_fa": "SOC کل اولیه",
        "label_en": "Initial total SOC",
        "help_fa": "مجموع کربن آلی لایه مدل (معمولاً ۰–۲۰ یا ۰–۳۰ سانتی‌متر).",
        "help_en": "Total organic C in modelled layer (often 0–20/30 cm).",
    },
    {
        "name": "iom_t_ha",
        "type": "float",
        "unit": "t C/ha",
        "default": None,
        "min": 0.0,
        "max": 50.0,
        "group": "initial_pools",
        "label_fa": "IOM (خنثی)",
        "label_en": "Inert organic matter",
        "help_fa": "اگر خالی باشد از رابطه Falloon یا ۱۰٪ SOC استفاده می‌شود.",
        "help_en": "If omitted: Falloon estimate or ~10% of SOC.",
    },
    {
        "name": "dpm_t_ha",
        "type": "float",
        "unit": "t C/ha",
        "default": None,
        "min": 0.0,
        "max": 50.0,
        "group": "initial_pools",
        "label_fa": "DPM اولیه",
        "label_en": "Initial DPM",
        "help_fa": "مواد گیاهی تجزیه‌پذیر. پیش‌فرض ≈۱٪ بخش فعال.",
        "help_en": "Decomposable plant material; default ~1% of active C.",
    },
    {
        "name": "rpm_t_ha",
        "type": "float",
        "unit": "t C/ha",
        "default": None,
        "min": 0.0,
        "max": 80.0,
        "group": "initial_pools",
        "label_fa": "RPM اولیه",
        "label_en": "Initial RPM",
        "help_fa": "مواد مقاوم گیاهی. پیش‌فرض ≈۱۲٪ بخش فعال.",
        "help_en": "Resistant plant material; default ~12% of active C.",
    },
    {
        "name": "bio_t_ha",
        "type": "float",
        "unit": "t C/ha",
        "default": None,
        "min": 0.0,
        "max": 20.0,
        "group": "initial_pools",
        "label_fa": "BIO اولیه",
        "label_en": "Initial microbial biomass C",
        "help_fa": "پیش‌فرض ≈۲٪ بخش فعال.",
        "help_en": "Default ~2% of active C.",
    },
    {
        "name": "hum_t_ha",
        "type": "float",
        "unit": "t C/ha",
        "default": None,
        "min": 0.0,
        "max": 150.0,
        "group": "initial_pools",
        "label_fa": "HUM اولیه",
        "label_en": "Initial humified OM",
        "help_fa": "باقی‌مانده بخش فعال پس از DPM+RPM+BIO.",
        "help_en": "Remainder of active pool after DPM+RPM+BIO.",
    },
    {
        "name": "c_input_t_ha_y",
        "type": "float",
        "unit": "t C/ha/y",
        "default": 1.5,
        "min": 0.0,
        "max": 15.0,
        "group": "management",
        "label_fa": "ورودی کربن سالانه",
        "label_en": "Annual C input",
        "help_fa": "مجموع بقایا + کود آلی (کربن). غلات دیم اغلب ۰.۸–۲؛ با کود حیوانی بالاتر.",
        "help_en": "Residues + manure C. Rainfed cereals often 0.8–2; higher with FYM.",
    },
    {
        "name": "dpm_rpm_ratio",
        "type": "float",
        "unit": "-",
        "default": DPM_RPM_CROPS,
        "min": 0.1,
        "max": 5.0,
        "group": "management",
        "label_fa": "نسبت DPM/RPM ورودی",
        "label_en": "Input DPM:RPM ratio",
        "help_fa": "محصولات ۱.۴۴؛ FYM ۱.۰؛ مرتع ~۰.۶۷؛ چوب ~۰.۲۵.",
        "help_en": "Crops 1.44; FYM 1.0; grass ~0.67; woody ~0.25.",
    },
    {
        "name": "plant_cover",
        "type": "bool",
        "unit": "-",
        "default": True,
        "group": "management",
        "label_fa": "پوشش گیاهی",
        "label_en": "Plant cover",
        "help_fa": "True → c=0.6 (کندتر)؛ False (آیش برهنه) → c=1.0.",
        "help_en": "True → c=0.6; bare fallow → c=1.0.",
    },
    {
        "name": "clay_pct",
        "type": "float",
        "unit": "%",
        "default": 25.0,
        "min": 0.0,
        "max": 80.0,
        "group": "soil",
        "label_fa": "رس",
        "label_en": "Clay content",
        "help_fa": "روی نسبت CO₂ به BIO+HUM و ظرفیت کمبود رطوبت اثر دارد.",
        "help_en": "Affects CO₂ vs BIO+HUM split and moisture deficit capacity.",
    },
    {
        "name": "temp_c",
        "type": "float",
        "unit": "°C",
        "default": 15.0,
        "min": -10.0,
        "max": 40.0,
        "group": "climate",
        "label_fa": "دمای میانگین سالانه",
        "label_en": "Mean annual temperature",
        "help_fa": "عامل a(T)؛ زیر −۵°C تجزیه عملاً متوقف است.",
        "help_en": "Rate modifier a(T); near zero below −5°C.",
    },
    {
        "name": "rain_mm_year",
        "type": "float",
        "unit": "mm/y",
        "default": 650.0,
        "min": 0.0,
        "max": 3000.0,
        "group": "climate",
        "label_fa": "بارش سالانه",
        "label_en": "Annual rainfall",
        "help_fa": "همراه ET برای عامل رطوبت b ماهانهٔ تقریبی.",
        "help_en": "With ET for simplified moisture factor b.",
    },
    {
        "name": "et_mm_year",
        "type": "float",
        "unit": "mm/y",
        "default": 700.0,
        "min": 0.0,
        "max": 3000.0,
        "group": "climate",
        "label_fa": "تبخیر-تعرق سالانه",
        "label_en": "Annual open-pan / PET proxy",
        "help_fa": "در مناطق خشک ایران اغلب ET ≫ بارش → b نزدیک ۰.۲.",
        "help_en": "In arid zones ET ≫ rain → b near 0.2.",
    },
    {
        "name": "use_falloon_iom",
        "type": "bool",
        "unit": "-",
        "default": True,
        "group": "initial_pools",
        "label_fa": "IOM از Falloon",
        "label_en": "Falloon IOM estimate",
        "help_fa": "IOM = 0.049 × SOC^1.139 وقتی iom_t_ha داده نشود.",
        "help_en": "IOM = 0.049 × SOC^1.139 if iom not set.",
    },
    {
        "name": "k_dpm",
        "type": "float",
        "unit": "1/y",
        "default": K_DPM,
        "min": 1.0,
        "max": 20.0,
        "group": "advanced",
        "label_fa": "k DPM",
        "label_en": "DPM rate constant",
        "help_fa": "استاندارد RothC = ۱۰.",
        "help_en": "RothC standard = 10.",
    },
    {
        "name": "k_rpm",
        "type": "float",
        "unit": "1/y",
        "default": K_RPM,
        "min": 0.05,
        "max": 2.0,
        "group": "advanced",
        "label_fa": "k RPM",
        "label_en": "RPM rate constant",
        "help_fa": "استاندارد = ۰.۳.",
        "help_en": "Standard = 0.3.",
    },
    {
        "name": "k_bio",
        "type": "float",
        "unit": "1/y",
        "default": K_BIO,
        "min": 0.1,
        "max": 2.0,
        "group": "advanced",
        "label_fa": "k BIO",
        "label_en": "BIO rate constant",
        "help_fa": "استاندارد = ۰.۶۶.",
        "help_en": "Standard = 0.66.",
    },
    {
        "name": "k_hum",
        "type": "float",
        "unit": "1/y",
        "default": K_HUM,
        "min": 0.005,
        "max": 0.1,
        "group": "advanced",
        "label_fa": "k HUM",
        "label_en": "HUM rate constant",
        "help_fa": "استاندارد = ۰.۰۲.",
        "help_en": "Standard = 0.02.",
    },
]

PRESETS: dict[str, dict[str, Any]] = {
    "default_arable": {
        "label_fa": "زراعت معتدل (پیش‌فرض)",
        "label_en": "Temperate arable default",
        "params": {
            "years": 20,
            "soc_t_ha": 40.0,
            "c_input_t_ha_y": 1.5,
            "dpm_rpm_ratio": DPM_RPM_CROPS,
            "plant_cover": True,
            "clay_pct": 25.0,
            "temp_c": 15.0,
            "rain_mm_year": 650.0,
            "et_mm_year": 700.0,
            "use_falloon_iom": True,
        },
    },
    "iran_arid_rainfed": {
        "label_fa": "دیم خشک (ایران مرکزی)",
        "label_en": "Arid rainfed (central Iran)",
        "params": {
            "years": 25,
            "soc_t_ha": 18.0,
            "c_input_t_ha_y": 0.9,
            "dpm_rpm_ratio": DPM_RPM_CROPS,
            "plant_cover": True,
            "clay_pct": 28.0,
            "temp_c": 17.5,
            "rain_mm_year": 280.0,
            "et_mm_year": 1400.0,
            "use_falloon_iom": True,
        },
    },
    "iran_irrigated": {
        "label_fa": "آبیاری + بقایا بیشتر",
        "label_en": "Irrigated + higher residues",
        "params": {
            "years": 20,
            "soc_t_ha": 28.0,
            "c_input_t_ha_y": 2.2,
            "dpm_rpm_ratio": DPM_RPM_CROPS,
            "plant_cover": True,
            "clay_pct": 30.0,
            "temp_c": 16.0,
            "rain_mm_year": 400.0,
            "et_mm_year": 1200.0,
            "use_falloon_iom": True,
        },
    },
    "fym_enriched": {
        "label_fa": "کود حیوانی (FYM)",
        "label_en": "Farmyard manure enriched",
        "params": {
            "years": 20,
            "soc_t_ha": 45.0,
            "c_input_t_ha_y": 3.5,
            "dpm_rpm_ratio": DPM_RPM_FYM,
            "plant_cover": True,
            "clay_pct": 25.0,
            "temp_c": 12.0,
            "rain_mm_year": 700.0,
            "et_mm_year": 650.0,
            "use_falloon_iom": True,
        },
    },
    "bare_fallow": {
        "label_fa": "آیش برهنه",
        "label_en": "Bare fallow",
        "params": {
            "years": 15,
            "soc_t_ha": 35.0,
            "c_input_t_ha_y": 0.2,
            "dpm_rpm_ratio": DPM_RPM_CROPS,
            "plant_cover": False,
            "clay_pct": 25.0,
            "temp_c": 15.0,
            "rain_mm_year": 600.0,
            "et_mm_year": 750.0,
            "use_falloon_iom": True,
        },
    },
}


def falloon_iom(soc_t_ha: float) -> float:
    """Falloon et al. IOM estimate (t C/ha)."""
    soc = max(0.1, float(soc_t_ha))
    return 0.049 * (soc**1.139)


def resolve_params(raw: dict[str, Any] | None = None) -> dict[str, Any]:
    """Merge defaults, clamp ranges, partition pools, return resolved dict."""
    p = dict(raw or {})
    defaults = {c["name"]: c["default"] for c in PARAM_CATALOG if c["default"] is not None}
    for k, v in defaults.items():
        p.setdefault(k, v)

    # clamp numeric catalog bounds
    for c in PARAM_CATALOG:
        name = c["name"]
        if name not in p or p[name] is None:
            continue
        if c["type"] in ("float", "int") and "min" in c and "max" in c:
            try:
                val = float(p[name])
                val = max(float(c["min"]), min(float(c["max"]), val))
                p[name] = int(val) if c["type"] == "int" else val
            except (TypeError, ValueError):
                p[name] = c["default"]

    soc0 = float(p["soc_t_ha"])
    use_falloon = bool(p.get("use_falloon_iom", True))
    if p.get("iom_t_ha") is None:
        iom = falloon_iom(soc0) if use_falloon else min(5.0, soc0 * 0.1)
    else:
        iom = float(p["iom_t_ha"])
    iom = min(iom, soc0 * 0.95)
    active = max(0.0, soc0 - iom)

    dpm = float(p["dpm_t_ha"]) if p.get("dpm_t_ha") is not None else active * 0.01
    rpm = float(p["rpm_t_ha"]) if p.get("rpm_t_ha") is not None else active * 0.12
    bio = float(p["bio_t_ha"]) if p.get("bio_t_ha") is not None else active * 0.02
    # scale if overshoot
    sub = dpm + rpm + bio
    if sub > active and sub > 0:
        scale = active / sub
        dpm, rpm, bio = dpm * scale, rpm * scale, bio * scale
        sub = dpm + rpm + bio
    if p.get("hum_t_ha") is not None:
        hum = float(p["hum_t_ha"])
        # renormalize to active
        total_act = dpm + rpm + bio + hum
        if total_act > 0 and abs(total_act - active) > 1e-6:
            s = active / total_act
            dpm, rpm, bio, hum = dpm * s, rpm * s, bio * s, hum * s
    else:
        hum = max(0.0, active - dpm - rpm - bio)

    p["iom_t_ha"] = round(iom, 4)
    p["dpm_t_ha"] = round(dpm, 4)
    p["rpm_t_ha"] = round(rpm, 4)
    p["bio_t_ha"] = round(bio, 4)
    p["hum_t_ha"] = round(hum, 4)
    p["k_dpm"] = float(p.get("k_dpm", K_DPM))
    p["k_rpm"] = float(p.get("k_rpm", K_RPM))
    p["k_bio"] = float(p.get("k_bio", K_BIO))
    p["k_hum"] = float(p.get("k_hum", K_HUM))
    p["plant_cover"] = bool(p.get("plant_cover", True))
    p["years"] = int(p.get("years", 15))
    return p


def schema_payload() -> dict[str, Any]:
    return {
        "model": "rothc_26_3",
        "citation": "Coleman & Jenkinson RothC-26.3; Falloon IOM optional",
        "parameters": PARAM_CATALOG,
        "presets": {
            k: {"label_fa": v["label_fa"], "label_en": v["label_en"], "params": v["params"]}
            for k, v in PRESETS.items()
        },
        "constants": {
            "k_dpm": K_DPM,
            "k_rpm": K_RPM,
            "k_bio": K_BIO,
            "k_hum": K_HUM,
            "bio_frac_of_bh": BIO_FRAC_OF_BH,
            "hum_frac_of_bh": HUM_FRAC_OF_BH,
            "dpm_rpm_crops": DPM_RPM_CROPS,
            "dpm_rpm_fym": DPM_RPM_FYM,
            "dpm_rpm_grass": DPM_RPM_GRASS,
            "dpm_rpm_wood": DPM_RPM_WOOD,
        },
        "notes_fa": (
            "گام سالانه با عوامل a(T)، b(رطوبت)، c(پوشش). "
            "پیاده‌سازی باز است نه نرم‌افزار رسمی Rothamsted."
        ),
    }
