"""IPCC AFOLU Emission Factors and Default Values

این ماژول شامل ضرایب انتشار و مقادیر پیش‌فرض IPCC برای محاسبات MRV است.
منابع:
- IPCC 2006 Guidelines for National Greenhouse Gas Inventories
- IPCC 2019 Refinement to the 2006 IPCC Guidelines
- ISO 14064-2:2019
"""
from typing import Dict


class IPCCFactors:
    """ضرایب و مقادیر پیش‌فرض IPCC AFOLU"""
    
    # ضرایب تبدیل کربن به CO2
    CARBON_TO_CO2 = 44.0 / 12.0  # 3.67
    
    # ضرایب پتانسیل گرمایش جهانی (GWP) برای دوره 100 ساله
    GWP_100 = {
        'CO2': 1.0,
        'CH4': 28.0,  # AR5
        'N2O': 265.0,  # AR5
    }
    
    # ضرایب انتشار N2O از خاک کشاورزی (kg N2O-N / kg N input)
    N2O_EMISSION_FACTORS = {
        'synthetic_fertilizer': 0.01,  # EF1
        'organic_fertilizer': 0.01,  # EF1
        'crop_residues': 0.01,  # EF2
        'mineralization': 0.01,  # EF3
    }
    
    # ضرایب انتشار CH4 از مدیریت کود دامی (kg CH4 / head / year)
    CH4_MANURE_MANAGEMENT = {
        'cattle': 1.0,
        'sheep': 0.15,
        'goats': 0.1,
        'poultry': 0.02,
    }
    
    # ضرایب انتشار CH4 از تخمیر enteric (kg CH4 / head / year)
    CH4_ENTERIC_FERMENTATION = {
        'cattle_dairy': 116.0,
        'cattle_other': 55.0,
        'sheep': 11.0,
        'goats': 5.0,
    }
    
    # مقادیر پیش‌فرض کربن آلی خاک (SOC) بر اساس نوع کاربری اراضی (t C/ha)
    DEFAULT_SOC_STOCKS = {
        'cropland': {
            'tropical': 30.0,
            'temperate': 50.0,
            'boreal': 80.0,
        },
        'grassland': {
            'tropical': 40.0,
            'temperate': 70.0,
            'boreal': 100.0,
        },
        'forest': {
            'tropical': 80.0,
            'temperate': 120.0,
            'boreal': 150.0,
        },
        'wetland': {
            'tropical': 200.0,
            'temperate': 250.0,
            'boreal': 300.0,
        },
    }
    
    # فاکتورهای تغییر کاربری اراضی (FLU)
    LAND_USE_CHANGE_FACTORS = {
        'forest_to_cropland': 0.69,
        'forest_to_grassland': 0.85,
        'cropland_to_forest': 1.25,
        'cropland_to_grassland': 1.10,
        'grassland_to_forest': 1.15,
        'grassland_to_cropland': 0.90,
    }
    
    # فاکتورهای مدیریت خاک (FMG)
    MANAGEMENT_FACTORS = {
        'conventional_tillage': 1.0,
        'reduced_tillage': 1.10,
        'no_till': 1.15,
        'cover_crops': 1.12,
        'agroforestry': 1.20,
        'organic_amendments': 1.18,
    }
    
    # فاکتورهای ورودی (FI) برای ماده آلی
    INPUT_FACTORS = {
        'low': 0.95,
        'medium': 1.00,
        'high': 1.05,
        'very_high': 1.10,
    }
    
    @classmethod
    def get_soc_reference(cls, climate_zone: str, land_use: str) -> float:
        """دریافت مقدار مرجع SOC بر اساس اقلیم و کاربری اراضی"""
        if land_use in cls.DEFAULT_SOC_STOCKS:
            return cls.DEFAULT_SOC_STOCKS[land_use].get(climate_zone, 50.0)
        return 50.0
    
    @classmethod
    def convert_carbon_to_co2(cls, carbon_tonnes: float) -> float:
        """تبدیل تن کربن به تن CO2"""
        return carbon_tonnes * cls.CARBON_TO_CO2
    
    @classmethod
    def convert_co2_to_carbon(cls, co2_tonnes: float) -> float:
        """تبدیل تن CO2 به تن کربن"""
        return co2_tonnes / cls.CARBON_TO_CO2
    
    @classmethod
    def calculate_co2_equivalent(
        cls,
        co2: float,
        ch4: float,
        n2o: float
    ) -> float:
        """محاسبه CO2 معادل بر اساس GWP"""
        return (
            co2 * cls.GWP_100['CO2'] +
            ch4 * cls.GWP_100['CH4'] +
            n2o * cls.GWP_100['N2O']
        )
