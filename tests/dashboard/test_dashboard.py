"""Unit tests for dashboard domain"""
import pytest
from datetime import datetime
from api.domains.dashboard.services.dss_service import DSSService
from api.domains.dashboard.services.dashboard_service import DashboardService


class TestDSSService:
    """تست‌های سامانه تصمیم‌یار"""
    
    def test_evaluate_water_stress_critical(self):
        """تست ارزیابی تنش آبی بحرانی"""
        dss = DSSService()
        
        result = dss.evaluate_water_stress(
            wue=0.3,
            groundwater_level_m=3.0,
            precipitation_anomaly_percent=-40
        )
        
        assert result["severity"] == "critical"
        assert len(result["recommendations"]) > 0
        assert "WATER_STRESS" in result["assessment"]
    
    def test_evaluate_water_stress_warning(self):
        """تست ارزیابی تنش آبی هشدار"""
        dss = DSSService()
        
        result = dss.evaluate_water_stress(
            wue=0.8,
            groundwater_level_m=12.0,
            precipitation_anomaly_percent=-20
        )
        
        assert result["severity"] == "warning"
        assert len(result["recommendations"]) > 0
    
    def test_evaluate_soil_health_critical(self):
        """تست ارزیابی سلامت خاک بحرانی"""
        dss = DSSService()
        
        result = dss.evaluate_soil_health(
            soc_percent=0.8,
            erosion_rate_t_ha_year=25.0,
            salinity_ds_m=10.0
        )
        
        assert result["severity"] == "critical"
        assert len(result["recommendations"]) > 0
    
    def test_evaluate_livelihood_resilience(self):
        """تست ارزیابی تاب‌آوری معیشت"""
        dss = DSSService()
        
        result = dss.evaluate_livelihood_resilience(
            income_diversity_index=0.4,
            food_security_score=65.0,
            poverty_rate_percent=25.0
        )
        
        assert "LIVELIHOOD_RESILIENCE" in result["assessment"]
        assert len(result["recommendations"]) > 0
    
    def test_evaluate_carbon_balance(self):
        """تست ارزیابی تراز کربن"""
        dss = DSSService()
        
        result = dss.evaluate_carbon_balance(
            net_carbon_balance_tCO2e=150.0,
            soc_sequestration_tCO2=200.0,
            emissions_tCO2e=50.0
        )
        
        assert "CARBON_BALANCE" in result["assessment"]
        assert len(result["recommendations"]) > 0
    
    def test_generate_comprehensive_recommendation(self):
        """تست تولید توصیه جامع"""
        dss = DSSService()
        
        water_assessment = dss.evaluate_water_stress(1.2, 12.5, -10)
        soil_assessment = dss.evaluate_soil_health(2.3, 8.5, 2.5)
        livelihood_assessment = dss.evaluate_livelihood_resilience(0.6, 75.0, 15.0)
        carbon_assessment = dss.evaluate_carbon_balance(150.0, 200.0, 50.0)
        
        result = dss.generate_comprehensive_recommendation(
            watershed_id="test_watershed",
            water_assessment=water_assessment,
            soil_assessment=soil_assessment,
            livelihood_assessment=livelihood_assessment,
            carbon_assessment=carbon_assessment
        )
        
        assert "watershed_id" in result
        assert "overall_severity" in result
        assert "priority_recommendations" in result
        assert len(result["priority_recommendations"]) > 0


class TestDashboardService:
    """تست‌های سرویس داشبوردها"""
    
    def test_get_watershed_manager_dashboard(self):
        """تست داشبورد مدیر حوضه"""
        service = DashboardService()
        
        dashboard = service.get_watershed_manager_dashboard("test_watershed")
        
        assert dashboard["dashboard_type"] == "watershed_manager"
        assert "widgets" in dashboard
        assert len(dashboard["widgets"]) > 0
        assert "recommendations" in dashboard
    
    def test_get_farmer_dashboard(self):
        """تست داشبورد کشاورز"""
        service = DashboardService()
        
        dashboard = service.get_farmer_dashboard("farmer_001", "farm_001")
        
        assert dashboard["dashboard_type"] == "farmer"
        assert "widgets" in dashboard
        assert len(dashboard["widgets"]) > 0
    
    def test_get_investor_dashboard(self):
        """تست داشبورد سرمایه‌گذار"""
        service = DashboardService()
        
        dashboard = service.get_investor_dashboard("project_001")
        
        assert dashboard["dashboard_type"] == "investor"
        assert "widgets" in dashboard
        assert len(dashboard["widgets"]) > 0
    
    def test_get_policy_maker_dashboard(self):
        """تست داشبورد سیاست‌گذار"""
        service = DashboardService()
        
        dashboard = service.get_policy_maker_dashboard("region_001")
        
        assert dashboard["dashboard_type"] == "policy_maker"
        assert "widgets" in dashboard
        assert len(dashboard["widgets"]) > 0
