"""Monitoring API — sensors, readings, alerts + WebSocket fan-out + RBAC on writes."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.monitoring.models import AlertEvent, AlertRule, Sensor, SensorReading
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac import require_permission
from apps.shared_core.schemas.pagination import build_meta, page_to_offset

router = APIRouter(prefix="/api/v1", tags=["Monitoring"])


class SensorIn(BaseModel):
    name: str = Field(..., min_length=1)
    sensor_type: str = Field(..., pattern="^(soil|weather|water|air)$")
    unit: str = "%"
    farm_id: int | None = None
    latitude: float | None = None
    longitude: float | None = None


class SensorOut(SensorIn):
    id: int
    is_active: bool = True

    model_config = {"from_attributes": True}


class ReadingOut(BaseModel):
    id: int
    sensor_id: int
    value: float
    recorded_at: datetime

    model_config = {"from_attributes": True}


class RuleIn(BaseModel):
    name: str
    sensor_type: str
    operator: str = "lt"
    threshold: float
    severity: str = "warning"


class RuleOut(RuleIn):
    id: int
    is_active: bool = True

    model_config = {"from_attributes": True}


async def _broadcast_alert(payload: dict) -> None:
    try:
        from apps.shared_core.websocket.manager import manager

        await manager.broadcast(
            "monitoring",
            {"type": "alert", "channel": "monitoring", **payload},
        )
    except Exception:
        pass


@router.get("/monitoring/overview")
async def monitoring_overview(session: AsyncSession = Depends(get_db_session)):
    sensors = int(
        (
            await session.execute(
                select(func.count()).select_from(Sensor).where(Sensor.is_deleted.is_(False))
            )
        ).scalar_one()
    )
    alerts = int(
        (
            await session.execute(
                select(func.count()).select_from(AlertEvent).where(AlertEvent.is_acked.is_(False))
            )
        ).scalar_one()
    )
    rules = int(
        (
            await session.execute(
                select(func.count()).select_from(AlertRule).where(AlertRule.is_deleted.is_(False))
            )
        ).scalar_one()
    )
    return {
        "sensors_count": sensors,
        "open_alerts": alerts,
        "rules_count": rules,
        "status": "ok",
        "updated_at": datetime.now(UTC).isoformat(),
    }


@router.get("/sensors")
async def list_sensors(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    q = select(Sensor).where(Sensor.is_deleted.is_(False))
    cq = select(func.count()).select_from(Sensor).where(Sensor.is_deleted.is_(False))
    total = int((await session.execute(cq)).scalar_one())
    rows = (
        (
            await session.execute(
                q.order_by(Sensor.id).offset(page_to_offset(page, size)).limit(size)
            )
        )
        .scalars()
        .all()
    )
    return {
        "data": [SensorOut.model_validate(r) for r in rows],
        "meta": build_meta(total, page, size),
    }


@router.post("/sensors", status_code=status.HTTP_201_CREATED)
async def create_sensor(
    body: SensorIn,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("monitoring:write")),
):
    s = Sensor(**body.model_dump())
    session.add(s)
    await session.flush()
    await session.refresh(s)
    return SensorOut.model_validate(s)


@router.get("/sensors/{sensor_id}/readings")
async def sensor_readings(
    sensor_id: int,
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db_session),
):
    rows = (
        (
            await session.execute(
                select(SensorReading)
                .where(SensorReading.sensor_id == sensor_id)
                .order_by(SensorReading.recorded_at.desc())
                .limit(limit)
            )
        )
        .scalars()
        .all()
    )
    return {"data": [ReadingOut.model_validate(r) for r in rows]}


@router.post("/sensors/{sensor_id}/readings", status_code=status.HTTP_201_CREATED)
async def push_reading(
    sensor_id: int,
    value: float = Query(...),
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("monitoring:write")),
):
    s = (
        await session.execute(
            select(Sensor).where(Sensor.id == sensor_id, Sensor.is_deleted.is_(False))
        )
    ).scalar_one_or_none()
    if not s:
        raise HTTPException(404, "Sensor not found")
    reading = SensorReading(sensor_id=sensor_id, value=value)
    session.add(reading)
    rules = (
        (
            await session.execute(
                select(AlertRule).where(
                    AlertRule.is_deleted.is_(False),
                    AlertRule.is_active.is_(True),
                    AlertRule.sensor_type == s.sensor_type,
                )
            )
        )
        .scalars()
        .all()
    )
    fired = []
    for rule in rules:
        ok = False
        if rule.operator == "lt":
            ok = value < rule.threshold
        elif rule.operator == "gt":
            ok = value > rule.threshold
        elif rule.operator == "lte":
            ok = value <= rule.threshold
        elif rule.operator == "gte":
            ok = value >= rule.threshold
        if ok:
            msg = f"{s.name}: {value} {rule.operator} {rule.threshold}"
            ev = AlertEvent(
                rule_id=rule.id,
                sensor_id=sensor_id,
                message=msg,
                severity=rule.severity,
            )
            session.add(ev)
            fired.append(rule.name)
            await _broadcast_alert(
                {
                    "severity": rule.severity,
                    "message": msg,
                    "sensor_id": sensor_id,
                    "rule": rule.name,
                    "value": value,
                    "ts": datetime.now(UTC).isoformat(),
                }
            )
    await session.flush()
    await session.refresh(reading)
    return {"reading": ReadingOut.model_validate(reading), "alerts_fired": fired}


@router.get("/alerts")
async def list_alerts(
    page: int = Query(1, ge=1),
    size: int = Query(50, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session),
):
    q = select(AlertEvent).order_by(AlertEvent.created_at.desc())
    cq = select(func.count()).select_from(AlertEvent)
    total = int((await session.execute(cq)).scalar_one())
    rows = (await session.execute(q.offset(page_to_offset(page, size)).limit(size))).scalars().all()
    return {
        "data": [
            {
                "id": r.id,
                "message": r.message,
                "severity": r.severity,
                "is_acked": r.is_acked,
                "created_at": r.created_at.isoformat() if r.created_at else None,
            }
            for r in rows
        ],
        "meta": build_meta(total, page, size),
    }


@router.post("/alert-rules", status_code=status.HTTP_201_CREATED)
async def create_rule(
    body: RuleIn,
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("monitoring:write")),
):
    rule = AlertRule(**body.model_dump())
    session.add(rule)
    await session.flush()
    await session.refresh(rule)
    return RuleOut.model_validate(rule)


@router.post("/monitoring/seed-demo")
async def seed_monitoring(
    session: AsyncSession = Depends(get_db_session),
    _: object = Depends(require_permission("monitoring:write")),
):
    count = int(
        (
            await session.execute(
                select(func.count()).select_from(Sensor).where(Sensor.is_deleted.is_(False))
            )
        ).scalar_one()
    )
    if count > 0:
        return {"seeded": 0}
    sensors = [
        Sensor(
            name="Soil moisture A", sensor_type="soil", unit="%", latitude=32.65, longitude=51.67
        ),
        Sensor(
            name="Air temp north", sensor_type="weather", unit="C", latitude=32.66, longitude=51.68
        ),
        Sensor(
            name="Reservoir level", sensor_type="water", unit="%", latitude=32.64, longitude=51.66
        ),
    ]
    for s in sensors:
        session.add(s)
    await session.flush()
    now = datetime.utcnow()
    for s in sensors:
        for i in range(12):
            session.add(
                SensorReading(
                    sensor_id=s.id,
                    value=30 + i * 1.5 if s.sensor_type == "soil" else 20 + i,
                    recorded_at=now - timedelta(hours=12 - i),
                )
            )
    session.add(
        AlertRule(
            name="Low soil moisture",
            sensor_type="soil",
            operator="lt",
            threshold=25,
            severity="warning",
        )
    )
    await session.flush()
    return {"seeded": len(sensors)}
