"""مدل‌های داده‌ای سنجش‌ازدور"""
from dataclasses import dataclass
from typing import Optional, Dict
from datetime import datetime


@dataclass
class SatelliteImage:
    """نماینده یک تصویر ماهواره‌ای"""
    image_id: str
    satellite: str  # Sentinel-2, Landsat, MODIS
    acquisition_date: datetime
    cloud_cover: float
    bounding_box: Dict  # lat_min, lat_max, lon_min, lon_max
    bands: Dict[str, str]  # band_name -> file_path


@dataclass
class SpectralIndex:
    """نماینده یک شاخص طیفی"""
    index_id: str
    index_type: str  # NDVI, EVI, NDWI, NDSI
    image_id: str
    values: str  # مسیر فایل یا serialized array
    statistics: Dict  # mean, min, max, std
    calculated_at: datetime


@dataclass
class VegetationHealth:
    """نماینده سلامت پوشش گیاهی"""
    location_lat: float
    location_lon: float
    ndvi: float
    health_class: int  # 1-5
    analysis_date: datetime
    satellite: str
