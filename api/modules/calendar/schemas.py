from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional, List

class EventReminderCreate(BaseModel):
    reminder_time: datetime
    method: str = "notification"

class EventReminder(EventReminderCreate):
    id: int
    is_sent: bool
    event_id: int
    
    class Config:
        from_attributes = True

class CalendarEventCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: str = ""
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    category: str = "general"
    is_all_day: bool = False
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    color: str = "#3b82f6"
    reminders: Optional[List[EventReminderCreate]] = None
    
    @field_validator("end_time")
    @classmethod
    def end_after_start(cls, v, info):
        start = info.data.get("start_time")
        if start and v <= start:
            raise ValueError("end_time must be after start_time")
        return v

class CalendarEvent(CalendarEventCreate):
    id: int
    user_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    reminders: List[EventReminder] = []
    
    class Config:
        from_attributes = True

class CalendarEventUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    location: Optional[str] = None
    category: Optional[str] = None
    is_all_day: Optional[bool] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    color: Optional[str] = None

class EventListResponse(BaseModel):
    items: List[CalendarEvent]
    total: int
    page: int = 1
    limit: int = 50
