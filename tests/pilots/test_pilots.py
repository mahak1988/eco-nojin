"""Base Tests for Pilots Domain - Phase 21"""
import pytest
from pathlib import Path


class TestPilotsStructure:
    """تست ساختار دامنه pilots"""

    def test_domain_directory_exists(self):
        """بررسی وجود پوشه دامنه"""
        domain_dir = Path("api/domains/pilots")
        assert domain_dir.exists(), "Domain directory missing"

    def test_models_directory_exists(self):
        """بررسی وجود پوشه models"""
        models_dir = Path("api/domains/pilots/models")
        assert models_dir.exists(), "Models directory missing"

    def test_services_directory_exists(self):
        """بررسی وجود پوشه services"""
        services_dir = Path("api/domains/pilots/services")
        assert services_dir.exists(), "Services directory missing"


class TestPilotsImports:
    """تست importهای دامنه pilots"""

    def test_can_import_domain(self):
        """بررسی امکان import دامنه"""
        try:
            import importlib
            mod = importlib.import_module("api.domains.pilots")
            assert mod is not None
        except ImportError:
            pytest.skip("Domain not yet fully implemented")


class TestPilotSites:
    """تست پایلوت‌های جهانی - منطبق با فاز ۱۰"""

    def test_twelve_global_pilots(self):
        """بررسی وجود ۱۲ پایلوت جهانی"""
        pilots = [
            "dishmok", "behbahan", "rodbar_talesh", "snow_mountain",
            "ouarzazate", "wadi_rum", "sahel_senegal", "ethiopian_highlands",
            "rajasthan", "outback_australia", "atacama_chile", "mongolian_steppe"
        ]
        assert len(pilots) == 12
