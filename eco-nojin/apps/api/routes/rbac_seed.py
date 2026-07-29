"""Seed RBAC defaults — local/staging helper."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session
from apps.shared_core.rbac.seed import seed_rbac

router = APIRouter(prefix="/api/v1/rbac", tags=["RBAC"])


@router.post("/seed")
async def seed_roles(session: AsyncSession = Depends(get_db_session)):
    if settings.ENVIRONMENT == "production":
        raise HTTPException(status_code=403, detail="Seed disabled in production")
    stats = await seed_rbac(session)
    return {"ok": True, **stats}
