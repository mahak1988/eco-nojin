"""RothC with full climate/soil parameter body (local / no Docker)."""

from __future__ import annotations

from typing import Any, Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.simulation.science_analysis import attach_analysis

router = APIRouter(prefix="/api/v1/science", tags=["RothC"])


class RothCBody(BaseModel):
    years: int = Field(15, ge=1, le=100)
    soc_t_ha: float = Field(40.0, ge=1, le=200)
    c_input_t_ha_y: float = Field(1.5, ge=0, le=20)
    clay_pct: float = Field(25.0, ge=0, le=80)
    temp_c: float = Field(15.0, ge=-10, le=45)
    rain_mm_year: float = Field(650.0, ge=0, le=3000)
    et_mm_year: float = Field(700.0, ge=0, le=3000)
    plant_cover: bool = True
    dpm_rpm_ratio: float = Field(1.44, ge=0.1, le=5.0)
    iom_t_ha: Optional[float] = None
    with_sa: bool = False
    persist: bool = True


@router.post("/rothc/run")
async def rothc_run_full(
    body: RothCBody,
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Full RothC parameter set + optional global SA + final report."""
    from apps.simulation.report_builder import report_rothc
    from apps.simulation.rothc_model import run_rothc

    params = body.model_dump()
    with_sa = params.pop("with_sa", False)
    persist = params.pop("persist", True)
    if params.get("iom_t_ha") is None:
        params.pop("iom_t_ha", None)

    result = attach_analysis("rothc", run_rothc(params))
    sa = None
    if with_sa:
        from apps.simulation.soil_sensitivity import global_sa_rothc

        sa = global_sa_rothc(n_src=60, n_morris=6, n_sobol=20)
        result["global_sensitivity"] = sa
    result["report"] = report_rothc(result, sensitivity=sa)
    result["params_used"] = params
    if persist:
        try:
            from apps.simulation.run_store import save_run_async

            row = await save_run_async(session, "rothc_26_3", params, result)
            result["run_id"] = row.id
        except Exception as e:
            result["persist_error"] = str(e)[:200]
    return result


@router.get("/rothc/defaults")
async def rothc_defaults() -> dict[str, Any]:
    return {
        "defaults": RothCBody().model_dump(),
        "labels_fa": {
            "years": "افق شبیه‌سازی (سال)",
            "soc_t_ha": "کربن آلی اولیه (t C/ha)",
            "c_input_t_ha_y": "ورودی کربن سالانه (بقایا/کود)",
            "clay_pct": "رس (%)",
            "temp_c": "دمای میانگین (°C)",
            "rain_mm_year": "بارش سالانه (mm)",
            "et_mm_year": "تبخیر-تعرق سالانه (mm)",
            "plant_cover": "پوشش گیاهی (کاهش نرخ تجزیه)",
            "dpm_rpm_ratio": "نسبت DPM/RPM ورودی",
        },
        "notes_fa": "پارامترها با موتور RothC-26.3 هم‌خوان هستند؛ باینری رسمی نیست.",
    }
