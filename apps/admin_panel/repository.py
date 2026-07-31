"""repository module with cursor-based pagination."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.repository import BaseRepository
from apps.shared_core.models import AdminSetting, AuditLog, SystemReport

logger = logging.getLogger(__name__)


class AdminSettingRepository(BaseRepository):
    """Repository for AdminSetting model."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AdminSetting)

    async def get_by_key(self, key: str) -> Optional[AdminSetting]:
        """Get setting by key."""
        stmt = select(AdminSetting).where(AdminSetting.key == key)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_multi_cursor(self, cursor: Optional[int] = None, limit: int = 100) -> List[AdminSetting]:
        """Get multiple settings with cursor-based pagination."""
        stmt = select(AdminSetting).order_by(AdminSetting.id.asc()).limit(limit)
        
        if cursor is not None:
            stmt = stmt.where(AdminSetting.id > cursor)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class AuditLogRepository(BaseRepository):
    """Repository for AuditLog model."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, AuditLog)

    async def filter_by_event_type(
        self,
        event_type: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> list[AuditLog]:
        stmt = select(AuditLog).order_by(desc(AuditLog.id))
        """Handle filter_by_event_type (event_type, limit, offset)."""
        if event_type:
            stmt = stmt.where(AuditLog.event_type == event_type)
        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def filter_by_params(
        self,
        event_type: Optional[str] = None,
        actor_email: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """Filter audit logs by multiple optional parameters including date range."""
        
        stmt = select(AuditLog).order_by(desc(AuditLog.id))

        conditions = []
        if event_type:
            conditions.append(AuditLog.event_type == event_type)
        if actor_email:
            conditions.append(AuditLog.actor_email == actor_email)
        if date_from:
            conditions.append(AuditLog.created_at >= date_from)
        if date_to:
            conditions.append(AuditLog.created_at <= date_to)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        stmt = stmt.limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def filter_by_params_cursor(
        self,
        cursor: Optional[int] = None,
        event_type: Optional[str] = None,
        actor_email: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Filter audit logs by parameters with cursor-based pagination."""
        
        stmt = select(AuditLog).order_by(AuditLog.id.asc()).limit(limit)

        conditions = []
        if cursor is not None:
            conditions.append(AuditLog.id > cursor)
        if event_type:
            conditions.append(AuditLog.event_type == event_type)
        if actor_email:
            conditions.append(AuditLog.actor_email == actor_email)
        if date_from:
            conditions.append(AuditLog.created_at >= date_from)
        if date_to:
            conditions.append(AuditLog.created_at <= date_to)

        if conditions:
            stmt = stmt.where(and_(*conditions))

        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class SystemReportRepository(BaseRepository):
    """Repository for SystemReport model."""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, SystemReport)

    async def get_multi_cursor(self, cursor: Optional[int] = None, limit: int = 100) -> List[SystemReport]:
        """Get multiple reports with cursor-based pagination."""
        stmt = select(SystemReport).order_by(SystemReport.id.asc()).limit(limit)
        
        if cursor is not None:
            stmt = stmt.where(SystemReport.id > cursor)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

# BaseRepository remains at the bottom since it's extended by the other repositories
class BaseRepository:
    """Base repository with common operations."""
    
    def __init__(self, session: AsyncSession, model):
        self.session = session
        self.model = model

    async def get_by_id(self, id_: int) -> Optional[Any]:
        """Get entity by ID."""
        stmt = select(self.model).where(self.model.id == id_)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_multi(self, limit: int = 100, offset: int = 0) -> List[Any]:
        """Get multiple entities with pagination."""
        stmt = select(self.model).limit(limit).offset(offset).order_by(desc(self.model.id))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())