from __future__ import annotations

from typing import Annotated, Optional, TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status

from apps.admin_panel.schemas import (
    AdminDashboardResponse,
    AdminSettingResponse,
    AdminSettingUpdate,
    AuditLogResponse,
    SystemReportResponse,
)
from apps.admin_panel.service import AdminService
from apps.shared_core.database.session import get_db_session
from apps.users.dependencies import get_current_active_superuser

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession
    from apps.shared_core.models import AdminSetting, AuditLog, SystemReport
    from apps.users.models import User

router = APIRouter(prefix="/admin", tags=["Admin"])

DBSessionDependency = Depends(get_db_session)
CurrentSuperuser = Annotated["User", Depends(get_current_active_superuser)]


async def get_admin_service(
    session: Annotated["AsyncSession", DBSessionDependency],
) -> AdminService:
    return AdminService(session)

AdminServiceDependency = Annotated[AdminService, Depends(get_admin_service)]


@router.get("/", response_model=AdminDashboardResponse)
async def admin_dashboard(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
) -> dict[str, int]:
    return await admin_service.get_dashboard_summary()


@router.get("/settings", response_model=list[AdminSettingResponse])
async def list_system_settings(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    limit: int = 100,
    offset: int = 0,
) -> list[AdminSettingResponse]:
    settings: list[AdminSetting] = await admin_service.get_system_settings(limit=limit, offset=offset)
    return [AdminSettingResponse.model_validate(setting) for setting in settings]


@router.put("/settings/{key}", response_model=AdminSettingResponse)
async def upsert_system_setting(
    key: str,
    payload: AdminSettingUpdate,
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
) -> AdminSettingResponse:
    if not any([payload.value is not None, payload.description is not None, payload.is_active is not None]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="حداقل یکی از فیلدهای value، description یا is_active باید تنظیم شود"
        )

    setting: AdminSetting = await admin_service.upsert_system_setting(
        key=key,
        value=payload.value,
        description=payload.description,
        is_active=payload.is_active,
    )
    return AdminSettingResponse.model_validate(setting)


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    event_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AuditLogResponse]:
    audit_logs: list[AuditLog] = await admin_service.list_audit_logs(event_type=event_type, limit=limit, offset=offset)
    return [AuditLogResponse.model_validate(log) for log in audit_logs]


@router.get("/reports", response_model=list[SystemReportResponse])
async def list_system_reports(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    limit: int = 100,
    offset: int = 0,
) -> list[SystemReportResponse]:
    reports: list[SystemReport] = await admin_service.list_system_reports(limit=limit, offset=offset)
    return [SystemReportResponse.model_validate(report) for report in reports]
