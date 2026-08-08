"""schemas module."""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from typing import Any

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


# ==========================================
# Advanced Settings Schemas (NEW FOR 4.3)
# ==========================================


class AdvancedSettingBase(BaseModel):
    key: str = Field(..., max_length=128)
    value: str
    description: str | None = None
    category: str = Field(..., max_length=64)  # e.g., 'performance', 'security', 'cache'
    is_active: bool | None = True


class AdvancedSettingCreate(AdvancedSettingBase):
    pass


class AdvancedSettingUpdate(BaseModel):
    value: str | None = None
    description: str | None = None
    category: str | None = Field(None, max_length=64)
    is_active: bool | None = None


class AdvancedSettingResponse(AdvancedSettingBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


# ==========================================
# Content Management Schemas (NEW FOR PHASE 2 & 5.2)
# ==========================================


class ContentTypeResponse(BaseModel):
    """Response schema for content types."""

    model_config = ConfigDict(from_attributes=True)

    name: str
    display_name: str
    description: str | None = None
    fields: list[dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ContentItemResponse(BaseModel):
    """Response schema for content items."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    type: str
    title: str
    slug: str
    content: dict[str, Any]
    status: str
    author_id: int
    published_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class ContentCreateRequest(BaseModel):
    """Request schema for creating content items."""

    title: str
    slug: str
    content: dict[str, Any]
    status: str = "draft"


class ContentUpdateRequest(BaseModel):
    """Request schema for updating content items."""

    title: str | None = None
    slug: str | None = None
    content: dict[str, Any] | None = None
    status: str | None = None


class ContentManagementResponse(BaseModel):
    """Response schema for content management operations."""

    content_type: str
    total_items: int
    published_items: int
    draft_items: int
    last_updated: datetime


class ContentVersionResponse(BaseModel):
    """Response schema for content versions."""

    id: int
    version_number: int
    content_id: int
    content_data: dict[str, Any]
    created_by: int
    created_at: datetime
    approved_by: int | None = None
    approved_at: datetime | None = None
    status: str  # draft, pending_approval, approved, rejected


class ContentApprovalResponse(BaseModel):
    """Response schema for content approval."""

    content_id: int
    approved_by: int
    approved_at: datetime
    status: str
    notes: str | None = None


# ==========================================
# Intelligent Features Schemas (NEW FOR PHASE 4 & 5.3)
# ==========================================


class SmartRecommendationResponse(BaseModel):
    """Response schema for smart recommendations."""

    id: str
    title: str
    description: str
    category: str
    priority: str  # 'high', 'medium', 'low'
    action: str  # Action to take


class UserBehaviorAnalysisResponse(BaseModel):
    """Response schema for user behavior analysis."""

    most_active_users: list[dict[str, Any]]
    peak_activity_days: list[tuple]  # (date, count)
    most_common_events: list[tuple]  # (event_type, count)
    total_activities: int
    insights: list[str]


class AdvancedAnalyticsResponse(BaseModel):
    """Response schema for advanced analytics."""

    dashboard_summary: dict[str, Any]
    user_behavior: UserBehaviorAnalysisResponse
    system_health: dict[str, Any]
    active_users_trend: dict[str, Any]
    content_growth: dict[str, Any]
    system_performance: dict[str, Any]
    prediction_insights: dict[str, Any]


class ContentSuggestionResponse(BaseModel):
    """Response schema for AI content suggestions."""

    id: str
    title: str
    description: str
    priority: str  # 'high', 'medium', 'low'
    estimated_effort: str  # 'low', 'medium', 'high'
    potential_impact: str  # 'low', 'medium', 'high'


class IntelligentAlertResponse(BaseModel):
    """Response schema for intelligent alerts."""

    id: str
    type: str  # 'error', 'warning', 'info'
    title: str
    description: str
    severity: str  # 'high', 'medium', 'low'
    timestamp: str
    action_required: bool


class IntelligentAnalyticsResponse(BaseModel):
    """Response schema for intelligent analytics dashboard."""

    summary: dict[str, int]
    recommendations: list[SmartRecommendationResponse]
    alerts: list[IntelligentAlertResponse]
    predictions: dict[str, Any]
    insights: dict[str, list[str]]


class AutoRecommendationResponse(BaseModel):
    """Response schema for automatic AI recommendations."""

    id: str
    title: str
    description: str
    category: str
    priority: str  # 'high', 'medium', 'low'
    confidence: float  # 0.0 to 1.0
    suggested_action: str
    created_at: datetime


class AdvancedAlertResponse(IntelligentAlertResponse):
    """Extended response schema for advanced intelligent alerts."""

    pattern_recognition_score: float
    related_incidents: list[str]
    recommended_resolution: str


# ==========================================
# User Management Schemas (Admin)
# ==========================================


class AdminUserResponse(BaseModel):
    """Response schema for admin user list/detail."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: str | None = None
    phone: str | None = None
    organization: str | None = None
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime


class AdminUserStatusUpdate(BaseModel):
    """Update user active status."""

    is_active: bool


class AdminUserRoleUpdate(BaseModel):
    """Update user role."""

    is_superuser: bool


class AdminUserSearchParams(BaseModel):
    """Search/filter params for admin user list."""

    search: str | None = Field(None, max_length=255)
    role: str | None = Field(None, max_length=40)
    is_active: bool | None = None
    is_superuser: bool | None = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


# ==========================================
# System Health Schemas
# ==========================================


class SystemHealthResponse(BaseModel):
    """System health check response."""

    database: str
    database_latency_ms: float | None = None
    redis: str = "not_configured"
    redis_latency_ms: float | None = None
    uptime_seconds: float | None = None
    total_users: int
    active_users_last_24h: int
    total_api_routes: int
    environment: str
    python_version: str


# ==========================================
# Audit Log Filtering
# ==========================================


class AuditLogFilterParams(BaseModel):
    event_type: str | None = Field(None, max_length=128)
    actor_email: str | None = Field(None, max_length=255)
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)


# ==========================================
# Report Generation
# ==========================================


class ReportGenerateRequest(BaseModel):
    report_name: str = Field(..., max_length=255)
    report_type: str = Field(default="csv", pattern=r"^(csv|json)$")


class ReportGenerateResponse(BaseModel):
    id: int
    report_name: str
    status: str
    message: str
