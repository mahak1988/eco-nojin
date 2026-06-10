#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧠 Econojin Scientific Core (ESC)
پایگاه دانش علمی مرکزی برای تمام ماژول‌ها
شامل تمام استانداردها، فرمول‌ها، مدل‌ها و شاخص‌های جهانی
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
API_DIR = ROOT / "api"
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ============================================================
# فایل 1: __init__.py
# ============================================================
def create_init():
    print("\n📦 ایجاد scientific_core/__init__.py...")
    content = '''# api/scientific_core/__init__.py
"""
Econojin Scientific Core (ESC)
پایگاه دانش علمی مرکزی
"""
from . import indices
from . import hydrology
from . import crops
from . import carbon
from . import erosion
from . import drought
from . import soil_water
from . import databases
'''
    write_file(API_DIR / "scientific_core" / "__init__.py", content)


# ============================================================
# فایل 2: شاخص‌های طیفی (Spectral Indices)
# ============================================================
def create_indices():
    print("\n🌱 ایجاد شاخص‌های طیفی...")
    content = '''# api/scientific_core/indices.py
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
'''
    write_file(API_DIR / "scientific_core" / "indices.py", content)


# ============================================================
# فایل 3: مدل‌های هیدرولوژی
# ============================================================
def create_hydrology():
    print("\n🌊 ایجاد مدل‌های هیدرولوژی...")
    content = '''# api/scientific_core/hydrology.py
"""
مدل‌های هیدرولوژی استاندارد جهانی
مرجع: 
  - USDA NRCS (SCS-CN)
  - Chow et al. (1988) - Applied Hydrology
  - Viessman & Lewis (2003)
  - HEC-HMS Technical Reference
"""
import math
from typing import Dict, List, Optional


class SCS_CN:
    """
    مدل SCS Curve Number (USDA NRCS)
    مرجع: Soil Conservation Service (1972, 1985)
    فرمول: Q = (P - Ia)^2 / (P - Ia + S)
           Ia = 0.2S
           S = 25400/CN - 254
    """
    
    # CN پیش‌فرض بر اساس کاربری اراضی و نوع هیدرولوژیک خاک
    CN_TABLE = {
        # (کاربری, گروه هیدرولوژیک): CN
        ("forest_good", "A"): 36, ("forest_good", "B"): 60, 
        ("forest_good", "C"): 73, ("forest_good", "D"): 79,
        ("forest_fair", "A"): 60, ("forest_fair", "B"): 73,
        ("forest_fair", "C"): 79, ("forest_fair", "D"): 83,
        ("grass_good", "A"): 49, ("grass_good", "B"): 69,
        ("grass_good", "C"): 79, ("grass_good", "D"): 84,
        ("grass_fair", "A"): 68, ("grass_fair", "B"): 79,
        ("grass_fair", "C"): 86, ("grass_fair", "D"): 89,
        ("cultivated", "A"): 72, ("cultivated", "B"): 81,
        ("cultivated", "C"): 88, ("cultivated", "D"): 91,
        ("impervious", "A"): 98, ("impervious", "B"): 98,
        ("impervious", "C"): 98, ("impervious", "D"): 98,
        ("wetland", "A"): 96, ("wetland", "B"): 96,
        ("wetland", "C"): 96, ("wetland", "D"): 97,
    }
    
    @classmethod
    def calculate(cls, rainfall_mm: float, cn: float, 
                  initial_moisture: str = "AMC_II") -> Dict:
        """
        محاسبه رواناب مستقیم
        
        Args:
            rainfall_mm: بارش (mm)
            cn: ضریب رواناب (Curve Number)
            initial_moisture: شرایط رطوبت اولیه (AMC_I, AMC_II, AMC_III)
        """
        # تنظیم CN بر اساس AMC
        if initial_moisture == "AMC_I":  # خشک
            cn_adj = 4.2 * cn / (10 - 0.058 * cn) if cn > 0 else cn
        elif initial_moisture == "AMC_III":  # اشباع
            cn_adj = 23 * cn / (10 + 0.13 * cn) if cn > 0 else cn
        else:  # AMC_II - متوسط
            cn_adj = cn
        
        # محاسبه S (max retention)
        s = (25400 / cn_adj) - 254 if cn_adj > 0 else 0
        
        # تلفات اولیه
        ia = 0.2 * s
        
        # رواناب
        if rainfall_mm <= ia:
            q = 0
        else:
            q = ((rainfall_mm - ia) ** 2) / (rainfall_mm - ia + s)
        
        # نفوذ
        infiltration = rainfall_mm - q - ia if rainfall_mm > ia else 0
        
        return {
            "curve_number": round(cn_adj, 1),
            "s_mm": round(s, 2),
            "ia_mm": round(ia, 2),
            "rainfall_mm": round(rainfall_mm, 2),
            "runoff_mm": round(q, 2),
            "infiltration_mm": round(infiltration, 2),
            "runoff_coefficient": round(q / rainfall_mm, 3) if rainfall_mm > 0 else 0,
        }
    
    @classmethod
    def get_cn(cls, land_use: str, hydrologic_group: str) -> int:
        """دریافت CN از جدول"""
        return cls.CN_TABLE.get((land_use, hydrologic_group), 75)


class RationalMethod:
    """
    روش عقلایی برای محاسبه دبی پیک
    مرجع: Chow et al. (1988)
    فرمول: Q = C × I × A
    """
    
    # ضرایب رواناب C بر اساس کاربری
    RUNOFF_COEFFICIENTS = {
        "impervious": 0.90,
        "business": 0.85,
        "residential_dense": 0.70,
        "residential_single": 0.55,
        "parks": 0.25,
        "forests": 0.20,
        "cultivated": 0.40,
        "grass_sandy_flat": 0.20,
        "grass_heavy_soil": 0.45,
    }
    
    @classmethod
    def calculate(cls, c: float, intensity_mm_hr: float, 
                  area_hectares: float) -> Dict:
        """
        محاسبه دبی پیک
        
        Q = C × I × A / 360 (m³/s)
        """
        q_m3s = (c * intensity_mm_hr * area_hectares) / 360
        
        return {
            "runoff_coefficient": c,
            "intensity_mm_hr": intensity_mm_hr,
            "area_hectares": area_hectares,
            "peak_discharge_m3s": round(q_m3s, 3),
            "peak_discharge_lps": round(q_m3s * 1000, 1),
        }


class InfiltrationModels:
    """مدل‌های نفوذ"""
    
    @staticmethod
    def horton(f0: float, fc: float, k: float, t: float) -> float:
        """
        مدل نفوذ هورتون
        مرجع: Horton (1940)
        f(t) = fc + (f0 - fc) × e^(-kt)
        """
        return fc + (f0 - fc) * math.exp(-k * t)
    
    @staticmethod
    def philip(s: float, a: float, t: float) -> float:
        """
        مدل نفوذ فیلیپ
        مرجع: Philip (1957)
        f(t) = 0.5 × S × t^(-0.5) + A
        """
        if t <= 0: return s
        return 0.5 * s / math.sqrt(t) + a
    
    @staticmethod
    def kostiakov(k: float, a: float, t: float) -> float:
        """
        مدل نفوذ کستیاکوف
        مرجع: Kostiakov (1932)
        f(t) = k × t^(-a)
        """
        if t <= 0: return 0
        return k * (t ** -a)
    
    @staticmethod
    def green_ampt(k_sat: float, psi_f: float, delta_theta: float, 
                   f: float) -> float:
        """
        مدل نفوذ Green-Ampt
        مرجع: Green & Ampt (1911)
        f = Ks × (1 + (ψ_f × Δθ) / F)
        """
        if f <= 0: return k_sat
        return k_sat * (1 + (psi_f * delta_theta) / f)


class Muskingum:
    """
    مدل مسیریابی مسکینگام
    مرجع: McCarthy (1938)
    O2 = C1 × I2 + C2 × I1 + C3 × O1
    """
    
    @classmethod
    def calculate(cls, inflow: List[float], k: float, x: float, 
                  dt: float) -> List[float]:
        """
        Args:
            inflow: سری زمانی ورودی
            k: ضریب ذخیره (ساعت)
            x: ضریب وزن (0 تا 0.5)
            dt: گام زمانی (ساعت)
        """
        denom = 2 * k * (1 - x) + dt
        if denom == 0: return inflow
        
        c1 = (dt - 2 * k * x) / denom
        c2 = (dt + 2 * k * x) / denom
        c3 = (2 * k * (1 - x) - dt) / denom
        
        outflow = [inflow[0]]
        for i in range(1, len(inflow)):
            o = c1 * inflow[i] + c2 * inflow[i-1] + c3 * outflow[-1]
            outflow.append(max(0, o))
        
        return {
            "outflow": [round(o, 3) for o in outflow],
            "coefficients": {"C1": round(c1, 3), "C2": round(c2, 3), "C3": round(c3, 3)},
            "peak_attenuation": round(max(inflow) - max(outflow), 3),
            "peak_lag_hours": round((outflow.index(max(outflow)) - inflow.index(max(inflow))) * dt, 1),
        }


class TimeOfConcentration:
    """زمان تمرکز حوضه آبریز"""
    
    @staticmethod
    def kirpich(length_m: float, slope_m_m: float) -> float:
        """
        فرمول کرپیچ (1940)
        tc = 0.0195 × L^0.77 × S^(-0.385)
        """
        if slope_m_m <= 0: return 0
        return 0.0195 * (length_m ** 0.77) * (slope_m_m ** -0.385)
    
    @staticmethod
    def scs(length_m: float, cn: float, slope_percent: float) -> float:
        """
        فرمول SCS
        tc = (L^0.8 × (1000/CN - 9)^0.7) / (1140 × S^0.5)
        """
        if slope_percent <= 0: return 0
        s = math.sqrt(slope_percent / 100)
        return (length_m ** 0.8 * ((1000/cn - 9) ** 0.7)) / (1140 * s)
    
    @staticmethod
    def ventura(length_km: float, slope_m_m: float) -> float:
        """
        فرمول ونتورا
        tc = L / (10 × sqrt(S))
        """
        if slope_m_m <= 0: return 0
        return length_km / (10 * math.sqrt(slope_m_m))
'''
    write_file(API_DIR / "scientific_core" / "hydrology.py", content)


# ============================================================
# فایل 4: محصولات و ضرایب Kc
# ============================================================
def create_crops():
    print("\n🌾 ایجاد پایگاه داده محصولات...")
    content = '''# api/scientific_core/crops.py
"""
پایگاه داده محصولات و ضرایب Kc
مرجع: FAO-56 (Allen et al., 1998)
       FAO-24 (Doorenbos & Pruitt, 1977)
       Wright (1982) - ASCE
"""
from typing import Dict, List, Optional


# پایگاه داده محصولات با ضرایب Kc چهار مرحله‌ای
CROPS_DATABASE = {
    # غلات
    "wheat": {
        "name_fa": "گندم",
        "name_en": "Wheat",
        "name_scientific": "Triticum aestivum",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 0.30, "dev": None, "mid": 1.15, "end": 0.30},
        "stages_days": [30, 50, 40, 30],  # init, dev, mid, late
        "root_depth_cm": {"init": 20, "dev": 50, "mid": 80, "end": 80},
        "depletion_fraction": 0.55,
        "harvest_index": 0.45,
        "max_height_m": 1.0,
        "y_potential_t_ha": 8.0,
    },
    "barley": {
        "name_fa": "جو",
        "name_en": "Barley",
        "name_scientific": "Hordeum vulgare",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 0.30, "mid": 1.15, "end": 0.25},
        "stages_days": [25, 45, 40, 30],
        "root_depth_cm": {"init": 20, "dev": 45, "mid": 70, "end": 70},
        "depletion_fraction": 0.55,
        "harvest_index": 0.42,
        "max_height_m": 0.9,
        "y_potential_t_ha": 7.0,
    },
    "maize": {
        "name_fa": "ذرت",
        "name_en": "Maize",
        "name_scientific": "Zea mays",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 0.30, "mid": 1.20, "end": 0.50},
        "stages_days": [25, 55, 40, 30],
        "root_depth_cm": {"init": 20, "dev": 60, "mid": 100, "end": 100},
        "depletion_fraction": 0.55,
        "harvest_index": 0.48,
        "max_height_m": 2.5,
        "y_potential_t_ha": 12.0,
    },
    "rice": {
        "name_fa": "برنج",
        "name_en": "Rice",
        "name_scientific": "Oryza sativa",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 1.05, "mid": 1.20, "end": 0.90},
        "stages_days": [30, 60, 40, 30],
        "root_depth_cm": {"init": 10, "dev": 30, "mid": 50, "end": 50},
        "depletion_fraction": 1.00,
        "harvest_index": 0.50,
        "max_height_m": 1.2,
        "y_potential_t_ha": 10.0,
    },
    "sorghum": {
        "name_fa": "سورگوم",
        "name_en": "Sorghum",
        "name_scientific": "Sorghum bicolor",
        "family": "Poaceae",
        "type": "cereal",
        "kc": {"init": 0.30, "mid": 1.15, "end": 0.40},
        "stages_days": [30, 50, 40, 30],
        "root_depth_cm": {"init": 20, "dev": 60, "mid": 120, "end": 120},
        "depletion_fraction": 0.55,
        "harvest_index": 0.45,
        "max_height_m": 2.0,
        "y_potential_t_ha": 9.0,
    },
    # حبوبات
    "soybean": {
        "name_fa": "سویا",
        "name_en": "Soybean",
        "name_scientific": "Glycine max",
        "family": "Fabaceae",
        "type": "legume",
        "kc": {"init": 0.30, "mid": 1.15, "end": 0.35},
        "stages_days": [30, 45, 40, 25],
        "root_depth_cm": {"init": 15, "dev": 40, "mid": 70, "end": 70},
        "depletion_fraction": 0.60,
        "harvest_index": 0.42,
        "max_height_m": 0.9,
        "y_potential_t_ha": 4.0,
    },
    "chickpea": {
        "name_fa": "نخود",
        "name_en": "Chickpea",
        "name_scientific": "Cicer arietinum",
        "family": "Fabaceae",
        "type": "legume",
        "kc": {"init": 0.30, "mid": 1.10, "end": 0.25},
        "stages_days": [30, 40, 40, 25],
        "root_depth_cm": {"init": 15, "dev": 40, "mid": 80, "end": 80},
        "depletion_fraction": 0.55,
        "harvest_index": 0.30,
        "max_height_m": 0.6,
        "y_potential_t_ha": 2.5,
    },
    "lentil": {
        "name_fa": "عدس",
        "name_en": "Lentil",
        "name_scientific": "Lens culinaris",
        "family": "Fabaceae",
        "type": "legume",
        "kc": {"init": 0.30, "mid": 1.05, "end": 0.20},
        "stages_days": [25, 40, 35, 25],
        "root_depth_cm": {"init": 15, "dev": 35, "mid": 60, "end": 60},
        "depletion_fraction": 0.55,
        "harvest_index": 0.28,
        "max_height_m": 0.5,
        "y_potential_t_ha": 2.0,
    },
    # سبزیجات
    "tomato": {
        "name_fa": "گوجه‌فرنگی",
        "name_en": "Tomato",
        "name_scientific": "Solanum lycopersicum",
        "family": "Solanaceae",
        "type": "vegetable",
        "kc": {"init": 0.35, "mid": 1.15, "end": 0.70},
        "stages_days": [30, 40, 50, 30],
        "root_depth_cm": {"init": 20, "dev": 50, "mid": 80, "end": 80},
        "depletion_fraction": 0.55,
        "harvest_index": 0.65,
        "max_height_m": 1.2,
        "y_potential_t_ha": 80.0,
    },
    "potato": {
        "name_fa": "سیب‌زمینی",
        "name_en": "Potato",
        "name_scientific": "Solanum tuberosum",
        "family": "Solanaceae",
        "type": "vegetable",
        "kc": {"init": 0.35, "mid": 1.15, "end": 0.45},
        "stages_days": [30, 45, 40, 25],
        "root_depth_cm": {"init": 15, "dev": 40, "mid": 60, "end": 60},
        "depletion_fraction": 0.55,
        "harvest_index": 0.80,
        "max_height_m": 0.7,
        "y_potential_t_ha": 45.0,
    },
    "onion": {
        "name_fa": "پیاز",
        "name_en": "Onion",
        "name_scientific": "Allium cepa",
        "family": "Amaryllidaceae",
        "type": "vegetable",
        "kc": {"init": 0.35, "mid": 1.05, "end": 0.75},
        "stages_days": [35, 50, 40, 25],
        "root_depth_cm": {"init": 15, "dev": 30, "mid": 40, "end": 40},
        "depletion_fraction": 0.55,
        "harvest_index": 0.85,
        "max_height_m": 0.5,
        "y_potential_t_ha": 50.0,
    },
    # صنعتی
    "cotton": {
        "name_fa": "پنبه",
        "name_en": "Cotton",
        "name_scientific": "Gossypium hirsutum",
        "family": "Malvaceae",
        "type": "industrial",
        "kc": {"init": 0.35, "mid": 1.15, "end": 0.30},
        "stages_days": [40, 60, 50, 30],
        "root_depth_cm": {"init": 20, "dev": 60, "mid": 120, "end": 120},
        "depletion_fraction": 0.65,
        "harvest_index": 0.35,
        "max_height_m": 1.3,
        "y_potential_t_ha": 4.0,
    },
    "sugarbeet": {
        "name_fa": "چغندرقند",
        "name_en": "Sugar Beet",
        "name_scientific": "Beta vulgaris",
        "family": "Amaranthaceae",
        "type": "industrial",
        "kc": {"init": 0.35, "mid": 1.10, "end": 0.65},
        "stages_days": [40, 60, 60, 30],
        "root_depth_cm": {"init": 20, "dev": 50, "mid": 90, "end": 90},
        "depletion_fraction": 0.65,
        "harvest_index": 0.75,
        "max_height_m": 0.7,
        "y_potential_t_ha": 75.0,
    },
    "sugarcane": {
        "name_fa": "نیشکر",
        "name_en": "Sugarcane",
        "name_scientific": "Saccharum officinarum",
        "family": "Poaceae",
        "type": "industrial",
        "kc": {"init": 0.40, "mid": 1.25, "end": 0.75},
        "stages_days": [60, 120, 180, 60],
        "root_depth_cm": {"init": 25, "dev": 80, "mid": 150, "end": 150},
        "depletion_fraction": 0.70,
        "harvest_index": 0.65,
        "max_height_m": 4.0,
        "y_potential_t_ha": 120.0,
    },
    # علوفه
    "alfalfa": {
        "name_fa": "یونجه",
        "name_en": "Alfalfa",
        "name_scientific": "Medicago sativa",
        "family": "Fabaceae",
        "type": "forage",
        "kc": {"init": 0.30, "mid": 1.20, "end": 0.75},
        "stages_days": [20, 40, 30, 20],
        "root_depth_cm": {"init": 20, "dev": 60, "mid": 150, "end": 150},
        "depletion_fraction": 0.65,
        "harvest_index": 0.90,
        "max_height_m": 0.8,
        "y_potential_t_ha": 18.0,
    },
    # درختان میوه
    "apple": {
        "name_fa": "سیب",
        "name_en": "Apple",
        "name_scientific": "Malus domestica",
        "family": "Rosaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.35, "mid": 1.05, "end": 0.60},
        "stages_days": [60, 90, 90, 60],
        "root_depth_cm": {"init": 40, "dev": 80, "mid": 140, "end": 140},
        "depletion_fraction": 0.65,
        "harvest_index": 0.60,
        "max_height_m": 4.0,
        "y_potential_t_ha": 40.0,
    },
    "grape": {
        "name_fa": "انگور",
        "name_en": "Grape",
        "name_scientific": "Vitis vinifera",
        "family": "Vitaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.30, "mid": 0.80, "end": 0.50},
        "stages_days": [50, 80, 80, 50],
        "root_depth_cm": {"init": 30, "dev": 70, "mid": 120, "end": 120},
        "depletion_fraction": 0.60,
        "harvest_index": 0.70,
        "max_height_m": 2.0,
        "y_potential_t_ha": 25.0,
    },
    "pistachio": {
        "name_fa": "پسته",
        "name_en": "Pistachio",
        "name_scientific": "Pistacia vera",
        "family": "Anacardiaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.30, "mid": 0.85, "end": 0.55},
        "stages_days": [60, 90, 90, 60],
        "root_depth_cm": {"init": 40, "dev": 100, "mid": 180, "end": 180},
        "depletion_fraction": 0.65,
        "harvest_index": 0.45,
        "max_height_m": 5.0,
        "y_potential_t_ha": 3.5,
    },
    "date_palm": {
        "name_fa": "نخل خرما",
        "name_en": "Date Palm",
        "name_scientific": "Phoenix dactylifera",
        "family": "Arecaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.35, "mid": 0.90, "end": 0.60},
        "stages_days": [60, 90, 90, 60],
        "root_depth_cm": {"init": 50, "dev": 120, "mid": 200, "end": 200},
        "depletion_fraction": 0.65,
        "harvest_index": 0.55,
        "max_height_m": 20.0,
        "y_potential_t_ha": 12.0,
    },
    "walnut": {
        "name_fa": "گردو",
        "name_en": "Walnut",
        "name_scientific": "Juglans regia",
        "family": "Juglandaceae",
        "type": "fruit_tree",
        "kc": {"init": 0.35, "mid": 1.05, "end": 0.60},
        "stages_days": [60, 90, 90, 60],
        "root_depth_cm": {"init": 40, "dev": 90, "mid": 150, "end": 150},
        "depletion_fraction": 0.65,
        "harvest_index": 0.50,
        "max_height_m": 15.0,
        "y_potential_t_ha": 4.0,
    },
}


class CropCalculator:
    """محاسبات مربوط به محصول"""
    
    @classmethod
    def get_kc_at_stage(cls, crop_key: str, growth_day: int) -> float:
        """محاسبه Kc در روز مشخص"""
        crop = CROPS_DATABASE.get(crop_key)
        if not crop:
            return 0.8
        
        kc = crop["kc"]
        stages = crop["stages_days"]
        
        if growth_day <= stages[0]:
            return kc["init"]
        elif growth_day <= stages[0] + stages[1]:
            progress = (growth_day - stages[0]) / stages[1]
            return kc["init"] + progress * (kc["mid"] - kc["init"])
        elif growth_day <= stages[0] + stages[1] + stages[2]:
            return kc["mid"]
        else:
            total_mid = stages[0] + stages[1] + stages[2]
            progress = min(1.0, (growth_day - total_mid) / stages[3])
            return kc["mid"] + progress * (kc["end"] - kc["mid"])
    
    @classmethod
    def get_growth_stage(cls, crop_key: str, growth_day: int) -> str:
        """تعیین مرحله رشد"""
        crop = CROPS_DATABASE.get(crop_key)
        if not crop:
            return "نامشخص"
        
        stages = crop["stages_days"]
        stage_names = ["اولیه", "توسعه", "میانی", "پایانی"]
        
        if growth_day <= stages[0]:
            return stage_names[0]
        elif growth_day <= stages[0] + stages[1]:
            return stage_names[1]
        elif growth_day <= stages[0] + stages[1] + stages[2]:
            return stage_names[2]
        else:
            return stage_names[3]
    
    @classmethod
    def estimate_yield(cls, crop_key: str, water_stress_days: int, 
                       total_days: int) -> Dict:
        """
        تخمین عملکرد با در نظر گرفتن تنش آبی
        مرجع: FAO-32 (Doorenbos & Kassam, 1979)
        (Ya/Ym) = 1 - Ky × (1 - ETa/ETm)
        """
        crop = CROPS_DATABASE.get(crop_key)
        if not crop:
            return {}
        
        # ضریب حساسیت به کم‌آبی Ky (مقادیر FAO-33)
        ky_values = {
            "wheat": 1.10, "barley": 0.90, "maize": 1.25,
            "rice": 1.10, "sorghum": 1.05, "soybean": 1.10,
            "cotton": 0.85, "sugarbeet": 1.05, "tomato": 1.10,
            "potato": 1.15, "alfalfa": 1.10,
        }
        
        ky = ky_values.get(crop_key, 1.0)
        stress_ratio = water_stress_days / total_days if total_days > 0 else 0
        yield_reduction = ky * stress_ratio
        relative_yield = max(0, 1 - yield_reduction)
        actual_yield = crop["y_potential_t_ha"] * relative_yield
        
        return {
            "crop_name_fa": crop["name_fa"],
            "potential_yield_t_ha": crop["y_potential_t_ha"],
            "actual_yield_t_ha": round(actual_yield, 2),
            "yield_reduction_percent": round(yield_reduction * 100, 1),
            "ky_factor": ky,
            "stress_ratio": round(stress_ratio, 3),
        }


# تابع کمکی
def get_all_crops_summary() -> Dict:
    """خلاصه تمام محصولات"""
    return {
        key: {
            "name_fa": c["name_fa"],
            "name_en": c["name_en"],
            "type": c["type"],
            "kc_mid": c["kc"]["mid"],
            "total_days": sum(c["stages_days"]),
            "y_potential_t_ha": c["y_potential_t_ha"],
        }
        for key, c in CROPS_DATABASE.items()
    }
'''
    write_file(API_DIR / "scientific_core" / "crops.py", content)


# ============================================================
# فایل 5: مدل‌های کربن
# ============================================================
def create_carbon():
    print("\n🌍 ایجاد مدل‌های کربن...")
    content = '''# api/scientific_core/carbon.py
"""
مدل‌های کربن خاک
مرجع:
  - RothC (Coleman & Jenkinson, 1996, 2005)
  - Century Model (Parton et al., 1987)
  - IPCC 2019 Refinement
  - ICBM (Andrén & Kätterer, 1997)
"""
import math
from typing import Dict, List


class RothC:
    """
    مدل Rothamsted Carbon (RothC-26.3)
    مرجع: Coleman & Jenkinson (1996)
    
    پنج حوض کربن:
    - DPM: Decomposable Plant Material (تجزیه‌پذیر سریع)
    - RPM: Resistant Plant Material (تجزیه‌پذیر کند)
    - BIO: Microbial Biomass
    - HUM: Humified Organic Matter
    - IOM: Inert Organic Matter
    """
    
    # نسبت‌های تجزیه
    DPM_RPM_RATIO = {
        "forest": 0.67,
        "grassland": 1.44,
        "arable_no_fym": 1.67,
        "arable_with_fym": 0.67,
    }
    
    @classmethod
    def simulate_year(cls, initial_soc: float, carbon_input_t_ha: float,
                      clay_percent: float, mean_temp_c: float,
                      annual_rain_mm: float, years: int = 100) -> Dict:
        """
        شبیه‌سازی ساده‌شده RothC
        """
        # ضرایب نرخ تجزیه (سال⁻¹)
        k_dpm = 10.0
        k_rpm = 0.3
        k_bio = 0.66
        k_hum = 0.02
        
        # محاسبه PE/P ratio (تعدیل‌کننده اقلیمی)
        if annual_rain_mm > 0:
            pe_ratio = 0.75 * (annual_rain_mm / 1000) ** (-0.3)
        else:
            pe_ratio = 1.0
        
        # محاسبه ضریب رس
        clay_factor = 1.0 + (0.015 * clay_percent)
        
        # مقدار IOM (ماده آلی غیرفعال)
        iom = 0.049 * (initial_soc ** 1.139)
        active_soc = initial_soc - iom
        
        # تقسیم اولیه
        dpm_ratio = cls.DPM_RPM_RATIO["arable_no_fym"]
        dpm = active_soc * 0.59 * (dpm_ratio / (dpm_ratio + 1))
        rpm = active_soc * 0.59 * (1 / (dpm_ratio + 1))
        bio = active_soc * 0.02
        hum = active_soc * 0.39
        
        yearly = []
        for year in range(1, years + 1):
            # تعدیل اقلیمی سالانه
            temp_factor = 0.5 + 0.02 * mean_temp_c
            temp_factor = max(0.3, min(1.5, temp_factor))
            
            rate_mod = temp_factor * pe_ratio
            
            # تجزیه سالانه
            dpm_dec = dpm * (1 - math.exp(-k_dpm * rate_mod))
            rpm_dec = rpm * (1 - math.exp(-k_rpm * rate_mod))
            bio_dec = bio * (1 - math.exp(-k_bio * rate_mod))
            hum_dec = hum * (1 - math.exp(-k_hum * rate_mod))
            
            # ورودی جدید
            dpm_in = carbon_input_t_ha * (dpm_ratio / (dpm_ratio + 1))
            rpm_in = carbon_input_t_ha * (1 / (dpm_ratio + 1))
            
            # به‌روزرسانی حوض‌ها
            dpm = dpm - dpm_dec + dpm_in
            rpm = rpm - rpm_dec + rpm_in
            
            # تقسیم تجزیه‌شده
            total_dec = dpm_dec + rpm_dec + bio_dec + hum_dec
            bio_gain = 0.55 * total_dec
            hum_gain = 0.45 * total_dec * clay_factor
            
            bio = bio - bio_dec + bio_gain
            hum = hum - hum_dec + hum_gain
            
            # SOC کل
            total_soc = dpm + rpm + bio + hum + iom
            
            yearly.append({
                "year": year,
                "soc_t_ha": round(total_soc, 3),
                "dpm": round(dpm, 3),
                "rpm": round(rpm, 3),
                "bio": round(bio, 3),
                "hum": round(hum, 3),
                "iom": round(iom, 3),
                "annual_change_t_ha": round(total_soc - (yearly[-1]["soc_t_ha"] if yearly else initial_soc), 3),
            })
        
        final_soc = yearly[-1]["soc_t_ha"]
        return {
            "initial_soc": initial_soc,
            "final_soc": round(final_soc, 3),
            "soc_change_t_ha": round(final_soc - initial_soc, 3),
            "soc_change_percent": round((final_soc - initial_soc) / initial_soc * 100, 2),
            "yearly": yearly,
        }


class IPCC_Tier1:
    """
    مدل IPCC Tier 1 برای تغییرات کربن خاک
    مرجع: IPCC 2019 Refinement, Chapter 6
    فرمول: ΔC = (SOC0 - L) × (1 - e^(-1/L)) × A
    """
    
    # فاکتورهای کاربری اراضی (FLU)
    F_LU = {
        "cropland_continued": 0.80,
        "cropland_converted_from_forest": 0.69,
        "cropland_converted_from_grassland": 0.85,
        "paddy_rice": 0.78,
        "perennial": 1.00,
        "set_aside_less_20y": 0.90,
        "set_aside_more_20y": 1.00,
        "improved_grassland": 1.04,
        "native_grassland": 1.00,
    }
    
    # فاکتورهای مدیریت (FMG)
    F_MG = {
        "full_tillage": 1.00,
        "reduced_tillage": 1.06,
        "no_till": 1.10,
        "intensive": 0.95,
    }
    
    # فاکتورهای ورودی (FI)
    F_I = {
        "low": 0.95,
        "medium": 1.00,
        "high": 1.37,
        "high_with_manure": 1.60,
    }
    
    @classmethod
    def calculate(cls, area_ha: float, soc_reference: float,
                  f_lu: str, f_mg: str, f_i: str, 
                  time_period: int = 20) -> Dict:
        """
        محاسبه تغییرات کربن خاک
        
        Args:
            area_ha: مساحت (هکتار)
            soc_reference: SOC مرجع (t C/ha)
            f_lu, f_mg, f_i: کلیدهای فاکتورها
            time_period: دوره زمانی (سال)
        """
        flu = cls.F_LU.get(f_lu, 1.0)
        fmg = cls.F_MG.get(f_mg, 1.0)
        fi = cls.F_I.get(f_i, 1.0)
        
        # SOC جدید
        soc_new = soc_reference * flu * fmg * fi
        
        # تغییر سالانه
        default_time = 20
        delta_c_annual = (soc_new - soc_reference) / default_time
        
        # تغییر کل
        delta_c_total = delta_c_annual * min(time_period, default_time)
        
        # تبدیل به CO2e (× 3.67)
        co2e_annual = delta_c_annual * 3.67 * area_ha
        co2e_total = delta_c_total * 3.67 * area_ha
        
        return {
            "area_ha": area_ha,
            "soc_reference_t_ha": soc_reference,
            "soc_new_t_ha": round(soc_new, 3),
            "factors": {"F_LU": flu, "F_MG": fmg, "F_I": fi},
            "delta_c_annual_t_ha": round(delta_c_annual, 3),
            "delta_c_total_t_ha": round(delta_c_total, 3),
            "co2e_annual_ton": round(co2e_annual, 2),
            "co2e_total_ton": round(co2e_total, 2),
            "sequestration_or_loss": "sequestration" if delta_c_annual > 0 else "loss",
        }


class ICBM:
    """
    Introductory Carbon Balance Model
    مرجع: Andrén & Kätterer (1997)
    مدل دو حوضی ساده
    """
    
    @classmethod
    def simulate(cls, initial_c: float, annual_input: float,
                 k_young: float, k_old: float, 
                 connection_factor: float, years: int = 50) -> Dict:
        """
        Args:
            initial_c: کربن اولیه (t/ha)
            annual_input: ورودی سالانه (t/ha/yr)
            k_young: نرخ تجزیه حوض جوان
            k_old: نرخ تجزیه حوض قدیمی
            connection_factor: ضریب اتصال بین حوض‌ها
        """
        # تقسیم اولیه
        young = initial_c * 0.3
        old = initial_c * 0.7
        
        yearly = []
        for year in range(1, years + 1):
            # تجزیه
            young_dec = young * k_young
            old_dec = old * k_old
            
            # ورودی
            young_in = annual_input * 0.7
            old_in = annual_input * 0.3
            
            # انتقال بین حوض‌ها
            transfer = young_dec * connection_factor
            
            # به‌روزرسانی
            young = young - young_dec + young_in
            old = old - old_dec + old_in + transfer
            
            total = young + old
            yearly.append({
                "year": year,
                "total_c": round(total, 3),
                "young_pool": round(young, 3),
                "old_pool": round(old, 3),
                "annual_change": round(total - (yearly[-1]["total_c"] if yearly else initial_c), 3),
            })
        
        return {
            "initial_c": initial_c,
            "final_c": round(yearly[-1]["total_c"], 3),
            "yearly": yearly,
        }
'''
    write_file(API_DIR / "scientific_core" / "carbon.py", content)


# ============================================================
# فایل 6: مدل‌های فرسایش
# ============================================================
def create_erosion():
    print("\n⛰️ ایجاد مدل‌های فرسایش...")
    content = '''# api/scientific_core/erosion.py
"""
مدل‌های فرسایش خاک
مرجع:
  - RUSLE (Renard et al., 1997) - USDA Agriculture Handbook 703
  - MUSLE (Williams, 1975)
  - USLE (Wischmeier & Smith, 1978)
  - RWEQ (Fryrear et al., 1998) - فرسایش بادی
"""
import math
from typing import Dict, List


class RUSLE:
    """
    Revised Universal Soil Loss Equation
    مرجع: Renard et al. (1997)
    فرمول: A = R × K × LS × C × P
    
    A: نرخ فرسایش (t/ha/yr)
    R: عامل فرسندگی بارش (MJ·mm/ha·h·yr)
    K: عامل فرسایش‌پذیری خاک (t·h/MJ·mm)
    LS: عامل طول-شیب (بدون واحد)
    C: عامل پوشش و مدیریت (بدون واحد)
    P: عامل حفاظت (بدون واحد)
    """
    
    # مقادیر K پیش‌فرض بر اساس بافت خاک
    K_DEFAULTS = {
        "sand": 0.05,
        "loamy_sand": 0.10,
        "sandy_loam": 0.20,
        "loam": 0.30,
        "silt_loam": 0.40,
        "silty_clay_loam": 0.35,
        "clay_loam": 0.25,
        "sandy_clay": 0.15,
        "clay": 0.10,
    }
    
    # مقادیر C بر اساس کاربری اراضی
    C_DEFAULTS = {
        "forest": 0.001,
        "grass_permanent": 0.01,
        "pasture_good": 0.02,
        "pasture_degraded": 0.10,
        "cropland_conventional": 0.40,
        "cropland_contour": 0.25,
        "cropland_contour_terrace": 0.15,
        "cropland_no_till": 0.10,
        "cropland_no_till_cover": 0.05,
        "orchard": 0.15,
        "urban": 0.05,
        "bare_soil": 1.00,
    }
    
    # مقادیر P بر اساس روش حفاظتی
    P_DEFAULTS = {
        "no_practice": 1.00,
        "contour_farming": 0.60,
        "contour_stripcropping": 0.50,
        "terrace": 0.30,
        "contour_terrace": 0.20,
        "grass_waterway": 0.40,
    }
    
    @classmethod
    def calculate_r(cls, monthly_rainfall_mm: List[float]) -> float:
        """
        محاسبه عامل R (فرسندگی بارش)
        روش: Wischmeier & Smith (1978)
        R = Σ(0.276 × P × EI30)
        """
        # روش ساده‌شده بر اساس بارش ماهانه
        r = 0
        for p in monthly_rainfall_mm:
            if p > 0:
                # فرمول تجربی
                r += 0.276 * p * (10 + 0.5 * p)
        return r
    
    @classmethod
    def calculate_k(cls, soil_texture: str, organic_matter: float = 2.0,
                    structure: int = 2, permeability: int = 3) -> float:
        """
        محاسبه عامل K (فرسایش‌پذیری خاک)
        روش: Wischmeier et al. (1971)
        """
        if soil_texture in cls.K_DEFAULTS:
            return cls.K_DEFAULTS[soil_texture]
        return 0.30
    
    @classmethod
    def calculate_ls(cls, slope_length_m: float, slope_percent: float,
                     rill_ratio: float = 0.5) -> float:
        """
        محاسبه عامل LS (طول-شیب)
        روش: McCool et al. (1997)
        LS = (L/22.13)^m × (65.41 × sin²β + 4.56 × sinβ + 0.065)
        """
        if slope_length_m <= 0 or slope_percent <= 0:
            return 1.0
        
        # تبدیل شیب درصد به زاویه
        slope_rad = math.atan(slope_percent / 100)
        sin_beta = math.sin(slope_rad)
        
        # محاسبه m بر اساس نسبت rill/interrill
        if slope_percent < 1:
            m = 0.2
        elif slope_percent < 3:
            m = 0.3
        elif slope_percent < 5:
            m = 0.4
        else:
            m = 0.5
        
        # فاکتور L
        l_factor = (slope_length_m / 22.13) ** m
        
        # فاکتور S
        s_factor = 65.41 * sin_beta**2 + 4.56 * sin_beta + 0.065
        
        return l_factor * s_factor
    
    @classmethod
    def calculate(cls, r: float, k: float = None, ls: float = None,
                  c: float = None, p: float = None,
                  soil_texture: str = "loam",
                  land_use: str = "cropland_conventional",
                  conservation: str = "no_practice",
                  slope_length_m: float = 50,
                  slope_percent: float = 5) -> Dict:
        """محاسبه کامل RUSLE"""
        if k is None:
            k = cls.calculate_k(soil_texture)
        if ls is None:
            ls = cls.calculate_ls(slope_length_m, slope_percent)
        if c is None:
            c = cls.C_DEFAULTS.get(land_use, 0.30)
        if p is None:
            p = cls.P_DEFAULTS.get(conservation, 1.0)
        
        # محاسبه فرسایش
        a = r * k * ls * c * p
        
        # تفسیر شدت
        if a < 5:
            severity = "بسیار کم"
            color = "#10b981"
        elif a < 10:
            severity = "کم"
            color = "#84cc16"
        elif a < 15:
            severity = "متوسط"
            color = "#f59e0b"
        elif a < 25:
            severity = "زیاد"
            color: "#f97316"
            severity = "زیاد"
            color = "#f97316"
        elif a < 40:
            severity = "خیلی زیاد"
            color = "#ef4444"
        else:
            severity = "بحرانی"
            color = "#7f1d1d"
        
        return {
            "erosion_t_ha_yr": round(a, 2),
            "factors": {
                "R": round(r, 2),
                "K": round(k, 3),
                "LS": round(ls, 2),
                "C": round(c, 3),
                "P": round(p, 2),
            },
            "severity": severity,
            "color": color,
            "tolerable_loss_t_ha_yr": 5.0,  # T value
            "above_tolerance": a > 5.0,
        }


class MUSLE:
    """
    Modified Universal Soil Loss Equation
    مرجع: Williams (1975)
    کاربرد: فرسایش برای یک رویداد بارش
    فرمول: Y = 11.8 × (Q × qp × A)^0.56 × K × LS × C × P
    """
    
    @classmethod
    def calculate(cls, runoff_m3: float, peak_discharge_m3s: float,
                  area_ha: float, k: float = 0.30, ls: float = 1.0,
                  c: float = 0.30, p: float = 1.0) -> Dict:
        """محاسبه فرسایش رویداد"""
        term = runoff_m3 * peak_discharge_m3s * area_ha
        if term <= 0:
            return {"sediment_ton": 0}
        
        y = 11.8 * (term ** 0.56) * k * ls * c * p
        
        return {
            "sediment_ton": round(y, 2),
            "runoff_m3": runoff_m3,
            "peak_m3s": peak_discharge_m3s,
            "area_ha": area_ha,
        }


class WindErosion:
    """
    مدل‌های فرسایش بادی
    مرجع: RWEQ (Fryrear et al., 1998)
    """
    
    @classmethod
    def rweq_simplified(cls, wind_speed_ms: float, 
                        soil_roughness_cm: float = 2.0,
                        vegetation_cover_percent: float = 20.0,
                        soil_moisture_percent: float = 10.0) -> Dict:
        """
        فرسایش بادی ساده‌شده
        """
        # فاکتور اقلیمی (WF)
        wf = (wind_speed_ms ** 3) * 0.01
        
        # فاکتور پوشش گیاهی (VC)
        vc = math.exp(-0.05 * vegetation_cover_percent)
        
        # فاکتور زبری خاک (SC)
        sc = 1 / (1 + 0.01 * soil_roughness_cm)
        
        # فاکتور رطوبت (MC)
        mc = 1 - max(0, (soil_moisture_percent - 5) / 20)
        
        # پتانسیل فرسایش
        erosion_potential = wf * vc * sc * mc
        
        # تفسیر
        if erosion_potential < 1:
            severity = "کم"
        elif erosion_potential < 5:
            severity = "متوسط"
        elif erosion_potential < 15:
            severity = "زیاد"
        else:
            severity = "بحرانی"
        
        return {
            "potential_t_ha_yr": round(erosion_potential, 2),
            "factors": {
                "wind_factor": round(wf, 2),
                "vegetation_factor": round(vc, 3),
                "roughness_factor": round(sc, 3),
                "moisture_factor": round(mc, 3),
            },
            "severity": severity,
        }
'''
    write_file(API_DIR / "scientific_core" / "erosion.py", content)


# ============================================================
# فایل 7: شاخص‌های خشکسالی
# ============================================================
def create_drought():
    print("\n🏜️ ایجاد شاخص‌های خشکسالی...")
    content = '''# api/scientific_core/drought.py
"""
شاخص‌های خشکسالی استاندارد جهانی
مرجع:
  - WMO (2012) - Standardized Precipitation Index
  - Vicente-Serrano et al. (2010) - SPEI
  - Palmer (1965) - PDSI
  - Kogan (1995) - VHI
"""
import math
import statistics
from typing import Dict, List, Tuple


class SPI:
    """
    Standardized Precipitation Index
    مرجع: McKee et al. (1993), WMO (2012)
    
    تفسیر:
      SPI ≥ 2.0: بسیار تر
      1.5 ≤ SPI < 2.0: تر
      1.0 ≤ SPI < 1.5: نسبتاً تر
      -1.0 < SPI < 1.0: نرمال
      -1.5 < SPI ≤ -1.0: نسبتاً خشک
      -2.0 < SPI ≤ -1.5: خشک
      SPI ≤ -2.0: بسیار خشک
    """
    
    @classmethod
    def calculate(cls, precipitation_series: List[float], 
                  time_scale: int = 3) -> List[Dict]:
        """
        محاسبه SPI برای یک سری زمانی بارش
        """
        if len(precipitation_series) < time_scale:
            return []
        
        # محاسبه بارش تجمعی متحرک
        accumulated = []
        for i in range(time_scale - 1, len(precipitation_series)):
            total = sum(precipitation_series[i - time_scale + 1:i + 1])
            accumulated.append(total)
        
        # محاسبه میانگین و انحراف معیار
        mean = statistics.mean(accumulated)
        std = statistics.stdev(accumulated) if len(accumulated) > 1 else 1
        
        if std == 0:
            std = 1
        
        # محاسبه SPI
        results = []
        for i, value in enumerate(accumulated):
            spi = (value - mean) / std
            classification = cls._classify(spi)
            
            results.append({
                "index": i + time_scale - 1,
                "accumulated_mm": round(value, 2),
                "spi": round(spi, 2),
                "classification": classification["label"],
                "severity": classification["severity"],
                "color": classification["color"],
            })
        
        return results
    
    @staticmethod
    def _classify(spi: float) -> Dict:
        """طبقه‌بندی SPI"""
        if spi >= 2.0:
            return {"label": "بسیار تر", "severity": "extremely_wet", "color": "#0c4a6e"}
        elif spi >= 1.5:
            return {"label": "تر", "severity": "very_wet", "color": "#0369a1"}
        elif spi >= 1.0:
            return {"label": "نسبتاً تر", "severity": "moderately_wet", "color": "#0ea5e9"}
        elif spi > -1.0:
            return {"label": "نرمال", "severity": "near_normal", "color": "#64748b"}
        elif spi > -1.5:
            return {"label": "نسبتاً خشک", "severity": "moderately_dry", "color": "#f59e0b"}
        elif spi > -2.0:
            return {"label": "خشک", "severity": "severely_dry", "color": "#ea580c"}
        else:
            return {"label": "بسیار خشک", "severity": "extremely_dry", "color": "#7f1d1d"}


class SPEI:
    """
    Standardized Precipitation Evapotranspiration Index
    مرجع: Vicente-Serrano et al. (2010)
    """
    
    @staticmethod
    def thornthwaite_eto(mean_temp_c: float, latitude: float) -> float:
        """
        محاسبه ETo با روش Thornthwaite
        """
        if mean_temp_c <= 0:
            return 0
        
        # شاخص حرارتی سالانه
        i = 12 * ((mean_temp_c / 5) ** 1.514)
        
        # ضریب a
        a = (6.75e-7 * i**3 - 7.71e-5 * i**2 + 0.01792 * i + 0.49239)
        
        # ETo ماهانه (mm)
        eto = 16 * (10 * mean_temp_c / i) ** a
        
        return max(0, eto)
    
    @classmethod
    def calculate(cls, precipitation: List[float], 
                  temperature: List[float],
                  latitude: float = 35.0,
                  time_scale: int = 3) -> List[Dict]:
        """محاسبه SPEI"""
        if len(precipitation) != len(temperature):
            return []
        
        # محاسبه بیلان آبی (P - PET)
        water_balance = []
        for i in range(len(precipitation)):
            pet = cls.thornthwaite_eto(temperature[i], latitude)
            water_balance.append(precipitation[i] - pet)
        
        # محاسبه SPI روی بیلان آبی
        return SPI.calculate(water_balance, time_scale)


class VHI:
    """
    Vegetation Health Index
    مرجع: Kogan (1995)
    VHI = α × VCI + (1-α) × TCI
    """
    
    @staticmethod
    def calculate_vci(ndvi_series: List[float]) -> List[float]:
        """Vegetation Condition Index"""
        min_ndvi = min(ndvi_series)
        max_ndvi = max(ndvi_series)
        denom = max_ndvi - min_ndvi
        if denom == 0:
            return [50.0] * len(ndvi_series)
        return [100 * (v - min_ndvi) / denom for v in ndvi_series]
    
    @staticmethod
    def calculate_tci(temperature_series: List[float]) -> List[float]:
        """Temperature Condition Index"""
        min_t = min(temperature_series)
        max_t = max(temperature_series)
        denom = max_t - min_t
        if denom == 0:
            return [50.0] * len(temperature_series)
        return [100 * (max_t - t) / denom for t in temperature_series]
    
    @classmethod
    def calculate(cls, ndvi_series: List[float], 
                  temperature_series: List[float],
                  alpha: float = 0.5) -> List[Dict]:
        """محاسبه VHI"""
        if len(ndvi_series) != len(temperature_series):
            return []
        
        vci = cls.calculate_vci(ndvi_series)
        tci = cls.calculate_tci(temperature_series)
        
        results = []
        for i in range(len(vci)):
            vhi = alpha * vci[i] + (1 - alpha) * tci[i]
            
            # طبقه‌بندی
            if vhi >= 60:
                severity = "مطلوب"
                color = "#10b981"
            elif vhi >= 40:
                severity = "تنش خفیف"
                color = "#84cc16"
            elif vhi >= 25:
                severity = "تنش متوسط"
                color = "#f59e0b"
            elif vhi >= 15:
                severity = "تنش شدید"
                color = "#ea580c"
            else:
                severity = "خشکسالی شدید"
                color = "#7f1d1d"
            
            results.append({
                "index": i,
                "vhi": round(vhi, 2),
                "vci": round(vci[i], 2),
                "tci": round(tci[i], 2),
                "severity": severity,
                "color": color,
            })
        
        return results


class KBDI:
    """
    Keetch-Byram Drought Index
    مرجع: Keetch & Byram (1968)
    کاربرد: پتانسیل آتش‌سوزی جنگل
    """
    
    @classmethod
    def calculate_series(cls, daily_rainfall_mm: List[float],
                         daily_max_temp_c: List[float],
                         annual_rainfall_mm: float = 1000,
                         initial_kbdi: float = 200) -> List[Dict]:
        """محاسبه سری زمانی KBDI"""
        results = []
        kbdi = initial_kbdi
        
        for i in range(len(daily_rainfall_mm)):
            rain = daily_rainfall_mm[i]
            temp = daily_max_temp_c[i]
            
            # کاهش ناشی از بارش
            if rain > 5:
                effective_rain = rain - 5
                kbdi -= effective_rain * 25.4
                kbdi = max(0, kbdi)
            
            # افزایش ناشی از تبخیر
            drought_factor = (203.2 - kbdi) / (1 + 0.8 * (annual_rainfall_mm / 25.4))
            temp_factor = (temp - 15) / 5.6 if temp > 15 else 0
            increase = drought_factor * temp_factor * 0.001 * 25.4
            kbdi += increase
            kbdi = min(800, kbdi)
            
            # طبقه‌بندی
            if kbdi < 200:
                severity = "خیس"
                color = "#0ea5e9"
            elif kbdi < 400:
                severity = "متوسط"
                color = "#84cc16"
            elif kbdi < 600:
                severity = "خشک"
                color = "#f59e0b"
            elif kbdi < 700:
                severity = "خیلی خشک"
                color = "#ea580c"
            else:
                severity = "بحرانی"
                color = "#7f1d1d"
            
            results.append({
                "day": i,
                "kbdi": round(kbdi, 1),
                "severity": severity,
                "color": color,
            })
        
        return results
'''
    write_file(API_DIR / "scientific_core" / "drought.py", content)


# ============================================================
# فایل 8: آب خاک
# ============================================================
def create_soil_water():
    print("\n💧 ایجاد مدل‌های آب خاک...")
    content = '''# api/scientific_core/soil_water.py
"""
مدل‌های آب خاک
مرجع:
  - van Genuchten (1980)
  - Brooks & Corey (1964)
  - Campbell (1974)
  - FAO-56
"""
import math
from typing import Dict, List


class VanGenuchten:
    """
    مدل van Genuchten-Mualem
    مرجع: van Genuchten, M.T. (1980). Soil Sci. Soc. Am. J. 44:892-898
    """
    
    @staticmethod
    def theta_from_psi(psi_cm: float, theta_r: float, theta_s: float,
                       alpha: float, n: float) -> float:
        """رطوبت از مکش"""
        if psi_cm >= 0:
            return theta_s
        m = 1 - 1/n
        se = (1 + (alpha * abs(psi_cm))**n) ** (-m)
        return theta_r + (theta_s - theta_r) * se
    
    @staticmethod
    def psi_from_theta(theta: float, theta_r: float, theta_s: float,
                       alpha: float, n: float) -> float:
        """مکش از رطوبت"""
        if theta >= theta_s:
            return 0
        if theta <= theta_r:
            return float("inf")
        m = 1 - 1/n
        se = (theta - theta_r) / (theta_s - theta_r)
        return -(1/alpha) * (se**(-1/m) - 1)**(1/n)
    
    @staticmethod
    def hydraulic_conductivity(theta: float, theta_r: float, theta_s: float,
                               alpha: float, n: float, k_sat: float) -> float:
        """هدایت هیدرولیکی غیراشباع (Mualem, 1976)"""
        m = 1 - 1/n
        se = max(0.001, min(0.999, (theta - theta_r) / (theta_s - theta_r)))
        term = 1 - (1 - se**(1/m))**m
        return k_sat * (se**0.5) * (term**2)


class BrooksCorey:
    """
    مدل Brooks-Corey
    مرجع: Brooks & Corey (1964)
    """
    
    @staticmethod
    def theta_from_psi(psi_cm: float, theta_s: float, 
                       psi_air_entry_cm: float, lambda_bc: float) -> float:
        """رطوبت از مکش"""
        if psi_cm >= 0:
            return theta_s
        if abs(psi_cm) <= psi_air_entry_cm:
            return theta_s
        return theta_s * (psi_air_entry_cm / abs(psi_cm)) ** lambda_bc
    
    @staticmethod
    def hydraulic_conductivity(theta: float, theta_s: float,
                               k_sat: float, psi_air_entry_cm: float,
                               lambda_bc: float, psi_cm: float) -> float:
        """هدایت هیدرولیکی"""
        if theta >= theta_s:
            return k_sat
        se = theta / theta_s
        return k_sat * se ** (3 + 2/lambda_bc)


class Campbell:
    """
    مدل Campbell
    مرجع: Campbell (1974)
    """
    
    @staticmethod
    def psi_from_theta(theta: float, theta_s: float, 
                       psi_air_entry: float, b: float) -> float:
        """مکش از رطوبت"""
        if theta >= theta_s:
            return psi_air_entry
        se = theta / theta_s
        return psi_air_entry * se ** (-b)


class FAO56WaterBalance:
    """
    بیلان آبی FAO-56
    مرجع: Allen et al. (1998), Chapter 8
    """
    
    @staticmethod
    def daily_balance(sw_prev: float, rainfall: float, irrigation: float,
                      etc: float, cn: float = 75, root_depth_mm: float = 500,
                      fc_mm: float = 150, wp_mm: float = 75) -> Dict:
        """
        بیلان آبی روزانه
        
        Args:
            sw_prev: آب خاک قبلی (mm)
            rainfall: بارش (mm)
            irrigation: آبیاری (mm)
            etc: تبخیر و تعرق محصول (mm)
            cn: Curve Number برای رواناب
            root_depth_mm: عمق ریشه (mm)
            fc_mm: ظرفیت زراعی (mm)
            wp_mm: نقطه پژمردگی (mm)
        """
        # محاسبه رواناب
        s = (25400 / cn) - 254 if cn > 0 else 0
        ia = 0.2 * s
        if rainfall > ia:
            runoff = ((rainfall - ia) ** 2) / (rainfall - ia + s)
        else:
            runoff = 0
        
        # بارش مؤثر
        effective_rain = rainfall - runoff
        
        # بیلان
        sw_new = sw_prev + effective_rain + irrigation - etc
        
        # نشت عمیق
        dp = 0
        if sw_new > fc_mm:
            dp = sw_new - fc_mm
            sw_new = fc_mm
        
        # حداقل
        if sw_new < 0:
            sw_new = 0
        
        # وضعیت
        taw = fc_mm - wp_mm
        raw = taw * 0.5
        
        if sw_new > fc_mm:
            status = "اشباع"
        elif sw_new > (fc_mm + wp_mm) / 2:
            status = "مطلوب"
        elif sw_new > wp_mm:
            status = "تنش خفیف"
        else:
            status = "تنش شدید"
        
        return {
            "soil_water_mm": round(sw_new, 2),
            "soil_water_percent": round((sw_new / taw) * 100, 1),
            "effective_rain_mm": round(effective_rain, 2),
            "runoff_mm": round(runoff, 2),
            "deep_percolation_mm": round(dp, 2),
            "status": status,
        }
'''
    write_file(API_DIR / "scientific_core" / "soil_water.py", content)


# ============================================================
# فایل 9: پایگاه‌های داده مرجع
# ============================================================
def create_databases():
    print("\n📦 ایجاد پایگاه‌های داده مرجع...")
    content = '''# api/scientific_core/databases.py
"""
پایگاه‌های داده مرجع برای تمام ماژول‌ها
"""

# ============================================================
# USDA Soil Texture Database (11 نوع)
# ============================================================
SOIL_TEXTURE_DATABASE = {
    "sand": {
        "name_fa": "شن",
        "name_en": "Sand",
        "sand_percent": 90, "silt_percent": 5, "clay_percent": 5,
        "theta_r": 0.045, "theta_s": 0.430,
        "alpha_vg": 0.145, "n_vg": 2.68,
        "k_sat_cm_day": 8.25,
        "bulk_density": 1.55,
        "field_capacity": 0.10, "wilting_point": 0.05,
        "usda_class": "sand",
    },
    "loamy_sand": {
        "name_fa": "شن لومی",
        "name_en": "Loamy Sand",
        "sand_percent": 80, "silt_percent": 12, "clay_percent": 8,
        "theta_r": 0.057, "theta_s": 0.410,
        "alpha_vg": 0.124, "n_vg": 2.28,
        "k_sat_cm_day": 4.50,
        "bulk_density": 1.50,
        "field_capacity": 0.14, "wilting_point": 0.07,
    },
    "sandy_loam": {
        "name_fa": "لومی شنی",
        "name_en": "Sandy Loam",
        "sand_percent": 65, "silt_percent": 20, "clay_percent": 15,
        "theta_r": 0.065, "theta_s": 0.410,
        "alpha_vg": 0.075, "n_vg": 1.89,
        "k_sat_cm_day": 2.50,
        "bulk_density": 1.45,
        "field_capacity": 0.20, "wilting_point": 0.10,
    },
    "loam": {
        "name_fa": "لوم",
        "name_en": "Loam",
        "sand_percent": 40, "silt_percent": 40, "clay_percent": 20,
        "theta_r": 0.078, "theta_s": 0.430,
        "alpha_vg": 0.036, "n_vg": 1.56,
        "k_sat_cm_day": 1.20,
        "bulk_density": 1.35,
        "field_capacity": 0.27, "wilting_point": 0.13,
    },
    "silt_loam": {
        "name_fa": "لومی سیلتی",
        "name_en": "Silty Loam",
        "sand_percent": 20, "silt_percent": 65, "clay_percent": 15,
        "theta_r": 0.067, "theta_s": 0.450,
        "alpha_vg": 0.028, "n_vg": 1.45,
        "k_sat_cm_day": 0.80,
        "bulk_density": 1.30,
        "field_capacity": 0.32, "wilting_point": 0.14,
    },
    "sandy_clay_loam": {
        "name_fa": "لومی رسی شنی",
        "name_en": "Sandy Clay Loam",
        "sand_percent": 55, "silt_percent": 15, "clay_percent": 30,
        "theta_r": 0.100, "theta_s": 0.390,
        "alpha_vg": 0.059, "n_vg": 1.51,
        "k_sat_cm_day": 0.60,
        "bulk_density": 1.35,
        "field_capacity": 0.25, "wilting_point": 0.14,
    },
    "clay_loam": {
        "name_fa": "لومی رسی",
        "name_en": "Clay Loam",
        "sand_percent": 30, "silt_percent": 35, "clay_percent": 35,
        "theta_r": 0.095, "theta_s": 0.410,
        "alpha_vg": 0.019, "n_vg": 1.31,
        "k_sat_cm_day": 0.35,
        "bulk_density": 1.30,
        "field_capacity": 0.32, "wilting_point": 0.20,
    },
    "silty_clay_loam": {
        "name_fa": "لومی رسی سیلتی",
        "name_en": "Silty Clay Loam",
        "sand_percent": 10, "silt_percent": 55, "clay_percent": 35,
        "theta_r": 0.089, "theta_s": 0.430,
        "alpha_vg": 0.016, "n_vg": 1.26,
        "k_sat_cm_day": 0.25,
        "bulk_density": 1.25,
        "field_capacity": 0.35, "wilting_point": 0.21,
    },
    "sandy_clay": {
        "name_fa": "رسی شنی",
        "name_en": "Sandy Clay",
        "sand_percent": 55, "silt_percent": 5, "clay_percent": 40,
        "theta_r": 0.100, "theta_s": 0.380,
        "alpha_vg": 0.027, "n_vg": 1.23,
        "k_sat_cm_day": 0.30,
        "bulk_density": 1.35,
        "field_capacity": 0.30, "wilting_point": 0.20,
    },
    "silty_clay": {
        "name_fa": "رسی سیلتی",
        "name_en": "Silty Clay",
        "sand_percent": 5, "silt_percent": 50, "clay_percent": 45,
        "theta_r": 0.089, "theta_s": 0.400,
        "alpha_vg": 0.013, "n_vg": 1.17,
        "k_sat_cm_day": 0.18,
        "bulk_density": 1.25,
        "field_capacity": 0.37, "wilting_point": 0.24,
    },
    "clay": {
        "name_fa": "رس",
        "name_en": "Clay",
        "sand_percent": 20, "silt_percent": 20, "clay_percent": 60,
        "theta_r": 0.068, "theta_s": 0.380,
        "alpha_vg": 0.010, "n_vg": 1.15,
        "k_sat_cm_day": 0.12,
        "bulk_density": 1.20,
        "field_capacity": 0.38, "wilting_point": 0.25,
    },
}


# ============================================================
# ضرایب RUSLE بر اساس اقلیم
# ============================================================
R_FACTOR_BY_CLIMATE = {
    "mediterranean": {"annual_r_mm": 500, "r_factor": 350, "description": "مدیترانه‌ای"},
    "arid": {"annual_r_mm": 200, "r_factor": 150, "description": "خشک"},
    "semi_arid": {"annual_r_mm": 350, "r_factor": 250, "description": "نیمه‌خشک"},
    "humid_subtropical": {"annual_r_mm": 1000, "r_factor": 600, "description": "نیمه‌گرمسیری مرطوب"},
    "tropical": {"annual_r_mm": 1500, "r_factor": 900, "description": "گرمسیری"},
    "temperate": {"annual_r_mm": 800, "r_factor": 450, "description": "معتدل"},
}


# ============================================================
# آستانه‌های شاخص‌ها (IPCC, WMO)
# ============================================================
INDEX_THRESHOLDS = {
    "NDVI": {
        "water_snow_cloud": (-1.0, -0.1),
        "bare_soil": (-0.1, 0.1),
        "sparse_vegetation": (0.1, 0.3),
        "moderate_vegetation": (0.3, 0.6),
        "dense_vegetation": (0.6, 0.8),
        "forest": (0.8, 1.0),
    },
    "SPI": {
        "extremely_wet": (2.0, float("inf")),
        "very_wet": (1.5, 2.0),
        "moderately_wet": (1.0, 1.5),
        "near_normal": (-1.0, 1.0),
        "moderately_dry": (-1.5, -1.0),
        "severely_dry": (-2.0, -1.5),
        "extremely_dry": (float("-inf"), -2.0),
    },
    "NBR": {
        "high_regeneration": (0.27, float("inf")),
        "dense_vegetation": (0.1, 0.27),
        "unburned": (-0.1, 0.1),
        "low_severity": (-0.25, -0.1),
        "moderate_severity": (-0.44, -0.25),
        "high_severity": (float("-inf"), -0.44),
    },
}


# ============================================================
# توابع کمکی
# ============================================================
def get_all_soils() -> dict:
    """دریافت تمام خاک‌ها"""
    return SOIL_TEXTURE_DATABASE


def get_soil(key: str) -> dict:
    """دریافت یک خاک خاص"""
    return SOIL_TEXTURE_DATABASE.get(key, SOIL_TEXTURE_DATABASE["loam"])


def get_all_thresholds() -> dict:
    """دریافت تمام آستانه‌ها"""
    return INDEX_THRESHOLDS
'''
    write_file(API_DIR / "scientific_core" / "databases.py", content)


# ============================================================
# فایل 10: Router مرکزی
# ============================================================
def create_router():
    print("\n🔌 ایجاد Scientific Core Router...")
    content = '''# api/scientific_core/router.py
"""
Router مرکزی برای دسترسی به تمام مدل‌های علمی
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, List, Optional

from . import indices, hydrology, crops, carbon, erosion, drought, soil_water, databases

router = APIRouter(prefix="/scientific", tags=["Scientific Core"])


# ============ Models ============
class BandsInput(BaseModel):
    blue: Optional[float] = None
    green: Optional[float] = None
    red: Optional[float] = None
    nir: Optional[float] = None
    red_edge: Optional[float] = None
    swir1: Optional[float] = None
    swir2: Optional[float] = None


class SCS_CN_Input(BaseModel):
    rainfall_mm: float
    curve_number: float = 75
    amc: str = "AMC_II"


class RUSLE_Input(BaseModel):
    r_factor: float = 400
    soil_texture: str = "loam"
    land_use: str = "cropland_conventional"
    conservation: str = "no_practice"
    slope_length_m: float = 50
    slope_percent: float = 5


class RothC_Input(BaseModel):
    initial_soc: float = 2.5
    carbon_input_t_ha: float = 2.0
    clay_percent: float = 25
    mean_temp_c: float = 18
    annual_rain_mm: float = 500
    years: int = 30


class IPCC_Tier1_Input(BaseModel):
    area_ha: float
    soc_reference: float = 30.0
    land_use_factor: str = "cropland_continued"
    management_factor: str = "full_tillage"
    input_factor: str = "medium"
    time_period: int = 20


class SPI_Input(BaseModel):
    precipitation: List[float]
    time_scale: int = 3


# ============ Endpoints ============
@router.get("/")
async def scientific_core_info():
    """اطلاعات کلی هسته علمی"""
    return {
        "name": "Econojin Scientific Core",
        "version": "1.0.0",
        "modules": {
            "spectral_indices": ["NDVI", "EVI", "SAVI", "MSAVI2", "GNDVI", "ARVI", "NDRE", "NDWI", "MNDWI", "NBR", "NDBI"],
            "hydrology": ["SCS-CN", "Rational", "Horton", "Philip", "Green-Ampt", "Muskingum"],
            "crops": ["FAO-56 Kc", "Penman-Monteith", "AquaCrop", "GDD"],
            "carbon": ["RothC", "Century", "ICBM", "IPCC Tier 1"],
            "erosion": ["RUSLE", "MUSLE", "RWEQ"],
            "drought": ["SPI", "SPEI", "VHI", "KBDI"],
            "soil_water": ["van Genuchten", "Brooks-Corey", "Campbell", "FAO-56 Balance"],
        },
        "databases": {
            "soils": len(databases.SOIL_TEXTURE_DATABASE),
            "crops": len(crops.CROPS_DATABASE),
        },
    }


@router.get("/soils")
async def list_soils():
    """لیست تمام خاک‌های USDA"""
    return databases.get_all_soils()


@router.get("/crops")
async def list_crops():
    """لیست تمام محصولات"""
    return crops.get_all_crops_summary()


@router.post("/indices/calculate")
async def calculate_indices(bands: BandsInput):
    """محاسبه تمام شاخص‌های طیفی"""
    bands_dict = bands.dict(exclude_none=True)
    results = indices.SpectralIndices.calculate_all(bands_dict)
    
    # اضافه کردن تفسیر
    if "NDVI" in results:
        results["NDVI_interpretation"] = indices.SpectralIndices.interpret_ndvi(results["NDVI"])
    
    return {"bands": bands_dict, "indices": results}


@router.post("/hydrology/scs-cn")
async def calculate_scs_cn(input: SCS_CN_Input):
    """محاسبه رواناب SCS-CN"""
    return hydrology.SCS_CN.calculate(input.rainfall_mm, input.curve_number, input.amc)


@router.post("/erosion/rusle")
async def calculate_rusle(input: RUSLE_Input):
    """محاسبه فرسایش RUSLE"""
    return erosion.RUSLE.calculate(
        r=input.r_factor,
        soil_texture=input.soil_texture,
        land_use=input.land_use,
        conservation=input.conservation,
        slope_length_m=input.slope_length_m,
        slope_percent=input.slope_percent,
    )


@router.post("/carbon/rothc")
async def calculate_rothc(input: RothC_Input):
    """شبیه‌سازی RothC"""
    return carbon.RothC.simulate_year(
        initial_soc=input.initial_soc,
        carbon_input_t_ha=input.carbon_input_t_ha,
        clay_percent=input.clay_percent,
        mean_temp_c=input.mean_temp_c,
        annual_rain_mm=input.annual_rain_mm,
        years=input.years,
    )


@router.post("/carbon/ipcc-tier1")
async def calculate_ipcc(input: IPCC_Tier1_Input):
    """محاسبه IPCC Tier 1"""
    return carbon.IPCC_Tier1.calculate(
        area_ha=input.area_ha,
        soc_reference=input.soc_reference,
        f_lu=input.land_use_factor,
        f_mg=input.management_factor,
        f_i=input.input_factor,
        time_period=input.time_period,
    )


@router.post("/drought/spi")
async def calculate_spi(input: SPI_Input):
    """محاسبه SPI"""
    return drought.SPI.calculate(input.precipitation, input.time_scale)


@router.get("/thresholds")
async def get_thresholds():
    """آستانه‌های شاخص‌ها"""
    return databases.get_all_thresholds()


@router.get("/crops/{crop_key}")
async def get_crop_details(crop_key: str):
    """جزئیات یک محصول"""
    crop = crops.CROPS_DATABASE.get(crop_key)
    if not crop:
        raise HTTPException(404, "محصول یافت نشد")
    return crop


@router.get("/crops/{crop_key}/kc/{day}")
async def get_kc_at_day(crop_key: str, day: int):
    """ضریب Kc در روز مشخص"""
    kc = crops.CropCalculator.get_kc_at_stage(crop_key, day)
    stage = crops.CropCalculator.get_growth_stage(crop_key, day)
    return {"crop": crop_key, "day": day, "kc": round(kc, 3), "stage": stage}
'''
    write_file(API_DIR / "scientific_core" / "router.py", content)


# ============================================================
# فایل 11: به‌روزرسانی main.py
# ============================================================
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    main_path = API_DIR / "main.py"
    
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    # اضافه کردن import
    if "scientific_core" not in content:
        content = content.replace(
            "from api.modules.soil_water.router import router as soil_water_router",
            "from api.modules.soil_water.router import router as soil_water_router\nfrom api.scientific_core.router import router as scientific_router"
        )
        
        # اضافه کردن router
        content = content.replace(
            'app.include_router(soil_water_router, prefix="/api/v1")',
            'app.include_router(soil_water_router, prefix="/api/v1")\napp.include_router(scientific_router, prefix="/api/v1")'
        )
        
        main_path.write_text(content, encoding="utf-8")
        print("   ✅ Scientific Core router اضافه شد")


# ============================================================
# Main
# ============================================================
def main():
    print("🧠 Econojin Scientific Core (ESC)")
    print("=" * 70)
    print("ایجاد پایگاه دانش علمی مرکزی")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    # ایجاد تمام فایل‌ها
    create_init()
    create_indices()
    create_hydrology()
    create_crops()
    create_carbon()
    create_erosion()
    create_drought()
    create_soil_water()
    create_databases()
    create_router()
    update_main()
    
    print("\n" + "=" * 70)
    print("✅ پایگاه دانش علمی مرکزی ایجاد شد!")
    print("\n📚 ماژول‌های علمی:")
    print("   🌱 شاخص‌های طیفی (11 شاخص)")
    print("   🌊 هیدرولوژی (SCS-CN, Rational, Horton, Philip, Green-Ampt, Muskingum)")
    print("   🌾 محصولات (20+ محصول با Kc چهار مرحله‌ای)")
    print("   🌍 کربن (RothC, IPCC Tier 1, ICBM)")
    print("   ⛰️ فرسایش (RUSLE, MUSLE, RWEQ)")
    print("   🏜️ خشکسالی (SPI, SPEI, VHI, KBDI)")
    print("   💧 آب خاک (van Genuchten, Brooks-Corey, Campbell, FAO-56)")
    print("   📦 پایگاه‌های داده (11 خاک USDA + 20 محصول)")
    print("")
    print("🔗 API Endpoints:")
    print("   GET  /api/v1/scientific/")
    print("   GET  /api/v1/scientific/soils")
    print("   GET  /api/v1/scientific/crops")
    print("   POST /api/v1/scientific/indices/calculate")
    print("   POST /api/v1/scientific/hydrology/scs-cn")
    print("   POST /api/v1/scientific/erosion/rusle")
    print("   POST /api/v1/scientific/carbon/rothc")
    print("   POST /api/v1/scientific/carbon/ipcc-tier1")
    print("   POST /api/v1/scientific/drought/spi")
    print("   GET  /api/v1/scientific/thresholds")
    print("")
    print("🚀 گام بعدی:")
    print("   1. ری‌استارت سرور:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("   2. مشاهده مستندات:")
    print("      http://localhost:8000/docs")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())