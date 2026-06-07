"""
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
