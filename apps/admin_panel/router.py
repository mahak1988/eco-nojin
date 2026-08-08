from __future__ import annotations

"""Admin panel API."""

import logging
import time
from datetime import datetime
from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.admin_panel import derived_analytics as da
from apps.admin_panel.content_version_service import ContentVersionService
from apps.admin_panel.middleware.rbac import require_permission
from apps.admin_panel.recommendation_engine import build_ml_recommendations
from apps.admin_panel.schemas import (
    AdminDashboardResponse,
    AdminSettingResponse,
    AdminSettingUpdate,
    AdminUserResponse,
    AdminUserRoleUpdate,
    AdminUserStatusUpdate,
    AdvancedAlertResponse,
    AdvancedAnalyticsResponse,
    AdvancedSettingResponse,
    AdvancedSettingUpdate,
    AuditLogResponse,
    AutoRecommendationResponse,
    ContentApprovalResponse,
    ContentCreateRequest,
    ContentItemResponse,
    ContentSuggestionResponse,
    ContentTypeResponse,
    ContentUpdateRequest,
    ContentVersionResponse,
    IntelligentAlertResponse,
    IntelligentAnalyticsResponse,
    ReportGenerateRequest,
    ReportGenerateResponse,
    SmartRecommendationResponse,
    SystemHealthResponse,
    SystemReportResponse,
    UserBehaviorAnalysisResponse,
)
from apps.admin_panel.service import AdminService
from apps.shared_core.database.session import get_db_session
from apps.users.dependencies import get_current_active_superuser

if TYPE_CHECKING:
    from apps.users.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])

DBSessionDependency = Depends(get_db_session)
CurrentSuperuser = Annotated["User", Depends(get_current_active_superuser)]


async def get_admin_service(
    session: Annotated[AsyncSession, DBSessionDependency],
) -> AdminService:
    return AdminService(session)


AdminServiceDependency = Annotated[AdminService, Depends(get_admin_service)]


@router.get("/", response_model=AdminDashboardResponse)
@require_permission("dashboard.view")
async def admin_dashboard(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    return await admin_service.get_dashboard_summary()


@router.get("/me/permissions")
async def my_permissions(current_user: CurrentSuperuser):
    return da.user_permissions_payload(current_user)


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
        [payload.value is not None, payload.description is not None, payload.is_active is not None]
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="At least one field required"
        )
    setting = await admin_service.upsert_system_setting(
        key=key, value=payload.value, description=payload.description, is_active=payload.is_active
    )
    return AdminSettingResponse.model_validate(setting)


@router.get("/advanced-settings", response_model=list[AdvancedSettingResponse])
@require_permission("advanced_settings.read")
async def list_advanced_settings(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    limit: int = 100,
    offset: int = 0,
):
    items = await da.list_advanced_settings(admin_service, limit=limit, offset=offset)
    return [AdvancedSettingResponse.model_validate(s) for s in items]


@router.put("/advanced-settings/{key}", response_model=AdvancedSettingResponse)
@require_permission("advanced_settings.write")
async def upsert_advanced_setting(
    key: str,
    payload: AdvancedSettingUpdate,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    item = await da.upsert_advanced_setting(
        admin_service,
        key=key,
        value=payload.value,
        description=payload.description,
        category=getattr(payload, "category", None),
        is_active=payload.is_active,
    )
    return AdvancedSettingResponse.model_validate(item)


@router.get("/content/types", response_model=list[ContentTypeResponse])
@require_permission("content.types.read")
async def list_content_types(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    content_types = await admin_service.get_content_types()
    return [ContentTypeResponse.model_validate(ct) for ct in content_types]


@router.get("/content/{content_type}", response_model=list[ContentItemResponse])
@require_permission("content.items.read")
async def list_content_items(
    content_type: str,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    search: str | None = None,
    status_filter: str | None = Query(default=None, alias="status"),
    limit: int = Query(default=20, le=100),
    offset: int = 0,
):
    content_items = await admin_service.get_content_items_by_type(
        content_type=content_type, search=search, status=status_filter, limit=limit, offset=offset
    )
    return [ContentItemResponse.model_validate(ci) for ci in content_items]


@router.post(
    "/content/{content_type}",
    response_model=ContentItemResponse,
    status_code=status.HTTP_201_CREATED,
)
@require_permission("content.items.create")
async def create_content_item(
    content_type: str,
    payload: ContentCreateRequest,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    session: Annotated[AsyncSession, DBSessionDependency],
):
    content_item = await admin_service.create_content_item(
        content_type=content_type,
        data=payload.data if hasattr(payload, "data") else payload.model_dump(),
        author_id=current_user.id,
    )
    # Phase 5: persist initial version
    try:
        cvs = ContentVersionService(session)
        data = payload.model_dump() if hasattr(payload, "model_dump") else {}
        await cvs.create_version(
            content_type=content_type,
            content_id=getattr(content_item, "id", 0),
            content_data=data,
            created_by=current_user.id,
            status=getattr(payload, "status", "draft") or "draft",
        )
    except Exception as e:
        logger.warning("content version create failed: %s", e)
    await admin_service.sync_content_to_modules(content_item, content_type, "create")
    return ContentItemResponse.model_validate(content_item)


@router.get("/content/{content_type}/{item_id}", response_model=ContentItemResponse)
@require_permission("content.items.read")
async def get_content_item(
    content_type: str,
    item_id: int,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    content_item = await admin_service.get_content_item_by_id(
        content_type=content_type, item_id=item_id
    )
    if not content_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")
    return ContentItemResponse.model_validate(content_item)


@router.put("/content/{content_type}/{item_id}", response_model=ContentItemResponse)
@require_permission("content.items.update")
async def update_content_item(
    content_type: str,
    item_id: int,
    payload: ContentUpdateRequest,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    session: Annotated[AsyncSession, DBSessionDependency],
):
    content_item = await admin_service.update_content_item(
        content_type=content_type,
        item_id=item_id,
        data=payload.model_dump(exclude_unset=True),
        updated_by_id=current_user.id,
    )
    if not content_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")
    try:
        cvs = ContentVersionService(session)
        await cvs.create_version(
            content_type=content_type,
            content_id=item_id,
            content_data=payload.model_dump(exclude_unset=True),
            created_by=current_user.id,
            status=getattr(payload, "status", None) or "draft",
        )
    except Exception as e:
        logger.warning("content version update failed: %s", e)
    await admin_service.sync_content_to_modules(content_item, content_type, "update")
    return ContentItemResponse.model_validate(content_item)


@router.delete("/content/{content_type}/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission("content.items.delete")
async def delete_content_item(
    content_type: str,
    item_id: int,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    success = await admin_service.delete_content_item(content_type=content_type, item_id=item_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Content item not found")
    await admin_service.sync_content_to_modules(None, content_type, "delete", item_id)


@router.get(
    "/content/{content_type}/{item_id}/versions", response_model=list[ContentVersionResponse]
)
@require_permission("content.versions.read")
async def get_content_versions(
    content_type: str,
    item_id: int,
    current_user: CurrentSuperuser,
    session: Annotated[AsyncSession, DBSessionDependency],
):
    """Phase 5 — load versions from DB (content_versions table)."""
    cvs = ContentVersionService(session)
    rows = await cvs.list_versions(content_type, item_id)
    if not rows:
        # fallback derived snapshot
        from apps.admin_panel import derived_analytics as _da

        versions = _da.content_versions_from_item(item_id, current_user.id, None)
        return [ContentVersionResponse.model_validate(v) for v in versions]
    return [
        ContentVersionResponse.model_validate(ContentVersionService.to_response_dict(r))
        for r in rows
    ]


@router.post("/content/{content_type}/{item_id}/approve", response_model=ContentApprovalResponse)
@require_permission("content.approval.manage")
async def approve_content(
    content_type: str,
    item_id: int,
    current_user: CurrentSuperuser,
    session: Annotated[AsyncSession, DBSessionDependency],
):
    cvs = ContentVersionService(session)
    row = await cvs.approve(content_type, item_id, current_user.id)
    return ContentApprovalResponse.model_validate(
        {
            "content_id": item_id,
            "approved_by": current_user.id,
            "approved_at": getattr(row, "approved_at", datetime.utcnow()) or datetime.utcnow(),
            "status": "approved",
            "notes": "محتوا تأیید شد",
        }
    )


@router.get("/smart-recommendations", response_model=list[SmartRecommendationResponse])
@require_permission("recommendations.view")
async def get_smart_recommendations(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    """Phase 5 — prefer ML-scored recommendations; fallback to service."""
    try:
        ml_recs = await build_ml_recommendations(admin_service)
        # Adapt to SmartRecommendationResponse (needs action field)
        adapted = []
        for r in ml_recs:
            adapted.append(
                {
                    "id": str(r.get("id", "")),
                    "title": r.get("title", ""),
                    "description": r.get("description", ""),
                    "category": r.get("category", "general"),
                    "priority": r.get("priority", "medium"),
                    "action": r.get("action") or r.get("suggested_action", "review"),
                }
            )
        if adapted:
            return [SmartRecommendationResponse.model_validate(a) for a in adapted]
    except Exception as e:
        logger.warning("ML recommendations failed: %s", e)
    recommendations = await admin_service.get_smart_recommendations(current_user.id)
    return [SmartRecommendationResponse.model_validate(rec) for rec in recommendations]


@router.get("/user-behavior-analysis", response_model=UserBehaviorAnalysisResponse)
@require_permission("analytics.behavior.view")
async def get_user_behavior_analysis(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    analysis = await admin_service.analyze_user_behavior()
    return UserBehaviorAnalysisResponse.model_validate(analysis)


@router.get("/advanced-analytics", response_model=AdvancedAnalyticsResponse)
@require_permission("analytics.advanced.view")
async def get_advanced_analytics(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    analytics = await admin_service.get_advanced_analytics()
    return AdvancedAnalyticsResponse.model_validate(analytics)


@router.get("/content-suggestions/{content_type}", response_model=list[ContentSuggestionResponse])
@require_permission("content.suggestions.view")
async def get_ai_content_suggestions(
    content_type: str,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    suggestions = await admin_service.get_ai_content_suggestions(content_type)
    return [ContentSuggestionResponse.model_validate(sug) for sug in suggestions]


@router.get("/intelligent-alerts", response_model=list[IntelligentAlertResponse])
@require_permission("alerts.intelligent.view")
async def get_intelligent_alerts(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    alerts = await admin_service.get_intelligent_alerts()
    return [IntelligentAlertResponse.model_validate(alert) for alert in alerts]


@router.get("/intelligent-analytics", response_model=IntelligentAnalyticsResponse)
@require_permission("analytics.intelligent.view")
async def get_intelligent_analytics(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    payload = await da.intelligent_analytics_payload(admin_service, current_user.id)
    return IntelligentAnalyticsResponse.model_validate(payload)


@router.get("/auto-recommendations", response_model=list[AutoRecommendationResponse])
@require_permission("recommendations.auto.view")
async def get_auto_recommendations(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    try:
        ml_recs = await build_ml_recommendations(admin_service)
        if ml_recs:
            return [AutoRecommendationResponse.model_validate(r) for r in ml_recs]
    except Exception as e:
        logger.warning("auto ML recs failed: %s", e)
    recs = await da.auto_recommendations_payload(admin_service, current_user.id)
    return [AutoRecommendationResponse.model_validate(rec) for rec in recs]


@router.get("/advanced-alerts", response_model=list[AdvancedAlertResponse])
@require_permission("alerts.advanced.view")
async def get_advanced_alerts(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    alerts = await da.advanced_alerts_payload(admin_service)
    return [AdvancedAlertResponse.model_validate(alert) for alert in alerts]


@router.get("/audit-logs", response_model=list[AuditLogResponse])
@require_permission("audit.logs.read")
async def list_audit_logs(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    event_type: str | None = None,
    actor_email: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
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
        report_name=payload.report_name, report_type=payload.report_type
    )
    return ReportGenerateResponse(
        id=report.id,
        report_name=report.report_name,
        status=report.status,
        message=f"Report '{report.report_name}' generated successfully.",
    )


@router.get("/users", response_model=list[AdminUserResponse])
@require_permission("users.read")
async def list_admin_users(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    search: str | None = None,
    role: str | None = None,
    is_active: bool | None = None,
    is_superuser: bool | None = None,
    limit: int = Query(default=100, le=500),
    offset: int = 0,
):
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
    user = await admin_service.get_user_detail(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.patch("/users/{user_id}/status", response_model=AdminUserResponse)
@require_permission("users.manage")
async def update_user_status(
    user_id: int,
    payload: AdminUserStatusUpdate,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    if current_user.id == user_id and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate yourself"
        )
    user = await admin_service.update_user_status(user_id, payload.is_active)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.patch("/users/{user_id}/role", response_model=AdminUserResponse)
@require_permission("users.manage")
async def update_user_role(
    user_id: int,
    payload: AdminUserRoleUpdate,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    user = await admin_service.update_user_role(user_id, payload.is_superuser)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AdminUserResponse.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_permission("users.manage")
async def delete_user(
    user_id: int,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete yourself"
        )
    success = await admin_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.get("/health", response_model=SystemHealthResponse)
@require_permission("system.health.check")
async def system_health(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    start_time = time.time()
    health_data = await admin_service.get_system_health()
    health_data["uptime_seconds"] = round(time.time() - start_time, 2)
    health_data["total_api_routes"] = len(router.routes)
    return SystemHealthResponse(**health_data)
