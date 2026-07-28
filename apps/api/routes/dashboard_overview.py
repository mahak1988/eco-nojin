"""Dashboard aggregate — health + science + recent runs (no Docker required)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/overview")
async def dashboard_overview(
    limit_runs: int = Query(8, ge=1, le=30),
    session: AsyncSession = Depends(get_db_session),
) -> dict[str, Any]:
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
        runs = []
        science["runs_error"] = str(e)[:120]

    # last RothC / soil metrics if present in run result JSON
    soil_snapshot: dict[str, Any] = {}
    for r in runs:
        model = str(r.get("model") or "")
        res = r.get("result") or r.get("outputs") or {}
        if isinstance(res, str):
            continue
        if "rothc" in model and not soil_snapshot.get("rothc"):
            soil_snapshot["rothc"] = {
                "soc_final": res.get("soc_final"),
                "delta": res.get("delta"),
                "run_id": r.get("id"),
            }
        if "rusle" in model or "scs" in model:
            soil_snapshot.setdefault("last_hydro_soil", {"model": model, "id": r.get("id")})

    return {
        "ok": True,
        "environment": "local",
        "science": science,
        "runs": runs,
        "runs_count": len(runs),
        "soil_snapshot": soil_snapshot,
        "links": {
            "science": "/science",
            "simulators": "/simulators",
            "rothc": "/simulators/rothc",
        },
    }
