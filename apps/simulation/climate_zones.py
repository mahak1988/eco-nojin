"""
Global climate–landscape packages for Eco Nojin (digital arm of Hydroma Nojin).

User-selectable climate archetypes — NO named pilot villages/cities.
Aligned with Köppen-style classes + dryland restoration practice.
"""

from __future__ import annotations

from typing import Any

CLIMATE_ZONES: list[dict[str, Any]] = [
    {
        "id": "arid_mountain",
        "label_en": "Arid / semi-arid mountain",
        "label_fa": "کوهستانی خشک و نیمه‌خشک",
        "koppen_hint": "BSk / BWh highlands",
        "traits": ["steep slopes", "shallow soils", "fragile rangeland", "rainfed + pastoral"],
        "priority_packages": [
            "swc_agmar",
            "rangeland_restore",
            "conservation_ag",
            "medicinal_diversify",
        ],
        "default_models": ["aquacrop", "rusle", "rothc"],
        "risk_triggers": ["SPI-3", "VHI", "soil_moisture"],
    },
    {
        "id": "semi_arid_saline_plain",
        "label_en": "Warm semi-arid saline plain",
        "label_fa": "دشت نیمه‌خشک شور",
        "koppen_hint": "BSh / BWh lowlands",
        "traits": ["high ET", "salinity", "groundwater pressure", "irrigated systems"],
        "priority_packages": [
            "salinity_manage",
            "efficient_irrigation",
            "drainage",
            "salt_tolerant_crops",
        ],
        "default_models": ["aquacrop", "weap", "rothc"],
        "risk_triggers": ["SPI-3", "SPEI", "ETDI"],
    },
    {
        "id": "humid_forest_hills",
        "label_en": "Humid / sub-humid forested hills",
        "label_fa": "جنگلی مرطوب و نیمه‌مرطوب",
        "koppen_hint": "Cfa / Cfb foothills",
        "traits": ["high rainfall", "landslide risk", "agroforestry potential"],
        "priority_packages": ["agroforestry", "slope_stabilize", "ntfp_value_chain"],
        "default_models": ["rusle", "hec_ras_proxy", "rothc"],
        "risk_triggers": ["extreme_rain", "VHI"],
    },
    {
        "id": "snowfed_highland",
        "label_en": "Snow-fed highland catchment",
        "label_fa": "کوهستان برف‌تأمین (بالادست)",
        "koppen_hint": "Dsa / Dsb / alpine",
        "traits": ["snowmelt timing", "short growing season", "upstream water security"],
        "priority_packages": ["snow_runoff_manage", "cold_crops", "pasture_protect"],
        "default_models": ["swat_proxy", "aquacrop", "weap"],
        "risk_triggers": ["SPEI", "snow_anomaly"],
    },
    {
        "id": "mediterranean_dry_summer",
        "label_en": "Mediterranean dry-summer",
        "label_fa": "مدیترانه‌ای با تابستان خشک",
        "koppen_hint": "Csa / Csb",
        "traits": ["winter rain", "summer drought", "orchards / olives"],
        "priority_packages": ["deficit_irrigation", "cover_crops", "soil_carbon"],
        "default_models": ["aquacrop", "rothc", "fao56"],
        "risk_triggers": ["SPI-6", "SPEI", "SSI"],
    },
    {
        "id": "tropical_savanna",
        "label_en": "Tropical savanna / seasonal wet-dry",
        "label_fa": "ساوانای استوایی (فصلی مرطوب–خشک)",
        "koppen_hint": "Aw / As",
        "traits": ["strong seasonality", "erosion in rains", "fire risk"],
        "priority_packages": ["contour_swc", "residue_manage", "diversified_livelihood"],
        "default_models": ["aquacrop", "rusle", "rothc"],
        "risk_triggers": ["SPI-3", "MSDI"],
    },
    {
        "id": "cold_steppe",
        "label_en": "Cold steppe / continental dry",
        "label_fa": "استپ سرد / قاره‌ای خشک",
        "koppen_hint": "BSk cold / Dwa",
        "traits": ["frost", "wind erosion", "short season"],
        "priority_packages": ["windbreaks", "conservation_tillage", "cold_tolerant_crops"],
        "default_models": ["rusle", "rothc", "aquacrop"],
        "risk_triggers": ["SPI-6", "PDSI"],
    },
    {
        "id": "coastal_arid",
        "label_en": "Coastal arid / fog-influenced desert",
        "label_fa": "خشک ساحلی",
        "koppen_hint": "BWh coastal",
        "traits": ["very high ET", "scarce rain", "desal / careful water"],
        "priority_packages": ["extreme_wue", "protected_ag", "soil_crust_manage"],
        "default_models": ["aquacrop", "fao56"],
        "risk_triggers": ["SPI-12", "SPEI"],
    },
]


def list_climate_zones() -> dict[str, Any]:
    return {
        "source": "Eco Nojin climate packages (global archetypes; user-selectable)",
        "note_en": "No site names — choose by climate type for decision support packages.",
        "note_fa": "بدون نام مکان پایلوت — کاربر اقلیم را انتخاب می‌کند و پکیج تصمیم‌یار پیشنهاد می‌شود.",
        "zones": CLIMATE_ZONES,
        "count": len(CLIMATE_ZONES),
    }


def get_climate_zone(zone_id: str) -> dict[str, Any] | None:
    for z in CLIMATE_ZONES:
        if z["id"] == zone_id:
            return z
    return None
