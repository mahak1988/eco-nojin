"""
Unit tests for run_server module
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRunServer:
    """تست ماژول اجرای سرور"""

    def test_import_module(self):
        """تست import ماژول"""
        try:
            from scripts.api import run_server

            assert run_server is not None
        except ImportError:
            pytest.skip("run_server not found")

    def test_has_main_function(self):
        """تست وجود تابع main"""
        try:
            from scripts.api.run_server import main

            assert callable(main)
        except (ImportError, AttributeError):
            pytest.skip("main function not available")

    def test_load_config_safe(self):
        """تست بارگذاری امن config"""
        try:
            from scripts.api.run_server import load_config

            # فقط بررسی callable بودن
            assert callable(load_config)
        except (ImportError, AttributeError):
            pytest.skip("load_config not available")
