# apps/backend-api/app/land_soil_water/admin_services.py

from __future__ import annotations

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.land_soil_water.schemas import IndicatorCode
from app.land_soil_water.models import LandUnitORM, AnalysisORM, IndicatorValueORM
from app.land_soil_water.analysis import (
    SOIL_LOSS_THRESHOLDS,
    EROSION_RISK_THRESHOLDS,
)


@dataclass
class LdnStatusCounts:
    degraded_area_ha: float
    not_degraded_area_ha: float
    unknown_area_ha: float
    degraded_units: int
    not_degraded_units: int
    unknown_units: int


@dataclass
class IndicatorDistribution:
    indicator: IndicatorCode
    min_value: Optional[float]
    max_value: Optional[float]
    avg_value: Optional[float]
    p25: Optional[float]
    p50: Optional[float]
    p75: Optional[float]


@dataclass
class AdminMetrics:
    total_analyses: int
    completed_analyses: int
    finalized_analyses: int
    on_chain_analyses: int
    ldn_status: LdnStatusCounts
    indicator_distributions: List[IndicatorDistribution]


async def _get_latest_analysis_per_land_unit(
    session: AsyncSession,
) -> Dict[str, AnalysisORM]:
    """
    آخرین تحلیل (براساس زمان ایجاد) برای هر LandUnit که وضعیت completed/finalized/on_chain دارد.
    """
    subq = (
        select(
            AnalysisORM.land_unit_id,
            func.max(AnalysisORM.created_at).label("max_created_at"),
        )
        .where(
            AnalysisORM.status.in_(
                ["completed", "finalized", "on_chain_registered"]
            )
        )
        .group_by(AnalysisORM.land_unit_id)
        .subquery()
    )

    q = await session.execute(
        select(AnalysisORM).join(
            subq,
            (AnalysisORM.land_unit_id == subq.c.land_unit_id)
            & (AnalysisORM.created_at == subq.c.max_created_at),
        )
    )
    analyses = q.scalars().all()
    return {a.land_unit_id: a for a in analyses}


async def _compute_ldn_status(
    session: AsyncSession,
    latest_analyses: Dict[str, AnalysisORM],
) -> LdnStatusCounts:
    """
    تعیین وضعیت degraded / not degraded برای هر LandUnit موجود در latest_analyses
    بر اساس فرسایش و شاخص ریسک فرسایش (به عنوان پراکسی وضعیت خاک/کربن). [web:22][web:33][web:43][web:46]
    """
    land_unit_ids = list(latest_analyses.keys())
    if not land_unit_ids:
        return LdnStatusCounts(
            degraded_area_ha=0.0,
            not_degraded_area_ha=0.0,
            unknown_area_ha=0.0,
            degraded_units=0,
            not_degraded_units=0,
            unknown_units=0,
        )

    q_lu = await session.execute(
        select(LandUnitORM).where(LandUnitORM.id.in_(land_unit_ids))
    )
    land_units = {lu.id: lu for lu in q_lu.scalars().all()}

    # میانگین شاخص‌ها برای هر analysis_id
    q_ind = await session.execute(
        select(
            IndicatorValueORM.analysis_id,
            IndicatorValueORM.indicator_code,
            func.avg(IndicatorValueORM.value).label("avg_value"),
        )
        .where(IndicatorValueORM.analysis_id.in_([a.id for a in latest_analyses.values()]))
        .group_by(IndicatorValueORM.analysis_id, IndicatorValueORM.indicator_code)
    )

    # ساخت map: analysis_id -> indicator_code -> value
    indicators_map: Dict[str, Dict[IndicatorCode, float]] = {}
    for analysis_id, code_str, value in q_ind:
        code = IndicatorCode(code_str)
        indicators_map.setdefault(str(analysis_id), {})[code] = float(value)

    degraded_area = 0.0
    not_degraded_area = 0.0
    unknown_area = 0.0
    degraded_units = 0
    not_degraded_units = 0
    unknown_units = 0

    for land_unit_id, analysis in latest_analyses.items():
        lu = land_units.get(land_unit_id)
        if lu is None:
            continue

        area = float(lu.area_ha or 0.0)
        ind = indicators_map.get(str(analysis.id), {})

        # اگر هیچ شاخصی نداریم، وضعیت unknown
        if not ind:
            unknown_area += area
            unknown_units += 1
            continue

        # قاعده one-out-all-out ساده: اگر فرسایش یا ریسک فرسایش از آستانه "متوسط" بالاتر باشد ⇒ degraded. [web:42][web:43][web:46]
        degraded = False

        soil_loss = ind.get(IndicatorCode.SOIL_LOSS_T_HA)
        if soil_loss is not None and soil_loss >= SOIL_LOSS_THRESHOLDS["moderate"]:
            degraded = True

        erosion_risk = ind.get(IndicatorCode.EROSION_RISK_INDEX)
        if erosion_risk is not None and erosion_risk >= EROSION_RISK_THRESHOLDS["moderate"]:
            degraded = True

        if degraded:
            degraded_area += area
            degraded_units += 1
        else:
            not_degraded_area += area
            not_degraded_units += 1

    return LdnStatusCounts(
        degraded_area_ha=degraded_area,
        not_degraded_area_ha=not_degraded_area,
        unknown_area_ha=unknown_area,
        degraded_units=degraded_units,
        not_degraded_units=not_degraded_units,
        unknown_units=unknown_units,
    )


async def _compute_indicator_distribution(
    session: AsyncSession,
    indicator: IndicatorCode,
) -> IndicatorDistribution:
    """
    محاسبه آمار پایه (min, max, avg, quantiles) برای یک شاخص در تمام تحلیل‌های completed/finalized/on_chain. [web:34][web:44]
    """
    q = await session.execute(
        select(
            func.min(IndicatorValueORM.value),
            func.max(IndicatorValueORM.value),
            func.avg(IndicatorValueORM.value),
        )
        .select_from(IndicatorValueORM)
        .join(AnalysisORM, AnalysisORM.id == IndicatorValueORM.analysis_id)
        .where(
            IndicatorValueORM.indicator_code == indicator.value,
            AnalysisORM.status.in_(
                ["completed", "finalized", "on_chain_registered"]
            ),
        )
    )
    min_v, max_v, avg_v = q.one()
    if min_v is None:
        return IndicatorDistribution(
            indicator=indicator,
            min_value=None,
            max_value=None,
            avg_value=None,
            p25=None,
            p50=None,
            p75=None,
        )

    # کوانتیل‌ها (اگر DB از percentile_disc پشتیبانی کند، بهتر است از آن استفاده شود؛
    # اینجا از روش ساده 25/50/75 درصد با نمونه‌گیری استفاده می‌کنیم).
    q_all = await session.execute(
        select(IndicatorValueORM.value)
        .join(AnalysisORM, AnalysisORM.id == IndicatorValueORM.analysis_id)
        .where(
            IndicatorValueORM.indicator_code == indicator.value,
            AnalysisORM.status.in_(
                ["completed", "finalized", "on_chain_registered"]
            ),
        )
        .order_by(IndicatorValueORM.value)
    )
    values = [float(v) for (v,) in q_all.all()]
    n = len(values)

    def quantile(p: float) -> float:
        if n == 0:
            return float("nan")
        idx = int(p * (n - 1))
        return values[idx]

    p25 = quantile(0.25)
    p50 = quantile(0.50)
    p75 = quantile(0.75)

    return IndicatorDistribution(
        indicator=indicator,
        min_value=float(min_v),
        max_value=float(max_v),
        avg_value=float(avg_v) if avg_v is not None else None,
        p25=p25,
        p50=p50,
        p75=p75,
    )


async def compute_admin_metrics(session: AsyncSession) -> AdminMetrics:
    """
    محاسبه متریک‌های مدیریتی و LDN برای ماژول Land & Soil-Water. [web:22][web:33][web:42][web:43]
    """
    # شمارش تحلیل‌ها
    q_total = await session.execute(select(func.count()).select_from(AnalysisORM))
    total_analyses = q_total.scalar_one() or 0

    q_completed = await session.execute(
        select(func.count())
        .select_from(AnalysisORM)
        .where(AnalysisORM.status == "completed")
    )
    completed_analyses = q_completed.scalar_one() or 0

    q_finalized = await session.execute(
        select(func.count())
        .select_from(AnalysisORM)
        .where(AnalysisORM.status == "finalized")
    )
    finalized_analyses = q_finalized.scalar_one() or 0

    q_on_chain = await session.execute(
        select(func.count())
        .select_from(AnalysisORM)
        .where(AnalysisORM.status == "on_chain_registered")
    )
    on_chain_analyses = q_on_chain.scalar_one() or 0

    # LDN status
    latest = await _get_latest_analysis_per_land_unit(session)
    ldn_status = await _compute_ldn_status(session, latest)

    # توزیع شاخص‌های کلیدی
    indicators = [
        IndicatorCode.SOIL_LOSS_T_HA,
        IndicatorCode.RUNOFF_MM,
        IndicatorCode.SOIL_WATER_CONTENT_MM,
        IndicatorCode.EROSION_RISK_INDEX,
    ]
    distributions: List[IndicatorDistribution] = []
    for ind in indicators:
        distributions.append(await _compute_indicator_distribution(session, ind))

    return AdminMetrics(
        total_analyses=total_analyses,
        completed_analyses=completed_analyses,
        finalized_analyses=finalized_analyses,
        on_chain_analyses=on_chain_analyses,
        ldn_status=ldn_status,
        indicator_distributions=distributions,
    )