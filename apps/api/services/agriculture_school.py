"""
Agriculture Schools Service
===========================
Business logic layer — orchestrates repositories and enforces rules.
"""

from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.repositories.agriculture_school import AgricultureSchoolRepository
from apps.api.schemas.agriculture_school import (
    AgricultureSchoolCreate, AgricultureSchoolUpdate
)
from apps.api.models.agriculture_school import AgricultureSchool


class AgricultureSchoolService:
    """Service for agriculture school operations."""

    def __init__(self, session: AsyncSession):
        self.repo = AgricultureSchoolRepository(session)

    async def list(
        self, skip: int = 0, limit: int = 100, search: Optional[str] = None, school_type: Optional[str] = None
    ) -> tuple[List[AgricultureSchool], int]:
        limit = min(limit, 200)
        return await self.repo.list(skip, limit, search, school_type)

    async def create(self, data: AgricultureSchoolCreate) -> AgricultureSchool:
        return await self.repo.create(data)

    async def get(self, school_id: int) -> AgricultureSchool:
        obj = await self.repo.get_by_id(school_id)
        if not obj:
            raise ValueError(f"AgricultureSchool with id={school_id} not found")
        return obj

    async def update(self, school_id: int, data: AgricultureSchoolUpdate) -> AgricultureSchool:
        obj = await self.repo.update(school_id, data)
        if not obj:
            raise ValueError(f"AgricultureSchool with id={school_id} not found")
        return obj

    async def delete(self, school_id: int) -> None:
        if not await self.repo.delete(school_id):
            raise ValueError(f"AgricultureSchool with id={school_id} not found")

    async def get_stats(self) -> dict:
        return await self.repo.get_stats()