"""FastAPI dependencies for RBAC (R6)."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from apps.shared_core.config import settings
from apps.shared_core.database.session import get_db_session
from apps.shared_core.deps import TokenDep, _extract_token, get_current_user
from apps.shared_core.rbac.service import user_has_permission


def require_permission(code: str) -> Callable:
    """Protect endpoint with permission code e.g. education:write."""

    async def _checker(
        request: Request,
        token: TokenDep,
        session: AsyncSession = Depends(get_db_session),
    ) -> dict[str, Any] | None:
        # Local soft mode: same gate as require_write_auth
        if not settings.REQUIRE_AUTH_FOR_WRITES and settings.ENVIRONMENT == "local":
            return None

        raw = _extract_token(request, token)
        if not raw:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )

        current_user = await get_current_user(request, session, raw)
        if current_user.get("is_superuser"):
            return current_user

        user_id = current_user.get("id")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

        try:
            uid = int(user_id)
        except (TypeError, ValueError):
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

        ok = await user_has_permission(session, uid, code)
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
