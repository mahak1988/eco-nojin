# -*- coding: utf-8 -*-
"""
مدل‌های داده برای محاسبات کربن
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum


class CarbonPoolType(str, Enum):
    """انواع مخازن کربن"""
    ABOVE_GROUND = "above_ground"      # بالای زمین (تنه، شاخه)
    BELOW_GROUND = "below_ground"      # زیر زمین (ریشه)
    DEAD_WOOD = "dead_wood"            # چوب مرده
    LITTER = "litter"                  # برگ و بقایا
    SOIL_ORGANIC = "soil_organic"      # کربن آلی خاک


@dataclass
class CarbonPool:
    """مخزن کربن"""
    pool_type: CarbonPoolType
    carbon_tons: float
    area_hectares: float
    measurement_date: datetime = field(default_factory=datetime.utcnow)
    uncertainty_percent: float = 10.0
    source: str = "IPCC"
    
    @property
    def carbon_density(self) -> float:
        """چگالی کربن (تن در هکتار)"""
        if self.area_hectares <= 0:
            return 0.0
        return self.carbon_tons / self.area_hectares
    
    def to_co2_equivalent(self) -> float:
        """تبدیل به CO2 equivalent"""
        return self.carbon_tons * 3.67  # C to CO2 factor


@dataclass
class CarbonFlux:
    """شار کربن (تغییرات در طول زمان)"""
    pool_type: CarbonPoolType
    start_date: datetime
    end_date: datetime
    carbon_change_tons: float  # مثبت = جذب، منفی = انتشار
    
    @property
    def duration_days(self) -> int:
        return (self.end_date - self.start_date).days
    
    @property
    def annual_rate_tons(self) -> float:
        """نرخ سالانه (تن در سال)"""
        if self.duration_days <= 0:
            return 0.0
        return self.carbon_change_tons * 365 / self.duration_days
    
    def is_sequestration(self) -> bool:
        """آیا جذب کربن است؟"""
        return self.carbon_change_tons > 0