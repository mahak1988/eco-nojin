"""
Library Repository
===================
Data access layer — all database queries live here.
"""

from typing import Optional, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.models.library import LibraryResource
from apps.api.schemas.library import LibraryResourceCreate, LibraryResourceUpdate


class LibraryRepository:
    """Repository for Library entities."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, resource_id: int) -> Optional[LibraryResource]:
        result = await self.session.execute(
            select(LibraryResource).where(LibraryResource.id == resource_id)
        )
        return result.scalar_one_or_none()

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        category: Optional[str] = None,
        author: Optional[str] = None
    ) -> tuple[List[LibraryResource], int]:
        query = select(LibraryResource)

        if search:
            search_term = f"%{search.lower()}%"
            query = query.where(
                (LibraryResource.title.ilike(search_term)) |
                (LibraryResource.description.ilike(search_term)) |
                (LibraryResource.tags.ilike(search_term))
            )

        if category:
            query = query.where(LibraryResource.category == category)

        if author:
            query = query.where(LibraryResource.author == author)

        query = query.order_by(LibraryResource.title).offset(skip).limit(limit)
        result = await self.session.execute(query)
        items = list(result.scalars().all())

        count_query = select(func.count()).select_from(LibraryResource)
        if search:
            search_term = f"%{search.lower()}%"
            count_query = count_query.where(
                (LibraryResource.title.ilike(search_term)) |
                (LibraryResource.description.ilike(search_term)) |
                (LibraryResource.tags.ilike(search_term))
            )
        if category:
            count_query = count_query.where(LibraryResource.category == category)
        if author:
            count_query = count_query.where(LibraryResource.author == author)

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one()
        return items, total

    async def create(self, data: LibraryResourceCreate) -> LibraryResource:
        # Convert tags list to comma-separated string
        data_dict = data.model_dump()
        if data_dict.get("tags"):
            data_dict["tags"] = ",".join(data_dict["tags"])

        obj = LibraryResource(**data_dict)
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, resource_id: int, data: LibraryResourceUpdate) -> Optional[LibraryResource]:
        obj = await self.get_by_id(resource_id)
        if not obj:
            return None

        update_data = data.model_dump(exclude_unset=True)
        # Convert tags list to comma-separated string
        if "tags" in update_data and update_data["tags"]:
            update_data["tags"] = ",".join(update_data["tags"])
        elif "tags" in update_data:
            update_data["tags"] = ""

        for key, value in update_data.items():
            setattr(obj, key, value)

        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, resource_id: int) -> bool:
        obj = await self.get_by_id(resource_id)
        if not obj:
            return False
        await self.session.delete(obj)
        await self.session.flush()
        return True

    async def increment_download(self, resource_id: int) -> bool:
        obj = await self.get_by_id(resource_id)
        if not obj:
            return False
        obj.download_count += 1
        await self.session.flush()
        return True

    async def get_stats(self) -> dict:
        result = await self.session.execute(select(LibraryResource))
        resources = result.scalars().all()

        return {
            "total_resources": len(resources),
            "total_downloads": sum(r.download_count for r in resources),
            "by_category": {
                cat: len([r for r in resources if r.category == cat])
                for cat in ["research", "guides", "policies", "reports", "training"]
            }
        }