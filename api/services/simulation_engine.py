"""Scientific simulation stubs — RothC, AquaCrop, coupling (globalized params)."""

from typing import Any


def simulate_rothc(
    initial_soc: float,
    clay_percent: float,
    mean_temp_c: float,
    annual_rain_mm: float,
    years: int = 1,
) -> dict[str, Any]:
    """RothC full model (scripts/rothc.py port) with simplified fallback."""
    try:
        from api.services.rothc_full import run_rothc_from_params

        return run_rothc_from_params(initial_soc, clay_percent, mean_temp_c, annual_rain_mm, years)
    except Exception:
        k = 0.02 + (clay_percent / 100) * 0.01
        soc = initial_soc
        series = []
        for y in range(years):
            soc = max(0, soc + 2.5 - soc * k)
            series.append({"year": y + 1, "soc_t_ha": round(soc, 3)})
        return {"model": "RothC-fallback", "final_soc_t_ha": round(soc, 3), "series": series}


def simulate_aquacrop(
    crop: str,
    area_ha: float,
    irrigation_mm: float,
    rainfall_mm: float,
) -> dict[str, Any]:
    """Simplified crop water productivity."""
    crop_kc = {"wheat": 1.1, "maize": 1.2, "rice": 1.35, "barley": 1.0}.get(crop.lower(), 1.05)
    et = (rainfall_mm * 0.6 + irrigation_mm * 0.85) * crop_kc
    yield_t_ha = max(0, (et / 500) * 4.5 * crop_kc)
    return {
        "model": "AquaCrop-simplified",
        "crop": crop,
        "area_ha": area_ha,
        "yield_t_ha": round(yield_t_ha, 2),
        "total_yield_t": round(yield_t_ha * area_ha, 2),
        "et_mm": round(et, 1),
        "irrigation_mm": irrigation_mm,
        "rainfall_mm": rainfall_mm,
    }


def simulate_coupling(modules: list[dict]) -> dict[str, Any]:
    results = []
    total_score = 0.0
    for m in modules:
        name = m.get("name", "unknown")
        if name == "rothc":
            r = simulate_rothc(
                **{
                    k: m[k]
                    for k in ("initial_soc", "clay_percent", "mean_temp_c", "annual_rain_mm")
                    if k in m
                }
            )
        elif name == "aquacrop":
            r = simulate_aquacrop(
                m.get("crop", "wheat"),
                m.get("area_ha", 1),
                m.get("irrigation_mm", 200),
                m.get("rainfall_mm", 300),
            )
        else:
            r = {"model": name, "status": "skipped"}
        results.append(r)
        total_score += r.get("final_soc_t_ha", r.get("total_yield_t", 0))
    return {"modules": results, "coupling_score": round(total_score, 3)}
