"""
FAO / WMO / IPCC-aligned indicators catalog for Eco Nojin science & monitors.
Metadata + simple SPI-like helpers where pure math is enough; full climate
series still come from climate_etl / external APIs.
"""

from __future__ import annotations

import math
from typing import Any

FAO_WATER_MODELS: list[dict[str, Any]] = [
    {
        "id": "fao_aez",
        "name_en": "FAO Agro-ecological Zone (AEZ)",
        "name_fa": "مدل اگرواکولوژیکی فائو",
        "domain": "land_evaluation",
        "use": "Suitability by soil, climate, terrain",
    },
    {
        "id": "fao56_pm",
        "name_en": "FAO-56 Penman–Monteith ET0",
        "name_fa": "پنمن–مونتیس فائو (FAO-56)",
        "domain": "irrigation_et",
        "use": "Reference crop evapotranspiration standard",
    },
    {
        "id": "etdi",
        "name_en": "Evapotranspiration Deficit Index (ETDI)",
        "name_fa": "شاخص کمبود تبخیر-تعرق",
        "domain": "agricultural_drought",
        "use": "Crop water stress in drylands",
    },
    {
        "id": "water_productivity",
        "name_en": "Water productivity (CPD/BPD/NBPD)",
        "name_fa": "شاخص‌های بهره‌وری آب",
        "domain": "water_management",
        "use": "Yield/income per unit water",
    },
    {
        "id": "epr",
        "name_en": "ET to Precipitation Ratio (EPR)",
        "name_fa": "نسبت تبخیر-تعرق به بارندگی",
        "domain": "water_sustainability",
        "use": "Climate water balance pressure",
    },
]

DROUGHT_INDICES: list[dict[str, Any]] = [
    {
        "id": "spi",
        "name_en": "Standardized Precipitation Index (SPI)",
        "name_fa": "شاخص بارش استاندارد (SPI)",
        "domain": "meteorological",
        "scales": ["1", "3", "6", "12"],
        "authority": "WMO / FAO practice",
    },
    {
        "id": "spei",
        "name_en": "SPEI",
        "name_fa": "شاخص بارش–تبخیر استاندارد (SPEI)",
        "domain": "meteorological",
        "scales": ["3", "6", "12"],
        "authority": "WMO literature",
    },
    {
        "id": "ssi",
        "name_en": "Standardized Soil Moisture Index (SSI)",
        "name_fa": "شاخص رطوبت خاک استاندارد",
        "domain": "agricultural",
        "authority": "research / ops DSS",
    },
    {
        "id": "msdi",
        "name_en": "Multivariate Standardized Drought Index",
        "name_fa": "شاخص خشکسالی چندمتغیره",
        "domain": "multivariate",
        "authority": "research",
    },
    {
        "id": "pdsi",
        "name_en": "Palmer Drought Severity Index",
        "name_fa": "شاخص شدت خشکسالی پالمر",
        "domain": "meteorological_soil",
        "authority": "classic",
    },
    {
        "id": "vhi",
        "name_en": "Vegetation Health Index (VHI)",
        "name_fa": "شاخص سلامت پوشش گیاهی",
        "domain": "remote_sensing",
        "authority": "NOAA / EO practice",
        "trigger_note": "Hydroma risk plan uses VHI with SPI-3",
    },
]

PROCESS_MODELS: list[dict[str, Any]] = [
    {"id": "aquacrop", "name": "AquaCrop-style (FAO concepts)", "role": "yield_water"},
    {"id": "rothc", "name": "RothC", "role": "soil_carbon"},
    {"id": "rusle", "name": "RUSLE", "role": "erosion"},
    {"id": "swat_proxy", "name": "SWAT+ process proxy", "role": "basin_water"},
    {"id": "weap_style", "name": "WEAP-style allocation (conceptual)", "role": "water_allocation"},
    {"id": "hec_ras_proxy", "name": "HEC-RAS-style routing proxy", "role": "flood_channel"},
]


def catalog() -> dict[str, Any]:
    return {
        "fao_water_models": FAO_WATER_MODELS,
        "drought_indices": DROUGHT_INDICES,
        "process_models": PROCESS_MODELS,
        "note_en": "Catalog for UI + monitors; SPI helper is simplified for demo series.",
        "note_fa": "کاتالوگ برای UI و پایشگر؛ SPI کمکی برای سری‌های دمو ساده‌سازی شده است.",
    }


def spi_simple(precip_series: list[float], scale: int = 3) -> list[float | None]:
    """Very simple rolling z-score SPI-like index (not full gamma SPI)."""
    if not precip_series or scale < 1:
        return []
    out: list[float | None] = [None] * (scale - 1)
    for i in range(scale - 1, len(precip_series)):
        window = precip_series[i - scale + 1 : i + 1]
        mu = sum(window) / scale
        var = sum((x - mu) ** 2 for x in window) / max(scale - 1, 1)
        sd = math.sqrt(var) if var > 1e-12 else 1.0
        out.append(round((window[-1] - mu) / sd, 3))
    return out
