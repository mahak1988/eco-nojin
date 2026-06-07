"""
GEDI - Global Ecosystem Dynamics Investigation
اندازه‌گیری ارتفاع جنگل و بیومس - رایگان
Documentation: https://gedi.umd.edu/
"""
import httpx
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pydantic import BaseModel


class GEDIShot(BaseModel):
    shot_number: int
    latitude: float
    longitude: float
    elevation: float
    canopy_height: float
    canopy_cover: float
    sensitivity: float
    quality: str
    date: str


class ForestMetrics(BaseModel):
    location: Dict[str, float]
    mean_canopy_height: float
    max_canopy_height: float
    canopy_cover: float
    estimated_biomass: float
    estimated_carbon: float
    forest_type: str
    shots_count: int


class GEDIService:
    """سرویس GEDI"""
    
    CMR_URL = "https://cmr.earthdata.nasa.gov/search"
    
    BIOMASS_COEFFICIENTS = {
        'tropical': {'a': 0.084, 'b': 2.616},
        'temperate': {'a': 0.091, 'b': 2.472},
        'boreal': {'a': 0.073, 'b': 2.587},
    }
    
    CARBON_FRACTION = 0.47
    
    async def search_footprints(
        self, bbox: Tuple[float, float, float, float],
        start_date: Optional[str] = None, end_date: Optional[str] = None,
        max_results: int = 100
    ) -> List[GEDIShot]:
        """جستجوی footprint های GEDI"""
        bbox_str = f"{bbox[0]},{bbox[1]},{bbox[2]},{bbox[3]}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            params = {
                "concept_id": "C1908471333-LPCLOUD",
                "bounding_box": bbox_str,
                "page_size": min(max_results, 2000)
            }
            
            if start_date and end_date:
                params["temporal"] = f"{start_date}T00:00:00Z,{end_date}T23:59:59Z"
            
            response = await client.get(
                f"{self.CMR_URL}/granules.json", params=params
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            shots = []
            
            for entry in data.get("feed", {}).get("entry", [])[:max_results]:
                shots.append(GEDIShot(
                    shot_number=int(entry.get("id", 0)),
                    latitude=entry.get("lat", 0),
                    longitude=entry.get("lon", 0),
                    elevation=0, canopy_height=0, canopy_cover=0,
                    sensitivity=0, quality="good",
                    date=entry.get("time_start", "")[:10]
                ))
            
            return shots
    
    async def get_forest_metrics(
        self, latitude: float, longitude: float, radius_km: float = 1.0
    ) -> ForestMetrics:
        """دریافت معیارهای جنگل"""
        bbox = (
            longitude - radius_km / 111, latitude - radius_km / 111,
            longitude + radius_km / 111, latitude + radius_km / 111
        )
        
        shots = await self.search_footprints(bbox)
        
        if not shots:
            return self._estimate_forest_metrics(latitude, longitude)
        
        heights = [s.canopy_height for s in shots if s.canopy_height > 0]
        covers = [s.canopy_cover for s in shots if s.canopy_cover > 0]
        
        mean_height = sum(heights) / len(heights) if heights else 0
        max_height = max(heights) if heights else 0
        mean_cover = sum(covers) / len(covers) if covers else 0
        
        biomass = self.estimate_biomass(mean_height, latitude)
        carbon = biomass * self.CARBON_FRACTION
        forest_type = self.classify_forest_type(latitude)
        
        return ForestMetrics(
            location={"lat": latitude, "lng": longitude},
            mean_canopy_height=round(mean_height, 2),
            max_canopy_height=round(max_height, 2),
            canopy_cover=round(mean_cover, 2),
            estimated_biomass=round(biomass, 2),
            estimated_carbon=round(carbon, 2),
            forest_type=forest_type,
            shots_count=len(shots)
        )
    
    def _estimate_forest_metrics(self, latitude: float, longitude: float) -> ForestMetrics:
        """تخمین معیارهای جنگل"""
        forest_type = self.classify_forest_type(latitude)
        
        typical_values = {
            'tropical_rainforest': {'height': 35, 'cover': 85, 'biomass': 300},
            'tropical_dry': {'height': 20, 'cover': 60, 'biomass': 150},
            'temperate': {'height': 25, 'cover': 70, 'biomass': 200},
            'boreal': {'height': 15, 'cover': 65, 'biomass': 120},
            'mediterranean': {'height': 10, 'cover': 40, 'biomass': 60},
            'arid': {'height': 3, 'cover': 10, 'biomass': 10},
            'non_forest': {'height': 0, 'cover': 0, 'biomass': 0}
        }
        
        values = typical_values.get(forest_type, typical_values['non_forest'])
        
        return ForestMetrics(
            location={"lat": latitude, "lng": longitude},
            mean_canopy_height=values['height'],
            max_canopy_height=values['height'] * 1.5,
            canopy_cover=values['cover'],
            estimated_biomass=values['biomass'],
            estimated_carbon=values['biomass'] * self.CARBON_FRACTION,
            forest_type=forest_type,
            shots_count=0
        )
    
    def estimate_biomass(self, canopy_height: float, latitude: float) -> float:
        """تخمین زیست‌توده"""
        if canopy_height <= 0:
            return 0
        
        forest_type = self.classify_forest_type(latitude)
        
        if 'tropical' in forest_type:
            coeffs = self.BIOMASS_COEFFICIENTS['tropical']
        elif 'boreal' in forest_type:
            coeffs = self.BIOMASS_COEFFICIENTS['boreal']
        else:
            coeffs = self.BIOMASS_COEFFICIENTS['temperate']
        
        return coeffs['a'] * (canopy_height ** coeffs['b'])
    
    def classify_forest_type(self, latitude: float) -> str:
        """طبقه‌بندی نوع جنگل"""
        abs_lat = abs(latitude)
        
        if abs_lat < 10:
            return 'tropical_rainforest'
        elif abs_lat < 23.5:
            return 'tropical_dry'
        elif abs_lat < 35:
            return 'mediterranean'
        elif abs_lat < 55:
            return 'temperate'
        elif abs_lat < 70:
            return 'boreal'
        else:
            return 'non_forest'
    
    def calculate_carbon_sequestration(
        self, biomass_change: float, area_ha: float
    ) -> Dict:
        """محاسبه جذب کربن"""
        carbon_sequestered = biomass_change * self.CARBON_FRACTION * area_ha
        co2_equivalent = carbon_sequestered * (44/12)
        carbon_price = 25
        economic_value = co2_equivalent * carbon_price
        
        return {
            "carbon_sequestered_tons": round(carbon_sequestered, 2),
            "co2_equivalent_tons": round(co2_equivalent, 2),
            "economic_value_usd": round(economic_value, 2),
            "per_hectare": round(co2_equivalent / area_ha, 2) if area_ha > 0 else 0
        }


gedi = GEDIService()
