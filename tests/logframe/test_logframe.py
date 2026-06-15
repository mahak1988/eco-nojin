"""LogFrame Integration Tests"""
import pytest
from api.domains.logframe.services.logframe_service import LogFrameService
from api.services.reporting.international_reporting_service import InternationalReportingService


class TestLogFrameService:
    def test_logframe_initialization(self):
        """تست مقداردهی LogFrame"""
        service = LogFrameService()
        logframe = service.get_logframe()
        
        assert logframe["total_entries"] >= 7
        assert logframe["impact"] == 1
        assert logframe["outcomes"] >= 6
    
    def test_sdg_indicators(self):
        """تست شاخص‌های SDG"""
        service = LogFrameService()
        
        sdg_6 = service.get_indicators_by_sdg("6")
        assert len(sdg_6) >= 3
        
        sdg_13 = service.get_indicators_by_sdg("13")
        assert len(sdg_13) >= 2
    
    def test_gef_core_indicators(self):
        """تست شاخص‌های Core GEF"""
        service = LogFrameService()
        gef = service.get_gef_core_indicators()
        
        assert len(gef) >= 5
        assert all("methodology" in i for i in gef)
    
    def test_gcf_core_indicators(self):
        """تست شاخص‌های Core GCF"""
        service = LogFrameService()
        gcf = service.get_gcf_core_indicators()
        
        assert len(gcf) >= 8
        assert any("tCO2e" in i["unit"] for i in gcf)
    
    def test_ndc_report_generation(self):
        """تست تولید گزارش NDC"""
        service = LogFrameService()
        report = service.generate_ndc_report("test_project", 2025)
        
        assert "mitigation_contribution" in report
        assert "adaptation_contribution" in report
        assert report["methodology"] == "IPCC AFOLU Tier 2"
        assert report["status"] == "ready_for_unfccc_submission"


class TestInternationalReporting:
    def test_unfccc_report(self):
        """تست گزارش UNFCCC"""
        service = InternationalReportingService()
        report = service.generate_unfccc_biennial_report("test_project")
        
        assert report["convention"] == "UNFCCC"
        assert "ghg_inventory" in report
        assert report["methodology"] == "IPCC 2019 Refinement Tier 2"
    
    def test_gcf_report(self):
        """تست گزارش GCF"""
        service = InternationalReportingService()
        report = service.generate_gcf_performance_report("test_project")
        
        assert report["fund"] == "Green Climate Fund"
        assert "paradigm_shift_potential" in report
        assert "impact_potential" in report
    
    def test_gef_report(self):
        """تست گزارش GEF"""
        service = InternationalReportingService()
        report = service.generate_gef_tracking_tool("test_project")
        
        assert report["fund"] == "Global Environment Facility"
        assert "focal_areas" in report
        assert "land_degradation" in report["focal_areas"]
    
    def test_unccd_report(self):
        """تست گزارش UNCCD"""
        service = InternationalReportingService()
        report = service.generate_unccd_prais_report("test_project")
        
        assert report["convention"] == "UNCCD"
        assert "ldn_targets" in report
        assert report["ldn_targets"]["ldn_achieved"] == True
    
    def test_sdg_report(self):
        """تست گزارش SDG"""
        service = InternationalReportingService()
        report = service.generate_sdg_progress_report("test_project")
        
        assert "sdgs" in report
        assert "SDG_2_zero_hunger" in report["sdgs"]
        assert "SDG_15_life_on_land" in report["sdgs"]
