"""Legacy path — redirects shape to science-focused overview (avoid duplicate /overview).

Canonical dashboard lives in apps.dashboard.router.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/science-overview")
async def science_dashboard_overview(
    limit_runs: int = Query(8, ge=1, le=30),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
    """Science-centric view (runs + soil). Prefer /api/v1/dashboard/overview for FE."""
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
        "science": science,
        "runs": runs,
        "runs_count": len(runs),
        "canonical": "/api/v1/dashboard/overview",
    }
