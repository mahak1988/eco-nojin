"""
Satellite & geospatial API catalog for Eco Nojin MRV / monitoring.
Public metadata only — keys stay in env; no secrets in repo.
"""

from __future__ import annotations

from typing import Any

SATELLITE_PLATFORMS: list[dict[str, Any]] = [
    {
        "id": "copernicus_sentinel",
        "name": "Copernicus (Sentinel)",
        "domains": ["land", "agriculture", "climate", "atmosphere"],
        "api": ["Sentinel Hub", "openEO", "OGC APIs", "CDSE"],
        "assets": ["Sentinel-1 SAR", "Sentinel-2 optical", "Sentinel-3", "Sentinel-5P"],
        "access": "free_registration",
        "priority_mrv": True,
        "notes_en": "Primary open stack for NDVI/VHI and change detection.",
    },
    {
        "id": "landsat_usgs",
        "name": "Landsat (USGS/NASA)",
        "domains": ["land", "agriculture", "water", "environment"],
        "api": ["USGS Earth Explorer API"],
        "assets": ["Landsat 8/9 OLI/TIRS"],
        "access": "public_domain",
        "priority_mrv": True,
        "notes_en": "Long archive for baseline and trend analysis.",
    },
    {
        "id": "nasa_power",
        "name": "NASA POWER",
        "domains": ["meteorology", "agrometeorology", "solar"],
        "api": ["NASA POWER API"],
        "assets": ["300+ climate/solar parameters"],
        "access": "free_api",
        "priority_mrv": True,
        "notes_en": "ET0 drivers and climate series for AquaCrop/FAO-56.",
    },
    {
        "id": "jaxa_earth",
        "name": "JAXA Earth API",
        "domains": ["precipitation", "topography", "land"],
        "api": ["JAXA Earth API"],
        "assets": ["GSMaP rainfall", "ALOS DEM"],
        "access": "no_key_required",
        "priority_mrv": True,
        "notes_en": "Rainfall + DEM for runoff and SWC design support.",
    },
    {
        "id": "google_earth_engine",
        "name": "Google Earth Engine",
        "domains": ["analysis", "all_earth_obs"],
        "api": ["JavaScript API", "Python API"],
        "assets": ["multi-catalog including Sentinel/Landsat"],
        "access": "registered_cloud",
        "priority_mrv": True,
        "notes_en": "Cloud processing layer; optional when credentials present.",
    },
    {
        "id": "cropwatch",
        "name": "CropWatch (agriculture monitoring)",
        "domains": ["crop", "food_security"],
        "api": ["configurable APIs"],
        "assets": ["agri-climate indicators"],
        "access": "institutional",
        "priority_mrv": False,
        "notes_en": "FAO-aligned agri monitoring indicators where available.",
    },
    {
        "id": "openweathermap",
        "name": "OpenWeatherMap",
        "domains": ["weather", "forecast"],
        "api": ["Weather API"],
        "assets": ["current + forecast"],
        "access": "api_key",
        "priority_mrv": False,
        "notes_en": "Operational weather for farm dashboards.",
    },
    {
        "id": "open_meteo",
        "name": "Open-Meteo",
        "domains": ["weather", "climate", "agriculture"],
        "api": ["Open-Meteo API"],
        "assets": ["ERA5-based reanalysis + forecast"],
        "access": "free_no_key",
        "priority_mrv": True,
        "notes_en": "Default live climate driver when online (Eco Nojin climate_etl).",
    },
]


def list_satellite_platforms() -> dict[str, Any]:
    return {
        "source": "Eco Nojin satellite & EO API catalog",
        "mrv_stack_recommended": [
            "copernicus_sentinel",
            "landsat_usgs",
            "nasa_power",
            "jaxa_earth",
            "open_meteo",
            "google_earth_engine",
        ],
        "platforms": SATELLITE_PLATFORMS,
        "count": len(SATELLITE_PLATFORMS),
    }
