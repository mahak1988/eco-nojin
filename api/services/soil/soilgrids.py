"""
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
