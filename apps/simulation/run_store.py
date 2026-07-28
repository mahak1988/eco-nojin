"""Persist / load simulation runs (sync helpers for Celery + async for API)."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.simulation.models_runs import SimulationRun

logger = logging.getLogger(__name__)


def _sync_engine():
    """Sync engine for Celery workers (asyncpg URL → psycopg/sqlite)."""
    from sqlalchemy import create_engine

    from apps.shared_core.database.session import DATABASE_URL

    url = DATABASE_URL
    if "+asyncpg" in url:
        url = url.replace("postgresql+asyncpg://", "postgresql+psycopg://", 1)
    elif url.startswith("sqlite+aiosqlite://"):
        url = url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    return create_engine(url, pool_pre_ping=True)


def save_run_sync(
    model: str,
    params: dict[str, Any],
    result: dict[str, Any],
    *,
    status: str = "completed",
    task_id: Optional[str] = None,
    farm_id: Optional[int] = None,
) -> int:
    from sqlalchemy.orm import Session

    eng = _sync_engine()
    with Session(eng) as session:
        row = SimulationRun(
            model=model,
            status=status,
            params_json=json.dumps(params, default=str),
            result_json=json.dumps(result, default=str),
            task_id=task_id,
            farm_id=farm_id,
            created_at=datetime.utcnow(),
        )
        session.add(row)
        session.commit()
        session.refresh(row)
        rid = int(row.id)
    eng.dispose()
    return rid


async def save_run_async(
    session: AsyncSession,
    model: str,
    params: dict[str, Any],
    result: dict[str, Any],
    *,
    status: str = "completed",
    task_id: Optional[str] = None,
    farm_id: Optional[int] = None,
) -> SimulationRun:
    row = SimulationRun(
        model=model,
        status=status,
        params_json=json.dumps(params, default=str),
        result_json=json.dumps(result, default=str),
        task_id=task_id,
        farm_id=farm_id,
        created_at=datetime.utcnow(),
    )
    session.add(row)
    await session.flush()
    await session.refresh(row)
    return row


async def get_run(session: AsyncSession, run_id: int) -> Optional[SimulationRun]:
    r = await session.execute(select(SimulationRun).where(SimulationRun.id == run_id))
    return r.scalar_one_or_none()


async def list_runs(
    session: AsyncSession,
    *,
    model: Optional[str] = None,
    farm_id: Optional[int] = None,
    limit: int = 50,
) -> list[SimulationRun]:
    q = select(SimulationRun).order_by(SimulationRun.id.desc()).limit(limit)
    if model:
        q = q.where(SimulationRun.model == model)
    if farm_id is not None:
        q = q.where(SimulationRun.farm_id == farm_id)
    return list((await session.execute(q)).scalars().all())


def run_to_dict(row: SimulationRun) -> dict[str, Any]:
    return {
        "id": row.id,
        "model": row.model,
        "status": row.status,
        "task_id": row.task_id,
        "farm_id": row.farm_id,
        "params": json.loads(row.params_json) if row.params_json else None,
        "result": json.loads(row.result_json) if row.result_json else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }
