# apps/backend-api/app/land_soil_water/services.py

from __future__ import annotations

from datetime import datetime
from typing import List, Optional, Dict

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.land_soil_water import schemas
from app.land_soil_water.schemas import (
    LandUnitFilter,
    LandUnitWithIndicators,
    LandUnitListResponse,
    CreateAnalysisRequest,
    CreateAnalysisResponse,
    AnalysisSummary,
    AnalysisDetail,
    IndicatorCode,
    AnalysisStatus,
    IndicatorDefinition,
    IndicatorListResponse,
)
from app.core import db  # فرض بر این است که Session/engine اینجا تعریف شده است. [file:21]

# نکته: مدل‌های ORM (LandUnitORM, AnalysisORM, IndicatorValueORM) باید در فایل models.py تعریف شوند.
from app.land_soil_water.models import (
    LandUnitORM,
    AnalysisORM,
    IndicatorValueORM,
    SoilProfileORM,
    ClimatePointORM,
)


INDICATOR_DEFINITIONS: Dict[IndicatorCode, IndicatorDefinition] = {
    IndicatorCode.RUNOFF_MM: IndicatorDefinition(
        code=IndicatorCode.RUNOFF_MM,
        unit="mm",
        title_fa="رواناب سطحی",
        title_en="Surface runoff",
        description_fa="حجم رواناب سطحی تجمعی طی دوره تحلیل بر حسب میلی‌متر.",
        description_en="Cumulative surface runoff over the analysis period in millimeters.",
    ),
    IndicatorCode.SOIL_LOSS_T_HA: IndicatorDefinition(
        code=IndicatorCode.SOIL_LOSS_T_HA,
        unit="t/ha",
        title_fa="فرسایش خاک",
        title_en="Soil loss",
        description_fa="برآورد فرسایش خاک بر حسب تن در هکتار در دوره تحلیل.",
        description_en="Estimated soil loss over the analysis period in tons per hectare.",
    ),
    IndicatorCode.SOIL_WATER_CONTENT_MM: IndicatorDefinition(
        code=IndicatorCode.SOIL_WATER_CONTENT_MM,
        unit="mm",
        title_fa="رطوبت خاک",
        title_en="Soil water content",
        description_fa="ذخیره رطوبت خاک در عمق مؤثر بر حسب میلی‌متر ستون آب.",
        description_en="Soil water storage in the effective root zone in millimeters.",
    ),
    IndicatorCode.INFILTRATION_MM: IndicatorDefinition(
        code=IndicatorCode.INFILTRATION_MM,
        unit="mm",
        title_fa="نفوذ",
        title_en="Infiltration",
        description_fa="حجم نفوذ تجمعی در خاک طی دوره تحلیل.",
        description_en="Cumulative water infiltration into the soil over the analysis period.",
    ),
    IndicatorCode.EROSION_RISK_INDEX: IndicatorDefinition(
        code=IndicatorCode.EROSION_RISK_INDEX,
        unit="-",
        title_fa="شاخص ریسک فرسایش",
        title_en="Erosion risk index",
        description_fa="شاخص بدون‌بعد ریسک فرسایش (۰: کم، ۱: بسیار بالا).",
        description_en="Dimensionless erosion risk index (0: low, 1: very high).",
    ),
}


async def list_indicators() -> IndicatorListResponse:
    return IndicatorListResponse(indicators=list(INDICATOR_DEFINITIONS.values()))


async def list_land_units(
    session: AsyncSession,
    filters: LandUnitFilter,
    limit: int = 50,
    offset: int = 0,
) -> LandUnitListResponse:
    query = select(LandUnitORM)
    if filters.region_id:
        query = query.where(LandUnitORM.region_id == filters.region_id)

    total = (await session.execute(query.with_only_columns(func.count()))).scalar_one()

    query = query.limit(limit).offset(offset)
    result = await session.execute(query)
    units: List[LandUnitORM] = result.scalars().all()

    items: List[LandUnitWithIndicators] = []

    for unit in units:
        ind_query = (
            select(
                IndicatorValueORM.indicator_code,
                func.avg(IndicatorValueORM.value).label("avg_value"),
            )
            .where(IndicatorValueORM.land_unit_id == unit.id)
            .group_by(IndicatorValueORM.indicator_code)
        )
        ind_result = await session.execute(ind_query)
        indicators_avg: Dict[IndicatorCode, float] = {}
        for row in ind_result:
            code = IndicatorCode(row.indicator_code)
            if filters.indicator and code != filters.indicator:
                continue
            value = float(row.avg_value)
            if filters.indicator_min is not None and value < filters.indicator_min:
                continue
            if filters.indicator_max is not None and value > filters.indicator_max:
                continue
            indicators_avg[code] = value

        items.append(
            LandUnitWithIndicators(
                land_unit=schemas.LandUnit(
                    id=unit.id,
                    name=unit.name,
                    geometry_type=unit.geometry_type,
                    area_ha=unit.area_ha,
                    centroid_lat=unit.centroid_lat,
                    centroid_lon=unit.centroid_lon,
                    region_id=unit.region_id,
                ),
                indicators_avg=indicators_avg,
            )
        )

    return LandUnitListResponse(items=items, total=total)


async def create_analysis(
    session: AsyncSession,
    user_id: str,
    payload: CreateAnalysisRequest,
) -> CreateAnalysisResponse:
    now = datetime.utcnow()

    lu = await session.get(LandUnitORM, payload.land_unit_id)
    if lu is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Land unit not found.",
        )

    analysis = AnalysisORM(
        user_id=user_id,
        land_unit_id=payload.land_unit_id,
        scenario_type=payload.scenario.scenario_type.value,
        status=AnalysisStatus.PENDING.value,
        created_at=now,
        updated_at=now,
        period_start=payload.scenario.start_date,
        period_end=payload.scenario.end_date,
    )
    session.add(analysis)
    await session.flush()

    # سناریو در جدول جداگانه یا به صورت JSON در AnalysisORM ذخیره می‌شود (بسته به طراحی DB).
    # اینجا فرض می‌کنیم فیلد jsonb با نام scenario_json داریم.
    analysis.scenario_json = payload.scenario.dict()

    # در این نقطه می‌توان یک job در صف (Celery / Redis) برای اجرای تحلیل اضافه کرد. [file:21]

    await session.commit()

    return CreateAnalysisResponse(
        analysis_id=str(analysis.id),
        status=AnalysisStatus(analysis.status),
    )


async def get_analysis_detail(
    session: AsyncSession,
    user_id: str,
    analysis_id: str,
    include_private: bool = False,
) -> AnalysisDetail:
    analysis: Optional[AnalysisORM] = await session.get(AnalysisORM, analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    # کنترل دسترسی: کاربر فقط تحلیل خود را می‌بیند، مگر نقش مدیریتی داشته باشد.
    if not include_private and analysis.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    soil_profile_orm: Optional[SoilProfileORM] = (
        await session.execute(
            select(SoilProfileORM).where(
                SoilProfileORM.land_unit_id == analysis.land_unit_id
            )
        )
    ).scalar_one_or_none()

    climate_points_orm: List[ClimatePointORM] = (
        await session.execute(
            select(ClimatePointORM).where(
                ClimatePointORM.analysis_id == analysis.id
            )
        )
    ).scalars().all()

    indicator_values = (
        await session.execute(
            select(
                IndicatorValueORM.indicator_code,
                IndicatorValueORM.date,
                IndicatorValueORM.value,
            )
            .where(IndicatorValueORM.analysis_id == analysis.id)
            .order_by(IndicatorValueORM.indicator_code, IndicatorValueORM.date)
        )
    ).all()

    timeseries_map: Dict[IndicatorCode, List[schemas.IndicatorTimeseriesPoint]] = {}
    for code_str, d, value in indicator_values:
        code = IndicatorCode(code_str)
        timeseries_map.setdefault(
            code, []
        ).append(schemas.IndicatorTimeseriesPoint(date=d, value=float(value)))

    timeseries_list = []
    for code, series in timeseries_map.items():
        defn = INDICATOR_DEFINITIONS[code]
        timeseries_list.append(
            schemas.IndicatorTimeseries(
                indicator=code,
                unit=defn.unit,
                series=series,
            )
        )

    soil_profile: Optional[schemas.SoilProfile] = None
    if soil_profile_orm:
        soil_profile = schemas.SoilProfile(
            land_unit_id=soil_profile_orm.land_unit_id,
            depth_cm=soil_profile_orm.depth_cm,
            texture=soil_profile_orm.texture,
            organic_carbon_pct=soil_profile_orm.organic_carbon_pct,
            bulk_density=soil_profile_orm.bulk_density,
            available_water_capacity=soil_profile_orm.available_water_capacity,
        )

    climate_points = [
        schemas.ClimatePoint(
            date=cp.date,
            precipitation_mm=cp.precipitation_mm,
            tmean_c=cp.tmean_c,
            et0_mm=cp.et0_mm,
        )
        for cp in climate_points_orm
    ]

    summary = AnalysisSummary(
        id=str(analysis.id),
        user_id=analysis.user_id,
        land_unit_id=analysis.land_unit_id,
        scenario_id=None,
        scenario_type=schemas.ScenarioType(analysis.scenario_type),
        status=AnalysisStatus(analysis.status),
        created_at=analysis.created_at,
        updated_at=analysis.updated_at,
        period_start=analysis.period_start,
        period_end=analysis.period_end,
        indicators_avg=analysis.indicators_avg or {},
    )

    return AnalysisDetail(
        summary=summary,
        soil_profile=soil_profile,
        climate=climate_points or None,
        timeseries=timeseries_list,
    )
# apps/backend-api/app/land_soil_water/services.py (افزودن انتهایی)

from io import StringIO
import csv
from datetime import datetime

from fastapi import Response
from fastapi.responses import JSONResponse, StreamingResponse

from app.land_soil_water.schemas import (
    FinalizeAnalysisRequest,
    FinalizeAnalysisResponse,
    ExportFormat,
    ExportMetadata,
)


async def finalize_analysis(
    session: AsyncSession,
    user_id: str,
    analysis_id: str,
    payload: FinalizeAnalysisRequest,
) -> FinalizeAnalysisResponse:
    analysis: AnalysisORM | None = await session.get(AnalysisORM, analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    if analysis.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied.",
        )

    if analysis.status not in {
        AnalysisStatus.COMPLETED.value,
        AnalysisStatus.FINALIZED.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis is not ready to be finalized.",
        )

    analysis.status = AnalysisStatus.FINALIZED.value
    analysis.updated_at = datetime.utcnow()
    await session.commit()

    on_chain_requested = False

    if payload.store_on_chain:
        # اینجا فقط flag را set می‌کنیم یا job را در صف قرار می‌دهیم.
        # در یک سرویس queue جدا (Celery/Redis) عملیات web3 انجام می‌شود. [file:21]
        on_chain_requested = True
        # مثال: enqueue_register_on_chain(analysis_id)

    return FinalizeAnalysisResponse(
        status=AnalysisStatus(analysis.status),
        on_chain_requested=on_chain_requested,
    )


async def prepare_export_data(
    session: AsyncSession,
    user_id: str,
    analysis_id: str,
    fmt: ExportFormat,
) -> Response:
    detail = await get_analysis_detail(
        session=session,
        user_id=user_id,
        analysis_id=analysis_id,
    )

    summary = detail.summary

    metadata = ExportMetadata(
        analysis_id=summary.id,
        land_unit_id=summary.land_unit_id,
        scenario_type=summary.scenario_type,
        period_start=summary.period_start,
        period_end=summary.period_end,
        indicators_avg=summary.indicators_avg or {},
        generated_at=datetime.utcnow(),
    )

    if fmt == ExportFormat.JSON:
        payload = {
            "metadata": metadata.dict(),
            "soil_profile": detail.soil_profile.dict() if detail.soil_profile else None,
            "climate": [cp.dict() for cp in (detail.climate or [])],
            "timeseries": [ts.dict() for ts in detail.timeseries],
        }
        return JSONResponse(content=payload)

    if fmt == ExportFormat.CSV:
        buffer = StringIO()
        writer = csv.writer(buffer)
        writer.writerow(
            [
                "indicator",
                "date",
                "value",
                "unit",
                "land_unit_id",
                "analysis_id",
            ]
        )
        for ts in detail.timeseries:
            for p in ts.series:
                writer.writerow(
                    [
                        ts.indicator.value,
                        p.date.isoformat(),
                        p.value,
                        ts.unit,
                        summary.land_unit_id,
                        summary.id,
                    ]
                )
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="text/csv",
            headers={
                "Content-Disposition": f'attachment; filename="analysis_{summary.id}.csv"'
            },
        )

    if fmt == ExportFormat.GEOJSON:
        # GeoJSON FeatureCollection بر اساس best-practice: geometry از LandUnit، properties از indicators. [web:38][web:41]
        # فرض می‌کنیم LandUnitORM.geometry به صورت WKB/WKT قابل تبدیل به GeoJSON است؛
        # در اینجا فقط اسکلت پاسخ را می‌سازیم و تبدیل واقعی در لایه GIS شما انجام می‌شود. [file:21]
        from app.land_soil_water.models import LandUnitORM  # type: ignore

        lu: LandUnitORM | None = await session.get(LandUnitORM, summary.land_unit_id)
        if lu is None or not getattr(lu, "geometry_geojson", None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="GeoJSON geometry is not available for this land unit.",
            )

        feature = {
            "type": "Feature",
            "geometry": lu.geometry_geojson,  # باید در ORM به صورت dict ذخیره شده باشد. [file:21]
            "properties": {
                "analysis_id": summary.id,
                "land_unit_id": summary.land_unit_id,
                "scenario_type": summary.scenario_type.value,
                "period_start": summary.period_start.isoformat()
                if summary.period_start
                else None,
                "period_end": summary.period_end.isoformat()
                if summary.period_end
                else None,
                "indicators_avg": summary.indicators_avg or {},
            },
        }
        collection = {"type": "FeatureCollection", "features": [feature]}
        return JSONResponse(content=collection)

    if fmt == ExportFormat.PDF:
        # برای ساده‌سازی، فعلاً یک JSON summary برمی‌گردانیم؛
        # در محیط production، این تابع باید به سرویس تولید PDF (WeasyPrint/ReportLab) متصل شود. [file:21]
        payload = {
            "metadata": metadata.dict(),
            "summary": summary.dict(),
            "note": "در محیط production این خروجی باید به PDF تبدیل شود.",
        }
        return JSONResponse(content=payload)

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Unsupported export format.",
    )