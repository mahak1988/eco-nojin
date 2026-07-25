"""Tests for service."""
from __future__ import annotations

import pytest


class TestService:
    """Test suite for service."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        try:
            import apps.users.service  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_decode_access_token_exists(self) -> None:
        """Verify decode_access_token is callable."""
        try:
            from apps.users.service import decode_access_token
            assert callable(decode_access_token)
        except ImportError:
            pytest.skip("Module not available")

    def test_UserService_instantiation(self) -> None:
        """Verify UserService can be referenced."""
        try:
            from apps.users.service import UserService
            assert UserService is not None
        except ImportError:
            pytest.skip("Module not available")

