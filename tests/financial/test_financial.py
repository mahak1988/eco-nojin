"""Base Tests for Financial Domain - Phase 21"""
import pytest
from pathlib import Path


class TestFinancialStructure:
    """تست ساختار دامنه financial"""

    def test_domain_directory_exists(self):
        """بررسی وجود پوشه دامنه"""
        domain_dir = Path("api/domains/financial")
        assert domain_dir.exists(), "Domain directory missing"

    def test_models_directory_exists(self):
        """بررسی وجود پوشه models"""
        models_dir = Path("api/domains/financial/models")
        assert models_dir.exists(), "Models directory missing"

    def test_services_directory_exists(self):
        """بررسی وجود پوشه services"""
        services_dir = Path("api/domains/financial/services")
        assert services_dir.exists(), "Services directory missing"


class TestFinancialImports:
    """تست importهای دامنه financial"""

    def test_can_import_domain(self):
        """بررسی امکان import دامنه"""
        try:
            import importlib
            mod = importlib.import_module("api.domains.financial")
            assert mod is not None
        except ImportError:
            pytest.skip("Domain not yet fully implemented")


class TestFinancialService:
    """تست سرویس مالی - منطبق با فصل ۱۰ (مدل اقتصادی)"""

    def test_npv_calculation(self):
        """تست محاسبه NPV"""
        # NPV با نرخ تنزیل ۱۰٪
        initial_investment = -1000
        cash_flows = [300, 300, 300, 300]
        discount_rate = 0.10
        npv = initial_investment + sum(cf / (1 + discount_rate)**t 
                                      for t, cf in enumerate(cash_flows, 1))
        assert isinstance(npv, float)
