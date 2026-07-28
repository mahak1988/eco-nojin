"""
Model monitors (پایشگرها) — evaluate science outputs against operational thresholds.

Each monitor watches a process model and optional live sensor proxies.
Produces severity-tagged events + fa/en messages for UI and alert fan-out.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

# Catalog of built-in monitors
MONITOR_CATALOG: list[dict[str, Any]] = [
    {
        "id": "aquacrop_yield",
        "model": "aquacrop",
        "title_fa": "عملکرد نسبی AquaCrop",
        "title_en": "AquaCrop relative yield",
        "metric": "yield_relative",
        "operator": "lt",
        "warning": 0.75,
        "critical": 0.55,
        "unit": "0–1",
        "icon": "sprout",
    },
    {
        "id": "aquacrop_irrigation",
        "model": "aquacrop",
        "title_fa": "نیاز آبیاری فصلی",
        "title_en": "Seasonal irrigation need",
        "metric": "irrigation_need_mm",
        "operator": "gt",
        "warning": 250.0,
        "critical": 400.0,
        "unit": "mm",
        "icon": "droplets",
    },
    {
        "id": "aquacrop_stress",
        "model": "aquacrop",
        "title_fa": "تنش رطوبت (Ks میانگین)",
        "title_en": "Mean water stress Ks",
        "metric": "mean_ks",
        "operator": "lt",
        "warning": 0.7,
        "critical": 0.45,
        "unit": "0–1",
        "icon": "activity",
    },
    {
        "id": "scs_runoff",
        "model": "scs",
        "title_fa": "رواناب سطحی سالانه",
        "title_en": "Annual surface runoff",
        "metric": "runoff_mm_year",
        "operator": "gt",
        "warning": 80.0,
        "critical": 150.0,
        "unit": "mm/y",
        "icon": "waves",
    },
    {
        "id": "scs_sediment",
        "model": "scs",
        "title_fa": "رسوب پروکسی",
        "title_en": "Sediment proxy",
        "metric": "sediment_t_km2_year",
        "operator": "gt",
        "warning": 5.0,
        "critical": 15.0,
        "unit": "t/km²/y",
        "icon": "mountain",
    },
    {
        "id": "rothc_soc_loss",
        "model": "rothc",
        "title_fa": "کاهش کربن آلی خاک",
        "title_en": "SOC decline",
        "metric": "delta",
        "operator": "lt",
        "warning": -0.5,
        "critical": -2.0,
        "unit": "t C/ha",
        "icon": "mountain",
    },
    {
        "id": "ndvi_greenness",
        "model": "ndvi",
        "title_fa": "سبزینگی NDVI",
        "title_en": "NDVI greenness",
        "metric": "mean_ndvi",
        "operator": "lt",
        "warning": 0.35,
        "critical": 0.2,
        "unit": "NDVI",
        "icon": "satellite",
    },
    {
        "id": "ndvi_canopy",
        "model": "ndvi",
        "title_fa": "پوشش تاج",
        "title_en": "Canopy cover",
        "metric": "mean_canopy",
        "operator": "lt",
        "warning": 0.35,
        "critical": 0.2,
        "unit": "0–1",
        "icon": "leaf",
    },
    {
        "id": "sensor_soil_moisture",
        "model": "sensor",
        "title_fa": "رطوبت خاک (سنسور)",
        "title_en": "Soil moisture sensor",
        "metric": "soil_moisture",
        "operator": "lt",
        "warning": 25.0,
        "critical": 15.0,
        "unit": "%",
        "icon": "droplets",
    },
    {
        "id": "sensor_temp",
        "model": "sensor",
        "title_fa": "دمای هوا (سنسور)",
        "title_en": "Air temperature",
        "metric": "air_temp_c",
        "operator": "gt",
        "warning": 38.0,
        "critical": 42.0,
        "unit": "°C",
        "icon": "sun",
    },
]


def _cmp(op: str, value: float, threshold: float) -> bool:
    if op == "lt":
        return value < threshold
    if op == "lte":
        return value <= threshold
    if op == "gt":
        return value > threshold
    if op == "gte":
        return value >= threshold
    return False


def _severity(op: str, value: float, warning: float, critical: float) -> str:
    # critical is "worse" side of the operator
    if _cmp(op, value, critical):
        return "critical"
    if _cmp(op, value, warning):
        return "warning"
    return "ok"


def extract_metrics(bundle: dict[str, Any]) -> dict[str, float]:
    """Flatten metrics from model result dicts."""
    m: dict[str, float] = {}
    aq = bundle.get("aquacrop") or {}
    if aq:
        m["yield_relative"] = float(aq.get("yield_relative") or 0)
        m["irrigation_need_mm"] = float(aq.get("irrigation_need_mm") or 0)
        m["etc_mm"] = float(aq.get("etc_mm") or 0)
        series = aq.get("series_sample") or []
        if series:
            ks_vals = [float(x.get("ks") or 1) for x in series]
            m["mean_ks"] = sum(ks_vals) / len(ks_vals)
        else:
            m["mean_ks"] = float(aq.get("relative_transpiration") or 1.0)
    scs = bundle.get("scs") or bundle.get("swat") or {}
    outs = scs.get("outputs") or scs
    if outs and ("runoff_mm_year" in outs or scs.get("model") == "scs_cn_basin_balance"):
        m["runoff_mm_year"] = float(outs.get("runoff_mm_year") or 0)
        m["sediment_t_km2_year"] = float(outs.get("sediment_t_km2_year") or 0)
        m["water_yield_mm_year"] = float(outs.get("water_yield_mm_year") or 0)
    rt = bundle.get("rothc") or {}
    if rt:
        m["delta"] = float(rt.get("delta") or 0)
        m["soc_final"] = float(rt.get("soc_final") or 0)
    nd = bundle.get("ndvi") or {}
    if nd:
        ndvi = nd.get("ndvi") or []
        cc = nd.get("canopy_cover") or []
        if ndvi:
            m["mean_ndvi"] = sum(float(x) for x in ndvi) / len(ndvi)
        if cc:
            m["mean_canopy"] = sum(float(x) for x in cc) / len(cc)
    sensors = bundle.get("sensors") or {}
    for k, v in sensors.items():
        try:
            m[str(k)] = float(v)
        except (TypeError, ValueError):
            pass
    return m


def evaluate_monitors(
    metrics: dict[str, float],
    *,
    monitor_ids: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for mon in MONITOR_CATALOG:
        if monitor_ids and mon["id"] not in monitor_ids:
            continue
        key = mon["metric"]
        if key not in metrics:
            continue
        value = float(metrics[key])
        sev = _severity(mon["operator"], value, float(mon["warning"]), float(mon["critical"]))
        events.append(
            {
                "monitor_id": mon["id"],
                "model": mon["model"],
                "title_fa": mon["title_fa"],
                "title_en": mon["title_en"],
                "metric": key,
                "value": round(value, 4),
                "unit": mon["unit"],
                "severity": sev,
                "thresholds": {"warning": mon["warning"], "critical": mon["critical"], "operator": mon["operator"]},
                "message_fa": _msg_fa(mon, value, sev),
                "message_en": _msg_en(mon, value, sev),
                "icon": mon.get("icon", "activity"),
                "observed_at": datetime.now(timezone.utc).isoformat(),
            }
        )
    # sort critical first
    order = {"critical": 0, "warning": 1, "ok": 2}
    events.sort(key=lambda e: order.get(e["severity"], 9))
    return events


def _msg_fa(mon: dict[str, Any], value: float, sev: str) -> str:
    if sev == "ok":
        return f«{mon["title_fa"]}: مقدار {value:.3g} {mon["unit"]} در محدودهٔ ایمن است.»
    if sev == "warning":
        return f«هشدار — {mon["title_fa"]}: {value:.3g} {mon["unit"]} از آستانه هشدار گذشته است.»
    return f«بحرانی — {mon["title_fa"]}: {value:.3g} {mon["unit"]}؛ اقدام فوری توصیه می‌شود.»


def _msg_en(mon: dict[str, Any], value: float, sev: str) -> str:
    if sev == "ok":
        return f'{mon["title_en"]}: {value:.3g} {mon["unit"]} within safe range.'
    if sev == "warning":
        return f'Warning — {mon["title_en"]}: {value:.3g} {mon["unit"]} breached warning threshold.'
    return f'Critical — {mon["title_en"]}: {value:.3g} {mon["unit"]}; immediate action advised.'


def synthetic_sensor_snapshot(lat: float = 32.65, lon: float = 51.67) -> dict[str, float]:
    """Offline-friendly sensor proxies (replace with live IoT when available)."""
    # mild spatial variation from lat/lon
    seed = abs(lat * 10 + lon) % 17
    return {
        "soil_moisture": 18.0 + (seed % 20),
        "air_temp_c": 28.0 + (seed % 12),
        "humidity_pct": 35.0 + (seed % 30),
        "rainfall_24h_mm": float(seed % 5),
    }


def run_full_watch(
    *,
    lat: float = 32.65,
    lon: float = 51.67,
    include_sensors: bool = True,
    aquacrop_params: Optional[dict[str, Any]] = None,
    scs_params: Optional[dict[str, Any]] = None,
    rothc_params: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Execute all process models + sensors and evaluate monitors."""
    from apps.simulation.aquacrop_advanced import run_aquacrop_advanced
    from apps.simulation.models_swat import run_swat_plus
    from apps.simulation.rothc_model import run_rothc
    from apps.simulation.science_analysis import attach_analysis

    aq = attach_analysis(
        "aquacrop",
        run_aquacrop_advanced(
            aquacrop_params
            or {
                "days": 40,
                "rain_mm_day": 0.4,
                "et0_mm_day": 5.0,
                "crop": "wheat",
                "lat": lat,
                "lon": lon,
            }
        ),
    )
    scs = attach_analysis(
        "scs",
        run_swat_plus(
            scs_params
            or {
                "precip_mm_year": 320.0,
                "curve_number": 75.0,
                "area_km2": 25.0,
            }
        ),
    )
    rt = attach_analysis(
        "rothc",
        run_rothc(rothc_params or {"years": 10, "soc_t_ha": 40.0, "c_input_t_ha_y": 1.5}),
    )

    ndvi_block: dict[str, Any] = {}
    try:
        import asyncio

        from apps.simulation.ndvi_canopy import fetch_ndvi_canopy_async
        from apps.simulation.science_analysis import attach_analysis as aa

        async def _nd() -> dict[str, Any]:
            return aa("ndvi", await fetch_ndvi_canopy_async(lat, lon, 60))

        try:
            ndvi_block = asyncio.get_event_loop().run_until_complete(_nd())
        except RuntimeError:
            ndvi_block = asyncio.run(_nd())
    except Exception as e:
        from apps.simulation.ndvi_canopy import _synthetic_ndvi, ndvi_to_canopy

        ndvi = _synthetic_ndvi(30)
        ndvi_block = attach_analysis(
            "ndvi",
            {
                "ndvi": ndvi,
                "canopy_cover": ndvi_to_canopy(ndvi),
                "provider": "synthetic-fallback",
                "count": len(ndvi),
                "error": str(e)[:80],
            },
        )

    sensors = synthetic_sensor_snapshot(lat, lon) if include_sensors else {}
    bundle = {
        "aquacrop": aq,
        "scs": scs,
        "rothc": rt,
        "ndvi": ndvi_block,
        "sensors": sensors,
    }
    metrics = extract_metrics(bundle)
    events = evaluate_monitors(metrics)
    counts = {
        "ok": sum(1 for e in events if e["severity"] == "ok"),
        "warning": sum(1 for e in events if e["severity"] == "warning"),
        "critical": sum(1 for e in events if e["severity"] == "critical"),
    }
    return {
        "watch": "full",
        "lat": lat,
        "lon": lon,
        "metrics": metrics,
        "events": events,
        "counts": counts,
        "models": {
            "aquacrop": {k: aq.get(k) for k in ("model", "yield_relative", "irrigation_need_mm", "analysis") if k in aq},
            "scs": {"model": scs.get("model"), "outputs": scs.get("outputs"), "analysis": scs.get("analysis")},
            "rothc": {k: rt.get(k) for k in ("model", "delta", "soc_final", "analysis") if k in rt},
            "ndvi": {
                "provider": ndvi_block.get("provider"),
                "count": ndvi_block.get("count"),
                "analysis": ndvi_block.get("analysis"),
            },
        },
        "sensors": sensors,
        "completed_at": datetime.now(timezone.utc).isoformat(),
    }
