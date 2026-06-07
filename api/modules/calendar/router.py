from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.core.database import get_db
from api.core.deps import require_write_auth
from api.modules.calendar import crud, models, schemas

router = APIRouter(tags=["Calendar"])


@router.get("/", response_model=schemas.EventListResponse)
async def list_events(
    start_date: Optional[datetime] = Query(None, description="Start of date range"),
    end_date: Optional[datetime] = Query(None, description="End of date range"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    user_id: str = "demo_user",  # Placeholder for auth
):
    events = await crud.get_events(
        db,
        user_id=user_id,
        start_date=start_date,
        end_date=end_date,
        category=category,
        skip=skip,
        limit=limit,
    )
    total = len(events)  # In production, use a count query
    return schemas.EventListResponse(items=events, total=total, page=skip // limit + 1, limit=limit)


@router.get("/{event_id}", response_model=schemas.CalendarEvent)
async def get_event(event_id: int, db: AsyncSession = Depends(get_db), user_id: str = "demo_user"):
    event = await crud.get_event_by_id(db, event_id, user_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.post("/", response_model=schemas.CalendarEvent, status_code=201)
async def create_event(
    event: schemas.CalendarEventCreate,
    db: AsyncSession = Depends(get_db),
    auth_user: str = Depends(require_write_auth),
    user_id: str = "demo_user",
):
    user_id = auth_user
    return await crud.create_event(db, event, user_id)


@router.put("/{event_id}", response_model=schemas.CalendarEvent)
async def update_event(
    event_id: int,
    event_update: schemas.CalendarEventUpdate,
    db: AsyncSession = Depends(get_db),
    auth_user: str = Depends(require_write_auth),
    user_id: str = "demo_user",
):
    user_id = auth_user
    updated = await crud.update_event(db, event_id, event_update, user_id)
    if not updated:
        raise HTTPException(status_code=404, detail="Event not found")
    return updated


@router.delete("/{event_id}", response_model=IDResponse)
async def delete_event(
    event_id: int,
    db: AsyncSession = Depends(get_db),
    auth_user: str = Depends(require_write_auth),
    user_id: str = "demo_user",
):
    user_id = auth_user
    success = await crud.delete_event(db, event_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"message": "Event deleted successfully"}


@router.get("/upcoming", response_model=List[schemas.CalendarEvent])
async def get_upcoming(
    hours: int = Query(24, ge=1, le=168),
    db: AsyncSession = Depends(get_db),
    user_id: str = "demo_user",
):
    return await crud.get_upcoming_events(db, user_id, hours)
