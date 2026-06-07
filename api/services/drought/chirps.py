"""
CHIRPS - Climate Hazards Group InfraRed Precipitation with Station data
داده‌های بارش ۴۰ ساله - کاملاً رایگان
Documentation: https://www.chc.ucsb.edu/data/chirps
Data Portal: https://data.chc.ucsb.edu/products/time_series/
"""
import httpx
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import json


class RainfallData(BaseModel):
    date: str
    precipitation: float  # mm/day
    anomaly: Optional[float] = None  # deviation from normal
    percentile: Optional[int] = None  # percentile rank


class RainfallStatistics(BaseModel):
    location: Dict[str, float]
    period: Dict[str, str]
    total_rainfall: float
    average_rainfall: float
    max_rainfall: float
    min_rainfall: float
    rainy_days: int
    dry_days: int
    data_points: int


class DroughtRisk(BaseModel):
    level: str  # normal, mild, moderate, severe, extreme
    score: float  # 0-100
    description: str
    color: str
    recommendation: str


class CHIRPSService:
    """سرویس CHIRPS - داده‌های بارش ۴۰ ساله"""
    
    # CHIRPS Data API (via Climate Engine or direct)
    BASE_URL = "https://data.chc.ucsb.edu/products"
    CLIMATE_ENGINE_URL = "https://climateengine.com/api/v1"
    
    # Alternative: Use NASA POWER API (free, no key)
    NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"
    
    # Drought thresholds (mm/day)
    DROUGHT_THRESHOLDS = {
        'extreme_drought': 0.1,
        'severe_drought': 0.5,
        'moderate_drought': 1.0,
        'mild_drought': 2.0,
        'normal': 5.0,
        'wet': 10.0,
        'extreme_wet': 20.0
    }
    
    async def get_daily_rainfall(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> List[RainfallData]:
        """دریافت داده‌های روزانه بارش"""
        # Using NASA POWER API as CHIRPS alternative (free, no key)
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.get(
                self.NASA_POWER_URL,
                params={
                    "parameters": "PRECTOTCORR",
                    "start": start_date.replace('-', ''),
                    "end": end_date.replace('-', ''),
                    "latitude": latitude,
                    "longitude": longitude,
                    "community": "AG",
                    "format": "JSON"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            rainfall_data = []
            properties = data.get("properties", {}).get("parameter", {})
            prec_data = properties.get("PRECTOTCORR", {})
            
            for date_str, value in prec_data.items():
                # Convert to mm/day (NASA POWER returns mm/day already)
                rainfall_data.append(RainfallData(
                    date=f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}",
                    precipitation=value if value is not None else 0.0
                ))
            
            return sorted(rainfall_data, key=lambda x: x.date)
    
    async def get_rainfall_statistics(
        self,
        latitude: float,
        longitude: float,
        start_date: str,
        end_date: str
    ) -> RainfallStatistics:
        """محاسبه آمار بارش"""
        rainfall_data = await self.get_daily_rainfall(
            latitude, longitude, start_date, end_date
        )
        
        if not rainfall_data:
            return RainfallStatistics(
                location={"lat": latitude, "lng": longitude},
                period={"start": start_date, "end": end_date},
                total_rainfall=0,
                average_rainfall=0,
                max_rainfall=0,
                min_rainfall=0,
                rainy_days=0,
                dry_days=0,
                data_points=0
            )
        
        values = [r.precipitation for r in rainfall_data]
        rainy_days = sum(1 for v in values if v >= 1.0)
        
        return RainfallStatistics(
            location={"lat": latitude, "lng": longitude},
            period={"start": start_date, "end": end_date},
            total_rainfall=sum(values),
            average_rainfall=sum(values) / len(values),
            max_rainfall=max(values),
            min_rainfall=min(values),
            rainy_days=rainy_days,
            dry_days=len(values) - rainy_days,
            data_points=len(values)
        )
    
    async def assess_drought_risk(
        self,
        latitude: float,
        longitude: float,
        days: int = 30
    ) -> DroughtRisk:
        """ارزیابی ریسک خشکسالی"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stats = await self.get_rainfall_statistics(
            latitude, longitude,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        
        avg_daily = stats.average_rainfall
        
        # Determine drought level
        if avg_daily < self.DROUGHT_THRESHOLDS['extreme_drought']:
            return DroughtRisk(
                level="extreme",
                score=95,
                description="خشکسالی شدید - بحران آب",
                color="#7f1d1d",
                recommendation="ممنوعیت کامل آبیاری غیرضروری، جیره‌بندی آب"
            )
        elif avg_daily < self.DROUGHT_THRESHOLDS['severe_drought']:
            return DroughtRisk(
                level="severe",
                score=80,
                description="خشکسالی بسیار جدی",
                color="#dc2626",
                recommendation="کاهش 50% آبیاری، استفاده از سیستم‌های قطره‌ای"
            )
        elif avg_daily < self.DROUGHT_THRESHOLDS['moderate_drought']:
            return DroughtRisk(
                level="moderate",
                score=60,
                description="خشکسالی متوسط",
                color="#ea580c",
                recommendation="کاهش 30% آبیاری، پایش رطوبت خاک"
            )
        elif avg_daily < self.DROUGHT_THRESHOLDS['mild_drought']:
            return DroughtRisk(
                level="mild",
                score=40,
                description="خشکسالی خفیف",
                color="#ca8a04",
                recommendation="پایش منظم، آماده‌باش برای کاهش آبیاری"
            )
        elif avg_daily < self.DROUGHT_THRESHOLDS['normal']:
            return DroughtRisk(
                level="normal",
                score=20,
                description="شرایط عادی",
                color="#16a34a",
                recommendation="ادامه مدیریت معمول"
            )
        else:
            return DroughtRisk(
                level="wet",
                score=10,
                description="شرایط مرطوب",
                color="#2563eb",
                recommendation="مدیریت رواناب، ذخیره آب"
            )
    
    def calculate_spi(self, rainfall_data: List[float], period_months: int = 3) -> float:
        """محاسبه Standardized Precipitation Index (SPI)"""
        if len(rainfall_data) < period_months:
            return 0.0
        
        # Calculate moving average
        moving_avg = []
        for i in range(len(rainfall_data) - period_months + 1):
            window = rainfall_data[i:i+period_months]
            moving_avg.append(sum(window) / period_months)
        
        if not moving_avg:
            return 0.0
        
        # Calculate mean and std
        mean = sum(moving_avg) / len(moving_avg)
        variance = sum((x - mean) ** 2 for x in moving_avg) / len(moving_avg)
        std = variance ** 0.5
        
        if std == 0:
            return 0.0
        
        # SPI = (current - mean) / std
        current = moving_avg[-1]
        return (current - mean) / std
    
    def classify_spi(self, spi: float) -> Dict:
        """طبقه‌بندی SPI"""
        if spi <= -2.0:
            return {"category": "extremely dry", "color": "#7f1d1d"}
        elif spi <= -1.5:
            return {"category": "severely dry", "color": "#dc2626"}
        elif spi <= -1.0:
            return {"category": "moderately dry", "color": "#ea580c"}
        elif spi <= -0.5:
            return {"category": "mildly dry", "color": "#ca8a04"}
        elif spi <= 0.5:
            return {"category": "near normal", "color": "#16a34a"}
        elif spi <= 1.0:
            return {"category": "mildly wet", "color": "#0ea5e9"}
        elif spi <= 1.5:
            return {"category": "moderately wet", "color": "#2563eb"}
        else:
            return {"category": "extremely wet", "color": "#1e40af"}


# Singleton
chirps = CHIRPSService()
