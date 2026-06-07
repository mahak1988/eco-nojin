# api/scientific_core/indices.py
"""
شاخص‌های طیفی استاندارد جهانی
مرجع: Index Database (https://www.indexdatabase.de/)
      Sentinel-2 Handbook (ESA)
      Thenkabail et al. (2016) - Remote Sensing of Vegetation
"""
import math
from typing import Dict, Optional, Tuple


class SpectralIndices:
    """مجموعه کامل شاخص‌های طیفی"""
    
    # ============ شاخص‌های پوشش گیاهی ============
    
    @staticmethod
    def ndvi(nir: float, red: float) -> float:
        """
        Normalized Difference Vegetation Index
        مرجع: Rouse et al. (1974)
        بازه: [-1, 1] - بالاتر = پوشش گیاهی بیشتر
        کاربرد: پایش عمومی پوشش گیاهی
        """
        if nir + red == 0: return 0
        return (nir - red) / (nir + red)
    
    @staticmethod
    def evi(nir: float, red: float, blue: float, 
            G: float = 2.5, C1: float = 6.0, C2: float = 7.5, L: float = 1.0) -> float:
        """
        Enhanced Vegetation Index
        مرجع: Huete et al. (2002) - MODIS
        بازه: [-1, 1] - حساس‌تر در مناطق متراکم
        کاربرد: کاهش اثر اتمسفر و خاک
        """
        denom = nir + C1 * red - C2 * blue + L
        if denom == 0: return 0
        return G * (nir - red) / denom
    
    @staticmethod
    def savi(nir: float, red: float, L: float = 0.5) -> float:
        """
        Soil Adjusted Vegetation Index
        مرجع: Huete (1988)
        بازه: [-1, 1] - L=0.5 پیش‌فرض
        کاربرد: مناطق با پوشش گیاهی کم
        """
        denom = nir + red + L
        if denom == 0: return 0
        return ((nir - red) / denom) * (1 + L)
    
    @staticmethod
    def msavi2(nir: float, red: float) -> float:
        """
        Modified SAVI 2
        مرجع: Qi et al. (1994)
        کاربرد: حذف نیاز به پارامتر L
        """
        term = (2 * nir + 1) ** 2 - 8 * (nir - red)
        if term < 0: term = 0
        return (2 * nir + 1 - math.sqrt(term)) / 2
    
    @staticmethod
    def gndvi(nir: float, green: float) -> float:
        """
        Green NDVI
        مرجع: Gitelson et al. (1996)
        کاربرد: حساس‌تر به کلروفیل
        """
        if nir + green == 0: return 0
        return (nir - green) / (nir + green)
    
    @staticmethod
    def arvi(nir: float, red: float, blue: float, gamma: float = 1.0) -> float:
        """
        Atmospherically Resistant Vegetation Index
        مرجع: Kaufman & Tanré (1992)
        کاربرد: کاهش اثر اتمسفر
        """
        rb = red - gamma * (blue - red)
        if nir + rb == 0: return 0
        return (nir - rb) / (nir + rb)
    
    @staticmethod
    def ndre(nir: float, red_edge: float) -> float:
        """
        Normalized Difference Red Edge
        مرجع: Gitelson & Merzlyak (1994)
        کاربرد: پایش سلامت گیاه (Sentinel-2 B5, B6, B7)
        """
        if nir + red_edge == 0: return 0
        return (nir - red_edge) / (nir + red_edge)
    
    @staticmethod
    def ci_green(nir: float, green: float) -> float:
        """
        Chlorophyll Index Green
        مرجع: Gitelson et al. (1996)
        کاربرد: تخمین کلروفیل
        """
        if green == 0: return 0
        return (nir / green) - 1
    
    @staticmethod
    def ci_rededge(nir: float, red_edge: float) -> float:
        """
        Chlorophyll Index Red Edge
        مرجع: Gitelson et al. (1996)
        کاربرد: تخمین دقیق کلروفیل
        """
        if red_edge == 0: return 0
        return (nir / red_edge) - 1
    
    @staticmethod
    def lai_estimate(ndvi: float) -> float:
        """
        تخمین LAI از NDVI
        مرجع: Paruelo et al. (1997)
        LAI = exp(NDVI × a) × b
        """
        if ndvi <= 0: return 0
        return math.exp(ndvi * 2.3) * 0.1
    
    # ============ شاخص‌های آب ============
    
    @staticmethod
    def ndwi(green: float, nir: float) -> float:
        """
        Normalized Difference Water Index
        مرجع: McFeeters (1996)
        بازه: [-1, 1] - بالاتر = آب بیشتر
        کاربرد: شناسایی آب سطحی
        """
        if green + nir == 0: return 0
        return (green - nir) / (green + nir)
    
    @staticmethod
    def mndwi(green: float, swir1: float) -> float:
        """
        Modified NDWI
        مرجع: Xu (2006)
        کاربرد: کاهش اثر خاک و ساختمان
        """
        if green + swir1 == 0: return 0
        return (green - swir1) / (green + swir1)
    
    @staticmethod
    def awei_nsh(blue: float, green: float, nir: float, swir1: float, swir2: float) -> float:
        """
        Automated Water Extraction Index (No Shadow)
        مرجع: Feyisa et al. (2014)
        """
        return 4 * (green - swir1) - (0.25 * nir + 2.75 * swir2)
    
    @staticmethod
    def wri(green: float, red: float, nir: float, swir1: float) -> float:
        """
        Water Ratio Index
        مرجع: Shen & Li (2010)
        """
        denom = nir + swir1
        if denom == 0: return 0
        return (green + red) / denom
    
    # ============ شاخص‌های خاک ============
    
    @staticmethod
    def ndsi(green: float, swir1: float) -> float:
        """
        Normalized Difference Soil Index
        کاربرد: شناسایی خاک برهنه
        """
        if green + swir1 == 0: return 0
        return (green - swir1) / (green + swir1)
    
    @staticmethod
    def bi(red: float, green: float, nir: float) -> float:
        """
        Brightness Index
        مرجع: Escadafal (1989)
        """
        return math.sqrt((red**2 + green**2 + nir**2) / 3)
    
    @staticmethod
    def bsi(blue: float, red: float, nir: float, swir1: float) -> float:
        """
        Bare Soil Index
        مرجع: Rikimaru et al. (2002)
        """
        denom = (nir + red) + (blue + swir1)
        if denom == 0: return 0
        return ((swir1 + red) - (nir + blue)) / denom
    
    # ============ شاخص‌های آتش‌سوزی ============
    
    @staticmethod
    def nbr(nir: float, swir2: float) -> float:
        """
        Normalized Burn Ratio
        مرجع: Key & Benson (2006) - USGS
        کاربرد: شناسایی مناطق سوخته
        """
        if nir + swir2 == 0: return 0
        return (nir - swir2) / (nir + swir2)
    
    @staticmethod
    def nbr2(swir1: float, swir2: float) -> float:
        """
        Normalized Burn Ratio 2
        مرجع: Key & Benson (2006)
        """
        if swir1 + swir2 == 0: return 0
        return (swir1 - swir2) / (swir1 + swir2)
    
    @staticmethod
    def bai(red: float, nir: float) -> float:
        """
        Burned Area Index
        مرجع: Chuvieco et al. (2003)
        """
        return 1 / ((0.1 - red)**2 + (0.06 - nir)**2)
    
    @staticmethod
    def dnbr(nbr_pre: float, nbr_post: float) -> float:
        """
        Differenced NBR
        مرجع: Key & Benson (2006)
        تفسیر:
          < -0.25: افزایش پوشش
          -0.25 to -0.1: افزایش کم
          -0.1 to 0.1: بدون تغییر
          0.1 to 0.27: سوختگی کم
          0.27 to 0.44: سوختگی متوسط
          0.44 to 0.66: سوختگی زیاد
          > 0.66: سوختگی شدید
        """
        return nbr_pre - nbr_post
    
    # ============ شاخص‌های شهری ============
    
    @staticmethod
    def ndbi(swir1: float, nir: float) -> float:
        """
        Normalized Difference Built-up Index
        مرجع: Zha et al. (2003)
        کاربرد: شناسایی مناطق شهری
        """
        if swir1 + nir == 0: return 0
        return (swir1 - nir) / (swir1 + nir)
    
    @staticmethod
    def ibi(nir: float, red: float, green: float, swir1: float) -> float:
        """
        Index-based Built-up Index
        مرجع: Xu (2008)
        """
        ndbi = SpectralIndices.ndbi(swir1, nir)
        savi = SpectralIndices.savi(nir, red)
        ndwi = SpectralIndices.ndwi(green, nir)
        denom = (ndbi + 1) - (savi + ndwi)
        if denom == 0: return 0
        return (2 * ndbi) / denom
    
    # ============ محاسبه همه شاخص‌ها ============
    
    @classmethod
    def calculate_all(cls, bands: Dict[str, float]) -> Dict[str, float]:
        """محاسبه تمام شاخص‌های ممکن بر اساس باندهای موجود"""
        results = {}
        nir = bands.get("nir")
        red = bands.get("red")
        green = bands.get("green")
        blue = bands.get("blue")
        swir1 = bands.get("swir1")
        swir2 = bands.get("swir2")
        red_edge = bands.get("red_edge")
        
        if nir and red:
            results["NDVI"] = round(cls.ndvi(nir, red), 4)
            if green:
                results["GNDVI"] = round(cls.gndvi(nir, green), 4)
            if blue:
                results["EVI"] = round(cls.evi(nir, red, blue), 4)
                results["ARVI"] = round(cls.arvi(nir, red, blue), 4)
            results["SAVI"] = round(cls.savi(nir, red), 4)
            results["MSAVI2"] = round(cls.msavi2(nir, red), 4)
            results["NBR"] = round(cls.nbr(nir, swir2 or nir*0.5), 4)
            results["LAI"] = round(cls.lai_estimate(cls.ndvi(nir, red)), 3)
        
        if green and nir:
            results["NDWI"] = round(cls.ndwi(green, nir), 4)
            results["CI_GREEN"] = round(cls.ci_green(nir, green), 4)
        
        if red_edge and nir:
            results["NDRE"] = round(cls.ndre(nir, red_edge), 4)
            results["CI_REDGE"] = round(cls.ci_rededge(nir, red_edge), 4)
        
        if green and swir1:
            results["MNDWI"] = round(cls.mndwi(green, swir1), 4)
        
        if nir and swir1:
            results["NDBI"] = round(cls.ndbi(swir1, nir), 4)
        
        if red and nir:
            results["BAI"] = round(cls.bai(red, nir), 4)
        
        if red and green and nir:
            results["BI"] = round(cls.bi(red, green, nir), 4)
        
        return results
    
    @staticmethod
    def interpret_ndvi(value: float) -> Dict:
        """تفسیر علمی NDVI بر اساس IPCC"""
        if value < -0.1:
            return {"class": "آب/برف/ابر", "color": "#1e40af", "health": 0}
        elif value < 0.1:
            return {"class": "خاک برهنه/شهری", "color": "#92400e", "health": 10}
        elif value < 0.2:
            return {"class": "پوشش بسیار کم", "color": "#fbbf24", "health": 25}
        elif value < 0.3:
            return {"class": "پوشش کم", "color": "#f59e0b", "health": 40}
        elif value < 0.4:
            return {"class": "پوشش متوسط-کم", "color": "#84cc16", "health": 55}
        elif value < 0.5:
            return {"class": "پوشش متوسط", "color": "#65a30d", "health": 70}
        elif value < 0.6:
            return {"class": "پوشش خوب", "color": "#22c55e", "health": 80}
        elif value < 0.7:
            return {"class": "پوشش متراکم", "color": "#16a34a", "health": 88}
        elif value < 0.8:
            return {"class": "پوشش بسیار متراکم", "color": "#15803d", "health": 94}
        else:
            return {"class": "جنگل متراکم", "color": "#14532d", "health": 100}
