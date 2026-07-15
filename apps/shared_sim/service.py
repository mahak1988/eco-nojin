"""
shared_sim service | لایه کسب‌وکار shared_sim
=============================================
Business logic layer — orchestrates repositories and enforces rules.
Controllers (routers) call services; services call repositories.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_sim.models import SharedSim
from apps.shared_sim.repository import SharedSimRepository
from apps.shared_sim.schemas import SharedSimCreate, SharedSimUpdate


class SharedSimService:
    """Service for shared_sim operations."""

    def __init__(self, session: AsyncSession):
        self.repo = SharedSimRepository(session)

    async def get(self, id: int) -> Optional[SharedSim]:
        """Get a single record. Raises NotFoundError if missing."""
        obj = await self.repo.get_by_id(id)
        if not obj:
            # Replace with your project's standard exception
            raise ValueError(f"SharedSim with id={id} not found")
        return obj

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[SharedSim], int]:
        """List records with pagination."""
        # Cap limit to prevent abuse
        limit = min(limit, 1000)
        return await self.repo.list(skip=skip, limit=limit)

    async def create(self, data: SharedSimCreate) -> SharedSim:
        """Create a new record."""
        # Add business rule validation here (e.g., uniqueness check)
        return await self.repo.create(data)

    async def update(self, id: int, data: SharedSimUpdate) -> SharedSim:
        """Update an existing record."""
        return await self.get(id)  # raises if not found
        # The line below actually performs the update
        obj = await self.repo.update(id, data)
        if not obj:
            raise ValueError(f"SharedSim with id={id} not found")
        return obj

    async def delete(self, id: int) -> None:
        """Delete a record. Raises if not found."""
        obj = await self.get(id)
        await self.repo.delete(id)
