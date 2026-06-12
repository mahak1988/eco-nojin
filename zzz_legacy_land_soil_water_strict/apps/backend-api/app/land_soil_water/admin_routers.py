# apps/backend-api/app/land_soil_water/admin_routers.py

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_session
from app.core.security import get_current_user_with_roles
from app.land_soil_water.admin_services import compute_admin_metrics

router = APIRouter(
    prefix="/api/v1/admin/land-soil-water",
    tags=["Admin - Land & Soil-Water"],
)


def _require_admin(user) -> None:
    roles = getattr(user, "roles", []) or []
    if "admin" not in roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin role required.",
        )


@router.get(
    "/metrics",
    summary="متریک‌های مدیریتی و LDN برای ماژول آب و خاک",
)
async def get_admin_metrics(
    session: AsyncSession = Depends(get_session),
    current_user=Depends(get_current_user_with_roles),
):
    _require_admin(current_user)
    metrics = await compute_admin_metrics(session)
    return {
        "total_analyses": metrics.total_analyses,
        "completed_analyses": metrics.completed_analyses,
        "finalized_analyses": metrics.finalized_analyses,
        "on_chain_analyses": metrics.on_chain_analyses,
        "ldn_status": {
            "degraded_area_ha": metrics.ldn_status.degraded_area_ha,
            "not_degraded_area_ha": metrics.ldn_status.not_degraded_area_ha,
            "unknown_area_ha": metrics.ldn_status.unknown_area_ha,
            "degraded_units": metrics.ldn_status.degraded_units,
            "not_degraded_units": metrics.ldn_status.not_degraded_units,
            "unknown_units": metrics.ldn_status.unknown_units,
        },
        "indicator_distributions": [
            {
                "indicator": d.indicator.value,
                "min_value": d.min_value,
                "max_value": d.max_value,
                "avg_value": d.avg_value,
                "p25": d.p25,
                "p50": d.p50,
                "p75": d.p75,
            }
            for d in metrics.indicator_distributions
        ],
    }