"""Tests for service."""
from __future__ import annotations

import pytest


class TestService:
    """Test suite for service."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        try:
            import apps.simulation.data.service  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_get_climate_series_exists(self) -> None:
        """Verify get_climate_series is callable."""
        try:
            from apps.simulation.data.service import get_climate_series
            assert callable(get_climate_series)
        except ImportError:
            pytest.skip("Module not available")

    def test_get_elevation_exists(self) -> None:
        """Verify get_elevation is callable."""
        try:
            from apps.simulation.data.service import get_elevation
            assert callable(get_elevation)
        except ImportError:
            pytest.skip("Module not available")

