"""Default roles & permissions (F0.3)."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.rbac.models import Permission, Role, RolePermission

# Five system roles
DEFAULT_ROLES: dict[str, str] = {
    "superadmin": "Full platform control",
    "admin": "Administration without destructive system ops",
    "expert": "Domain expert: advisory, content, review",
    "farmer": "Farmer operator: own farms, enrollments, reports",
    "viewer": "Read-only access",
}

# Permission catalog: resource:action
DEFAULT_PERMISSIONS: list[tuple[str, str]] = [
    ("*:*", "All permissions"),
    ("users:read", "List/view users"),
    ("users:write", "Create/update users"),
    ("roles:write", "Manage roles"),
    ("education:read", "View courses"),
    ("education:write", "Manage courses"),
    ("accounting:read", "View accounting"),
    ("accounting:write", "Manage accounting"),
    ("farms:read", "View farms"),
    ("farms:write", "Manage farms"),
    ("simulation:read", "View simulations"),
    ("simulation:write", "Run simulations"),
    ("admin:read", "Admin panel read"),
    ("admin:write", "Admin panel write"),
    ("community:read", "View community"),
    ("community:write", "Post/moderate community"),
]

# role -> permission codes
ROLE_PERMISSION_MAP: dict[str, list[str]] = {
    "superadmin": ["*:*"],
    "admin": [
        "users:read",
        "users:write",
        "education:read",
        "education:write",
        "accounting:read",
        "accounting:write",
        "farms:read",
        "farms:write",
        "simulation:read",
        "simulation:write",
        "admin:read",
        "admin:write",
        "community:read",
        "community:write",
    ],
    "expert": [
        "education:read",
        "education:write",
        "farms:read",
        "simulation:read",
        "simulation:write",
        "community:read",
        "community:write",
        "accounting:read",
    ],
    "farmer": [
        "education:read",
        "farms:read",
        "farms:write",
        "simulation:read",
        "community:read",
        "community:write",
        "accounting:read",
    ],
    "viewer": [
        "education:read",
        "farms:read",
        "simulation:read",
        "community:read",
        "accounting:read",
        "admin:read",
    ],
}


async def seed_rbac(session: AsyncSession) -> dict[str, int]:
    """Idempotent seed of roles, permissions, and links."""
    perm_by_code: dict[str, Permission] = {}
    for code, desc in DEFAULT_PERMISSIONS:
        result = await session.execute(select(Permission).where(Permission.code == code))
        perm = result.scalar_one_or_none()
        if not perm:
            perm = Permission(code=code, description=desc)
            session.add(perm)
            await session.flush()
        perm_by_code[code] = perm

    role_by_name: dict[str, Role] = {}
    for name, desc in DEFAULT_ROLES.items():
        result = await session.execute(select(Role).where(Role.name == name))
        role = result.scalar_one_or_none()
        if not role:
            role = Role(name=name, description=desc, is_system=True)
            session.add(role)
            await session.flush()
        role_by_name[name] = role

    links = 0
    for role_name, codes in ROLE_PERMISSION_MAP.items():
        role = role_by_name[role_name]
        for code in codes:
            perm = perm_by_code[code]
            result = await session.execute(
                select(RolePermission).where(
                    RolePermission.role_id == role.id,
                    RolePermission.permission_id == perm.id,
                )
            )
            if result.scalar_one_or_none() is None:
                session.add(RolePermission(role_id=role.id, permission_id=perm.id))
                links += 1

    await session.flush()
    return {
        "roles": len(role_by_name),
        "permissions": len(perm_by_code),
        "new_links": links,
    }
