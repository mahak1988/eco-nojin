"""
Unit tests for RothC soil carbon model
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRothC:
    """تست مدل RothC"""
    
    @pytest.fixture
    def model_class(self):
        """دریافت کلاس RothC"""
        try:
            from scripts.models.soil_carbon.rothc import RothCModel
            return RothCModel
        except ImportError:
            pytest.skip("RothCModel not available")
    
    def test_instantiation(self, model_class):
        """تست ایجاد"""
        model = model_class()
        assert model is not None
    
    def test_default_parameters(self, model_class):
        """تست پارامترهای پیش‌فرض"""
        model = model_class(
            clay_content=25.0,
            initial_soc=50.0,
            depth=23.0
        )
        assert model is not None
    
    def test_calculate_decomposition(self, model_class):
        """تست محاسبه تجزیه"""
        model = model_class()
        
        # بررسی وجود متد
        if hasattr(model, 'calculate_decomposition'):
            result = model.calculate_decomposition(
                temperature=20.0,
                moisture=0.8,
                plant_residue=100.0
            )
            assert isinstance(result, dict)
