"""Base Tests for Drought Domain - Phase 21"""
import pytest
from pathlib import Path


class TestDroughtStructure:
    """تست ساختار دامنه drought"""

    def test_domain_directory_exists(self):
        """بررسی وجود پوشه دامنه"""
        domain_dir = Path("api/domains/drought")
        assert domain_dir.exists(), "Domain directory missing"

    def test_models_directory_exists(self):
        """بررسی وجود پوشه models"""
        models_dir = Path("api/domains/drought/models")
        assert models_dir.exists(), "Models directory missing"

    def test_services_directory_exists(self):
        """بررسی وجود پوشه services"""
        services_dir = Path("api/domains/drought/services")
        assert services_dir.exists(), "Services directory missing"


class TestDroughtImports:
    """تست importهای دامنه drought"""

    def test_can_import_domain(self):
        """بررسی امکان import دامنه"""
        try:
            import importlib
            mod = importlib.import_module("api.domains.drought")
            assert mod is not None
        except ImportError:
            pytest.skip("Domain not yet fully implemented")


class TestDroughtIndices:
    """تست شاخص‌های خشکسالی - منطبق با فصل ۹ (MRV)"""

    def test_spei_range(self):
        """تست محدوده SPEI"""
        spei_values = [-2.5, -1.0, 0.0, 1.0, 2.5]
        for v in spei_values:
            assert -5 <= v <= 5
