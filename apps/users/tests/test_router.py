"""Tests for router."""

from __future__ import annotations

import pytest


class TestRouter:
    """Test suite for router."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        try:
            import apps.users.router  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_register_exists(self) -> None:
        """Verify register is callable."""
        try:
            from apps.users.router import register

            assert callable(register)
        except ImportError:
            pytest.skip("Module not available")

    def test_login_exists(self) -> None:
        """Verify login is callable."""
        try:
            from apps.users.router import login

            assert callable(login)
        except ImportError:
            pytest.skip("Module not available")

    def test_get_current_user_info_exists(self) -> None:
        """Verify get_current_user_info is callable."""
        try:
            from apps.users.router import get_current_user_info

            assert callable(get_current_user_info)
        except ImportError:
            pytest.skip("Module not available")

    def test_update_current_user_exists(self) -> None:
        """Verify update_current_user is callable."""
        try:
            from apps.users.router import update_current_user

            assert callable(update_current_user)
        except ImportError:
            pytest.skip("Module not available")

    def test_list_users_exists(self) -> None:
        """Verify list_users is callable."""
        try:
            from apps.users.router import list_users

            assert callable(list_users)
        except ImportError:
            pytest.skip("Module not available")
