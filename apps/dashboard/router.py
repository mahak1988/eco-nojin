"""Dashboard overview aggregates."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session

router = APIRouter(prefix="/api/v1/dashboard", tags=["Dashboard"])


@router.get("/overview")
@router.get("/stats")
async def overview(session: AsyncSession = Depends(get_db_session)):
    farms = crops = sensors = 0
    try:
        from apps.farms.models import Farm

        farms = int(
            (await session.execute(select(func.count()).select_from(Farm).where(Farm.is_deleted.is_(False)))).scalar_one()
        )
    except Exception:
        pass
    try:
        from apps.crops.models import Crop

        crops = int(
            (await session.execute(select(func.count()).select_from(Crop).where(Crop.is_deleted.is_(False)))).scalar_one()
        )
    except Exception:
        pass
    try:
        from apps.monitoring.models import Sensor

        sensors = int(
            (await session.execute(select(func.count()).select_from(Sensor).where(Sensor.is_deleted.is_(False)))).scalar_one()
        )
    except Exception:
        pass

    return {
        "farms_count": farms,
        "crops_count": crops,
        "sensors_count": sensors,
        "alerts_open": 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "status": "ok",
    }
