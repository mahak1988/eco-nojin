"""
shared_ai repository | لایه دسترسی داده shared_ai
==================================================
Data access layer — all database queries live here.
Services call repositories; repositories never call services.
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_ai.models import SharedAi
from apps.shared_ai.schemas import SharedAiCreate, SharedAiUpdate


class SharedAiRepository:
    """Repository for SharedAi entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[SharedAi]:
        """Fetch a single record by ID."""
        result = await self.session.execute(
            select(SharedAi).where(SharedAi.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[SharedAi], int]:
        """Fetch a paginated list of records + total count."""
        result = await self.session.execute(
            select(SharedAi)
            .order_by(SharedAi.id.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(result.scalars().all())

        count_result = await self.session.execute(
            select(func.count()).select_from(SharedAi)
        )
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: SharedAiCreate) -> SharedAi:
        """Insert a new record."""
        obj = SharedAi(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, data: SharedAiUpdate) -> Optional[SharedAi]:
        """Update an existing record. Returns None if not found."""
        obj = await self.get_by_id(id)
        if not obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(obj, key, value)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, id: int) -> bool:
        """Delete a record. Returns True if deleted, False if not found."""
        obj = await self.get_by_id(id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True
