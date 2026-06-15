"""Unit tests for hydrology domain"""
import pytest
from datetime import datetime
from api.services.hydrology.swat_wrapper import SWATWrapper
from api.services.hydrology.weap_wrapper import WEAPWrapper


class TestSWATWrapper:
    """تست‌های Wrapper SWAT"""
    
    def test_create_project(self):
        """تست ایجاد پروژه SWAT"""
        swat = SWATWrapper()
        
        result = swat.create_project(
            project_name="test_project",
            watershed_area_km2=100.0,
            elevation_range=(500, 1500),
            soil_types=["loam", "clay"],
            land_uses=["forest", "agriculture"]
        )
        
        assert "project_path" in result
        assert result["status"] == "created"
    
    def test_run_simulation(self):
        """تست اجرای شبیه‌سازی SWAT"""
        swat = SWATWrapper()
        
        # ایجاد پروژه
        swat.create_project(
            project_name="test_sim",
            watershed_area_km2=100.0,
            elevation_range=(500, 1500),
            soil_types=["loam"],
            land_uses=["agriculture"]
        )
        
        # اجرای شبیه‌سازی
        climate_data = {
            "precipitation_monthly": [50] * 120
        }
        
        result = swat.run_simulation(
            project_name="test_sim",
            start_year=2020,
            end_year=2029,
            climate_data=climate_data
        )
        
        assert "runoff_monthly" in result
        assert "water_balance" in result
        assert len(result["runoff_monthly"]) == 120  # 10 years * 12 months
    
    def test_get_water_yield(self):
        """تست محاسبه تولید آب"""
        swat = SWATWrapper()
        
        # ایجاد و اجرای پروژه
        swat.create_project(
            project_name="test_yield",
            watershed_area_km2=100.0,
            elevation_range=(500, 1500),
            soil_types=["loam"],
            land_uses=["agriculture"]
        )
        
        swat.run_simulation(
            project_name="test_yield",
            start_year=2020,
            end_year=2029,
            climate_data={"precipitation_monthly": [50] * 120}
        )
        
        # دریافت تولید آب
        result = swat.get_water_yield("test_yield", 2025)
        
        assert "year" in result
        assert "water_yield_mm" in result
        assert result["year"] == 2025


class TestWEAPWrapper:
    """تست‌های Wrapper WEAP"""
    
    def test_create_project(self):
        """تست ایجاد پروژه WEAP"""
        weap = WEAPWrapper()
        
        result = weap.create_project(
            project_name="test_weap",
            demand_sectors=["agriculture", "domestic"],
            water_sources=["surface", "groundwater"]
        )
        
        assert "project_path" in result
        assert result["status"] == "created"
    
    def test_run_allocation(self):
        """تست اجرای تخصیص آب"""
        weap = WEAPWrapper()
        
        # ایجاد پروژه
        weap.create_project(
            project_name="test_alloc",
            demand_sectors=["agriculture", "domestic"],
            water_sources=["surface"]
        )
        
        # داده‌های تقاضا و عرضه
        demand_data = {
            "agriculture": [100] * 5,
            "domestic": [50] * 5
        }
        
        supply_data = {
            "total_supply": [200] * 5
        }
        
        result = weap.run_allocation(
            project_name="test_alloc",
            start_year=2020,
            end_year=2024,
            demand_data=demand_data,
            supply_data=supply_data
        )
        
        assert "allocations" in result
        assert "performance_indicators" in result
        assert "reliability" in result["performance_indicators"]
    
    def test_analyze_scenario(self):
        """تست تحلیل سناریو"""
        weap = WEAPWrapper()
        
        # ایجاد پروژه
        weap.create_project(
            project_name="test_scenario",
            demand_sectors=["agriculture"],
            water_sources=["surface"]
        )
        
        result = weap.analyze_scenario(
            project_name="test_scenario",
            scenario_name="climate_change",
            climate_change={
                "precipitation_change_percent": -10,
                "temperature_change_c": 2.0
            },
            demand_growth={
                "annual_growth_percent": 2.0
            }
        )
        
        assert "scenario_name" in result
        assert "indicators" in result
        assert "water_stress_index" in result["indicators"]
        assert "recommendations" in result
