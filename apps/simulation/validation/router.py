import logging
logger = logging.getLogger('econojin')
"""
Validation Router — calibration data + goodness-of-fit + uncertainty + sensitivity.
"""
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from apps.simulation.data.faostat import fetch_crop_yield
from apps.simulation.validation.engine import (
    goodness_of_fit, monte_carlo, morris_sensitivity,
)
from apps.simulation.base import SimulationRegistry

router = APIRouter(prefix="/api/v1/simulation", tags=["🔬 Validation"])


class CalibrationRequest(BaseModel):
    simulator_id: str = "aquacrop"
    crop: str = "wheat"
    area_code: str = "IRN"
    parameters: dict = Field(default_factory=dict)
    run_uncertainty: bool = True
    run_sensitivity: bool = True


@router.post("/validation", summary="Calibration + validation + uncertainty + sensitivity")
async def validation(req: CalibrationRequest):
    # ۱. دادهٔ واقعی از FAOSTAT
    fao = await fetch_crop_yield(req.crop, req.area_code)
    observed = list(fao.get("data", {}).values())

    # ۲. اجرای شبیه‌ساز برای مقایسه (با میانگین شرایط)
    sim_cls = SimulationRegistry.get(req.simulator_id)
    if not sim_cls:
        raise HTTPException(404, f"Simulator '{req.simulator_id}' not found")
    # Instantiate if it's a class (Registry might return class or instance)
    sim = sim_cls() if isinstance(sim_cls, type) else sim_cls

    # Filter parameters through simulator's schema to drop unsupported ones
    sim_params = dict(req.parameters)
    sim_params.setdefault("crop", req.crop)
    validated_params = {}
    try:
        config_schema = getattr(sim, "config", None) or getattr(sim_cls, "config", None)
        if config_schema and hasattr(config_schema, "parameters"):
            valid_keys = {p.key for p in config_schema.parameters}
            for k, v in sim_params.items():
                if k in valid_keys:
                    validated_params[k] = v
            # اگر پارامتر ضروری نیست، crop را حتماً نگه دار
            if "crop" not in validated_params:
                validated_params["crop"] = req.crop
        else:
            validated_params = sim_params
    except Exception:
        validated_params = sim_params

    try:
        result = await sim.run(validated_params)
        metrics = result.metrics or {}
        # Try multiple metric keys (not just yield_t_ha)
        sim_yield = None
        for k in ("yield_t_ha", "yield", "grain_yield", "biomass_t_ha", "total_biomass"):
            if k in metrics and isinstance(metrics[k], (int, float)):
                sim_yield = metrics[k]
                break
        if sim_yield is None:
            # Fallback: first numeric metric
            for v in metrics.values():
                if isinstance(v, (int, float)):
                    sim_yield = v
                    break
    except Exception as e:
        sim_yield = None
        metrics = {"error": str(e)}

    # ۳. اعتبارسنجی (مقایسهٔ عملکرد شبیه‌سازی‌شده با میانگین دادهٔ واقعی)
    gof = None
    if observed and isinstance(sim_yield, (int, float)):
        mean_obs = round(sum(observed) / len(observed), 3)
        # ساخت سری شبیه‌سازی‌شده حول مقدار مدل برای مقایسه با سری مشاهده‌ای
        simulated_series = [sim_yield] * len(observed)
        gof = goodness_of_fit(observed, simulated_series)
        gof["observed_mean_t_ha"] = mean_obs
        gof["simulated_t_ha"] = round(sim_yield, 3)
        gof["yield_gap_pct"] = round((sim_yield - mean_obs) / mean_obs * 100, 1) if mean_obs else 0

    # ۴. عدم قطعیت (Monte Carlo)
    uncertainty = None
    if req.run_uncertainty:
        async def run_fn(p):
            try:
                r = await sim.run(p)
                return {"metrics": r.metrics or {}, "outputs": r.outputs or {}}
            except Exception as e:
                logger.warning(f'Monte Carlo run failed: {e}')
                return {"metrics": {}, "outputs": {}}
        uncertainty = await monte_carlo(run_fn, validated_params)

    # ۵. حساسیت (Morris)
    sensitivity = None
    if req.run_sensitivity:
        async def run_fn2(p):
            try:
                r = await sim.run(p)
                return {"metrics": r.metrics or {}, "outputs": r.outputs or {}}
            except Exception as e:
                logger.warning(f'Monte Carlo run failed: {e}')
                return {"metrics": {}, "outputs": {}}
        sensitivity = await morris_sensitivity(run_fn2, validated_params)

    return {
        "simulator_id": req.simulator_id,
        "crop": req.crop,
        "calibration_data": fao,
        "goodness_of_fit": gof,
        "uncertainty": uncertainty,
        "sensitivity": sensitivity,
    }
