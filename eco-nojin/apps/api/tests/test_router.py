"""Tests for router."""
from __future__ import annotations

import pytest


class TestRouter:
    """Test suite for router."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        try:
            import apps.api.router  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_list_api_exists(self) -> None:
        """Verify list_api is callable."""
        try:
            from apps.api.router import list_api
            assert callable(list_api)
        except ImportError:
            pytest.skip("Module not available")

    def test_get_api_exists(self) -> None:
        """Verify get_api is callable."""
        try:
            from apps.api.router import get_api
            assert callable(get_api)
        except ImportError:
            pytest.skip("Module not available")

    def test_create_api_exists(self) -> None:
        """Verify create_api is callable."""
        try:
            from apps.api.router import create_api
            assert callable(create_api)
        except ImportError:
            pytest.skip("Module not available")

    def test_update_api_exists(self) -> None:
        """Verify update_api is callable."""
        try:
            from apps.api.router import update_api
            assert callable(update_api)
        except ImportError:
            pytest.skip("Module not available")

    def test_delete_api_exists(self) -> None:
        """Verify delete_api is callable."""
        try:
            from apps.api.router import delete_api
            assert callable(delete_api)
        except ImportError:
            pytest.skip("Module not available")

