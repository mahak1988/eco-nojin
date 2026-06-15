"""تست‌های واحد برای سنجش‌ازدور"""
import pytest
import numpy as np
from api.services.remote_sensing.spectral_indices import SpectralIndicesCalculator


class TestSpectralIndices:
    """تست‌های شاخص‌های طیفی"""
    
    def test_ndvi_calculation(self):
        """تست محاسبه NDVI"""
        nir = np.array([100, 200, 150, 50])
        red = np.array([50, 100, 150, 100])
        
        ndvi = SpectralIndicesCalculator.calculate_ndvi(nir, red)
        
        assert len(ndvi) == 4
        assert ndvi[0] == 1.0  # (100-50)/(100+50)
        assert ndvi[1] == 1.0  # (200-100)/(200+100)
        assert ndvi[2] == 0.0  # (150-150)/(150+150)
        assert ndvi[3] == -1.0  # (50-100)/(50+100)
    
    def test_ndvi_clipping(self):
        """تست محدود شدن NDVI بین -1 و 1"""
        nir = np.array([1000, 0])
        red = np.array([0, 1000])
        
        ndvi = SpectralIndicesCalculator.calculate_ndvi(nir, red)
        
        assert np.all(ndvi >= -1)
        assert np.all(ndvi <= 1)
    
    def test_evi_calculation(self):
        """تست محاسبه EVI"""
        nir = np.array([200, 150])
        red = np.array([100, 80])
        blue = np.array([50, 40])
        
        evi = SpectralIndicesCalculator.calculate_evi(nir, red, blue)
        
        assert len(evi) == 2
        assert np.all(evi >= -1)
        assert np.all(evi <= 1)
    
    def test_ndwi_calculation(self):
        """تست محاسبه NDWI"""
        green = np.array([150, 100, 50])
        nir = np.array([50, 100, 150])
        
        ndwi = SpectralIndicesCalculator.calculate_ndwi(green, nir)
        
        assert len(ndwi) == 3
        assert ndwi[0] > 0  # آب
        assert ndwi[1] == 0  # مرز
        assert ndwi[2] < 0  # خاک
    
    def test_ndsi_calculation(self):
        """تست محاسبه NDSI"""
        green = np.array([200, 150, 100])
        swir = np.array([100, 150, 200])
        
        ndsi = SpectralIndicesCalculator.calculate_ndsi(green, swir)
        
        assert len(ndsi) == 3
        assert ndsi[0] > 0  # شوری بالا
        assert ndsi[1] == 0  # مرز
        assert ndsi[2] < 0  # شوری کم
    
    def test_vegetation_health_classification(self):
        """تست طبقه‌بندی سلامت پوشش گیاهی"""
        ndvi = np.array([0.05, 0.15, 0.25, 0.40, 0.60])
        
        health = SpectralIndicesCalculator.classify_vegetation_health(ndvi)
        
        assert health[0] == 1  # Very Poor
        assert health[1] == 2  # Poor
        assert health[2] == 3  # Fair
        assert health[3] == 4  # Good
        assert health[4] == 5  # Very Good
    
    def test_water_body_classification(self):
        """تست طبقه‌بندی پیکره‌های آبی"""
        ndwi = np.array([0.5, 0.2, -0.1])
        
        water_mask = SpectralIndicesCalculator.classify_water_body(ndwi, threshold=0.3)
        
        assert water_mask[0] == 1  # آب
        assert water_mask[1] == 0  # غیر آب
        assert water_mask[2] == 0  # غیر آب
    
    def test_salinity_classification(self):
        """تست طبقه‌بندی شوری"""
        ndsi = np.array([0.05, 0.15, 0.25, 0.35])
        
        salinity = SpectralIndicesCalculator.classify_salinity(ndsi)
        
        assert salinity[0] == 1  # Non-saline
        assert salinity[1] == 2  # Slightly saline
        assert salinity[2] == 3  # Moderately saline
        assert salinity[3] == 4  # Strongly saline


class TestSentinel2Service:
    """تست‌های سرویس Sentinel-2"""
    
    def test_band_combinations(self):
        """تست ترکیب باندها"""
        from api.services.remote_sensing.sentinel2_service import Sentinel2Service
        
        service = Sentinel2Service()
        
        ndvi_bands = service.get_band_combination_for_ndvi()
        assert ndvi_bands['nir'] == 'B8'
        assert ndvi_bands['red'] == 'B4'
        
        ndwi_bands = service.get_band_combination_for_ndwi()
        assert ndwi_bands['green'] == 'B3'
        assert ndwi_bands['nir'] == 'B8'
