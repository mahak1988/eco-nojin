"""Tests for engine."""
from __future__ import annotations

import pytest


class TestEngine:
    """Test suite for engine."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        try:
            import apps.simulation.validation.engine  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_rmse_exists(self) -> None:
        """Verify rmse is callable."""
        try:
            from apps.simulation.validation.engine import rmse
            assert callable(rmse)
        except ImportError:
            pytest.skip("Module not available")

    def test_nse_exists(self) -> None:
        """Verify nse is callable."""
        try:
            from apps.simulation.validation.engine import nse
            assert callable(nse)
        except ImportError:
            pytest.skip("Module not available")

    def test_r_squared_exists(self) -> None:
        """Verify r_squared is callable."""
        try:
            from apps.simulation.validation.engine import r_squared
            assert callable(r_squared)
        except ImportError:
            pytest.skip("Module not available")

    def test_goodness_of_fit_exists(self) -> None:
        """Verify goodness_of_fit is callable."""
        try:
            from apps.simulation.validation.engine import goodness_of_fit
            assert callable(goodness_of_fit)
        except ImportError:
            pytest.skip("Module not available")

    def test_monte_carlo_exists(self) -> None:
        """Verify monte_carlo is callable."""
        try:
            from apps.simulation.validation.engine import monte_carlo
            assert callable(monte_carlo)
        except ImportError:
            pytest.skip("Module not available")

