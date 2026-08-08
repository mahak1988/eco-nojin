"""Phase 5 — Content version persistence."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.models import ContentVersion


def _now() -> datetime:
    return datetime.now(UTC)


class ContentVersionService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def next_version_number(self, content_type: str, content_id: int) -> int:
        stmt = select(func.coalesce(func.max(ContentVersion.version_number), 0)).where(
            ContentVersion.content_type == content_type,
            ContentVersion.content_id == content_id,
        )
        result = await self.session.execute(stmt)
        current = result.scalar_one()
        return int(current) + 1

    async def create_version(
        self,
        *,
        content_type: str,
        content_id: int,
        content_data: Any,
        created_by: int | None,
        status: str = "draft",
    ) -> ContentVersion:
        if not isinstance(content_data, str):
            content_data = json.dumps(content_data, ensure_ascii=False, default=str)
        version_number = await self.next_version_number(content_type, content_id)
        row = ContentVersion(
            content_type=content_type,
            content_id=content_id,
            version_number=version_number,
            content_data=content_data,
            created_by=created_by,
            status=status,
        )
        self.session.add(row)
        await self.session.commit()
        await self.session.refresh(row)
        return row

    async def list_versions(
        self, content_type: str, content_id: int, limit: int = 50
    ) -> list[ContentVersion]:
        stmt = (
            select(ContentVersion)
            .where(
                ContentVersion.content_type == content_type,
                ContentVersion.content_id == content_id,
            )
            .order_by(desc(ContentVersion.version_number))
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def approve(
        self, content_type: str, content_id: int, approved_by: int, notes: str = ""
    ) -> ContentVersion | None:
        versions = await self.list_versions(content_type, content_id, limit=1)
        if not versions:
            # create approved snapshot if none exist
            row = await self.create_version(
                content_type=content_type,
                content_id=content_id,
                content_data={"notes": notes},
                created_by=approved_by,
                status="approved",
            )
            row.approved_by = approved_by
            row.approved_at = _now()
            await self.session.commit()
            await self.session.refresh(row)
            return row

        row = versions[0]
        row.status = "approved"
        row.approved_by = approved_by
        row.approved_at = _now()
        await self.session.commit()
        await self.session.refresh(row)
        return row

    @staticmethod
    def to_response_dict(row: ContentVersion) -> dict[str, Any]:
        try:
            data = json.loads(row.content_data or "{}")
        except Exception:
            data = {"raw": row.content_data}
        return {
            "id": row.id,
            "version_number": row.version_number,
            "content_id": row.content_id,
            "content_data": data if isinstance(data, dict) else {"value": data},
            "created_by": row.created_by or 0,
            "created_at": row.created_at,
            "approved_by": row.approved_by,
            "approved_at": row.approved_at,
            "status": row.status,
        }
