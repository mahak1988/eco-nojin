"""
api service | لایه کسب‌وکار api
=============================================
Business logic layer — orchestrates repositories and enforces rules.
Controllers (routers) call services; services call repositories.
"""

from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models import Api
from apps.api.repository import ApiRepository
from apps.api.schemas import ApiCreate, ApiUpdate
from apps.shared_core.exceptions import NotFoundError


class ApiService:
    """Service for api operations."""

    def __init__(self, session: AsyncSession):
        self.repo = ApiRepository(session)

    async def get(self, id: int) -> Api:
        """Get a single record. Raises NotFoundError if missing."""
        obj = await self.repo.get_by_id(id)
        if not obj:
            raise NotFoundError(resource="Api", item_id=id)
        return obj

    async def list(self, skip: int = 0, limit: int = 100) -> tuple[list[Api], int]:
        """List records with pagination."""
        # Cap limit to prevent abuse
        limit = min(limit, 1000)
        return await self.repo.list(skip=skip, limit=limit)

    async def create(self, data: ApiCreate) -> Api:
        """Create a new record."""
        # Add business rule validation here (e.g., uniqueness check)
        return await self.repo.create(data)

    async def update(self, id: int, data: ApiUpdate) -> Api:
        """Update an existing record."""
        existing = await self.get(id)  # raises if not found
        
        # Business rule validation
        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            return existing  # No changes needed
        
        # Perform the actual update
        obj = await self.repo.update(id, data)
        
        # Audit logging (optional - can be enhanced later)
        # await self._audit_log("update", id, update_data)
        
        return obj

    async def delete(self, id: int) -> None:
        """Delete a record. Raises if not found."""
        obj = await self.get(id)  # raises if not found
        deleted = await self.repo.delete(id)
        if not deleted:
            raise NotFoundError(resource="Api", item_id=id)

