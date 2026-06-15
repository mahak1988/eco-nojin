"""سرویس Landsat برای دریافت و پردازش تصاویر ماهواره‌ای

Landsat 8/9 دارای 11 باند طیفی است.
باندهای کلیدی:
- B2 (Blue): 480nm
- B3 (Green): 560nm
- B4 (Red): 655nm
- B5 (NIR): 865nm
- B6 (SWIR1): 1610nm
"""
import os
import numpy as np
from typing import Dict, Optional
from datetime import datetime


class LandsatService:
    """سرویس پردازش تصاویر Landsat"""
    
    # باندهای Landsat 8/9
    BANDS = {
        'B2': {'name': 'Blue', 'resolution': 30, 'wavelength': 480},
        'B3': {'name': 'Green', 'resolution': 30, 'wavelength': 560},
        'B4': {'name': 'Red', 'resolution': 30, 'wavelength': 655},
        'B5': {'name': 'NIR', 'resolution': 30, 'wavelength': 865},
        'B6': {'name': 'SWIR1', 'resolution': 30, 'wavelength': 1610},
    }
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('LANDSAT_API_KEY')
    
    def calculate_ndvi_from_bands(
        self,
        nir_band: np.ndarray,
        red_band: np.ndarray
    ) -> np.ndarray:
        """محاسبه NDVI از باندهای Landsat"""
        from .spectral_indices import SpectralIndicesCalculator
        return SpectralIndicesCalculator.calculate_ndvi(nir_band, red_band)
    
    def calculate_ndwi_from_bands(
        self,
        green_band: np.ndarray,
        nir_band: np.ndarray
    ) -> np.ndarray:
        """محاسبه NDWI از باندهای Landsat"""
        from .spectral_indices import SpectralIndicesCalculator
        return SpectralIndicesCalculator.calculate_ndwi(green_band, nir_band)
    
    def analyze_vegetation_health(
        self,
        nir_band: np.ndarray,
        red_band: np.ndarray
    ) -> Dict:
        """تحلیل سلامت پوشش گیاهی"""
        from .spectral_indices import SpectralIndicesCalculator
        
        ndvi = self.calculate_ndvi_from_bands(nir_band, red_band)
        health_classes = SpectralIndicesCalculator.classify_vegetation_health(ndvi)
        
        stats = {
            'mean_ndvi': float(np.nanmean(ndvi)),
            'min_ndvi': float(np.nanmin(ndvi)),
            'max_ndvi': float(np.nanmax(ndvi)),
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
