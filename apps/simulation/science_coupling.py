"""
Coupled science run for Eco Nojin DSS.

Optional free engines (AquaCrop-OSPy / pyRothC) via engine=ospy|pyrothc|free.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from apps.simulation.aquacrop_ospy_engine import run_aquacrop_with_optional_ospy
from apps.simulation.fao_crop_params import get_crop_params
from apps.simulation.rothc_pyrothc_engine import run_rothc_with_optional_pyrothc


def _rothc_light(params: dict[str, Any]) -> dict[str, Any]:
    try:
        return run_rothc_with_optional_pyrothc(
            {
                "years": int(params.get("rothc_years", 10)),
                "soc_t_ha": float(params.get("soc_t_ha", 40.0)),
                "c_input_t_ha_y": float(params.get("c_input_t_ha_y", 1.5)),
                "clay_pct": float(params.get("clay_pct", 25.0)),
                "engine": params.get("engine", "conceptual"),
            }
        )
    except Exception as e:
        return {"error": str(e)[:160], "model": "rothc_unavailable"}


def run_coupled_science(params: dict[str, Any] | None = None) -> dict[str, Any]:
    p = dict(params or {})
    crop = str(p.get("crop", "wheat"))
    crop_meta = get_crop_params(crop)

    aq = run_aquacrop_with_optional_ospy(p)
    rc = _rothc_light(p)

    yield_t_ha = float(aq.get("yield_t_ha") or 0)
    irr_mm = float(aq.get("irrigation_need_mm") or 0)
    etc_mm = float(aq.get("etc_mm") or 1)
    area_ha = float(aq.get("area_ha") or 1)

    water_m3 = max(irr_mm + float(aq.get("rain_total_mm") or 0), 1.0) * 10.0 * area_ha
    wue_kg_m3 = (yield_t_ha * 1000.0 * area_ha) / water_m3

    soc_final = None
    if isinstance(rc, dict) and not rc.get("error"):
        soc_final = rc.get("soc_final") or rc.get("soc_final_t_ha") or rc.get("total_soc_t_ha") or rc.get("soc_t_ha")

    risks: list[dict[str, str]] = []
    if float(aq.get("yield_relative") or 1) < 0.75:
        risks.append(
            {
                "level": "warning",
                "code": "yield_stress",
                "msg_en": "Relative yield < 75% — check irrigation threshold / TAW",
                "msg_fa": "عملکرد نسبی زیر ۷۵٪ — آستانه آبیاری و TAW را بررسی کنید",
            }
        )
    if irr_mm > 600:
        risks.append(
            {
                "level": "info",
                "code": "high_irrigation",
                "msg_en": "High simulated seasonal irrigation — consider deficit strategies",
                "msg_fa": "نیاز آبیاری فصلی بالا — استراتژی کم‌آبیاری را بررسی کنید",
            }
        )

    advice_en = [
        f"Crop {crop_meta.get('label_en')}: use Kc≈{crop_meta.get('kc_mid')}, Ky≈{crop_meta.get('ky')} (FAO56/33 library).",
        "Tune TAW to soil texture; optional NDVI canopy calibration improves stress timing.",
        "Couple RothC C-input with residue management for MRV soil-carbon narratives.",
    ]
    advice_fa = [
        f"محصول {crop_meta.get('label_fa')}: Kc≈{crop_meta.get('kc_mid')}، Ky≈{crop_meta.get('ky')} از کتابخانه FAO56/33.",
        "TAW را با بافت خاک تنظیم کنید؛ NDVI برای کالیبره تاج پوشش مفید است.",
        "ورودی کربن RothC را با مدیریت بقایا برای MRV هماهنگ کنید.",
    ]

    return {
        "pipeline": "coupled_science_v1",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "references": [
            "FAO56 crop coefficients",
            "FAO33 yield response Ky",
            "RothC soil organic carbon",
            "AquaCrop-style daily water balance (conceptual / optional OSPy)",
        ],
        "global_alignment": {
            "aquacrop_family": aq.get("engine") or "conceptual_fao_not_binary",
            "rothc": rc.get("engine") or "embedded",
            "patterns": [
                "AquaCrop-OSPy / FAO DSS water-yield",
                "OpenET-style ETc & irrigation need",
                "Farmdee-Mesook style advisory metrics",
            ],
        },
        "aquacrop": aq,
        "rothc": rc,
        "kpis": {
            "yield_t_ha": round(yield_t_ha, 3),
            "yield_relative": aq.get("yield_relative"),
            "etc_mm": round(etc_mm, 1),
            "irrigation_need_mm": round(irr_mm, 1),
            "wue_kg_m3": round(wue_kg_m3, 3),
            "soc_t_ha": soc_final,
            "area_ha": area_ha,
            "crop": crop,
        },
        "risks": risks,
        "advice_en": advice_en,
        "advice_fa": advice_fa,
        "crop_meta": {
            "label_en": crop_meta.get("label_en"),
            "label_fa": crop_meta.get("label_fa"),
            "references": crop_meta.get("references"),
        },
    }
