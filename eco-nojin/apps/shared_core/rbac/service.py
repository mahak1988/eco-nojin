"""RBAC permission checks."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from apps.shared_core.rbac.models import Permission, Role, UserRole


async def get_user_permission_codes(session: AsyncSession, user_id: int) -> set[str]:
    result = await session.execute(
        select(Role)
        .join(UserRole, UserRole.role_id == Role.id)
        .where(UserRole.user_id == user_id)
        .options(selectinload(Role.permissions))
    )
    roles = result.scalars().unique().all()
    codes: set[str] = set()
    for role in roles:
        for p in role.permissions or []:
            codes.add(p.code)
    return codes


def permission_granted(codes: set[str], required: str) -> bool:
    if "*:*" in codes:
        return True
    if required in codes:
        return True
    # resource:* wildcard
    if ":" in required:
        resource = required.split(":", 1)[0]
        if f"{resource}:*" in codes:
            return True
    return False


async def user_has_permission(session: AsyncSession, user_id: int, required: str) -> bool:
    codes = await get_user_permission_codes(session, user_id)
    return permission_granted(codes, required)


async def assign_role(session: AsyncSession, user_id: int, role_name: str) -> None:
    result = await session.execute(select(Role).where(Role.name == role_name))
    role = result.scalar_one_or_none()
    if not role:
        raise ValueError(f"Role not found: {role_name}")
    existing = await session.execute(
        select(UserRole).where(UserRole.user_id == user_id, UserRole.role_id == role.id)
    )
    if existing.scalar_one_or_none() is None:
        session.add(UserRole(user_id=user_id, role_id=role.id))
        await session.flush()
