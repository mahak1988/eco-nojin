"""Unit tests for MRV calculations"""
import pytest
from datetime import datetime
from api.services.mrv.mrv_calculator import MRVCalculator
from api.services.mrv.ipcc_factors import IPCCFactors
from api.services.mrv.carbon_credit_service import CarbonCreditService


class TestIPCCFactors:
    """تست‌های فاکتورها و ضرایب IPCC"""
    
    def test_carbon_to_co2_conversion(self):
        """تست تبدیل کربن به CO2"""
        carbon = 100.0  # تن کربن
        co2 = IPCCFactors.convert_carbon_to_co2(carbon)
        assert co2 == pytest.approx(367.0, rel=0.01)
    
    def test_co2_to_carbon_conversion(self):
        """تست تبدیل CO2 به کربن"""
        co2 = 367.0  # تن CO2
        carbon = IPCCFactors.convert_co2_to_carbon(co2)
        assert carbon == pytest.approx(100.0, rel=0.01)
    
    def test_co2_equivalent_calculation(self):
        """تست محاسبه CO2 معادل"""
        co2_eq = IPCCFactors.calculate_co2_equivalent(
            co2=100.0,
            ch4=10.0,
            n2o=1.0
        )
        # 100*1 + 10*28 + 1*265 = 100 + 280 + 265 = 645
        assert co2_eq == pytest.approx(645.0, rel=0.01)
    
    def test_get_soc_reference(self):
        """تست دریافت مقدار مرجع SOC"""
        soc = IPCCFactors.get_soc_reference('temperate', 'forest')
        assert soc == 120.0


class TestMRVCalculator:
    """تست‌های ماشین حساب MRV"""
    
    def test_soc_change_calculation(self):
        """تست محاسبه تغییرات SOC"""
        calculator = MRVCalculator()
        
        result = calculator.calculate_soc_change(
            initial_soc=30.0,
            final_soc=35.0,
            area_ha=100.0,
            time_period_years=20
        )
        
        assert result['total_soc_change_tC'] == 500.0
        assert result['total_co2_sequestered_tCO2'] > 0
        assert result['annual_soc_change_tC_ha_year'] > 0
    
    def test_n2o_emissions_calculation(self):
        """تست محاسبه انتشار N2O"""
        calculator = MRVCalculator()
        
        nitrogen_inputs = {
            'synthetic_fertilizer': 1000.0,
            'organic_fertilizer': 500.0
        }
        
        result = calculator.calculate_n2o_emissions(nitrogen_inputs)
        
        assert result['total_nitrogen_input_kg'] == 1500.0
        assert result['n2o_emissions_kg'] > 0
        assert result['co2_equivalent_kg'] > 0
    
    def test_ch4_emissions_calculation(self):
        """تست محاسبه انتشار CH4"""
        calculator = MRVCalculator()
        
        livestock_counts = {
            'cattle': 50,
            'sheep': 100
        }
        
        result = calculator.calculate_ch4_emissions(livestock_counts)
        
        assert result['ch4_emissions_kg'] > 0
        assert result['co2_equivalent_kg'] > 0
    
    def test_biomass_carbon_sequestration(self):
        """تست محاسبه ترسیب کربن زیست‌توده"""
        calculator = MRVCalculator()
        
        result = calculator.calculate_biomass_carbon_sequestration(
            initial_biomass_carbon=10.0,
            final_biomass_carbon=15.0,
            area_ha=50.0,
            years=5
        )
        
        assert result['carbon_change_tC'] == 250.0
        assert result['co2_sequestered_tCO2'] > 0
    
    def test_net_carbon_balance(self):
        """تست محاسبه تراز خالص کربن"""
        calculator = MRVCalculator()
        
        result = calculator.calculate_net_carbon_balance(
            soc_sequestration_tCO2=1000.0,
            biomass_sequestration_tCO2=500.0,
            n2o_emissions_tCO2e=200.0,
            ch4_emissions_tCO2e=100.0
        )
        
        assert result['total_sequestration_tCO2'] == 1500.0
        assert result['total_emissions_tCO2e'] == 300.0
        assert result['net_carbon_balance_tCO2e'] == 1200.0
        assert result['is_carbon_negative'] == True
    
    def test_full_mrv_report(self):
        """تست تولید گزارش کامل MRV"""
        calculator = MRVCalculator()
        
        report = calculator.generate_mrv_report(
            project_id="test_project_001",
            area_ha=100.0,
            land_use="cropland",
            climate_zone="temperate",
            initial_soc=30.0,
            final_soc=35.0,
            nitrogen_inputs={'synthetic_fertilizer': 1000.0},
            livestock_counts={'cattle': 20},
            initial_biomass=10.0,
            final_biomass=15.0,
            reporting_period_years=1
        )
        
        assert report['project_id'] == "test_project_001"
        assert 'soc_analysis' in report
        assert 'n2o_analysis' in report
        assert 'ch4_analysis' in report
        assert 'biomass_analysis' in report
        assert 'net_carbon_balance' in report
        assert report['methodology'] == 'IPCC AFOLU Tier 1'


class TestCarbonCreditService:
    """تست‌های سرویس اعتبار کربن"""
    
    def test_issue_carbon_credit(self):
        """تست صدور اعتبار کربن"""
        service = CarbonCreditService()
        
        credit = service.issue_carbon_credit(
            project_id="test_project_001",
            volume_tCO2e=1000.0,
            verification_date=datetime.utcnow(),
            price_per_ton=25.0
        )
        
        assert credit['project_id'] == "test_project_001"
        assert credit['volume_tCO2e'] == 1000.0
        assert credit['total_value'] == 25000.0
        assert credit['status'] == 'VERIFIED'
    
    def test_get_project_credits(self):
        """تست دریافت اعتبارات پروژه"""
        service = CarbonCreditService()
        
        # صدور چند اعتبار
        service.issue_carbon_credit("project_001", 500.0, datetime.utcnow())
        service.issue_carbon_credit("project_001", 300.0, datetime.utcnow())
        service.issue_carbon_credit("project_002", 200.0, datetime.utcnow())
        
        credits = service.get_project_credits("project_001")
        
        assert len(credits) == 2
        assert all(c['project_id'] == "project_001" for c in credits)
    
    def test_get_total_issued_volume(self):
        """تست محاسبه حجم کل اعتبارات"""
        service = CarbonCreditService()
        
        service.issue_carbon_credit("project_001", 500.0, datetime.utcnow())
        service.issue_carbon_credit("project_001", 300.0, datetime.utcnow())
        
        total = service.get_total_issued_volume("project_001")
        
        assert total == 800.0
