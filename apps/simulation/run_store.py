"""Persist / load science runs."""

from __future__ import annotations

import json
import logging
from typing import Any, Optional

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.timeutil import utc_now
from apps.simulation.models_runs import ScienceRun

logger = logging.getLogger(__name__)

_DDL = """
CREATE TABLE IF NOT EXISTS science_runs (
    id SERIAL PRIMARY KEY,
    model VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'completed',
    params_json TEXT,
    result_json TEXT,
    task_id VARCHAR(128),
    farm_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

_DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS science_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model VARCHAR(64) NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'completed',
    params_json TEXT,
    result_json TEXT,
    task_id VARCHAR(128),
    farm_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


async def ensure_science_runs_table(session: AsyncSession) -> None:
    bind = session.get_bind()
    dialect = bind.dialect.name if bind is not None else "sqlite"
    ddl = _DDL if dialect == "postgresql" else _DDL_SQLITE
    await session.execute(text(ddl))
    await session.commit()


def _sync_engine():
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
    with eng.begin() as conn:
        dialect = eng.dialect.name
        conn.execute(text(_DDL if dialect == "postgresql" else _DDL_SQLITE))
    with Session(eng) as session:
        row = ScienceRun(
            model=model,
            status=status,
            params_json=json.dumps(params, default=str),
            result_json=json.dumps(result, default=str),
            task_id=task_id,
            farm_id=farm_id,
            created_at=utc_now(),
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
) -> ScienceRun:
    try:
        await ensure_science_runs_table(session)
    except Exception as e:
        logger.debug("ensure table: %s", e)
    row = ScienceRun(
        model=model,
        status=status,
        params_json=json.dumps(params, default=str),
        result_json=json.dumps(result, default=str),
        task_id=task_id,
        farm_id=farm_id,
        created_at=utc_now(),
    )
    session.add(row)
    await session.commit()
    await session.refresh(row)
    return row


async def get_run(session: AsyncSession, run_id: int) -> Optional[ScienceRun]:
    r = await session.execute(select(ScienceRun).where(ScienceRun.id == run_id))
    return r.scalar_one_or_none()


async def list_runs(
    session: AsyncSession,
    *,
    model: Optional[str] = None,
    farm_id: Optional[int] = None,
    limit: int = 50,
) -> list[ScienceRun]:
    try:
        await ensure_science_runs_table(session)
    except Exception:
        pass
    q = select(ScienceRun).order_by(ScienceRun.id.desc()).limit(limit)
    if model:
        q = q.where(ScienceRun.model == model)
    if farm_id is not None:
        q = q.where(ScienceRun.farm_id == farm_id)
    return list((await session.execute(q)).scalars().all())


def run_to_dict(row: ScienceRun) -> dict[str, Any]:
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
