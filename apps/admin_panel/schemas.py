"""schemas module."""

import logging

logger = logging.getLogger(__name__)
from datetime import datetime
from typing import Optional, Dict, Any, List

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


# ==========================================
# Advanced Settings Schemas (NEW FOR 4.3)
# ==========================================

class AdvancedSettingBase(BaseModel):
    key: str = Field(..., max_length=128)
    value: str
    description: Optional[str] = None
    category: str = Field(..., max_length=64)  # e.g., 'performance', 'security', 'cache'
    is_active: Optional[bool] = True


class AdvancedSettingCreate(AdvancedSettingBase):
    pass


class AdvancedSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = Field(None, max_length=64)
    is_active: Optional[bool] = None


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
    description: Optional[str] = None
    fields: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime


class ContentItemResponse(BaseModel):
    """Response schema for content items."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    type: str
    title: str
    slug: str
    content: Dict[str, Any]
    status: str
    author_id: int
    published_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ContentCreateRequest(BaseModel):
    """Request schema for creating content items."""
    title: str
    slug: str
    content: Dict[str, Any]
    status: str = "draft"


class ContentUpdateRequest(BaseModel):
    """Request schema for updating content items."""
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[Dict[str, Any]] = None
    status: Optional[str] = None


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
    content_data: Dict[str, Any]
    created_by: int
    created_at: datetime
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    status: str  # draft, pending_approval, approved, rejected


class ContentApprovalResponse(BaseModel):
    """Response schema for content approval."""
    content_id: int
    approved_by: int
    approved_at: datetime
    status: str
    notes: Optional[str] = None


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
    most_active_users: List[Dict[str, Any]]
    peak_activity_days: List[tuple]  # (date, count)
    most_common_events: List[tuple]  # (event_type, count)
    total_activities: int
    insights: List[str]


class AdvancedAnalyticsResponse(BaseModel):
    """Response schema for advanced analytics."""
    dashboard_summary: Dict[str, Any]
    user_behavior: UserBehaviorAnalysisResponse
    system_health: Dict[str, Any]
    active_users_trend: Dict[str, Any]
    content_growth: Dict[str, Any]
    system_performance: Dict[str, Any]
    prediction_insights: Dict[str, Any]


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
    summary: Dict[str, int]
    recommendations: List[SmartRecommendationResponse]
    alerts: List[IntelligentAlertResponse]
    predictions: Dict[str, Any]
    insights: Dict[str, List[str]]


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
    related_incidents: List[str]
    recommended_resolution: str


# ==========================================
# User Management Schemas (Admin)
# ==========================================

class AdminUserResponse(BaseModel):
    """Response schema for admin user list/detail."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    organization: Optional[str] = None
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
    search: Optional[str] = Field(None, max_length=255)
    role: Optional[str] = Field(None, max_length=40)
    is_active: Optional[bool] = None
    is_superuser: Optional[bool] = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


# ==========================================
# System Health Schemas
# ==========================================

class SystemHealthResponse(BaseModel):
    """System health check response."""
    database: str
    database_latency_ms: Optional[float] = None
    redis: str = "not_configured"
    redis_latency_ms: Optional[float] = None
    uptime_seconds: Optional[float] = None
    total_users: int
    active_users_last_24h: int
    total_api_routes: int
    environment: str
    python_version: str


# ==========================================
# Audit Log Filtering
# ==========================================

class AuditLogFilterParams(BaseModel):
    event_type: Optional[str] = Field(None, max_length=128)
    actor_email: Optional[str] = Field(None, max_length=255)
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
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