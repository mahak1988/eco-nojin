"""Soil & Water Domain Models."""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class SoilAnalysis:
    location_lat: float
    location_lon: float
    soil_type: str
    organic_matter_percent: float
    moisture_content: float
    ph_level: float
    timestamp: datetime


@dataclass
class WaterBalance:
    date: datetime
    precipitation: float
    evapotranspiration: float
    runoff: float
    infiltration: float
    soil_moisture_change: float


@dataclass
class ErosionRisk:
    location_lat: float
    location_lon: float
    risk_level: str
    rusle_value: float
    contributing_factors: list
