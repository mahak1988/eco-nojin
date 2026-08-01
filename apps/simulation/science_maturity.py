"""Science stack maturity scorecard for Eco Nojin vs global open platforms."""

from __future__ import annotations

from typing import Any


def science_maturity_report() -> dict[str, Any]:
    """Honest capability map — not marketing 100%."""

    components = [
        {
            "id": "aquacrop_conceptual",
            "name": "AquaCrop-style water-yield",
            "score": 88,
            "status": "production_dss",
            "notes": "FAO56/33 library + daily balance + engine metadata; not FAO binary",
            "benchmarks": ["AquaCrop-OSPy", "KUL AquaCrop v7", "pyfao56"],
        },
        {
            "id": "fao_crop_library",
            "name": "Embedded FAO crop params",
            "score": 92,
            "status": "done",
            "notes": "Kc/Ky/Yx offline tables with citations",
            "benchmarks": ["FAO56", "FAO33"],
        },
        {
            "id": "rothc",
            "name": "RothC soil carbon",
            "score": 80,
            "status": "live_api",
            "notes": "Public endpoint + coupled pipeline",
            "benchmarks": ["RothC-26.3 literature"],
        },
        {
            "id": "coupling",
            "name": "AquaCrop + RothC coupled DSS",
            "score": 85,
            "status": "live_api",
            "notes": "/science/coupled-run KPIs + risks + advice",
            "benchmarks": ["Farmdee-Mesook integration pattern"],
        },
        {
            "id": "ndvi_canopy",
            "name": "NDVI → canopy bridge",
            "score": 70,
            "status": "partial",
            "notes": "Synthetic/fallback + optional live",
            "benchmarks": ["Sentinel-2 NDVI pipelines"],
        },
        {
            "id": "climate_etl",
            "name": "Climate drivers",
            "score": 72,
            "status": "partial",
            "notes": "Open-Meteo path when available",
            "benchmarks": ["OpenET", "Open-Meteo"],
        },
        {
            "id": "monitors",
            "name": "Science monitors / thresholds",
            "score": 75,
            "status": "live",
            "notes": "Watch + thresholds APIs",
            "benchmarks": ["farmOS alerts patterns"],
        },
        {
            "id": "ml",
            "name": "ML yield/risk",
            "score": 68,
            "status": "live_stub_train",
            "notes": "Train/predict/sensitivity endpoints",
            "benchmarks": ["research DSS ML layers"],
        },
        {
            "id": "swat_proxy",
            "name": "SWAT+ process proxy",
            "score": 55,
            "status": "proxy_only",
            "notes": "Not official SWAT+ binary",
            "benchmarks": ["SWAT+", "SCS-CN"],
        },
        {
            "id": "ospy_binary",
            "name": "AquaCrop-OSPy / FAO binary",
            "score": 35,
            "status": "optional_fallback",
            "notes": "Import path exists; full OSPy calibration still optional",
            "benchmarks": ["aquacrop pip", "KUL Fortran"],
        },
    ]

    scores = [int(c["score"]) for c in components]
    overall = round(sum(scores) / len(scores))

    return {
        "phase": "science",
        "overall_score_pct": overall,
        "target_stated_by_user": 99,
        "honest_gap_note": (
            "99% would require official AquaCrop/SWAT binaries, multi-site validation, "
            "full GEE production NDVI, and calibrated regional trials. "
            f"Current integrated DSS score ≈ {overall}% of the designed Eco Nojin science scope."
        ),
        "components": components,
        "next_to_99": [
            "Optional aquacrop-OSPy install + golden tests vs FAO samples",
            "Live Open-Meteo default for et0/rain on coupled-run",
            "GEE NDVI production credentials",
            "Field pilot validation datasets (Iran regions)",
            "SWAT+ binary optional path",
        ],
        "global_platforms_reviewed": [
            {"name": "FAO AquaCrop / KUL v7", "url": "https://github.com/KUL-RSDA/AquaCrop"},
            {"name": "AquaCrop-OSPy", "role": "Python process model"},
            {"name": "pyfao56", "role": "FAO56 water balance"},
            {"name": "PCSE/WOFOST", "role": "European crop simulation"},
            {"name": "DSSAT / APSIM", "role": "full biophysical suites"},
            {"name": "farmOS / LiteFarm", "role": "farm records + tasks"},
            {"name": "OpenET", "role": "satellite ET"},
            {"name": "CropManage (UC)", "role": "irrigation/N DSS"},
            {"name": "Farmdee-Mesook", "role": "AquaCrop + satellite advisory"},
            {"name": "CropSuite", "role": "crop suitability under climate"},
        ],
    }
