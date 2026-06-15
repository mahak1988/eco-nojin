"""سرویس MODIS برای پایش در مقیاس بزرگ

MODIS دارای رزولوشن پایین (250m-1km) اما پوشش زمانی بالا است.
مناسب برای پایش تغییرات فصلی و بلندمدت.
"""
import numpy as np
from typing import Dict
from datetime import datetime


class MODISService:
    """سرویس پردازش تصاویر MODIS"""
    
    def __init__(self):
        self.base_url = 'https://modis.ornl.gov'
    
    def calculate_ndvi_timeseries(
        self,
        nir_bands: list,
        red_bands: list,
        dates: list
    ) -> Dict:
        """محاسبه سری زمانی NDVI"""
        from .spectral_indices import SpectralIndicesCalculator
        
        timeseries = []
        for nir, red, date in zip(nir_bands, red_bands, dates):
            ndvi = SpectralIndicesCalculator.calculate_ndvi(nir, red)
            timeseries.append({
                'date': date,
                'mean_ndvi': float(np.nanmean(ndvi)),
                'max_ndvi': float(np.nanmax(ndvi)),
                'min_ndvi': float(np.nanmin(ndvi))
            })
        
        return {
            'timeseries': timeseries,
            'sensor': 'MODIS',
            'generated_at': datetime.utcnow().isoformat()
        }
    
    def detect_vegetation_trend(
        self,
        timeseries: list
    ) -> Dict:
        """تشخیص روند تغییرات پوشش گیاهی"""
        if len(timeseries) < 2:
            return {'trend': 'INSUFFICIENT_DATA'}
        
        ndvi_values = [ts['mean_ndvi'] for ts in timeseries]
        
        # محاسبه روند خطی ساده
        n = len(ndvi_values)
        x = np.arange(n)
        slope = np.polyfit(x, ndvi_values, 1)[0]
        
        if slope > 0.01:
            trend = 'IMPROVING'
        elif slope < -0.01:
            trend = 'DEGRADING'
        else:
            trend = 'STABLE'
        
        return {
            'trend': trend,
            'slope': float(slope),
            'mean_ndvi': float(np.mean(ndvi_values)),
            'min_ndvi': float(np.min(ndvi_values)),
            'max_ndvi': float(np.max(ndvi_values))
        }
