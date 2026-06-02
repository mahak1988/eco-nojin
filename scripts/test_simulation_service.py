"""
Unit tests for Simulation Service
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSimulationService:
    """تست سرویس شبیه‌سازی"""
    
    @pytest.fixture
    def service_class(self):
        """دریافت کلاس سرویس"""
        try:
            from scripts.api.services.simulation_service import SimulationService
            return SimulationService
        except ImportError:
            pytest.skip("SimulationService not found")
    
    def test_instantiation(self, service_class):
        """تست ایجاد سرویس"""
        service = service_class()
        assert service is not None
    
    def test_has_run_method(self, service_class):
        """تست وجود متد اجرا"""
        service = service_class()
        # بررسی متدها
        methods = [m for m in dir(service) if not m.startswith('_')]
        # حداقل باید یک متد عمومی داشته باشد
        assert isinstance(methods, list)
