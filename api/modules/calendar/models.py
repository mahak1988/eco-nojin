from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from api.core.database import Base


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, default="")
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    location = Column(String(200), default="")
    category = Column(String(50), default="general")  # work, personal, meeting, reminder
    is_all_day = Column(Boolean, default=False)
    is_recurring = Column(Boolean, default=False)
    recurrence_rule = Column(String(100), default="")  # RRULE format
    color = Column(String(7), default="#3b82f6")  # hex color
    user_id = Column(String(100), index=True)  # برای چندکاربره در آینده
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    reminders = relationship("EventReminder", back_populates="event", cascade="all, delete-orphan")


class EventReminder(Base):
    __tablename__ = "event_reminders"

    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("calendar_events.id"), nullable=False)
    reminder_time = Column(DateTime(timezone=True), nullable=False)
    method = Column(String(20), default="notification")  # notification, email, sms
    is_sent = Column(Boolean, default=False)

    event = relationship("CalendarEvent", back_populates="reminders")
