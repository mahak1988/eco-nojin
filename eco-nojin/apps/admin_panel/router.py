"""Admin panel API."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Annotated

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
async def admin_dashboard(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
):
    return await admin_service.get_dashboard_summary()


@router.get("/settings", response_model=list[AdminSettingResponse])
async def list_system_settings(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    limit: int = 100,
    offset: int = 0,
):
    settings_list = await admin_service.get_system_settings(limit=limit, offset=offset)
    return [AdminSettingResponse.model_validate(s) for s in settings_list]


@router.put("/settings/{key}", response_model=AdminSettingResponse)
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


@router.get("/audit-logs", response_model=list[AuditLogResponse])
async def list_audit_logs(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    event_type: str | None = None,
    limit: int = 100,
    offset: int = 0,
):
    logs = await admin_service.list_audit_logs(
        event_type=event_type, limit=limit, offset=offset
    )
    return [AuditLogResponse.model_validate(log) for log in logs]


@router.get("/reports", response_model=list[SystemReportResponse])
async def list_system_reports(
    current_user: CurrentSuperuser,
    admin_service: AdminServiceDependency,
    limit: int = 100,
    offset: int = 0,
):
    reports = await admin_service.list_system_reports(limit=limit, offset=offset)
    return [SystemReportResponse.model_validate(r) for r in reports]
