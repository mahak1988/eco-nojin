"""Compatibility shim — Base lives in session.py; re-export for legacy imports."""

from apps.shared_core.database.session import Base

__all__ = ["Base"]
