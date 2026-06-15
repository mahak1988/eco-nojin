"""سرویس محاسبه شاخص‌های طیفی (Spectral Indices)

این ماژول الگوریتم‌های استاندارد محاسبه شاخص‌های طیفی را پیاده‌سازی می‌کند:
- NDVI (Normalized Difference Vegetation Index)
- EVI (Enhanced Vegetation Index)
- NDWI (Normalized Difference Water Index)
- NDSI (Normalized Difference Salinity Index)
- SAVI (Soil Adjusted Vegetation Index)
"""
import numpy as np
from typing import Tuple, Optional


class SpectralIndicesCalculator:
    """ماشین حساب شاخص‌های طیفی"""
    
    @staticmethod
    def calculate_ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
        """
        محاسبه شاخص NDVI (Normalized Difference Vegetation Index)
        
        فرمول: NDVI = (NIR - Red) / (NIR + Red)
        
        Args:
            nir: باند مادون قرمز نزدیک (Sentinel-2: B8, Landsat: B5)
            red: باند قرمز (Sentinel-2: B4, Landsat: B4)
        
        Returns:
            آرایه NDVI با مقادیر بین -1 تا 1
        """
        # جلوگیری از تقسیم بر صفر
        denominator = nir.astype(float) + red.astype(float)
        denominator[denominator == 0] = np.nan
        
        ndvi = (nir.astype(float) - red.astype(float)) / denominator
        return np.clip(ndvi, -1, 1)
    
    @staticmethod
    def calculate_evi(
        nir: np.ndarray, 
        red: np.ndarray, 
        blue: np.ndarray,
        G: float = 2.5,
        C1: float = 6.0,
        C2: float = 7.5,
        L: float = 1.0
    ) -> np.ndarray:
        """
        محاسبه شاخص EVI (Enhanced Vegetation Index)
        
        فرمول: EVI = G * (NIR - Red) / (NIR + C1*Red - C2*Blue + L)
        
        EVI نسبت به NDVI حساسیت کمتری به اثرات اتمسفر و خاک دارد.
        
        Args:
            nir: باند مادون قرمز نزدیک
            red: باند قرمز
            blue: باند آبی (Sentinel-2: B2, Landsat: B2)
            G, C1, C2, L: ضرایب استاندارد EVI
        
        Returns:
            آرایه EVI با مقادیر بین -1 تا 1
        """
        denominator = nir.astype(float) + C1 * red.astype(float) - C2 * blue.astype(float) + L
        denominator[denominator == 0] = np.nan
        
        evi = G * (nir.astype(float) - red.astype(float)) / denominator
        return np.clip(evi, -1, 1)
    
    @staticmethod
    def calculate_ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
        """
        محاسبه شاخص NDWI (Normalized Difference Water Index)
        
        فرمول: NDWI = (Green - NIR) / (Green + NIR)
        
        برای تشخیص آب و رطوبت پوشش گیاهی استفاده می‌شود.
        
        Args:
            green: باند سبز (Sentinel-2: B3, Landsat: B3)
            nir: باند مادون قرمز نزدیک
        
        Returns:
            آرایه NDWI با مقادیر بین -1 تا 1
        """
        denominator = green.astype(float) + nir.astype(float)
        denominator[denominator == 0] = np.nan
        
        ndwi = (green.astype(float) - nir.astype(float)) / denominator
        return np.clip(ndwi, -1, 1)
    
    @staticmethod
    def calculate_ndsi(green: np.ndarray, swir: np.ndarray) -> np.ndarray:
        """
        محاسبه شاخص NDSI (Normalized Difference Salinity Index)
        
        فرمول: NDSI = (Green - SWIR) / (Green + SWIR)
        
        برای تشخیص شوری خاک استفاده می‌شود.
        
        Args:
            green: باند سبز
            swir: باند مادون قرمز کوتاه‌موج (Sentinel-2: B11, Landsat: B6)
        
        Returns:
            آرایه NDSI با مقادیر بین -1 تا 1
        """
        denominator = green.astype(float) + swir.astype(float)
        denominator[denominator == 0] = np.nan
        
        ndsi = (green.astype(float) - swir.astype(float)) / denominator
        return np.clip(ndsi, -1, 1)
    
    @staticmethod
    def calculate_savi(
        nir: np.ndarray, 
        red: np.ndarray,
        L: float = 0.5
    ) -> np.ndarray:
        """
        محاسبه شاخص SAVI (Soil Adjusted Vegetation Index)
        
        فرمول: SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)
        
        برای مناطق با پوشش گیاهی کم و اثر خاک مناسب است.
        
        Args:
            nir: باند مادون قرمز نزدیک
            red: باند قرمز
            L: ضریب تنظیم خاک (0 تا 1)
        
        Returns:
            آرایه SAVI با مقادیر بین -1 تا 1
        """
        denominator = nir.astype(float) + red.astype(float) + L
        denominator[denominator == 0] = np.nan
        
        savi = ((nir.astype(float) - red.astype(float)) / denominator) * (1 + L)
        return np.clip(savi, -1, 1)
    
    @staticmethod
    def classify_vegetation_health(ndvi: np.ndarray) -> np.ndarray:
        """
        طبقه‌بندی سلامت پوشش گیاهی بر اساس NDVI
        
        Categories:
        - Very Poor: NDVI < 0.1
        - Poor: 0.1 <= NDVI < 0.2
        - Fair: 0.2 <= NDVI < 0.3
        - Good: 0.3 <= NDVI < 0.5
        - Very Good: NDVI >= 0.5
        """
        health = np.zeros_like(ndvi, dtype=int)
        health[ndvi < 0.1] = 1  # Very Poor
        health[(ndvi >= 0.1) & (ndvi < 0.2)] = 2  # Poor
        health[(ndvi >= 0.2) & (ndvi < 0.3)] = 3  # Fair
        health[(ndvi >= 0.3) & (ndvi < 0.5)] = 4  # Good
        health[ndvi >= 0.5] = 5  # Very Good
        
        return health
    
    @staticmethod
    def classify_water_body(ndwi: np.ndarray, threshold: float = 0.3) -> np.ndarray:
        """
        طبقه‌بندی آب بر اساس NDWI
        
        Args:
            ndwi: آرایه NDWI
            threshold: آستانه تشخیص آب (پیش‌فرض 0.3)
        
        Returns:
            آرایه باینری: 1 برای آب، 0 برای غیر آب
        """
        water_mask = np.zeros_like(ndwi, dtype=int)
        water_mask[ndwi > threshold] = 1
        return water_mask
    
    @staticmethod
    def classify_salinity(ndsi: np.ndarray) -> np.ndarray:
        """
        طبقه‌بندی شوری خاک بر اساس NDSI
        
        Categories:
        - Non-saline: NDSI < 0.1
        - Slightly saline: 0.1 <= NDSI < 0.2
        - Moderately saline: 0.2 <= NDSI < 0.3
        - Strongly saline: NDSI >= 0.3
        """
        salinity = np.zeros_like(ndsi, dtype=int)
        salinity[ndsi < 0.1] = 1  # Non-saline
        salinity[(ndsi >= 0.1) & (ndsi < 0.2)] = 2  # Slightly saline
        salinity[(ndsi >= 0.2) & (ndsi < 0.3)] = 3  # Moderately saline
        salinity[ndsi >= 0.3] = 4  # Strongly saline
        
        return salinity
