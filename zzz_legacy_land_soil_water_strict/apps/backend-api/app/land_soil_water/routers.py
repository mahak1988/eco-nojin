# apps/backend-api/app/land_soil_water/routers.py

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user  # تابعی که user را از JWT استخراج می‌کند. [file:21]
from app.land_soil_water import schemas, services

router = APIRouter(
    prefix="/api/v1/land-soil-water",
    tags=["Land & Soil-Water"],
)


@router.get(
    "/indicators",
    response_model=schemas.IndicatorListResponse,
    summary="دریافت فهرست شاخص‌های آب و خاک",
)
async def get_indicators():
    return await services.list_indicators()


@router.get(
    "/units",
    response_model=schemas.LandUnitListResponse,
    summary="لیست واحدهای مکانی با شاخص‌های میانگین",
)
async def list_units(
    region_id: str | None = Query(default=None),
    indicator: schemas.IndicatorCode | None = Query(default=None),
    indicator_min: float | None = Query(default=None),
    indicator_max: float | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    session: AsyncSession = Depends(get_session),
):
    filters = schemas.LandUnitFilter(
        region_id=region_id,
        indicator=indicator,
        indicator_min=indicator_min,
        indicator_max=indicator_max,
    )
    return await services.list_land_units(
        session=session,
        filters=filters,
        limit=limit,
        offset=offset,
    )


@router.post(
    "/analyses",
    response_model=schemas.CreateAnalysisResponse,
    status_code=201,
    summary="ایجاد تحلیل جدید برای واحد و سناریوی مشخص",
)
async def create_analysis(
    payload: schemas.CreateAnalysisRequest,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    # current_user باید حداقل شامل فیلد id باشد. [file:21]
    return await services.create_analysis(
        session=session,
        user_id=str(current_user.id),
        payload=payload,
    )


@router.get(
    "/analyses/me",
    response_model=List[schemas.AnalysisSummary],
    summary="لیست تحلیل‌های کاربر جاری",
)
async def list_my_analyses(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    from app.land_soil_water.models import AnalysisORM  # import محلی برای جلوگیری از حلقه.

    q = (
        await session.execute(
            AnalysisORM.select_for_user(current_user.id)  # فرض: متد کلاس در ORM تعریف شده. [file:21]
        )
    )
    analyses = q.scalars().all()

    summaries: List[schemas.AnalysisSummary] = []
    for a in analyses:
        summaries.append(
            schemas.AnalysisSummary(
                id=str(a.id),
                user_id=a.user_id,
                land_unit_id=a.land_unit_id,
                scenario_id=None,
                scenario_type=schemas.ScenarioType(a.scenario_type),
                status=schemas.AnalysisStatus(a.status),
                created_at=a.created_at,
                updated_at=a.updated_at,
                period_start=a.period_start,
                period_end=a.period_end,
                indicators_avg=a.indicators_avg or {},
            )
        )
    return summaries


@router.get(
    "/analyses/{analysis_id}",
    response_model=schemas.AnalysisDetail,
    summary="دریافت جزئیات کامل یک تحلیل",
)
async def get_analysis(
    analysis_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return await services.get_analysis_detail(
        session=session,
        user_id=str(current_user.id),
        analysis_id=analysis_id,
    )
# apps/backend-api/app/land_soil_water/routers.py (افزودن انتهایی)

from fastapi import Response
from app.land_soil_water.schemas import FinalizeAnalysisRequest, ExportFormat


@router.post(
    "/analyses/{analysis_id}/finalize",
    response_model=schemas.FinalizeAnalysisResponse,
    summary="نهایی‌سازی تحلیل و در صورت درخواست، آماده‌سازی ثبت روی زنجیره",
)
async def finalize_analysis_endpoint(
    analysis_id: str,
    payload: FinalizeAnalysisRequest,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return await services.finalize_analysis(
        session=session,
        user_id=str(current_user.id),
        analysis_id=analysis_id,
        payload=payload,
    )


@router.get(
    "/analyses/{analysis_id}/export",
    summary="خروجی تحلیل به فرمت‌های JSON/CSV/GeoJSON/PDF",
)
async def export_analysis_endpoint(
    analysis_id: str,
    format: ExportFormat,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user),
):
    return await services.prepare_export_data(
        session=session,
        user_id=str(current_user.id),
        analysis_id=analysis_id,
        fmt=format,
    )