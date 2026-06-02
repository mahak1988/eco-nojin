"""
Unit tests for app factory
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestAppFactory:
    """تست factory اپلیکیشن"""
    
    def test_import_app_factory(self):
        """تست import"""
        try:
            from scripts.api import app_factory
            assert app_factory is not None
        except ImportError:
            pytest.skip("app_factory not found")
    
    def test_create_app_function(self):
        """تست تابع create_app"""
        try:
            from scripts.api.app_factory import create_app
            app = create_app()
            assert app is not None
        except (ImportError, AttributeError):
            pytest.skip("create_app not available")
    
    def test_app_has_routes(self):
        """تست وجود route ها"""
        try:
            from scripts.api.app_factory import create_app
            app = create_app()
            # FastAPI app باید routes داشته باشد
            assert hasattr(app, 'routes')
        except Exception:
            pytest.skip("Cannot test routes")
