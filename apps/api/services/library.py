"""
Library Service
================
Business logic layer — orchestrates repositories and enforces rules.
"""

from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.repositories.library import LibraryRepository
from apps.api.schemas.library import LibraryResourceCreate, LibraryResourceUpdate
from apps.api.models.library import LibraryResource


class LibraryService:
    """Service for library operations."""

    def __init__(self, session: AsyncSession):
        self.repo = LibraryRepository(session)

    async def list(
        self, skip: int = 0, limit: int = 100,
        search: Optional[str] = None, category: Optional[str] = None, author: Optional[str] = None
    ) -> tuple[List[LibraryResource], int]:
        limit = min(limit, 200)
        return await self.repo.list(skip, limit, search, category, author)

    async def create(self, data: LibraryResourceCreate) -> LibraryResource:
        return await self.repo.create(data)

    async def get(self, resource_id: int) -> LibraryResource:
        obj = await self.repo.get_by_id(resource_id)
        if not obj:
            raise ValueError(f"LibraryResource with id={resource_id} not found")
        return obj

    async def update(self, resource_id: int, data: LibraryResourceUpdate) -> LibraryResource:
        obj = await self.repo.update(resource_id, data)
        if not obj:
            raise ValueError(f"LibraryResource with id={resource_id} not found")
        return obj

    async def delete(self, resource_id: int) -> None:
        if not await self.repo.delete(resource_id):
            raise ValueError(f"LibraryResource with id={resource_id} not found")

    async def download(self, resource_id: int) -> LibraryResource:
        """Record a download and return the resource."""
        obj = await self.get(resource_id)
        await self.repo.increment_download(resource_id)
        return obj

    async def get_stats(self) -> dict:
        return await self.repo.get_stats()