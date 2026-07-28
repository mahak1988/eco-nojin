"""RothC full parameter body, schema, presets."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.simulation.rothc_params import PRESETS, resolve_params, schema_payload
from apps.simulation.science_analysis import attach_analysis

router = APIRouter(prefix="/api/v1/science", tags=["RothC"])


class RothCBody(BaseModel):
    years: int = Field(15, ge=1, le=100, description="Simulation years")
    soc_t_ha: float = Field(40.0, ge=5, le=200, description="Initial total SOC t C/ha")
    c_input_t_ha_y: float = Field(1.5, ge=0, le=15, description="Annual C input")
    clay_pct: float = Field(25.0, ge=0, le=80)
    temp_c: float = Field(15.0, ge=-10, le=40)
    rain_mm_year: float = Field(650.0, ge=0, le=3000)
    et_mm_year: float = Field(700.0, ge=0, le=3000)
    plant_cover: bool = True
    dpm_rpm_ratio: float = Field(1.44, ge=0.1, le=5.0)
    iom_t_ha: Optional[float] = Field(None, ge=0, le=50)
    dpm_t_ha: Optional[float] = Field(None, ge=0, le=50)
    rpm_t_ha: Optional[float] = Field(None, ge=0, le=80)
    bio_t_ha: Optional[float] = Field(None, ge=0, le=20)
    hum_t_ha: Optional[float] = Field(None, ge=0, le=150)
    use_falloon_iom: bool = True
    k_dpm: float = Field(10.0, ge=1, le=20)
    k_rpm: float = Field(0.3, ge=0.05, le=2)
    k_bio: float = Field(0.66, ge=0.1, le=2)
    k_hum: float = Field(0.02, ge=0.005, le=0.1)
    preset: Optional[str] = Field(None, description="Preset id from /rothc/presets")
    with_sa: bool = False
    persist: bool = True


@router.get("/rothc/schema")
async def rothc_schema() -> dict[str, Any]:
    """Full parameter catalog for UI forms."""
    return schema_payload()


@router.get("/rothc/presets")
async def rothc_presets() -> dict[str, Any]:
    return {
        "items": [
            {"id": k, "label_fa": v["label_fa"], "label_en": v["label_en"], "params": v["params"]}
            for k, v in PRESETS.items()
        ]
    }


@router.get("/rothc/defaults")
async def rothc_defaults(preset: Optional[str] = Query(None)) -> dict[str, Any]:
    base = RothCBody().model_dump()
    if preset:
        if preset not in PRESETS:
            raise HTTPException(400, f"Unknown preset: {preset}. Use /rothc/presets")
        base.update(PRESETS[preset]["params"])
    resolved = resolve_params(base)
    return {
        "defaults": base,
        "resolved_pools": {
            "iom_t_ha": resolved["iom_t_ha"],
            "dpm_t_ha": resolved["dpm_t_ha"],
            "rpm_t_ha": resolved["rpm_t_ha"],
            "bio_t_ha": resolved["bio_t_ha"],
            "hum_t_ha": resolved["hum_t_ha"],
        },
        "preset": preset,
        "labels_fa": {c["name"]: c["label_fa"] for c in schema_payload()["parameters"]},
        "groups": ["simulation", "initial_pools", "management", "soil", "climate", "advanced"],
        "notes_fa": schema_payload()["notes_fa"],
    }


@router.post("/rothc/run")
async def rothc_run_full(
    body: RothCBody,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    from apps.simulation.report_builder import report_rothc
    from apps.simulation.rothc_model import run_rothc

    params = body.model_dump()
    with_sa = params.pop("with_sa", False)
    persist = params.pop("persist", True)
    preset = params.pop("preset", None)
    if preset:
        if preset not in PRESETS:
            raise HTTPException(400, f"Unknown preset: {preset}")
        # preset fills missing / overrides as base then body wins for explicit fields
        merged = {**PRESETS[preset]["params"], **{k: v for k, v in params.items() if v is not None}}
        params = merged

    # drop Nones so resolve_params can partition
    params = {k: v for k, v in params.items() if v is not None}

    result = attach_analysis("rothc", run_rothc(params))
    sa = None
    if with_sa:
        from apps.simulation.soil_sensitivity import global_sa_rothc

        sa = global_sa_rothc(n_src=60, n_morris=6, n_sobol=20)
        result["global_sensitivity"] = sa
    result["report"] = report_rothc(result, sensitivity=sa)
    if persist:
        try:
            from apps.simulation.run_store import save_run_async

            row = await save_run_async(session, "rothc_26_3", result.get("params_resolved") or params, result)
            result["run_id"] = row.id
        except Exception as e:
            result["persist_error"] = str(e)[:200]
    return result
