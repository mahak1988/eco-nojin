"""schemas module."""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AdminSettingBase(BaseModel):
    key: str = Field(..., max_length=128)
    value: str
    description: str | None = None
    is_active: bool | None = True


class AdminSettingCreate(AdminSettingBase):
    pass


class AdminSettingUpdate(BaseModel):
    value: str | None = None
    description: str | None = None
    is_active: bool | None = None


class AdminSettingResponse(AdminSettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: int | None
    actor_email: str | None
    event_type: str
    event_data: str | None = None
    created_at: datetime


class SystemReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_name: str
    status: str
    report_data: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class AdminDashboardResponse(BaseModel):
    user_count: int
    active_user_count: int
    superuser_count: int
    total_settings: int
    total_audit_logs: int
    total_reports: int
