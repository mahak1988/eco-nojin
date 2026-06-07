"""
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
