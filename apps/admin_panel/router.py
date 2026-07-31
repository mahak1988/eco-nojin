from __future__ import annotations
from sqlalchemy.ext.asyncio import AsyncSession
from apps.shared_core.database.session import get_db_session
from apps.shared_core.database.session import get_db_session

"""Admin panel API."""







import logging

import time

from datetime import datetime

from typing import TYPE_CHECKING, Annotated, Optional



from fastapi import APIRouter, Depends, HTTPException, Query, status



from apps.admin_panel.schemas import (

    AdminDashboardResponse,

    AdminSettingResponse,

    AdminSettingUpdate,

    AdminUserResponse,

    AdminUserRoleUpdate,

    AdminUserSearchParams,

    AdminUserStatusUpdate,

    AuditLogFilterParams,

    AuditLogResponse,

    ReportGenerateRequest,

    ReportGenerateResponse,

    SystemHealthResponse,

    SystemReportResponse,

    # New content management schemas

    ContentTypeResponse,

    ContentItemResponse,

    ContentCreateRequest,

    ContentUpdateRequest,

    # New AI and analytics schemas

    SmartRecommendationResponse,

    UserBehaviorAnalysisResponse,

    AdvancedAnalyticsResponse,

    ContentSuggestionResponse,

    IntelligentAlertResponse,

    # Advanced settings schemas

    AdvancedSettingResponse,

    AdvancedSettingUpdate,

    AdvancedSettingCreate,

    # Content management schemas

    ContentManagementResponse,

    ContentVersionResponse,

    ContentApprovalResponse,

    # Intelligent analytics schemas

    IntelligentAnalyticsResponse,

    AutoRecommendationResponse,

    AdvancedAlertResponse

)

from apps.admin_panel.service import AdminService

from apps.users.dependencies import get_current_active_superuser



if TYPE_CHECKING:

    from sqlalchemy.ext.asyncio import AsyncSession



    from apps.users.models import User



logger = logging.getLogger(__name__)



router = APIRouter(prefix="/admin", tags=["Admin"])



DBSessionDependency = Depends(get_db_session)

CurrentSuperuser = Annotated["User", Depends(get_current_active_superuser)]



# Import RBAC utilities after defining basic types to avoid circular imports
from apps.admin_panel.middleware.rbac import require_permission, require_any_permission



async def get_admin_service(

    session: Annotated["AsyncSession", DBSessionDependency],

) -> AdminService:

    return AdminService(session)





AdminServiceDependency = Annotated[AdminService, Depends(get_admin_service)]



# ==========================================

# Dashboard

# ==========================================



@router.get("/", response_model=AdminDashboardResponse)

@require_permission("dashboard.view")

async def admin_dashboard(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    return await admin_service.get_dashboard_summary()



# ==========================================

# System Settings

# ==========================================



@router.get("/settings", response_model=list[AdminSettingResponse])

@require_permission("settings.read")

async def list_system_settings(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

    limit: int = 100,

    offset: int = 0,

):

    settings_list = await admin_service.get_system_settings(limit=limit, offset=offset)

    return [AdminSettingResponse.model_validate(s) for s in settings_list]



@router.put("/settings/{key}", response_model=AdminSettingResponse)

@require_permission("settings.write")

async def upsert_system_setting(

    key: str,

    payload: AdminSettingUpdate,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    if not any(

        [

            payload.value is not None,

            payload.description is not None,

            payload.is_active is not None,

        ]

    ):

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="At least one of value, description, is_active required",

        )

    setting = await admin_service.upsert_system_setting(

        key=key,

        value=payload.value,

        description=payload.description,

        is_active=payload.is_active,

    )

    return AdminSettingResponse.model_validate(setting)



# ==========================================

# Advanced Settings (NEW FOR PHASE 4.3)

# ==========================================



@router.get("/advanced-settings", response_model=list[AdvancedSettingResponse])

@require_permission("advanced_settings.read")

async def list_advanced_settings(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

    limit: int = 100,

    offset: int = 0,

):

    """List all advanced system settings."""

    # In a real implementation, this would fetch from a dedicated advanced settings table

    # For now, returning mock data

    mock_settings = [

        {

            "id": 1,

            "key": "cache_ttl",

            "value": "300",

            "description": "زمان انقضا کش (ثانیه)",

            "category": "performance",

            "is_active": True,

            "created_at": datetime.utcnow(),

            "updated_at": datetime.utcnow()

        },

        {

            "id": 2,

            "key": "max_upload_size",

            "value": "10485760",  # 10MB

            "description": "حداکثر اندازه آپلود (بایت)",

            "category": "security",

            "is_active": True,

            "created_at": datetime.utcnow(),

            "updated_at": datetime.utcnow()

        },

        {

            "id": 3,

            "key": "rate_limit_requests",

            "value": "100",

            "description": "محدودیت درخواست در دقیقه",

            "category": "security",

            "is_active": True,

            "created_at": datetime.utcnow(),

            "updated_at": datetime.utcnow()

        }

    ]

    return [AdvancedSettingResponse.model_validate(s) for s in mock_settings[:limit]]



@router.put("/advanced-settings/{key}", response_model=AdvancedSettingResponse)

@require_permission("advanced_settings.write")

async def upsert_advanced_setting(

    key: str,

    payload: AdvancedSettingUpdate,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Update or create an advanced system setting."""

    # In a real implementation, this would interact with a dedicated advanced settings table

    # For now, returning mock data

    mock_setting = {

        "id": 1,

        "key": key,

        "value": payload.value,

        "description": payload.description,

        "category": payload.category,

        "is_active": payload.is_active,

        "created_at": datetime.utcnow(),

        "updated_at": datetime.utcnow()

    }

    return AdvancedSettingResponse.model_validate(mock_setting)



# ==========================================

# Content Management (NEW FOR PHASE 2 & 5.2)

# ==========================================



@router.get("/content/types", response_model=list[ContentTypeResponse])

@require_permission("content.types.read")

async def list_content_types(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """List all available content types in the system."""

    content_types = await admin_service.get_content_types()

    return [ContentTypeResponse.model_validate(ct) for ct in content_types]



@router.get("/content/{content_type}", response_model=list[ContentItemResponse])

@require_permission("content.items.read")

async def list_content_items(

    content_type: str,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

    search: Optional[str] = None,

    status: Optional[str] = None,

    limit: int = Query(default=20, le=100),

    offset: int = 0,

):

    """List content items of a specific type."""

    content_items = await admin_service.get_content_items_by_type(

        content_type=content_type,

        search=search,

        status=status,

        limit=limit,

        offset=offset

    )

    return [ContentItemResponse.model_validate(ci) for ci in content_items]



@router.post("/content/{content_type}", response_model=ContentItemResponse, status_code=status.HTTP_201_CREATED)

@require_permission("content.items.create")

async def create_content_item(

    content_type: str,

    payload: ContentCreateRequest,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Create a new content item of specified type."""

    content_item = await admin_service.create_content_item(

        content_type=content_type,

        data=payload.data,

        author_id=current_user.id

    )

    # Sync content to other modules

    await admin_service.sync_content_to_modules(content_item, content_type, 'create')

    return ContentItemResponse.model_validate(content_item)



@router.get("/content/{content_type}/{item_id}", response_model=ContentItemResponse)

@require_permission("content.items.read")

async def get_content_item(

    content_type: str,

    item_id: int,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get details of a specific content item."""

    content_item = await admin_service.get_content_item_by_id(

        content_type=content_type,

        item_id=item_id

    )

    if not content_item:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"Content item not found: {content_type}/{item_id}"

        )

    return ContentItemResponse.model_validate(content_item)



@router.put("/content/{content_type}/{item_id}", response_model=ContentItemResponse)

@require_permission("content.items.update")

async def update_content_item(

    content_type: str,

    item_id: int,

    payload: ContentUpdateRequest,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Update an existing content item."""

    content_item = await admin_service.update_content_item(

        content_type=content_type,

        item_id=item_id,

        data=payload.data,

        updated_by_id=current_user.id

    )

    if not content_item:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"Content item not found: {content_type}/{item_id}"

        )

    # Sync content to other modules

    await admin_service.sync_content_to_modules(content_item, content_type, 'update')

    return ContentItemResponse.model_validate(content_item)



@router.delete("/content/{content_type}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)

@require_permission("content.items.delete")

async def delete_content_item(

    content_type: str,

    item_id: int,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Delete a content item."""

    success = await admin_service.delete_content_item(

        content_type=content_type,

        item_id=item_id

    )

    if not success:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail=f"Content item not found: {content_type}/{item_id}"

        )

    # Sync content deletion to other modules

    await admin_service.sync_content_to_modules(None, content_type, 'delete', item_id)

    

    

# ==========================================

# Content Versioning and Approval (NEW FOR 5.2)

# ==========================================



@router.get("/content/{content_type}/{item_id}/versions", response_model=list[ContentVersionResponse])

@require_permission("content.versions.read")

async def get_content_versions(

    content_type: str,

    item_id: int,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get all versions of a content item."""

    # In a real implementation, this would fetch from a version history table

    # For now, returning mock data

    mock_versions = [

        {

            "id": 1,

            "version_number": 1,

            "content_id": item_id,

            "content_data": {"title": "عنوان اولیه", "content": "محتوای اولیه"},

            "created_by": current_user.id,

            "created_at": datetime.utcnow(),

            "approved_by": None,

            "approved_at": None,

            "status": "draft"

        },

        {

            "id": 2,

            "version_number": 2,

            "content_id": item_id,

            "content_data": {"title": "عنوان ویرایش شده", "content": "محتوای ویرایش شده"},

            "created_by": current_user.id,

            "created_at": datetime.utcnow(),

            "approved_by": current_user.id,

            "approved_at": datetime.utcnow(),

            "status": "approved"

        }

    ]

    return [ContentVersionResponse.model_validate(v) for v in mock_versions]



@router.post("/content/{content_type}/{item_id}/approve", response_model=ContentApprovalResponse)

@require_permission("content.approval.manage")

async def approve_content(

    content_type: str,

    item_id: int,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Approve a content item for publication."""

    # In a real implementation, this would update the approval status

    # For now, returning mock data

    approval_data = {

        "content_id": item_id,

        "approved_by": current_user.id,

        "approved_at": datetime.utcnow(),

        "status": "approved",

        "notes": "محتوا تأیید شد"

    }

    return ContentApprovalResponse.model_validate(approval_data)

    

    

# ==========================================

# Intelligent Features - AI Powered Recommendations (NEW FOR PHASE 4 & 5.3)

# ==========================================



@router.get("/smart-recommendations", response_model=list[SmartRecommendationResponse])

@require_permission("recommendations.view")

async def get_smart_recommendations(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get intelligent recommendations for optimal settings and optimizations."""

    recommendations = await admin_service.get_smart_recommendations(current_user.id)

    return [SmartRecommendationResponse.model_validate(rec) for rec in recommendations]



@router.get("/user-behavior-analysis", response_model=UserBehaviorAnalysisResponse)

@require_permission("analytics.behavior.view")

async def get_user_behavior_analysis(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get analysis of user behavior patterns to suggest optimizations."""

    analysis = await admin_service.analyze_user_behavior()

    return UserBehaviorAnalysisResponse.model_validate(analysis)



# ==========================================

# Advanced Analytics and Reporting (NEW FOR PHASE 4 & 5.3)

# ==========================================



@router.get("/advanced-analytics", response_model=AdvancedAnalyticsResponse)

@require_permission("analytics.advanced.view")

async def get_advanced_analytics(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get advanced analytics dashboard with predictive insights."""

    analytics = await admin_service.get_advanced_analytics()

    return AdvancedAnalyticsResponse.model_validate(analytics)



@router.get("/content-suggestions/{content_type}", response_model=list[ContentSuggestionResponse])

@require_permission("content.suggestions.view")

async def get_ai_content_suggestions(

    content_type: str,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get AI-generated content suggestions for a specific content type."""

    suggestions = await admin_service.get_ai_content_suggestions(content_type)

    return [ContentSuggestionResponse.model_validate(sug) for sug in suggestions]



@router.get("/intelligent-alerts", response_model=list[IntelligentAlertResponse])

@require_permission("alerts.intelligent.view")

async def get_intelligent_alerts(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get intelligent alerts based on system patterns and anomalies."""

    alerts = await admin_service.get_intelligent_alerts()

    return [IntelligentAlertResponse.model_validate(alert) for alert in alerts]

    

    

# ==========================================

# Intelligent Analytics Dashboard (NEW FOR 5.3)

# ==========================================



@router.get("/intelligent-analytics", response_model=IntelligentAnalyticsResponse)

@require_permission("analytics.intelligent.view")

async def get_intelligent_analytics(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get intelligent analytics dashboard with AI insights."""

    # In a real implementation, this would fetch from AI analytics services

    # For now, returning mock data

    mock_analytics = {

        "summary": {

            "total_recommendations": 5,

            "active_alerts": 3,

            "predicted_improvements": 12

        },

        "recommendations": await admin_service.get_smart_recommendations(current_user.id),

        "alerts": await admin_service.get_intelligent_alerts(),

        "predictions": {

            "user_growth_prediction": "+15% next month",

            "resource_utilization": "75% capacity",

            "performance_trends": "improving"

        },

        "insights": {

            "top_performing_content": ["مقاله ۱", "مقاله ۲"],

            "underperforming_areas": ["بخش تماس", "درباره ما"],

            "optimization_opportunities": ["بهینه سازی تصاویر", "کش گذاری"]

        }

    }

    return IntelligentAnalyticsResponse.model_validate(mock_analytics)

    

    

# ==========================================

# Auto Recommendations (NEW FOR 5.3)

# ==========================================



@router.get("/auto-recommendations", response_model=list[AutoRecommendationResponse])

@require_permission("recommendations.auto.view")

async def get_auto_recommendations(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get automatic recommendations based on AI analysis."""

    # In a real implementation, this would fetch from AI recommendation engine

    # For now, returning mock data

    mock_recommendations = [

        {

            "id": "rec_001",

            "title": "بهینه سازی عملکرد پایگاه داده",

            "description": "تحلیل هوشمند نشان می‌دهد که عملکرد پایگاه داده نیاز به بهینه سازی دارد",

            "category": "performance",

            "priority": "high",

            "confidence": 0.92,

            "suggested_action": "index_optimization",

            "created_at": datetime.utcnow()

        },

        {

            "id": "rec_002",

            "title": "افزایش امنیت سیستم",

            "description": "شناسایی نقاط ضعف امنیتی که نیاز به توجه دارند",

            "category": "security",

            "priority": "medium",

            "confidence": 0.78,

            "suggested_action": "security_audit",

            "created_at": datetime.utcnow()

        }

    ]

    return [AutoRecommendationResponse.model_validate(rec) for rec in mock_recommendations]

    

    

# ==========================================

# Advanced Alerts (NEW FOR 5.3)

# ==========================================



@router.get("/advanced-alerts", response_model=list[AdvancedAlertResponse])

@require_permission("alerts.advanced.view")

async def get_advanced_alerts(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get advanced intelligent alerts based on pattern recognition."""

    # In a real implementation, this would fetch from AI alert system

    # For now, returning mock data based on intelligent alerts

    base_alerts = await admin_service.get_intelligent_alerts()

    mock_advanced_alerts = []

    for alert in base_alerts:

        mock_advanced_alerts.append({

            "id": f"adv_{alert['id']}",

            "type": alert["type"],

            "title": alert["title"],

            "description": alert["description"],

            "severity": alert["severity"],

            "timestamp": alert["timestamp"],

            "action_required": alert["action_required"],

            "pattern_recognition_score": 0.85,

            "related_incidents": ["incident_001", "incident_002"],

            "recommended_resolution": "Follow standard procedures"

        })

    return [AdvancedAlertResponse.model_validate(alert) for alert in mock_advanced_alerts]

    

    

# ==========================================

# Audit Logs (Enhanced)

# ==========================================



@router.get("/audit-logs", response_model=list[AuditLogResponse])

@require_permission("audit.logs.read")

async def list_audit_logs(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

    event_type: Optional[str] = None,

    actor_email: Optional[str] = None,

    date_from: Optional[datetime] = None,

    date_to: Optional[datetime] = None,

    limit: int = Query(default=100, le=1000),

    offset: int = 0,

):

    logs = await admin_service.list_audit_logs(

        event_type=event_type,

        actor_email=actor_email,

        date_from=date_from,

        date_to=date_to,

        limit=limit,

        offset=offset,

    )

    return [AuditLogResponse.model_validate(log) for log in logs]



# ==========================================

# System Reports

# ==========================================



@router.get("/reports", response_model=list[SystemReportResponse])

@require_permission("reports.read")

async def list_system_reports(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

    limit: int = 100,

    offset: int = 0,

):

    reports = await admin_service.list_system_reports(limit=limit, offset=offset)

    return [SystemReportResponse.model_validate(r) for r in reports]



@router.post("/reports", response_model=ReportGenerateResponse, status_code=status.HTTP_201_CREATED)

@require_permission("reports.generate")

async def generate_report(

    payload: ReportGenerateRequest,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    report = await admin_service.create_system_report(

        report_name=payload.report_name,

        report_type=payload.report_type,

    )

    return ReportGenerateResponse(

        id=report.id,

        report_name=report.report_name,

        status=report.status,

        message=f"Report '{report.report_name}' generated successfully.",

    )



# ==========================================

# User Management (Admin)

# ==========================================



@router.get("/users", response_model=list[AdminUserResponse])

@require_permission("users.read")

async def list_admin_users(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

    search: Optional[str] = None,

    role: Optional[str] = None,

    is_active: Optional[bool] = None,

    is_superuser: Optional[bool] = None,

    limit: int = Query(default=100, le=500),

    offset: int = 0,

):

    """List all users with optional search and filtering."""

    users = await admin_service.list_users(

        search=search,

        role=role,

        is_active=is_active,

        is_superuser=is_superuser,

        limit=limit,

        offset=offset,

    )

    return [AdminUserResponse.model_validate(u) for u in users]



@router.get("/users/{user_id}", response_model=AdminUserResponse)

@require_permission("users.read")

async def get_user_detail(

    user_id: int,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get detailed information for a specific user."""

    user = await admin_service.get_user_detail(user_id)

    if not user:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="User not found",

        )

    return AdminUserResponse.model_validate(user)



@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)

@require_permission("users.manage")

async def update_user_status(

    user_id: int,

    payload: AdminUserStatusUpdate,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Activate or deactivate a user."""

    # Prevent self-deactivation

    if current_user.id == user_id and not payload.is_active:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Cannot deactivate yourself",

        )

    user = await admin_service.update_user_status(user_id, payload.is_active)

    if not user:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="User not found",

        )

    return AdminUserResponse.model_validate(user)



@router.patch("/users/{user_id}/role", response_model=AdminUserResponse)

@require_permission("users.manage")

async def update_user_role(

    user_id: int,

    payload: AdminUserRoleUpdate,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Promote or demote a user (superuser status)."""

    user = await admin_service.update_user_role(user_id, payload.is_superuser)

    if not user:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="User not found",

        )

    return AdminUserResponse.model_validate(user)



@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)

@require_permission("users.manage")

async def delete_user(

    user_id: int,

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Permanently delete a user."""

    # Prevent self-deletion

    if current_user.id == user_id:

        raise HTTPException(

            status_code=status.HTTP_400_BAD_REQUEST,

            detail="Cannot delete yourself",

        )

    success = await admin_service.delete_user(user_id)

    if not success:

        raise HTTPException(

            status_code=status.HTTP_404_NOT_FOUND,

            detail="User not found",

        )



# ==========================================

# System Health

# ==========================================



@router.get("/health", response_model=SystemHealthResponse)

@require_permission("system.health.check")

async def system_health(

    current_user: CurrentSuperuser,

    admin_service: AdminServiceDependency,

):

    """Get system health status."""

    start_time = time.time()

    health_data = await admin_service.get_system_health()

    health_data["uptime_seconds"] = round(time.time() - start_time, 2)



    # Count how many routes are registered in this router

    route_count = len(router.routes)

    health_data["total_api_routes"] = route_count



    return SystemHealthResponse(**health_data)