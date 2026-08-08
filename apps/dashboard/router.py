"""Dashboard aggregates — single source for /overview and /stats."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


async def _counts(session: AsyncSession) -> dict[str, int]:
    out = {"farms": 0, "crops": 0, "sensors": 0, "courses": 0}
    try:
        from apps.farms.models import Farm

        out["farms"] = int(
            (
                await session.execute(
                    select(func.count()).select_from(Farm).where(Farm.is_deleted.is_(False))
                )
            ).scalar_one()
        )
    except Exception:
        pass
    try:
        from apps.crops.models import Crop

        out["crops"] = int(
            (
                await session.execute(
                    select(func.count()).select_from(Crop).where(Crop.is_deleted.is_(False))
                )
            ).scalar_one()
        )
    except Exception:
        pass
    try:
        from apps.monitoring.models import Sensor

        out["sensors"] = int(
            (
                await session.execute(
                    select(func.count()).select_from(Sensor).where(Sensor.is_deleted.is_(False))
                )
            ).scalar_one()
        )
    except Exception:
        pass
    try:
        from apps.education.models import Course

        out["courses"] = int(
            (await session.execute(select(func.count()).select_from(Course))).scalar_one()
        )
    except Exception:
        pass
    return out


@router.get("/stats")
async def dashboard_stats(session: AsyncSession = Depends(get_db_session)) -> dict[str, Any]:
    c = await _counts(session)
    return {
        "ok": True,
        "farms_count": c["farms"],
        "crops_count": c["crops"],
        "sensors_count": c["sensors"],
        "courses_count": c["courses"],
        "alerts_open": 0,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "updated_at": datetime.now(UTC).isoformat(),
        "status": "ok",
    }


@router.get("/overview")
async def dashboard_overview(
    limit_runs: int = Query(8, ge=1, le=30),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    c = await _counts(session)
    science: dict[str, Any] = {"ok": False}
    try:
        from apps.api.routes.science import science_status

        science = await science_status()
    except Exception as e:
        science = {"ok": False, "error": str(e)[:120]}

    runs: list[dict[str, Any]] = []
    try:
        from apps.simulation.run_store import list_runs, run_to_dict

        rows = await list_runs(session, limit=limit_runs)
        runs = [run_to_dict(r) for r in rows]
    except Exception as e:
        science["runs_error"] = str(e)[:120]

    return {
        "ok": True,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION,
        "counts": c,
        "farms_count": c["farms"],
        "crops_count": c["crops"],
        "sensors_count": c["sensors"],
        "science": science,
        "runs": runs,
        "runs_count": len(runs),
        "updated_at": datetime.now(UTC).isoformat(),
        "links": {
            "science": "/science",
            "simulators": "/simulators",
            "farms": "/farms",
            "docs": "/docs",
        },
        "status": "ok",
    }
