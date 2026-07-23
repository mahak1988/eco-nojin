"""
SimulationRun model — persists a simulation execution with its metrics,
advisory (analysis/recommendations/scenarios) and an optional user note.
Uses the project's shared Base so init_db's create_all builds it automatically.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Text, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

# resolve the project's declarative Base (fallback to a local one)
try:
    from apps.shared_core.database.base import Base
except Exception:
    try:
        from apps.shared_core.database.session import Base
    except Exception:
        from sqlalchemy.orm import DeclarativeBase

        class Base(DeclarativeBase):
            pass


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True, index=True)
    simulator_id: Mapped[str] = mapped_column(String(50), index=True)
    simulator_name: Mapped[str] = mapped_column(String(200), default="")
    parameters: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    advisory: Mapped[dict] = mapped_column(JSON, default=dict)
    scenario_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
