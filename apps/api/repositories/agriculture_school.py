"""
Agriculture Schools Repository
=============================
Data access layer — all database queries live here.
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.agriculture_school import AgricultureSchool, SchoolField
from apps.api.schemas.agriculture_school import (
    AgricultureSchoolCreate, AgricultureSchoolUpdate
)


class AgricultureSchoolRepository:
    """Repository for AgricultureSchool entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, school_id: int) -> Optional[AgricultureSchool]:
        result = await self.session.execute(
            select(AgricultureSchool).where(AgricultureSchool.id == school_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        school_type: Optional[str] = None
    ) -> tuple[List[AgricultureSchool], int]:
        query = select(AgricultureSchool)
        
        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                (AgricultureSchool.name.ilike(search_term)) |
                (AgricultureSchool.province.ilike(search_term)) |
                (AgricultureSchool.city.ilike(search_term))
            )
        
        if school_type:
            query = query.where(AgricultureSchool.school_type == school_type)
        
        query = query.order_by(AgricultureSchool.name).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(AgricultureSchool)
        if search:
            search_term = f"%{search.lower()}%"
            count_query = count_query.where(
                (AgricultureSchool.name.ilike(search_term)) |
                (AgricultureSchool.province.ilike(search_term)) |
                (AgricultureSchool.city.ilike(search_term))
            )
        if school_type:
            count_query = count_query.where(AgricultureSchool.school_type == school_type)
        
        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: AgricultureSchoolCreate) -> AgricultureSchool:
        obj = AgricultureSchool(**data.model_dump(exclude={"fields"}))
        
        # Add fields
        for field_name in (data.fields or []):
            obj.fields.append(SchoolField(field_name=field_name))
        
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, school_id: int, data: AgricultureSchoolUpdate) -> Optional[AgricultureSchool]:
        obj = await self.get_by_id(school_id)
        if not obj:
            return None
        
        update_data = data.model_dump(exclude_unset=True, exclude={"fields"})
        for key, value in update_data.items():
            setattr(obj, key, value)
        
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, school_id: int) -> bool:
        obj = await self.get_by_id(school_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def get_stats(self) -> dict:
        result = await self.session.execute(select(AgricultureSchool))
        schools = result.scalars().all()
        
        return {
            "total_schools": len(schools),
            "total_students": sum(s.students_count for s in schools),
            "provinces_count": len(set(s.province for s in schools)),
            "by_type": {
                t: len([s for s in schools if s.school_type == t])
                for t in ["university", "institute", "training-center"]
            }
        }