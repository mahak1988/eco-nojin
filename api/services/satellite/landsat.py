"""
Landsat 8/9 Service
تصاویر ماهواره‌ای Landsat - رایگان
Documentation: https://www.usgs.gov/landsat-missions
API: https://m2m.cr.usgs.gov/
"""
import httpx
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pydantic import BaseModel


class LandsatScene(BaseModel):
    entity_id: str
    display_id: str
    acquisition_date: str
    cloud_cover: float
    path: int
    row: int
    bbox: List[float]
    download_url: Optional[str] = None


class LandsatService:
    """سرویس Landsat 8/9"""
    
    M2M_URL = "https://m2m.cr.usgs.gov/api/api/json/stable"
    EARTH_EXPLORER_URL = "https://earthexplorer.usgs.gov"
    
    BANDS = {
        'L8': {
            'coastal': 'B1', 'blue': 'B2', 'green': 'B3', 'red': 'B4',
            'nir': 'B5', 'swir1': 'B6', 'swir2': 'B7', 'pan': 'B8',
            'cirrus': 'B9', 'tirs1': 'B10', 'tirs2': 'B11'
        },
        'L9': {
            'coastal': 'B1', 'blue': 'B2', 'green': 'B3', 'red': 'B4',
            'nir': 'B5', 'swir1': 'B6', 'swir2': 'B7', 'pan': 'B8',
            'cirrus': 'B9', 'tirs1': 'B10', 'tirs2': 'B11'
        }
    }
    
    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        self.username = username
        self.password = password
        self.api_key = None
    
    async def authenticate(self) -> bool:
        """احراز هویت در USGS M2M"""
        if not self.username or not self.password:
            return False
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.M2M_URL}/login",
                json={"username": self.username, "password": self.password}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.api_key = data.get("data")
                return True
            return False
    
    async def search_scenes(
        self,
        bbox: Tuple[float, float, float, float],
        start_date: str,
        end_date: str,
        cloud_cover_max: float = 20.0,
        max_results: int = 10,
        dataset: str = "landsat_ot_c2_l2"
    ) -> List[LandsatScene]:
        """جستجوی صحنه‌های Landsat"""
        if not self.api_key:
            auth_success = await self.authenticate()
            if not auth_success:
                return []
        
        spatial_filter = {
            "filterType": "mbr",
            "lowerLeft": {"latitude": bbox[1], "longitude": bbox[0]},
            "upperRight": {"latitude": bbox[3], "longitude": bbox[2]}
        }
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.M2M_URL}/scene-search",
                headers={"X-Auth-Token": self.api_key},
                json={
                    "datasetName": dataset,
                    "sceneFilter": {
                        "spatialFilter": spatial_filter,
                        "acquisitionFilter": {"start": start_date, "end": end_date},
                        "cloudCoverFilter": {
                            "min": 0, "max": cloud_cover_max, "includeUnknown": False
                        }
                    },
                    "maxResults": max_results,
                    "startingNumber": 1,
                    "sortDirection": "DESC",
                    "sortBy": "acquisitionDate"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            scenes = []
            for result in data.get("data", {}).get("results", []):
                scenes.append(LandsatScene(
                    entity_id=result["entityId"],
                    display_id=result["displayId"],
                    acquisition_date=result["temporalCoverage"]["startDate"],
                    cloud_cover=result["cloudCover"],
                    path=result.get("path", 0),
                    row=result.get("row", 0),
                    bbox=list(bbox)
                ))
            
            return scenes
    
    def calculate_ndvi(self, red: float, nir: float) -> float:
        """محاسبه NDVI"""
        if red + nir == 0:
            return 0
        return (nir - red) / (nir + red)
    
    def calculate_nbr(self, nir: float, swir2: float) -> float:
        """محاسبه Normalized Burn Ratio"""
        if nir + swir2 == 0:
            return 0
        return (nir - swir2) / (nir + swir2)
    
    def calculate_ndmi(self, nir: float, swir1: float) -> float:
        """محاسبه Normalized Difference Moisture Index"""
        if nir + swir1 == 0:
            return 0
        return (nir - swir1) / (nir + swir1)
    
    def classify_land_cover(self, ndvi: float, nbr: float) -> Dict:
        """طبقه‌بندی پوشش زمین"""
        if ndvi > 0.6:
            return {"class": "جنگل متراکم", "code": "dense_forest", "color": "#14532d"}
        elif ndvi > 0.4:
            return {"class": "جنگل باز", "code": "open_forest", "color": "#166534"}
        elif ndvi > 0.2:
            return {"class": "بوته‌زار", "code": "shrubland", "color": "#4d7c0f"}
        elif ndvi > 0.1:
            return {"class": "کشاورزی", "code": "agriculture", "color": "#84cc16"}
        elif ndvi > 0:
            return {"class": "علفزار", "code": "grassland", "color": "#a3e635"}
        elif nbr < -0.1:
            return {"class": "آب", "code": "water", "color": "#1e40af"}
        elif ndvi > -0.1:
            return {"class": "خاک برهنه", "code": "bare_soil", "color": "#78716c"}
        else:
            return {"class": "شهری", "code": "urban", "color": "#57534e"}
    
    def detect_change(self, ndvi_before: float, ndvi_after: float, threshold: float = 0.1) -> Dict:
        """تشخیص تغییر پوشش زمین"""
        change = ndvi_after - ndvi_before
        
        if abs(change) < threshold:
            return {"changed": False, "type": "no_change", "description": "بدون تغییر", "magnitude": abs(change)}
        elif change > 0:
            return {"changed": True, "type": "vegetation_increase", "description": "افزایش پوشش گیاهی", "magnitude": change}
        else:
            return {"changed": True, "type": "vegetation_decrease", "description": "کاهش پوشش گیاهی", "magnitude": abs(change)}
    
    def estimate_surface_temperature(self, tirs_band: float, emissivity: float = 0.95) -> float:
        """تخمین دمای سطحی"""
        k1, k2 = 774.89, 1321.08
        if tirs_band <= 0:
            return 0
        bt = k2 / (1 + (k1 / tirs_band)) - 273.15
        lst = bt / (1 + (10.6 * 0.000001 * bt / 1.4388) * (1 - emissivity))
        return lst


landsat = LandsatService()
