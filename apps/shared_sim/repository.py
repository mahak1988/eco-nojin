"""
shared_sim repository | لایه دسترسی داده shared_sim
==================================================
Data access layer — all database queries live here.
Services call repositories; repositories never call services.
"""

from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_sim.models import SharedSim
from apps.shared_sim.schemas import SharedSimCreate, SharedSimUpdate


class SharedSimRepository:
    """Repository for SharedSim entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, id: int) -> Optional[SharedSim]:
        """Fetch a single record by ID."""
        result = await self.session.execute(
            select(SharedSim).where(SharedSim.id == id)
        )
        return result.scalar_one_or_none()

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[SharedSim], int]:
        """Fetch a paginated list of records + total count."""
        result = await self.session.execute(
            select(SharedSim)
            .order_by(SharedSim.id.desc())
            .offset(skip)
            .limit(limit)
        )
        items = list(result.scalars().all())

        count_result = await self.session.execute(
            select(func.count()).select_from(SharedSim)
        )
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: SharedSimCreate) -> SharedSim:
        """Insert a new record."""
        obj = SharedSim(**data.model_dump())
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, id: int, data: SharedSimUpdate) -> Optional[SharedSim]:
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
