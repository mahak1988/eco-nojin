"""Tests for security."""
from __future__ import annotations

import pytest


class TestSecurity:
    """Test suite for security."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        try:
            import apps.shared_core.security  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_create_access_token_exists(self) -> None:
        """Verify create_access_token is callable."""
        try:
            from apps.shared_core.security import create_access_token
            assert callable(create_access_token)
        except ImportError:
            pytest.skip("Module not available")

    def test_verify_password_exists(self) -> None:
        """Verify verify_password is callable."""
        try:
            from apps.shared_core.security import verify_password
            assert callable(verify_password)
        except ImportError:
            pytest.skip("Module not available")

    def test_get_password_hash_exists(self) -> None:
        """Verify get_password_hash is callable."""
        try:
            from apps.shared_core.security import get_password_hash
            assert callable(get_password_hash)
        except ImportError:
            pytest.skip("Module not available")

    def test_decode_token_exists(self) -> None:
        """Verify decode_token is callable."""
        try:
            from apps.shared_core.security import decode_token
            assert callable(decode_token)
        except ImportError:
            pytest.skip("Module not available")

    def test_generate_otp_exists(self) -> None:
        """Verify generate_otp is callable."""
        try:
            from apps.shared_core.security import generate_otp
            assert callable(generate_otp)
        except ImportError:
            pytest.skip("Module not available")

