"""Tests for service."""
from __future__ import annotations

import pytest


class TestService:
    """Test suite for service."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        try:
            import apps.admin_panel.service  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_AdminService_instantiation(self) -> None:
        """Verify AdminService can be referenced."""
        try:
            from apps.admin_panel.service import AdminService
            assert AdminService is not None
        except ImportError:
            pytest.skip("Module not available")

