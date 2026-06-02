from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import Optional, List
from api.modules.calendar.models import CalendarEvent, EventReminder
from api.modules.calendar.schemas import CalendarEventCreate, CalendarEventUpdate

async def get_events(
    db: AsyncSession,
    user_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[str] = None,
    skip: int = 0,
    limit: int = 50
) -> List[CalendarEvent]:
    query = select(CalendarEvent)
    
    if user_id:
        query = query.where(CalendarEvent.user_id == user_id)
    if start_date:
        query = query.where(CalendarEvent.end_time >= start_date)
    if end_date:
        query = query.where(CalendarEvent.start_time <= end_date)
    if category:
        query = query.where(CalendarEvent.category == category)
    
    query = query.offset(skip).limit(limit).options(selectinload(CalendarEvent.reminders))
    result = await db.execute(query)
    return result.scalars().all()

async def get_event_by_id(db: AsyncSession, event_id: int, user_id: Optional[str] = None) -> Optional[CalendarEvent]:
    query = select(CalendarEvent).where(CalendarEvent.id == event_id)
    if user_id:
        query = query.where(CalendarEvent.user_id == user_id)
    query = query.options(selectinload(CalendarEvent.reminders))
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def create_event(db: AsyncSession, event: CalendarEventCreate, user_id: str) -> CalendarEvent:
    data = event.model_dump(exclude={"reminders"})
    db_event = CalendarEvent(**data, user_id=user_id)
    if event.reminders:
        db_event.reminders = [EventReminder(**r.model_dump()) for r in event.reminders]
    db.add(db_event)
    await db.commit()
    await db.refresh(db_event)
    return db_event

async def update_event(db: AsyncSession, event_id: int, update_data: CalendarEventUpdate, user_id: str) -> Optional[CalendarEvent]:
    event = await get_event_by_id(db, event_id, user_id)
    if not event:
        return None
    update_dict = {k: v for k, v in update_data.model_dump(exclude_unset=True).items() if v is not None}
    for key, value in update_dict.items():
        setattr(event, key, value)
    await db.commit()
    await db.refresh(event)
    return event

async def delete_event(db: AsyncSession, event_id: int, user_id: str) -> bool:
    event = await get_event_by_id(db, event_id, user_id)
    if not event:
        return False
    await db.delete(event)
    await db.commit()
    return True

async def get_upcoming_events(db: AsyncSession, user_id: str, hours: int = 24) -> List[CalendarEvent]:
    now = datetime.utcnow()
    end = now + timedelta(hours=hours)
    return await get_events(db, user_id=user_id, start_date=now, end_date=end, limit=10)
