# apps/backend-api/app/land_soil_water/manager_routers.py

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.db import get_session
from app.core.security import get_current_user_with_roles  # باید نقش‌ها را برگرداند. [file:21]
from app.land_soil_water import schemas, services, analysis as analysis_module
from app.land_soil_water.models import AnalysisORM
from app.land_soil_water.schemas import AnalysisStatus

router = APIRouter(
    prefix="/api/v1/land-soil-water/manager",
    tags=["Land & Soil-Water Manager"],
)


def _require_manager(user) -> None:
    roles = getattr(user, "roles", []) or []
    if "land_soil_water_manager" not in roles and "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Manager role required.",
        )


@router.get(
    "/analyses/pending",
    response_model=List[schemas.AnalysisSummary],
    summary="لیست تحلیل‌های در انتظار تایید",
)
async def list_pending_analyses(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user_with_roles),
):
    _require_manager(current_user)

    q = await session.execute(
        select(AnalysisORM).where(
            AnalysisORM.status.in_(
                [
                    AnalysisStatus.COMPLETED.value,
                    AnalysisStatus.FINALIZED.value,
                ]
            )
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
    "/analyses/{analysis_id}/assessment",
    summary="دریافت تحلیل و توصیه برای بررسی مدیر",
)
async def get_analysis_assessment(
    analysis_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user_with_roles),
):
    _require_manager(current_user)

    detail = await services.get_analysis_detail(
        session=session,
        user_id=str(current_user.id),
        analysis_id=analysis_id,
        include_private=True,
    )
    recs = analysis_module.assess_analysis(detail)
    return {
        "detail": detail,
        "recommendations": {
            "overall_risk_fa": recs.overall_risk_fa,
            "overall_risk_en": recs.overall_risk_en,
            "indicator_assessments": [
                {
                    "indicator": a.indicator,
                    "value": a.value,
                    "severity": a.severity,
                    "message_fa": a.message_fa,
                    "message_en": a.message_en,
                }
                for a in recs.indicator_assessments
            ],
            "management_recommendations_fa": recs.management_recommendations_fa,
            "management_recommendations_en": recs.management_recommendations_en,
        },
    }


@router.post(
    "/analyses/{analysis_id}/approve",
    status_code=204,
    summary="تایید تحلیل برای ثبت نهایی و ارسال به قرارداد هوشمند",
)
async def approve_analysis(
    analysis_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user_with_roles),
):
    _require_manager(current_user)

    analysis: AnalysisORM | None = await session.get(AnalysisORM, analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    if analysis.status not in {
        AnalysisStatus.COMPLETED.value,
        AnalysisStatus.FINALIZED.value,
    }:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Analysis is not ready for approval.",
        )

    analysis.status = AnalysisStatus.FINALIZED.value
    await session.commit()

    # TODO: اینجا می‌توان job ارسال به قرارداد هوشمند را در صف قرار داد. [file:21]

    return


@router.post(
    "/analyses/{analysis_id}/reject",
    status_code=204,
    summary="رد تحلیل (به دلیل کیفیت داده یا خطا)",
)
async def reject_analysis(
    analysis_id: str,
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user_with_roles),
):
    _require_manager(current_user)

    analysis: AnalysisORM | None = await session.get(AnalysisORM, analysis_id)
    if analysis is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found.",
        )

    analysis.status = AnalysisStatus.FAILED.value
    await session.commit()
    return