"""
User Module Exceptions
======================
Standard authentication exceptions for consistent error handling.
Based on patterns from fastapi-best-practices.
"""

import logging

logger = logging.getLogger(__name__)
from fastapi import HTTPException, status


class AuthExceptions:
    """
    Standard authentication exceptions.
    Use these instead of inline HTTPException for consistency.
    """

    InvalidCredentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    TokenExpired = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token has expired",
        headers={"WWW-Authenticate": "Bearer"},
    )

    AccountLocked = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Account is locked or inactive",
    )

    UserNotFound = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="User not found",
    )

    EmailExists = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Email already registered",
    )


# Convenience exports
def raise_invalid_credentials() -> None:
    """Raise invalid credentials exception."""
    raise AuthExceptions.InvalidCredentials


def raise_token_expired() -> None:
    """Raise token expired exception."""
    raise AuthExceptions.TokenExpired


def raise_account_locked() -> None:
    """Raise account locked exception."""
    raise AuthExceptions.AccountLocked
