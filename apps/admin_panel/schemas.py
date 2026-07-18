from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AdminSettingBase(BaseModel):
    key: str = Field(..., max_length=128)
    value: str
    description: Optional[str] = None
    is_active: Optional[bool] = True


class AdminSettingCreate(AdminSettingBase):
    pass


class AdminSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class AdminSettingResponse(AdminSettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    actor_id: Optional[int]
    actor_email: Optional[str]
    event_type: str
    event_data: Optional[str] = None
    created_at: datetime


class SystemReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    report_name: str
    status: str
    report_data: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class AdminDashboardResponse(BaseModel):
    user_count: int
    active_user_count: int
    superuser_count: int
    total_settings: int
    total_audit_logs: int
    total_reports: int
