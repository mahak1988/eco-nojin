"""Integration tests for MRV system"""
import pytest
from datetime import datetime
from api.services.mrv.mrv_calculator import MRVCalculator
from api.services.mrv.carbon_credit_service import CarbonCreditService


def test_mrv_to_carbon_credit_workflow():
    """تست گردش کار کامل از محاسبه MRV تا صدور اعتبار کربن"""
    # مرحله 1: محاسبه MRV
    calculator = MRVCalculator()
    
    mrv_report = calculator.generate_mrv_report(
        project_id="integration_test_project",
        area_ha=200.0,
        land_use="agroforestry",
        climate_zone="temperate",
        initial_soc=25.0,
        final_soc=32.0,
        nitrogen_inputs={'organic_fertilizer': 2000.0},
        livestock_counts={'sheep': 50, 'goats': 30},
        initial_biomass=15.0,
        final_biomass=25.0,
        reporting_period_years=5
    )
    
    # مرحله 2: استخراج تراز خالص کربن
    net_balance = mrv_report['net_carbon_balance']
    assert net_balance['net_carbon_balance_tCO2e'] > 0
    
    # مرحله 3: صدور اعتبار کربن
    credit_service = CarbonCreditService()
    
    credit = credit_service.issue_carbon_credit(
        project_id="integration_test_project",
        volume_tCO2e=net_balance['net_carbon_balance_tCO2e'],
        verification_date=datetime.utcnow(),
        price_per_ton=30.0
    )
    
    # مرحله 4: تأیید
    assert credit['volume_tCO2e'] == net_balance['net_carbon_balance_tCO2e']
    assert credit['total_value'] > 0
    assert credit['status'] == 'VERIFIED'


def test_multiple_reporting_periods():
    """تست گزارش‌دهی در دوره‌های زمانی مختلف"""
    calculator = MRVCalculator()
    
    # سال اول
    report_year1 = calculator.generate_mrv_report(
        project_id="multi_year_project",
        area_ha=100.0,
        land_use="cropland",
        climate_zone="temperate",
        initial_soc=30.0,
        final_soc=31.0,
        nitrogen_inputs={'synthetic_fertilizer': 500.0},
        livestock_counts={'cattle': 10},
        initial_biomass=10.0,
        final_biomass=12.0,
        reporting_period_years=1
    )
    
    # سال دوم
    report_year2 = calculator.generate_mrv_report(
        project_id="multi_year_project",
        area_ha=100.0,
        land_use="cropland",
        climate_zone="temperate",
        initial_soc=31.0,
        final_soc=32.5,
        nitrogen_inputs={'synthetic_fertilizer': 500.0},
        livestock_counts={'cattle': 10},
        initial_biomass=12.0,
        final_biomass=15.0,
        reporting_period_years=1
    )
    
    # تأیید روند مثبت
    assert report_year2['net_carbon_balance']['net_carbon_balance_tCO2e'] >=            report_year1['net_carbon_balance']['net_carbon_balance_tCO2e']
