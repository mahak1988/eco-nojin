"""
Unit tests for SWAT+ hydrological model
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.models.hydrology.swat_plus import SWATPlusModel


class TestSWATPlusModel:
    """تست مدل SWAT+"""

    @pytest.fixture
    def model(self):
        """ایجاد نمونه مدل"""
        return SWATPlusModel()

    def test_instantiation(self, model):
        """تست ایجاد مدل"""
        assert model is not None

    def test_has_config(self, model):
        """تست وجود پیکربندی"""
        assert hasattr(model, "config")
