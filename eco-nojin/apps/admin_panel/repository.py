"""repository module."""

import logging

logger = logging.getLogger(__name__)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.repository import BaseRepository
from apps.shared_core.models import AdminSetting, AuditLog, SystemReport


class AdminSettingRepository(BaseRepository[AdminSetting]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AdminSetting)
        """Handle __init__ (session)."""

    async def get_by_key(self, key: str) -> AdminSetting | None:
        stmt = select(AdminSetting).where(AdminSetting.key == key)
        """Handle get_by_key (key)."""
        result = await self.session.execute(stmt)
        return result.scalars().first()


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AuditLog)
        """Handle __init__ (session)."""

    async def filter_by_event_type(
        self,
        event_type: str | None = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        stmt = select(AuditLog)
        """Handle filter_by_event_type (event_type, limit, offset)."""
        if event_type:
            stmt = stmt.where(AuditLog.event_type == event_type)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SystemReportRepository(BaseRepository[SystemReport]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, SystemReport)
        """Handle __init__ (session)."""
