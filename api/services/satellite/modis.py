"""
MODIS - Moderate Resolution Imaging Spectroradiometer
پایش روزانه جهانی - رایگان
Documentation: https://modis.gsfc.nasa.gov/
Data: https://modis.ornl.gov/
"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel


class MODISDataPoint(BaseModel):
    date: str
    value: float
    quality: str
    product: str


class MODISService:
    """سرویس MODIS"""
    
    ORNL_DAAC_URL = "https://modis.ornl.gov/rst/api/v1"
    
    PRODUCTS = {
        'MOD13Q1': {'name': 'Vegetation Indices', 'resolution': '250m', 'temporal': '16 روز'},
        'MOD11A1': {'name': 'Land Surface Temperature', 'resolution': '1km', 'temporal': 'روزانه'},
        'MOD15A2H': {'name': 'Leaf Area Index', 'resolution': '500m', 'temporal': '8 روز'},
        'MOD16A2': {'name': 'Evapotranspiration', 'resolution': '500m', 'temporal': '8 روز'},
        'MOD14A1': {'name': 'Fire/Thermal Anomalies', 'resolution': '1km', 'temporal': 'روزانه'},
    }
    
    async def get_ndvi_timeseries(
        self, latitude: float, longitude: float,
        start_date: str, end_date: str, product: str = 'MOD13Q1'
    ) -> List[MODISDataPoint]:
        """دریافت سری زمانی NDVI"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{self.ORNL_DAAC_URL}/{product}/subset",
                params={
                    "latitude": latitude, "longitude": longitude,
                    "startDate": start_date, "endDate": end_date,
                    "kmAboveBelow": 0, "kmLeftRight": 0
                }
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            data_points = []
            dates = data.get("dates", [])
            ndvi_data = data.get("data", {}).get("250m 16 days NDVI", [])
            
            for i, date in enumerate(dates):
                if i < len(ndvi_data) and ndvi_data[i] is not None:
                    value = ndvi_data[i] / 10000.0
                    data_points.append(MODISDataPoint(
                        date=date, value=value, quality="good", product=product
                    ))
            
            return data_points
    
    async def get_lst_timeseries(
        self, latitude: float, longitude: float,
        start_date: str, end_date: str
    ) -> List[MODISDataPoint]:
        """دریافت سری زمانی دمای سطح زمین"""
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                f"{self.ORNL_DAAC_URL}/MOD11A1/subset",
                params={
                    "latitude": latitude, "longitude": longitude,
                    "startDate": start_date, "endDate": end_date
                }
            )
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            data_points = []
            dates = data.get("dates", [])
            lst_day = data.get("data", {}).get("LST_Day_1km", [])
            
            for i, date in enumerate(dates):
                if i < len(lst_day) and lst_day[i] is not None:
                    value = lst_day[i] * 0.02 - 273.15
                    data_points.append(MODISDataPoint(
                        date=date, value=value, quality="good", product="MOD11A1"
                    ))
            
            return data_points
    
    def analyze_vegetation_phenology(self, ndvi_timeseries: List[MODISDataPoint]) -> Dict:
        """تحلیل فنولوژی پوشش گیاهی"""
        if not ndvi_timeseries:
            return {}
        
        values = [p.value for p in ndvi_timeseries]
        peak_idx = values.index(max(values))
        min_idx = values.index(min(values))
        
        return {
            "peak_date": ndvi_timeseries[peak_idx].date,
            "peak_value": round(values[peak_idx], 3),
            "min_date": ndvi_timeseries[min_idx].date,
            "min_value": round(values[min_idx], 3),
            "amplitude": round(values[peak_idx] - values[min_idx], 3),
            "mean": round(sum(values) / len(values), 3),
            "growing_season_length": sum(1 for v in values if v > 0.2) * 16
        }
    
    def detect_fire_risk(self, ndvi: float, lst: float, et: float) -> Dict:
        """تشخیص ریسک آتش‌سوزی"""
        risk_score = 0
        
        if ndvi > 0.4:
            risk_score += 30
        elif ndvi > 0.2:
            risk_score += 15
        
        if lst > 35:
            risk_score += 30
        elif lst > 30:
            risk_score += 15
        
        if et < 1:
            risk_score += 40
        elif et < 2:
            risk_score += 20
        
        if risk_score >= 80:
            level, color = "extreme", "#7f1d1d"
        elif risk_score >= 60:
            level, color = "high", "#dc2626"
        elif risk_score >= 40:
            level, color = "moderate", "#ea580c"
        elif risk_score >= 20:
            level, color = "low", "#ca8a04"
        else:
            level, color = "very_low", "#16a34a"
        
        return {"score": risk_score, "level": level, "color": color}


modis = MODISService()
