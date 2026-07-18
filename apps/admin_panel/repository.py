from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from apps.shared_core.database.repository import BaseRepository
from apps.shared_core.models import AdminSetting, AuditLog, SystemReport


class AdminSettingRepository(BaseRepository[AdminSetting]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AdminSetting)

    async def get_by_key(self, key: str) -> Optional[AdminSetting]:
        stmt = select(AdminSetting).where(AdminSetting.key == key)
        result = await self.session.execute(stmt)
        return result.scalars().first()


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLog)

    async def filter_by_event_type(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        stmt = select(AuditLog)
        if event_type:
            stmt = stmt.where(AuditLog.event_type == event_type)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SystemReportRepository(BaseRepository[SystemReport]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, SystemReport)
