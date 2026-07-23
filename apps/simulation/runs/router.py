"""
Saved Runs Router — save / list / fetch / delete simulation runs.
"""
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.simulation.runs.models import SimulationRun


async def _ensure_table(db: AsyncSession):
    """Idempotently create the simulation_runs table on first use."""
    try:
        from apps.simulation.runs.models import SimulationRun
        bind = db.get_bind()
        async with bind.begin() as conn:
            await conn.run_sync(SimulationRun.metadata.create_all)
    except Exception:
        pass


router = APIRouter(prefix="/api/v1/simulation/runs", tags=["💾 Saved Runs"])


class RunCreate(BaseModel):
    simulator_id: str
    simulator_name: str = ""
    parameters: dict = Field(default_factory=dict)
    metrics: dict = Field(default_factory=dict)
    advisory: dict = Field(default_factory=dict)
    scenario_name: Optional[str] = None
    note: Optional[str] = Field(default=None, max_length=1000)
    user_id: Optional[str] = None


def _to_dict(r: SimulationRun) -> dict:
    return {
        "id": r.id, "user_id": r.user_id, "simulator_id": r.simulator_id,
        "simulator_name": r.simulator_name, "parameters": r.parameters,
        "metrics": r.metrics, "advisory": r.advisory,
        "scenario_name": r.scenario_name, "note": r.note,
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }


@router.post("", summary="Save a simulation run to the dashboard")
async def save_run(data: RunCreate, db: AsyncSession = Depends(get_db_session)):
    await _ensure_table(db)
    run = SimulationRun(
        id=str(uuid.uuid4()),
        user_id=data.user_id,
        simulator_id=data.simulator_id,
        simulator_name=data.simulator_name,
        parameters=data.parameters,
        metrics=data.metrics,
        advisory=data.advisory,
        scenario_name=data.scenario_name,
        note=data.note,
        created_at=datetime.utcnow(),
    )
    db.add(run)
    await db.commit()
    return {"id": run.id, "status": "saved"}


@router.get("", summary="List saved runs (newest first)")
async def list_runs(
    simulator_id: Optional[str] = Query(None),
    user_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db_session),
):
    q = select(SimulationRun).order_by(desc(SimulationRun.created_at)).limit(limit)
    if simulator_id:
        q = q.where(SimulationRun.simulator_id == simulator_id)
    if user_id:
        q = q.where(SimulationRun.user_id == user_id)
    result = await db.execute(q)
    runs = result.scalars().all()
    return {"total": len(runs), "runs": [_to_dict(r) for r in runs]}


@router.get("/{run_id}", summary="Get one saved run")
async def get_run(run_id: str, db: AsyncSession = Depends(get_db_session)):
    await _ensure_table(db)
    run = await db.get(SimulationRun, run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    return _to_dict(run)


@router.delete("/{run_id}", summary="Delete a saved run")
async def delete_run(run_id: str, db: AsyncSession = Depends(get_db_session)):
    await _ensure_table(db)
    run = await db.get(SimulationRun, run_id)
    if not run:
        raise HTTPException(404, "Run not found")
    await db.delete(run)
    await db.commit()
    return {"status": "deleted", "id": run_id}
