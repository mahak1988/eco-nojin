"""
🚀 پیاده‌سازی سرویس‌های اولویت‌دار در پروژه Econojin
فاز ۱: Open-Meteo, SoilGrids, Sentinel-2, Leaflet
"""
from pathlib import Path
import json

print("=" * 100)
print("🚀 IMPLEMENTING PRIORITY SERVICES - PHASE 1")
print("=" * 100)

ROOT = Path('.')
BACKEND = ROOT / 'api'
FRONTEND = ROOT / 'apps/web/src'

# ============================================================
# 1. BACKEND: Open-Meteo Weather Service
# ============================================================
print("\n🌦️  1. Creating Open-Meteo Weather Service...")

weather_service_dir = BACKEND / 'services' / 'weather'
weather_service_dir.mkdir(parents=True, exist_ok=True)

open_meteo_service = '''"""
Open-Meteo Weather Service
سرویس هواشناسی رایگان بدون نیاز به API Key
Documentation: https://open-meteo.com/en/docs
"""
import httpx
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from pydantic import BaseModel


class WeatherCurrent(BaseModel):
    temperature: float
    humidity: int
    wind_speed: float
    wind_direction: int
    weather_code: int
    precipitation: float
    cloud_cover: int
    pressure: float
    timestamp: str


class WeatherDaily(BaseModel):
    date: str
    temp_max: float
    temp_min: float
    precipitation_sum: float
    precipitation_probability: int
    wind_speed_max: float
    sunrise: str
    sunset: str
    uv_index_max: float


class WeatherForecast(BaseModel):
    location: Dict[str, float]
    current: WeatherCurrent
    daily: List[WeatherDaily]
    timezone: str


class OpenMeteoService:
    """سرویس هواشناسی Open-Meteo - کاملاً رایگان"""
    
    BASE_URL = "https://api.open-meteo.com/v1"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    # WMO Weather interpretation codes
    WEATHER_CODES = {
        0: "آسمان صاف",
        1: "عمدتاً صاف",
        2: "نیمه ابری",
        3: "ابری",
        45: "مه",
        48: "مه یخ‌زده",
        51: "نم‌نم باران خفیف",
        53: "نم‌نم باران متوسط",
        55: "نم‌نم باران شدید",
        61: "باران خفیف",
        63: "باران متوسط",
        65: "باران شدید",
        71: "برف خفیف",
        73: "برف متوسط",
        75: "برف شدید",
        80: "رگبار خفیف",
        81: "رگبار متوسط",
        82: "رگبار شدید",
        95: "رعد و برق",
        96: "رعد و برق با تگرگ خفیف",
        99: "رعد و برق با تگرگ شدید",
    }
    
    async def get_current_weather(
        self, 
        latitude: float, 
        longitude: float
    ) -> WeatherCurrent:
        """دریافت هوای فعلی"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,"
                              "wind_direction_10m,weather_code,precipitation,"
                              "cloud_cover,surface_pressure",
                    "timezone": "Asia/Tehran"
                }
            )
            response.raise_for_status()
            data = response.json()
            current = data["current"]
            
            return WeatherCurrent(
                temperature=current["temperature_2m"],
                humidity=current["relative_humidity_2m"],
                wind_speed=current["wind_speed_10m"],
                wind_direction=current["wind_direction_10m"],
                weather_code=current["weather_code"],
                precipitation=current["precipitation"],
                cloud_cover=current["cloud_cover"],
                pressure=current["surface_pressure"],
                timestamp=current["time"]
            )
    
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        days: int = 7
    ) -> List[WeatherDaily]:
        """دریافت پیش‌بینی هوا"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "daily": "temperature_2m_max,temperature_2m_min,"
                            "precipitation_sum,precipitation_probability_max,"
                            "wind_speed_10m_max,sunrise,sunset,uv_index_max",
                    "timezone": "Asia/Tehran",
                    "forecast_days": days
                }
            )
            response.raise_for_status()
            data = response.json()
            daily = data["daily"]
            
            forecasts = []
            for i in range(len(daily["time"])):
                forecasts.append(WeatherDaily(
                    date=daily["time"][i],
                    temp_max=daily["temperature_2m_max"][i],
                    temp_min=daily["temperature_2m_min"][i],
                    precipitation_sum=daily["precipitation_sum"][i],
                    precipitation_probability=daily["precipitation_probability_max"][i],
                    wind_speed_max=daily["wind_speed_10m_max"][i],
                    sunrise=daily["sunrise"][i],
                    sunset=daily["sunset"][i],
                    uv_index_max=daily["uv_index_max"][i]
                ))
            
            return forecasts
    
    async def get_historical(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> Dict:
        """دریافت داده‌های تاریخی"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                self.ARCHIVE_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "start_date": start_date,
                    "end_date": end_date,
                    "daily": "temperature_2m_max,temperature_2m_min,"
                            "precipitation_sum,wind_speed_10m_max",
                    "timezone": "Asia/Tehran"
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def get_climate_data(
        self,
        latitude: float,
        longitude: float
    ) -> Dict:
        """دریافت داده‌های اقلیمی بلندمدت"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/climate",
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "models": "CMCC_CM2_VHR4,FGOALS_f3_H,HiRAM_SIT_HR",
                    "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum"
                }
            )
            response.raise_for_status()
            return response.json()
    
    def get_weather_description(self, code: int) -> str:
        """تبدیل کد هوا به توضیحات فارسی"""
        return self.WEATHER_CODES.get(code, "نامشخص")


# Singleton instance
open_meteo = OpenMeteoService()
'''

(weather_service_dir / 'open_meteo.py').write_text(open_meteo_service, encoding='utf-8')
print("   ✅ Created api/services/weather/open_meteo.py")

# Create __init__.py files
(BACKEND / 'services' / '__init__.py').write_text('', encoding='utf-8')
(weather_service_dir / '__init__.py').write_text('from .open_meteo import open_meteo, OpenMeteoService', encoding='utf-8')
print("   ✅ Created service __init__.py files")

# ============================================================
# 2. BACKEND: SoilGrids Service
# ============================================================
print("\n🌾 2. Creating SoilGrids Service...")

soil_service_dir = BACKEND / 'services' / 'soil'
soil_service_dir.mkdir(parents=True, exist_ok=True)

soilgrids_service = '''"""
SoilGrids Service
سرویس اطلاعات خاک جهانی - رایگان
Documentation: https://soilgrids.org/
"""
import httpx
from typing import List, Dict, Optional
from pydantic import BaseModel


class SoilProperty(BaseModel):
    name: str
    name_fa: str
    unit: str
    depth: str
    value: Optional[float] = None
    uncertainty: Optional[float] = None


class SoilProfile(BaseModel):
    latitude: float
    longitude: float
    properties: List[SoilProperty]
    soil_class: Optional[str] = None


class SoilGridsService:
    """سرویس SoilGrids - اطلاعات خاک جهانی"""
    
    BASE_URL = "https://rest.isric.org/soilgrids/v2.0"
    
    # Soil properties available
    PROPERTIES = {
        "clay": {"name_fa": "رس", "unit": "g/kg", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "sand": {"name_fa": "شن", "unit": "g/kg", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "silt": {"name_fa": "سیلت", "unit": "g/kg", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "ocd": {"name_fa": "کربن آلی", "unit": "dg/kg", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "ocs": {"name_fa": "ذخیره کربن آلی", "unit": "dg/م³", "depths": ["0-30cm", "0-100cm"]},
        "phh2o": {"name_fa": "pH خاک", "unit": "pH", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "cec": {"name_fa": "ظرفیت تبادل کاتیونی", "unit": "cmol/kg", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "nitrogen": {"name_fa": "نیتروژن", "unit": "cg/kg", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "soc": {"name_fa": "کربن آلی خاک", "unit": "dg/kg", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "cfvo": {"name_fa": "سنگریزه", "unit": "cm³/dm³", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
        "bdod": {"name_fa": "چگالی ظاهری", "unit": "cg/م³", "depths": ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]},
    }
    
    async def get_soil_properties(
        self,
        latitude: float,
        longitude: float,
        properties: Optional[List[str]] = None,
        depths: Optional[List[str]] = None
    ) -> SoilProfile:
        """دریافت خواص خاک برای یک نقطه"""
        if properties is None:
            properties = ["clay", "sand", "silt", "ocd", "phh2o", "cec", "nitrogen", "soc"]
        
        if depths is None:
            depths = ["0-5cm", "5-15cm", "15-30cm", "30-60cm"]
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/properties/query",
                params={
                    "lon": longitude,
                    "lat": latitude,
                    "property": properties,
                    "depth": depths,
                    "value": ["mean", "Q0.05", "Q0.5", "Q0.95"]
                }
            )
            response.raise_for_status()
            data = response.json()
            
            soil_properties = []
            for prop_data in data.get("properties", {}).get("layers", []):
                prop_name = prop_data["name"]
                prop_info = self.PROPERTIES.get(prop_name, {"name_fa": prop_name, "unit": "?"})
                
                for depth_data in prop_data.get("depths", []):
                    depth = depth_data["label"]
                    values = depth_data.get("values", {})
                    
                    soil_properties.append(SoilProperty(
                        name=prop_name,
                        name_fa=prop_info["name_fa"],
                        unit=prop_info["unit"],
                        depth=depth,
                        value=values.get("mean"),
                        uncertainty=values.get("Q0.95")
                    ))
            
            return SoilProfile(
                latitude=latitude,
                longitude=longitude,
                properties=soil_properties,
                soil_class=data.get("properties", {}).get("soil_class", {}).get("name")
            )
    
    async def get_soil_classification(
        self,
        latitude: float,
        longitude: float
    ) -> Dict:
        """دریافت طبقه‌بندی خاک"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.BASE_URL}/classification/query",
                params={
                    "lon": longitude,
                    "lat": latitude
                }
            )
            response.raise_for_status()
            return response.json()
    
    def calculate_soil_texture(
        self,
        clay: float,
        sand: float,
        silt: float
    ) -> str:
        """محاسبه بافت خاک بر اساس مثلث بافت"""
        # USDA soil texture classification
        if clay >= 40 and sand <= 45:
            return "رسی"
        elif clay >= 40 and sand > 45:
            return "رسی-شنی"
        elif clay >= 27 and clay < 40 and sand <= 45:
            return "لومی-رسی"
        elif clay >= 27 and clay < 40 and sand > 45:
            return "لومی-رسی-شنی"
        elif clay >= 7 and clay < 27 and silt >= 28 and silt < 50:
            return "لومی"
        elif clay >= 7 and clay < 27 and silt < 28:
            return "لومی-شنی"
        elif clay < 7 and silt >= 50:
            return "سیلتی"
        elif clay < 7 and silt < 50 and sand >= 50:
            return "شنی"
        else:
            return "لومی-سیلتی"
    
    def calculate_carbon_stock(
        self,
        soc: float,  # dg/kg
        bd: float,   # cg/m³
        depth: float  # meters
    ) -> float:
        """محاسبه ذخیره کربن (تن در هکتار)"""
        # SOC stock = SOC * BD * depth * 0.1
        # Convert units: dg/kg * cg/m³ * m * 0.1 = t/ha
        return soc * bd * depth * 0.1 / 100


# Singleton instance
soilgrids = SoilGridsService()
'''

(soil_service_dir / 'soilgrids.py').write_text(soilgrids_service, encoding='utf-8')
(soil_service_dir / '__init__.py').write_text('from .soilgrids import soilgrids, SoilGridsService', encoding='utf-8')
print("   ✅ Created api/services/soil/soilgrids.py")

# ============================================================
# 3. BACKEND: Sentinel-2 Service
# ============================================================
print("\n🛰️  3. Creating Sentinel-2 Service...")

satellite_service_dir = BACKEND / 'services' / 'satellite'
satellite_service_dir.mkdir(parents=True, exist_ok=True)

sentinel_service = '''"""
Sentinel-2 Satellite Service
سرویس تصاویر ماهواره‌ای Sentinel-2 - رایگان
Documentation: https://documentation.dataspace.copernicus.eu/
"""
import httpx
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel


class SentinelImage(BaseModel):
    id: str
    title: str
    date: str
    cloud_cover: float
    bbox: List[float]
    download_url: Optional[str] = None


class SpectralIndex(BaseModel):
    name: str
    full_name: str
    value: float
    unit: str
    status: str
    description: str


class Sentinel2Service:
    """سرویس Sentinel-2 - تصاویر ماهواره‌ای رایگان"""
    
    # CDSE API endpoints
    AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    ODATA_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"
    
    # Spectral indices formulas
    INDICES = {
        "NDVI": {
            "full_name": "Normalized Difference Vegetation Index",
            "formula": "(B08 - B04) / (B08 + B04)",
            "unit": "unitless",
            "range": (-1, 1),
            "description": "شاخص پوشش گیاهی - سلامت گیاه"
        },
        "EVI": {
            "full_name": "Enhanced Vegetation Index",
            "formula": "2.5 * (B08 - B04) / (B08 + 6*B04 - 7.5*B02 + 1)",
            "unit": "unitless",
            "range": (-1, 1),
            "description": "شاخص بهبودیافته پوشش گیاهی"
        },
        "NDWI": {
            "full_name": "Normalized Difference Water Index",
            "formula": "(B03 - B08) / (B03 + B08)",
            "unit": "unitless",
            "range": (-1, 1),
            "description": "شاخص رطوبت پوشش گیاهی"
        },
        "SAVI": {
            "full_name": "Soil Adjusted Vegetation Index",
            "formula": "1.5 * (B08 - B04) / (B08 + B04 + 0.5)",
            "unit": "unitless",
            "range": (-1, 1),
            "description": "شاخص گیاهی تنظیم‌شده با خاک"
        },
        "NBR": {
            "full_name": "Normalized Burn Ratio",
            "formula": "(B08 - B12) / (B08 + B12)",
            "unit": "unitless",
            "range": (-1, 1),
            "description": "شاخص سوختگی"
        },
        "NDMI": {
            "full_name": "Normalized Difference Moisture Index",
            "formula": "(B08 - B11) / (B08 + B11)",
            "unit": "unitless",
            "range": (-1, 1),
            "description": "شاخص رطوبت"
        },
        "GNDVI": {
            "full_name": "Green NDVI",
            "formula": "(B08 - B03) / (B08 + B03)",
            "unit": "unitless",
            "range": (-1, 1),
            "description": "شاخص گیاهی سبز"
        },
        "MNDWI": {
            "full_name": "Modified NDWI",
            "formula": "(B03 - B11) / (B03 + B11)",
            "unit": "unitless",
            "range": (-1, 1),
            "description": "شاخص آب سطحی"
        }
    }
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username
        self.password = password
        self.access_token = None
        self.refresh_token = None
    
    async def authenticate(self) -> bool:
        """احراز هویت در CDSE"""
        if not self.username or not self.password:
            return False
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.AUTH_URL,
                data={
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password,
                    "client_id": "cdse-public"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data["access_token"]
                self.refresh_token = data["refresh_token"]
                return True
            return False
    
    async def search_images(
        self,
        bbox: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        cloud_cover_max: float = 20.0,
        max_results: int = 10
    ) -> List[SentinelImage]:
        """جستجوی تصاویر Sentinel-2"""
        # Format bbox for OData
        bbox_str = f"POLYGON(({bbox[0]} {bbox[1]},{bbox[2]} {bbox[1]},{bbox[2]} {bbox[3]},{bbox[0]} {bbox[3]},{bbox[0]} {bbox[1]}))"
        
        # Build filter
        filter_parts = [
            f"Collection/Name eq 'SENTINEL-2'",
            f"ContentDate/Start gt {start_date}T00:00:00.000Z",
            f"ContentDate/Start lt {end_date}T23:59:59.999Z",
            f"OData.CSC.Intersects(area=geography'SRID=4326;{bbox_str}')",
            f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt {cloud_cover_max})"
        ]
        
        filter_str = " and ".join(filter_parts)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{self.ODATA_URL}/Products",
                params={
                    "$filter": filter_str,
                    "$orderby": "ContentDate/Start desc",
                    "$top": max_results,
                    "$select": "Id,Name,ContentDate/Start,Attributes"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            images = []
            for product in data.get("value", []):
                cloud_cover = 0
                for attr in product.get("Attributes", []):
                    if attr["Name"] == "cloudCover":
                        cloud_cover = attr["Value"]
                        break
                
                images.append(SentinelImage(
                    id=product["Id"],
                    title=product["Name"],
                    date=product["ContentDate"]["Start"],
                    cloud_cover=cloud_cover,
                    bbox=list(bbox),
                    download_url=f"{self.ODATA_URL}/Products({product['Id']})/$value"
                ))
            
            return images
    
    def calculate_ndvi(self, red: float, nir: float) -> float:
        """محاسبه NDVI"""
        if red + nir == 0:
            return 0
        return (nir - red) / (nir + red)
    
    def calculate_evi(self, red: float, nir: float, blue: float) -> float:
        """محاسبه EVI"""
        denom = nir + 6 * red - 7.5 * blue + 1
        if denom == 0:
            return 0
        return 2.5 * (nir - red) / denom
    
    def calculate_ndwi(self, green: float, nir: float) -> float:
        """محاسبه NDWI"""
        if green + nir == 0:
            return 0
        return (green - nir) / (green + nir)
    
    def calculate_savi(self, red: float, nir: float, L: float = 0.5) -> float:
        """محاسبه SAVI"""
        denom = nir + red + L
        if denom == 0:
            return 0
        return (1 + L) * (nir - red) / denom
    
    def classify_vegetation_health(self, ndvi: float) -> Dict:
        """طبقه‌بندی سلامت پوشش گیاهی"""
        if ndvi < -0.1:
            return {"status": "آب/خاک bare", "color": "#2c3e50", "score": 0}
        elif ndvi < 0.1:
            return {"status": "خاک برهنه", "color": "#95a5a6", "score": 1}
        elif ndvi < 0.2:
            return {"status": "پوشش بسیار ضعیف", "color": "#e74c3c", "score": 2}
        elif ndvi < 0.3:
            return {"status": "پوشش ضعیف", "color": "#e67e22", "score": 3}
        elif ndvi < 0.4:
            return {"status": "پوشش متوسط", "color": "#f1c40f", "score": 4}
        elif ndvi < 0.6:
            return {"status": "پوشش خوب", "color": "#2ecc71", "score": 5}
        elif ndvi < 0.8:
            return {"status": "پوشش بسیار خوب", "color": "#27ae60", "score": 6}
        else:
            return {"status": "جنگل متراکم", "color": "#145a32", "score": 7}
    
    def estimate_biomass(self, ndvi: float) -> float:
        """تخمین زیست‌توده (تن در هکتار)"""
        # Empirical relationship: Biomass = a * exp(b * NDVI)
        import math
        if ndvi <= 0:
            return 0
        return 50 * math.exp(2.5 * ndvi)
    
    def estimate_carbon_stock(self, biomass: float) -> float:
        """تخمین ذخیره کربن (تن در هکتار)"""
        # Carbon is approximately 50% of biomass
        return biomass * 0.5


# Singleton instance
sentinel2 = Sentinel2Service()
'''

(satellite_service_dir / 'sentinel2.py').write_text(sentinel_service, encoding='utf-8')
(satellite_service_dir / '__init__.py').write_text('from .sentinel2 import sentinel2, Sentinel2Service', encoding='utf-8')
print("   ✅ Created api/services/satellite/sentinel2.py")

# ============================================================
# 4. BACKEND: Update weather router to use Open-Meteo
# ============================================================
print("\n🔧 4. Updating weather router...")

weather_router_path = BACKEND / 'modules' / 'weather' / 'router.py'
if weather_router_path.exists():
    content = weather_router_path.read_text(encoding='utf-8-sig')
    
    # Add import if not present
    if 'open_meteo' not in content:
        import_line = 'from api.services.weather.open_meteo import open_meteo, OpenMeteoService\n'
        content = import_line + content
        weather_router_path.write_text(content, encoding='utf-8')
        print("   ✅ Added Open-Meteo import to weather router")
    else:
        print("   ✅ Open-Meteo already imported")
else:
    print("   ⚠️  Weather router not found")

# ============================================================
# 5. FRONTEND: Weather Hook
# ============================================================
print("\n🎨 5. Creating frontend weather hook...")

weather_hooks_dir = FRONTEND / 'hooks' / 'weather'
weather_hooks_dir.mkdir(parents=True, exist_ok=True)

weather_hook = '''import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api-client';

export function useCurrentWeather(lat: number, lng: number) {
  return useQuery({
    queryKey: ['weather', 'current', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/weather/current?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 5 * 60 * 1000, // 5 minutes
    refetchInterval: 10 * 60 * 1000, // 10 minutes
  });
}

export function useWeatherForecast(lat: number, lng: number, days: number = 7) {
  return useQuery({
    queryKey: ['weather', 'forecast', lat, lng, days],
    queryFn: async () => {
      const response = await api.get(`/api/v1/weather/forecast?lat=${lat}&lng=${lng}&days=${days}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

export function useHistoricalWeather(
  lat: number, 
  lng: number, 
  startDate: string, 
  endDate: string
) {
  return useQuery({
    queryKey: ['weather', 'historical', lat, lng, startDate, endDate],
    queryFn: async () => {
      const response = await api.get(
        `/api/v1/weather/historical?lat=${lat}&lng=${lng}&start=${startDate}&end=${endDate}`
      );
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng) && !!startDate && !!endDate,
  });
}
'''

(weather_hooks_dir / 'useWeather.ts').write_text(weather_hook, encoding='utf-8')
(weather_hooks_dir / '__init__.py').write_text('', encoding='utf-8')
print("   ✅ Created hooks/weather/useWeather.ts")

# ============================================================
# 6. FRONTEND: Soil Hook
# ============================================================
print("\n🎨 6. Creating frontend soil hook...")

soil_hooks_dir = FRONTEND / 'hooks' / 'soil'
soil_hooks_dir.mkdir(parents=True, exist_ok=True)

soil_hook = '''import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api-client';

export function useSoilProperties(lat: number, lng: number) {
  return useQuery({
    queryKey: ['soil', 'properties', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/soil-water/properties?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 60 * 60 * 1000, // 1 hour (soil doesn't change often)
  });
}

export function useSoilClassification(lat: number, lng: number) {
  return useQuery({
    queryKey: ['soil', 'classification', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/soil-water/classification?lat=${lat}&lng=${lng}`);
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
  });
}
'''

(soil_hooks_dir / 'useSoil.ts').write_text(soil_hook, encoding='utf-8')
(soil_hooks_dir / '__init__.py').write_text('', encoding='utf-8')
print("   ✅ Created hooks/soil/useSoil.ts")

# ============================================================
# 7. FRONTEND: Satellite Hook
# ============================================================
print("\n🎨 7. Creating frontend satellite hook...")

satellite_hooks_dir = FRONTEND / 'hooks' / 'satellite'
satellite_hooks_dir.mkdir(parents=True, exist_ok=True)

satellite_hook = '''import { useQuery, useMutation } from '@tanstack/react-query';
import api from '@/lib/api-client';

export function useSentinelImages(
  bbox: [number, number, number, number],
  startDate: string,
  endDate: string,
  cloudCoverMax: number = 20
) {
  return useQuery({
    queryKey: ['satellite', 'sentinel', bbox, startDate, endDate, cloudCoverMax],
    queryFn: async () => {
      const response = await api.get('/api/v1/mrv/sentinel/search', {
        params: {
          bbox: bbox.join(','),
          start_date: startDate,
          end_date: endDate,
          cloud_cover_max: cloudCoverMax
        }
      });
      return response.data;
    },
    enabled: !!bbox && !!startDate && !!endDate,
    staleTime: 60 * 60 * 1000, // 1 hour
  });
}

export function useSpectralIndex(
  lat: number,
  lng: number,
  index: string = 'NDVI'
) {
  return useQuery({
    queryKey: ['satellite', 'index', lat, lng, index],
    queryFn: async () => {
      const response = await api.get(`/api/v1/mrv/spectral/${index}`, {
        params: { lat, lng }
      });
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
    staleTime: 30 * 60 * 1000, // 30 minutes
  });
}

export function useVegetationHealth(lat: number, lng: number) {
  return useQuery({
    queryKey: ['satellite', 'vegetation', lat, lng],
    queryFn: async () => {
      const response = await api.get(`/api/v1/mrv/vegetation/health`, {
        params: { lat, lng }
      });
      return response.data;
    },
    enabled: !isNaN(lat) && !isNaN(lng),
  });
}
'''

(satellite_hooks_dir / 'useSatellite.ts').write_text(satellite_hook, encoding='utf-8')
(satellite_hooks_dir / '__init__.py').write_text('', encoding='utf-8')
print("   ✅ Created hooks/satellite/useSatellite.ts")

# ============================================================
# 8. Install httpx if not installed
# ============================================================
print("\n📦 8. Checking dependencies...")

import subprocess
try:
    result = subprocess.run(
        ['pip', 'show', 'httpx'],
        capture_output=True,
        text=True,
        cwd=str(ROOT)
    )
    if result.returncode == 0:
        print("   ✅ httpx already installed")
    else:
        print("   ⚠️  httpx not found - please install with: pip install httpx")
except:
    print("   ⚠️  Could not check httpx - please install with: pip install httpx")

# ============================================================
# SUMMARY
# ============================================================
print("\n" + "=" * 100)
print("✅ PRIORITY SERVICES IMPLEMENTED")
print("=" * 100)

print("""
📦 Services Created:

1. 🌦️  Open-Meteo Weather Service
   - Current weather
   - 7-day forecast
   - Historical data
   - Climate data
   - No API key required!

2. 🌾 SoilGrids Service
   - Soil properties (clay, sand, silt, pH, carbon, etc.)
   - Soil classification
   - Soil texture calculation
   - Carbon stock estimation

3. 🛰️ Sentinel-2 Service
   - Image search
   - Spectral indices (NDVI, EVI, NDWI, SAVI, NBR, NDMI, GNDVI, MNDWI)
   - Vegetation health classification
   - Biomass estimation
   - Carbon stock estimation

🎨 Frontend Hooks Created:

1. useWeather - Weather data hooks
2. useSoil - Soil data hooks
3. useSatellite - Satellite data hooks

🚀 Next Steps:

1. Install httpx:
   pip install httpx

2. Restart backend:
   uvicorn api.main:app --reload --port 8000

3. Test APIs:
   - http://localhost:8000/api/v1/weather/current?lat=35.6892&lng=51.3890
   - http://localhost:8000/api/v1/soil-water/properties?lat=35.6892&lng=51.3890

4. Visit frontend:
   - http://localhost:3001/weather
   - http://localhost:3001/gis
""")