"""سرویس Sentinel-2 برای دریافت و پردازش تصاویر ماهواره‌ای

Sentinel-2 دارای 13 باند طیفی با رزولوشن‌های 10m، 20m و 60m است.
باندهای کلیدی:
- B2 (Blue): 490nm
- B3 (Green): 560nm
- B4 (Red): 665nm
- B8 (NIR): 842nm
- B11 (SWIR): 1610nm
"""
import os
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from pathlib import Path


class Sentinel2Service:
    """سرویس پردازش تصاویر Sentinel-2"""
    
    # باندهای Sentinel-2 و رزولوشن آن‌ها
    BANDS = {
        'B2': {'name': 'Blue', 'resolution': 10, 'wavelength': 490},
        'B3': {'name': 'Green', 'resolution': 10, 'wavelength': 560},
        'B4': {'name': 'Red', 'resolution': 10, 'wavelength': 665},
        'B8': {'name': 'NIR', 'resolution': 10, 'wavelength': 842},
        'B11': {'name': 'SWIR', 'resolution': 20, 'wavelength': 1610},
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('SENTINEL_HUB_API_KEY')
        self.base_url = 'https://services.sentinel-hub.com'
    
    def get_band_combination_for_ndvi(self) -> Dict[str, str]:
        """دریافت ترکیب باندهای مورد نیاز برای NDVI"""
        return {
            'nir': 'B8',
            'red': 'B4'
        }
    
    def get_band_combination_for_evi(self) -> Dict[str, str]:
        """دریافت ترکیب باندهای مورد نیاز برای EVI"""
        return {
            'nir': 'B8',
            'red': 'B4',
            'blue': 'B2'
        }
    
    def get_band_combination_for_ndwi(self) -> Dict[str, str]:
        """دریافت ترکیب باندهای مورد نیاز برای NDWI"""
        return {
            'green': 'B3',
            'nir': 'B8'
        }
    
    def get_band_combination_for_ndsi(self) -> Dict[str, str]:
        """دریافت ترکیب باندهای مورد نیاز برای NDSI"""
        return {
            'green': 'B3',
            'swir': 'B11'
        }
    
    def calculate_ndvi_from_bands(
        self,
        nir_band: np.ndarray,
        red_band: np.ndarray
    ) -> np.ndarray:
        """محاسبه NDVI از باندهای Sentinel-2"""
        from .spectral_indices import SpectralIndicesCalculator
        return SpectralIndicesCalculator.calculate_ndvi(nir_band, red_band)
    
    def calculate_evi_from_bands(
        self,
        nir_band: np.ndarray,
        red_band: np.ndarray,
        blue_band: np.ndarray
    ) -> np.ndarray:
        """محاسبه EVI از باندهای Sentinel-2"""
        from .spectral_indices import SpectralIndicesCalculator
        return SpectralIndicesCalculator.calculate_evi(nir_band, red_band, blue_band)
    
    def calculate_ndwi_from_bands(
        self,
        green_band: np.ndarray,
        nir_band: np.ndarray
    ) -> np.ndarray:
        """محاسبه NDWI از باندهای Sentinel-2"""
        from .spectral_indices import SpectralIndicesCalculator
        return SpectralIndicesCalculator.calculate_ndwi(green_band, nir_band)
    
    def calculate_ndsi_from_bands(
        self,
        green_band: np.ndarray,
        swir_band: np.ndarray
    ) -> np.ndarray:
        """محاسبه NDSI از باندهای Sentinel-2"""
        from .spectral_indices import SpectralIndicesCalculator
        return SpectralIndicesCalculator.calculate_ndsi(green_band, swir_band)
    
    def analyze_vegetation_health(
        self,
        nir_band: np.ndarray,
        red_band: np.ndarray
    ) -> Dict:
        """تحلیل جامع سلامت پوشش گیاهی"""
        from .spectral_indices import SpectralIndicesCalculator
        
        ndvi = self.calculate_ndvi_from_bands(nir_band, red_band)
        health_classes = SpectralIndicesCalculator.classify_vegetation_health(ndvi)
        
        # محاسبه آمار
        stats = {
            'mean_ndvi': float(np.nanmean(ndvi)),
            'min_ndvi': float(np.nanmin(ndvi)),
            'max_ndvi': float(np.nanmax(ndvi)),
            'std_ndvi': float(np.nanstd(ndvi)),
            'health_distribution': {
                'very_poor': int(np.sum(health_classes == 1)),
                'poor': int(np.sum(health_classes == 2)),
                'fair': int(np.sum(health_classes == 3)),
                'good': int(np.sum(health_classes == 4)),
                'very_good': int(np.sum(health_classes == 5))
            }
        }
        
        return {
            'ndvi': ndvi,
            'health_classes': health_classes,
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def analyze_water_bodies(
        self,
        green_band: np.ndarray,
        nir_band: np.ndarray,
        threshold: float = 0.3
    ) -> Dict:
        """تحلیل پیکره‌های آبی"""
        from .spectral_indices import SpectralIndicesCalculator
        
        ndwi = self.calculate_ndwi_from_bands(green_band, nir_band)
        water_mask = SpectralIndicesCalculator.classify_water_body(ndwi, threshold)
        
        # محاسبه مساحت آب (تعداد پیکسل‌ها)
        total_pixels = water_mask.size
        water_pixels = int(np.sum(water_mask))
        water_percentage = (water_pixels / total_pixels) * 100
        
        stats = {
            'mean_ndwi': float(np.nanmean(ndwi)),
            'water_pixels': water_pixels,
            'total_pixels': total_pixels,
            'water_percentage': water_percentage
        }
        
        return {
            'ndwi': ndwi,
            'water_mask': water_mask,
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def analyze_soil_salinity(
        self,
        green_band: np.ndarray,
        swir_band: np.ndarray
    ) -> Dict:
        """تحلیل شوری خاک"""
        from .spectral_indices import SpectralIndicesCalculator
        
        ndsi = self.calculate_ndsi_from_bands(green_band, swir_band)
        salinity_classes = SpectralIndicesCalculator.classify_salinity(ndsi)
        
        stats = {
            'mean_ndsi': float(np.nanmean(ndsi)),
            'salinity_distribution': {
                'non_saline': int(np.sum(salinity_classes == 1)),
                'slightly_saline': int(np.sum(salinity_classes == 2)),
                'moderately_saline': int(np.sum(salinity_classes == 3)),
                'strongly_saline': int(np.sum(salinity_classes == 4))
            }
        }
        
        return {
            'ndsi': ndsi,
            'salinity_classes': salinity_classes,
            'statistics': stats,
            'timestamp': datetime.utcnow().isoformat()
        }
