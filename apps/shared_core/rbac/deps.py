"""FastAPI dependencies for RBAC (R6)."""

from __future__ import annotations

from typing import Callable

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.database.session import get_db_session
from apps.shared_core.deps import get_current_active_user
from apps.shared_core.rbac.service import user_has_permission


def require_permission(code: str) -> Callable:
    """Decorator-style dependency: @router.get(..., dependencies=[Depends(require_permission('farms:write'))])."""

    async def _checker(
        current_user=Depends(get_current_active_user),
        session: AsyncSession = Depends(get_db_session),
    ):
        user_id = current_user.get("id") if isinstance(current_user, dict) else getattr(
            current_user, "id", None
        )
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
        # Superuser short-circuit
        if isinstance(current_user, dict) and current_user.get("is_superuser"):
            return current_user
        if hasattr(current_user, "is_superuser") and getattr(current_user, "is_superuser"):
            return current_user
        ok = await user_has_permission(session, int(user_id), code)
        if not ok:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "PERMISSION_DENIED",
                        "message": f"Missing permission: {code}",
                        "details": [{"permission": code}],
                    }
                },
            )
        return current_user

    return _checker
