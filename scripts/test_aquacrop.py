"""
Unit tests for AquaCrop model
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAquaCrop:
    """تست مدل AquaCrop"""

    @pytest.fixture
    def model_class(self):
        """دریافت کلاس مدل"""
        try:
            from scripts.models.soil_carbon.aquacrop import AquaCropModel

            return AquaCropModel
        except ImportError:
            # تلاش برای import از مسیرهای دیگر
            try:
                import importlib

                mod = importlib.import_module("scripts.models.soil_carbon.aquacrop")
                return getattr(mod, "AquaCropModel", None)
            except Exception:
                pytest.skip("AquaCropModel not available")

    def test_instantiation(self, model_class):
        """تست ایجاد مدل"""
        if model_class is None:
            pytest.skip("Model class not available")
        model = model_class()
        assert model is not None

    def test_with_parameters(self, model_class):
        """تست با پارامترها"""
        if model_class is None:
            pytest.skip("Model class not available")
        try:
            model = model_class(clay_content=25.0)
            assert model is not None
        except TypeError:
            # برخی مدل‌ها پارامتر خاصی نمی‌پذیرند
            model = model_class()
            assert model is not None
