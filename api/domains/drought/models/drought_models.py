"""Drought Domain Models.

این ماژول شامل تعاریف مدل‌های داده‌ای مرتبط با خشکسالی است.
"""
from typing import Optional, List
from datetime import datetime
from dataclasses import dataclass


@dataclass
class DroughtIndex:
    """نماینده یک شاخص خشکسالی"""
    name: str
    value: float
    timestamp: datetime
    location_lat: float
    location_lon: float
    severity: Optional[str] = None


@dataclass
class SPEIValue:
    """مقدار شاخص SPEI"""
    station_id: str
    date: datetime
    value: float
    scale_months: int


@dataclass
class CHIRPSData:
    """داده‌های بارش CHIRPS"""
    date: datetime
    lat: float
    lon: float
    precipitation: float
    anomaly: Optional[float] = None
