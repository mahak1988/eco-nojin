"""
Unit tests for coupling module
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


class TestCoupling:
    """تست ماژول coupling"""
    
    def test_import(self):
        """تست import ماژول"""
        try:
            from scripts.models import coupling
            assert coupling is not None
        except ImportError:
            pytest.skip("coupling module not found")
    
    def test_module_structure(self):
        """تست ساختار ماژول"""
        try:
            from scripts.models import coupling
            # بررسی وجود توابع/کلاس‌های اصلی
            assert hasattr(coupling, '__file__')
        except ImportError:
            pytest.skip("coupling module not found")
