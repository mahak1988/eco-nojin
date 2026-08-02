"""Timezone-aware UTC helpers (replaces deprecated datetime.utcnow)."""

from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Return current UTC time as timezone-aware datetime."""
    return datetime.now(timezone.utc)
