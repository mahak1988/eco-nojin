"""Persisted science simulation runs (separate from legacy simulation_runs UUID table)."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from apps.shared_core.database.session import Base


class ScienceRun(Base):
    """Phase-3 science persistence — avoids conflict with apps.simulation.runs.models.SimulationRun."""

    __tablename__ = "science_runs"
    __table_args__ = {"extend_existing": True}

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), default="completed", nullable=False)
    params_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    result_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    farm_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


# Back-compat alias for imports
SimulationRun = ScienceRun
