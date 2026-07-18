from typing import Optional, Dict, Any
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.admin_panel.repository import AdminSettingRepository, AuditLogRepository, SystemReportRepository
from apps.shared_core.models import AdminSetting, AuditLog, SystemReport
from apps.users.models import User


class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.settings_repo = AdminSettingRepository(session)
        self.audit_repo = AuditLogRepository(session)
        self.report_repo = SystemReportRepository(session)

    async def get_system_settings(self, limit: int = 100, offset: int = 0) -> list[AdminSetting]:
        return await self.settings_repo.get_multi(limit=limit, offset=offset)

    async def get_setting_by_key(self, key: str) -> Optional[AdminSetting]:
        return await self.settings_repo.get_by_key(key)

    async def upsert_system_setting(
        self,
        key: str,
        value: Optional[str] = None,
        description: Optional[str] = None,
        is_active: Optional[bool] = None
    ) -> AdminSetting:
        existing = await self.get_setting_by_key(key)
        payload: Dict[str, Any] = {}
        if value is not None:
            payload["value"] = value
        if description is not None:
            payload["description"] = description
        if is_active is not None:
            payload["is_active"] = is_active

        if existing:
            return await self.settings_repo.update(existing, payload)

        payload.update({
            "key": key,
            "value": value or "",
            "description": description or "",
            "is_active": is_active if is_active is not None else True,
        })
        return await self.settings_repo.create(payload)

    async def list_audit_logs(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        return await self.audit_repo.filter_by_event_type(event_type, limit=limit, offset=offset)

    async def record_audit_event(
        self,
        event_type: str,
        event_data: Optional[str] = None,
        actor: Optional[User] = None
    ) -> AuditLog:
        payload = {
            "event_type": event_type,
            "event_data": event_data,
            "actor_id": actor.id if actor else None,
            "actor_email": actor.email if actor else None,
        }
        return await self.audit_repo.create(payload)

    async def list_system_reports(self, limit: int = 100, offset: int = 0) -> list[SystemReport]:
        return await self.report_repo.get_multi(limit=limit, offset=offset)

    async def get_dashboard_summary(self) -> dict:
        user_count = await self._count_users()
        active_user_count = await self._count_users(filter_by={"is_active": True})
        superuser_count = await self._count_users(filter_by={"is_superuser": True})
        total_settings = await self.settings_repo.count()
        total_audit_logs = await self.audit_repo.count()
        total_reports = await self.report_repo.count()

        return {
            "user_count": user_count,
            "active_user_count": active_user_count,
            "superuser_count": superuser_count,
            "total_settings": total_settings,
            "total_audit_logs": total_audit_logs,
            "total_reports": total_reports,
        }

    async def _count_users(self, filter_by: Optional[dict] = None) -> int:
        stmt = select(func.count()).select_from(User)
        if filter_by:
            for key, value in filter_by.items():
                stmt = stmt.where(getattr(User, key) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one()
