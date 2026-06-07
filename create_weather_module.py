#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌦️ ماژول جامع هواشناسی کشاورزی
- اتصال به Open-Meteo API (رایگان، بدون کلید)
- پیش‌بینی ۱۶ روزه
- شاخص‌های کشاورزی (GDD, ETo, THI)
- سیستم هشدار هوشمند
- نقشه هواشناسی تعاملی
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
# فایل 1: سرویس هواشناسی با Open-Meteo
# ============================================================
def create_weather_service():
    print("\n📡 ایجاد سرویس هواشناسی...")
    
    content = '''# api/services/weather_service.py
"""
سرویس هواشناسی با اتصال به Open-Meteo API
مرجع: https://open-meteo.com/en/docs
رایگان، بدون نیاز به API Key، پوشش جهانی
"""
import httpx
import math
from typing import Dict, List, Optional
from datetime import datetime, timedelta


# پایگاه داده شهرهای مهم ایران و جهان
CITIES_DATABASE = {
    # ایران
    "tehran": {"name_fa": "تهران", "lat": 35.6892, "lon": 51.3890, "elevation": 1100, "country": "ایران"},
    "mashhad": {"name_fa": "مشهد", "lat": 36.2605, "lon": 59.6168, "elevation": 999, "country": "ایران"},
    "isfahan": {"name_fa": "اصفهان", "lat": 32.6546, "lon": 51.6680, "elevation": 1574, "country": "ایران"},
    "shiraz": {"name_fa": "شیراز", "lat": 29.5918, "lon": 52.5837, "elevation": 1486, "country": "ایران"},
    "tabriz": {"name_fa": "تبریز", "lat": 38.0962, "lon": 46.2738, "elevation": 1372, "country": "ایران"},
    "karaj": {"name_fa": "کرج", "lat": 35.8355, "lon": 50.9917, "elevation": 1313, "country": "ایران"},
    "ahvaz": {"name_fa": "اهواز", "lat": 31.3183, "lon": 48.6706, "elevation": 22, "country": "ایران"},
    "qom": {"name_fa": "قم", "lat": 34.6401, "lon": 50.8764, "elevation": 927, "country": "ایران"},
    "kerman": {"name_fa": "کرمان", "lat": 30.2839, "lon": 57.0834, "elevation": 1755, "country": "ایران"},
    "rasht": {"name_fa": "رشت", "lat": 37.2808, "lon": 49.5832, "elevation": 7, "country": "ایران"},
    "yazd": {"name_fa": "یزد", "lat": 31.8974, "lon": 54.3569, "elevation": 1236, "country": "ایران"},
    "hamadan": {"name_fa": "همدان", "lat": 34.7988, "lon": 48.5146, "elevation": 1740, "country": "ایران"},
    "ardebil": {"name_fa": "اردبیل", "lat": 38.2498, "lon": 48.2933, "elevation": 1350, "country": "ایران"},
    "bandar_abbas": {"name_fa": "بندرعباس", "lat": 27.1832, "lon": 56.2666, "elevation": 9, "country": "ایران"},
    "zabol": {"name_fa": "زابل", "lat": 31.0286, "lon": 61.5011, "elevation": 497, "country": "ایران"},
    "birjand": {"name_fa": "بیرجند", "lat": 32.8649, "lon": 59.2262, "elevation": 1491, "country": "ایران"},
    "urmia": {"name_fa": "ارومیه", "lat": 37.5527, "lon": 45.0761, "elevation": 1331, "country": "ایران"},
    "sari": {"name_fa": "ساری", "lat": 36.5659, "lon": 53.0601, "elevation": 17, "country": "ایران"},
    "sanandaj": {"name_fa": "سنندج", "lat": 35.3219, "lon": 46.9861, "elevation": 1515, "country": "ایران"},
    "khorramabad": {"name_fa": "خرم‌آباد", "lat": 33.4878, "lon": 48.3558, "elevation": 1180, "country": "ایران"},
    # جهان
    "london": {"name_fa": "لندن", "lat": 51.5074, "lon": -0.1278, "elevation": 11, "country": "انگلستان"},
    "new_york": {"name_fa": "نیویورک", "lat": 40.7128, "lon": -74.0060, "elevation": 10, "country": "آمریکا"},
    "tokyo": {"name_fa": "توکیو", "lat": 35.6762, "lon": 139.6503, "elevation": 40, "country": "ژاپن"},
    "cairo": {"name_fa": "قاهره", "lat": 30.0444, "lon": 31.2357, "elevation": 75, "country": "مصر"},
    "dubai": {"name_fa": "دبی", "lat": 25.2048, "lon": 55.2708, "elevation": 5, "country": "امارات"},
    "istanbul": {"name_fa": "استانبول", "lat": 41.0082, "lon": 28.9784, "elevation": 40, "country": "ترکیه"},
    "baghdad": {"name_fa": "بغداد", "lat": 33.3152, "lon": 44.3661, "elevation": 34, "country": "عراق"},
    "kabul": {"name_fa": "کابل", "lat": 34.5553, "lon": 69.2075, "elevation": 1791, "country": "افغانستان"},
}


class OpenMeteoService:
    """سرویس اتصال به Open-Meteo API"""
    
    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
    
    @classmethod
    async def get_forecast(cls, lat: float, lon: float, days: int = 16) -> Dict:
        """
        دریافت پیش‌بینی هواشناسی
        مرجع: https://open-meteo.com/en/docs
        """
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "weather_code",
                "temperature_2m_max",
                "temperature_2m_min",
                "apparent_temperature_max",
                "apparent_temperature_min",
                "precipitation_sum",
                "rain_sum",
                "showers_sum",
                "snowfall_sum",
                "precipitation_hours",
                "precipitation_probability_max",
                "wind_speed_10m_max",
                "wind_gusts_10m_max",
                "wind_direction_10m_dominant",
                "et0_fao_evapotranspiration",
                "sunrise",
                "sunset",
                "uv_index_max",
            ],
            "hourly": [
                "temperature_2m",
                "relative_humidity_2m",
                "precipitation",
                "wind_speed_10m",
                "weather_code",
            ],
            "timezone": "Asia/Tehran",
            "forecast_days": min(days, 16),
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(cls.BASE_URL, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    @classmethod
    async def get_historical(cls, lat: float, lon: float, 
                             start_date: str, end_date: str) -> Dict:
        """دریافت داده‌های تاریخی"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "et0_fao_evapotranspiration",
            ],
            "timezone": "Asia/Tehran",
        }
        
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(cls.ARCHIVE_URL, params=params)
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": str(e)}


class AgriculturalIndices:
    """شاخص‌های هواشناسی کشاورزی"""
    
    @staticmethod
    def growing_degree_days(t_max: float, t_min: float, 
                            t_base: float = 10.0) -> float:
        """
        درجه-روز رشد (GDD)
        مرجع: McMaster & Wilhelm (1997)
        GDD = max(0, (T_max + T_min)/2 - T_base)
        """
        t_avg = (t_max + t_min) / 2
        return max(0, t_avg - t_base)
    
    @staticmethod
    def chilling_hours(t: float) -> float:
        """
        ساعات سرما‌نیازی (Chilling Hours)
        مدل Utah (Richardson et al., 1974)
        """
        if t < 1.5:
            return 0
        elif t < 2.5:
            return 0.5
        elif t < 9.2:
            return 1
        elif t < 16:
            return 0.5
        elif t < 18:
            return 0
        else:
            return -0.5
    
    @staticmethod
    def temperature_humidity_index(t_c: float, rh: float) -> float:
        """
        شاخص دما-رطوبت (THI)
        مرجع: NRC (1971)
        THI = T - (0.55 - 0.0055 × RH) × (T - 14.5)
        """
        return t_c - (0.55 - 0.0055 * rh) * (t_c - 14.5)
    
    @staticmethod
    def heat_index(t_c: float, rh: float) -> float:
        """
        شاخص گرمای هوا (Heat Index)
        مرجع: Rothfusz (1990) - NOAA
        """
        t_f = t_c * 9/5 + 32  # تبدیل به فارنهایت
        
        if t_f < 80:
            hi_f = 0.5 * (t_f + 61 + (t_f - 68) * 1.2 + rh * 0.094)
        else:
            hi_f = (-42.379 + 2.04901523*t_f + 10.14333127*rh
                   - 0.22475541*t_f*rh - 0.00683783*t_f**2
                   - 0.05481717*rh**2 + 0.00122874*t_f**2*rh
                   + 0.00085282*t_f*rh**2 - 0.00000199*t_f**2*rh**2)
        
        return (hi_f - 32) * 5/9  # تبدیل به سانتیگراد
    
    @staticmethod
    def wind_chill(t_c: float, wind_kmh: float) -> float:
        """
        شاخص سرمای باد (Wind Chill)
        مرجع: OSC (2001) - Canada
        """
        if t_c > 10 or wind_kmh < 4.8:
            return t_c
        
        wind_kph = wind_kmh
        wc = (13.12 + 0.6215*t_c - 11.37*(wind_kph**0.16)
              + 0.3965*t_c*(wind_kph**0.16))
        return wc
    
    @staticmethod
    def frost_risk(t_min: float) -> Dict:
        """
        ارزیابی ریسک یخبندان
        """
        if t_min <= -5:
            return {"risk": "بحرانی", "level": 5, "color": "#7f1d1d", 
                    "description": "یخبندان شدید - خسارت جدی"}
        elif t_min <= -2:
            return {"risk": "شدید", "level": 4, "color": "#dc2626",
                    "description": "یخبندان شدید - خسارت گسترده"}
        elif t_min <= 0:
            return {"risk": "متوسط", "level": 3, "color": "#f97316",
                    "description": "یخبندان - هشدار"}
        elif t_min <= 2:
            return {"risk": "خفیف", "level": 2, "color": "#f59e0b",
                    "description": "احتمال یخبندان خفیف"}
        elif t_min <= 5:
            return {"risk": "کم", "level": 1, "color": "#eab308",
                    "description": "نزدیک به دمای یخبندان"}
        else:
            return {"risk": "بدون ریسک", "level": 0, "color": "#10b981",
                    "description": "بدون خطر یخبندان"}
    
    @staticmethod
    def drought_stress(precip_30d: float, eto_30d: float) -> Dict:
        """
        ارزیابی تنش خشکسالی
        """
        if eto_30d == 0:
            return {"level": 0, "severity": "نامشخص", "color": "#64748b"}
        
        ratio = precip_30d / eto_30d
        
        if ratio < 0.2:
            return {"level": 5, "severity": "خشکسالی استثنایی", "color": "#7f1d1d"}
        elif ratio < 0.4:
            return {"level": 4, "severity": "خشکسالی شدید", "color": "#dc2626"}
        elif ratio < 0.6:
            return {"level": 3, "severity": "خشکسالی متوسط", "color": "#f97316"}
        elif ratio < 0.8:
            return {"level": 2, "severity": "خشکسالی خفیف", "color": "#f59e0b"}
        elif ratio < 1.0:
            return {"level": 1, "severity": "نرمال خشک", "color": "#eab308"}
        else:
            return {"level": 0, "severity": "نرمال/مرطوب", "color": "#10b981"}


class WeatherAlerts:
    """سیستم هشدار هواشناسی کشاورزی"""
    
    @classmethod
    def generate_alerts(cls, daily_data: Dict, crop: str = "wheat") -> List[Dict]:
        """تولید هشدارهای کشاورزی"""
        alerts = []
        
        if "daily" not in daily_data:
            return alerts
        
        daily = daily_data["daily"]
        dates = daily.get("time", [])
        t_max = daily.get("temperature_2m_max", [])
        t_min = daily.get("temperature_2m_min", [])
        precip = daily.get("precipitation_sum", [])
        wind = daily.get("wind_speed_10m_max", [])
        precip_prob = daily.get("precipitation_probability_max", [])
        
        for i, date in enumerate(dates[:7]):  # فقط ۷ روز آینده
            # هشدار یخبندان
            if i < len(t_min) and t_min[i] is not None:
                frost = AgriculturalIndices.frost_risk(t_min[i])
                if frost["level"] >= 2:
                    alerts.append({
                        "type": "frost",
                        "severity": "high" if frost["level"] >= 3 else "medium",
                        "date": date,
                        "title": f"⚠️ هشدار یخبندان - {frost['risk']}",
                        "description": f"دمای حداقل {t_min[i]:.1f}°C در {date}. {frost['description']}",
                        "action": _get_frost_action(frost["level"]),
                        "color": frost["color"],
                        "icon": "❄️",
                    })
            
            # هشدار موج گرم
            if i < len(t_max) and t_max[i] is not None:
                if t_max[i] >= 40:
                    alerts.append({
                        "type": "heat_wave",
                        "severity": "critical",
                        "date": date,
                        "title": "🔥 هشدار موج گرم بحرانی",
                        "description": f"دمای حداکثر {t_max[i]:.1f}°C - خطر سوختگی گیاهان",
                        "action": "آبیاری خنک‌کننده، سایبان، به تعویق انداختن عملیات زراعی",
                        "color": "#7f1d1d",
                        "icon": "🔥",
                    })
                elif t_max[i] >= 35:
                    alerts.append({
                        "type": "heat_stress",
                        "severity": "high",
                        "date": date,
                        "title": "🌡️ هشدار تنش گرمایی",
                        "description": f"دمای حداکثر {t_max[i]:.1f}°C - تنش گرمایی گیاهان",
                        "action": "افزایش آبیاری، آبیاری صبح زود یا غروب",
                        "color": "#dc2626",
                        "icon": "🌡️",
                    })
            
            # هشدار بارش شدید
            if i < len(precip) and precip[i] is not None:
                if precip[i] >= 50:
                    alerts.append({
                        "type": "heavy_rain",
                        "severity": "critical",
                        "date": date,
                        "title": "🌊 هشدار بارش شدید",
                        "description": f"بارش {precip[i]:.1f} میلی‌متر - خطر سیلاب و آب‌گرفتگی",
                        "action": "ایجاد زهکشی، عدم آبیاری، محافظت از خاک",
                        "color": "#1e40af",
                        "icon": "🌊",
                    })
                elif precip[i] >= 25:
                    alerts.append({
                        "type": "rain",
                        "severity": "medium",
                        "date": date,
                        "title": "🌧️ بارش قابل توجه",
                        "description": f"بارش {precip[i]:.1f} میلی‌متر پیش‌بینی شده",
                        "action": "به تعویق انداختن آبیاری، بررسی زهکشی",
                        "color": "#3b82f6",
                        "icon": "🌧️",
                    })
            
            # هشدار باد شدید
            if i < len(wind) and wind[i] is not None:
                if wind[i] >= 60:
                    alerts.append({
                        "type": "strong_wind",
                        "severity": "critical",
                        "date": date,
                        "title": "💨 هشدار باد شدید",
                        "description": f"سرعت باد {wind[i]:.1f} km/h - خطر وارسدگی و خسارت",
                        "action": "محافظت از گلخانه‌ها، عدم سم‌پاشی، مهار کردن تجهیزات",
                        "color": "#6b21a8",
                        "icon": "💨",
                    })
                elif wind[i] >= 40:
                    alerts.append({
                        "type": "wind",
                        "severity": "medium",
                        "date": date,
                        "title": "🌬️ باد قابل توجه",
                        "description": f"سرعت باد {wind[i]:.1f} km/h",
                        "action": "عدم سم‌پاشی، مهار کردن سازه‌های سبک",
                        "color": "#7c3aed",
                        "icon": "🌬️",
                    })
        
        # مرتب‌سازی بر اساس شدت
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        alerts.sort(key=lambda x: severity_order.get(x["severity"], 4))
        
        return alerts


def _get_frost_action(level: int) -> str:
    """دریافت اقدام برای یخبندان"""
    actions = {
        2: "پایش دما، آماده‌باش برای اقدام",
        3: "آبیاری قبل از یخبندان، استفاده از پوشش، دوددهی",
        4: "آبیاری فوری، فعال‌سازی سیستم‌های ضد یخبندان، پوشش کامل",
        5: "اقدامات اضطراری - تمام سیستم‌های حفاظتی فعال شوند",
    }
    return actions.get(level, "پایش")


def get_all_cities() -> Dict:
    """دریافت تمام شهرها"""
    return CITIES_DATABASE


def get_city(key: str) -> Optional[Dict]:
    """دریافت یک شهر"""
    return CITIES_DATABASE.get(key)
'''
    
    write_file(API_DIR / "services" / "weather_service.py", content)


# ============================================================
# فایل 2: Router هواشناسی
# ============================================================
def create_weather_router():
    print("\n🔌 ایجاد Weather Router...")
    
    content = '''# api/modules/weather/router.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, timedelta

from api.services.weather_service import (
    OpenMeteoService, AgriculturalIndices, WeatherAlerts,
    CITIES_DATABASE, get_all_cities
)

router = APIRouter(prefix="/weather", tags=["Weather"])


class CityInput(BaseModel):
    city_key: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


@router.get("/cities")
async def list_cities():
    """لیست تمام شهرهای موجود"""
    return {
        key: {
            "name_fa": c["name_fa"],
            "lat": c["lat"],
            "lon": c["lon"],
            "elevation": c["elevation"],
            "country": c["country"],
        }
        for key, c in CITIES_DATABASE.items()
    }


@router.get("/forecast/{city_key}")
async def get_forecast(city_key: str, days: int = Query(7, ge=1, le=16)):
    """پیش‌بینی هواشناسی یک شهر"""
    if city_key not in CITIES_DATABASE:
        raise HTTPException(404, f"شهر یافت نشد: {city_key}")
    
    city = CITIES_DATABASE[city_key]
    forecast = await OpenMeteoService.get_forecast(city["lat"], city["lon"], days)
    
    if "error" in forecast:
        raise HTTPException(500, forecast["error"])
    
    # محاسبه شاخص‌های کشاورزی
    daily = forecast.get("daily", {})
    enhanced_daily = _enhance_daily_data(daily)
    
    # تولید هشدارها
    alerts = WeatherAlerts.generate_alerts(forecast)
    
    # آمار کلی
    summary = _calculate_summary(daily)
    
    return {
        "city": {
            "key": city_key,
            "name_fa": city["name_fa"],
            "lat": city["lat"],
            "lon": city["lon"],
            "elevation": city["elevation"],
        },
        "forecast": enhanced_daily,
        "alerts": alerts,
        "summary": summary,
        "generated_at": datetime.utcnow().isoformat(),
        "source": "Open-Meteo API",
    }


@router.get("/forecast/coordinates")
async def get_forecast_by_coords(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    days: int = Query(7, ge=1, le=16)
):
    """پیش‌بینی بر اساس مختصات"""
    forecast = await OpenMeteoService.get_forecast(lat, lon, days)
    
    if "error" in forecast:
        raise HTTPException(500, forecast["error"])
    
    daily = forecast.get("daily", {})
    enhanced_daily = _enhance_daily_data(daily)
    alerts = WeatherAlerts.generate_alerts(forecast)
    summary = _calculate_summary(daily)
    
    return {
        "coordinates": {"lat": lat, "lon": lon},
        "forecast": enhanced_daily,
        "alerts": alerts,
        "summary": summary,
    }


@router.get("/historical/{city_key}")
async def get_historical(
    city_key: str,
    days_back: int = Query(30, ge=7, le=365)
):
    """داده‌های تاریخی"""
    if city_key not in CITIES_DATABASE:
        raise HTTPException(404, f"شهر یافت نشد: {city_key}")
    
    city = CITIES_DATABASE[city_key]
    end_date = datetime.utcnow().date() - timedelta(days=2)
    start_date = end_date - timedelta(days=days_back)
    
    historical = await OpenMeteoService.get_historical(
        city["lat"], city["lon"],
        start_date.isoformat(), end_date.isoformat()
    )
    
    if "error" in historical:
        raise HTTPException(500, historical["error"])
    
    return {
        "city": city["name_fa"],
        "period": f"{start_date} to {end_date}",
        "data": historical.get("daily", {}),
    }


@router.get("/compare")
async def compare_cities(cities: str = Query(..., description="لیست شهرها با کاما")):
    """مقایسه هواشناسی چند شهر"""
    city_keys = [c.strip() for c in cities.split(",")]
    results = []
    
    for key in city_keys[:5]:  # حداکثر ۵ شهر
        if key not in CITIES_DATABASE:
            continue
        
        city = CITIES_DATABASE[key]
        forecast = await OpenMeteoService.get_forecast(city["lat"], city["lon"], 3)
        
        if "error" in forecast or "daily" not in forecast:
            continue
        
        daily = forecast["daily"]
        results.append({
            "key": key,
            "name_fa": city["name_fa"],
            "today_max": daily.get("temperature_2m_max", [None])[0],
            "today_min": daily.get("temperature_2m_min", [None])[0],
            "today_precip": daily.get("precipitation_sum", [None])[0],
            "today_eto": daily.get("et0_fao_evapotranspiration", [None])[0],
            "alerts_count": len(WeatherAlerts.generate_alerts(forecast)),
        })
    
    return {"cities": results}


# ============ توابع کمکی ============
def _enhance_daily_data(daily: Dict) -> Dict:
    """افزودن شاخص‌های کشاورزی به داده‌های روزانه"""
    enhanced = {}
    
    dates = daily.get("time", [])
    t_max = daily.get("temperature_2m_max", [])
    t_min = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    wind = daily.get("wind_speed_10m_max", [])
    eto = daily.get("et0_fao_evapotranspiration", [])
    uv = daily.get("uv_index_max", [])
    sunrise = daily.get("sunrise", [])
    sunset = daily.get("sunset", [])
    weather_code = daily.get("weather_code", [])
    
    days_data = []
    for i in range(len(dates)):
        # شاخص‌های کشاورزی
        gdd = AgriculturalIndices.growing_degree_days(
            t_max[i] if i < len(t_max) and t_max[i] is not None else 20,
            t_min[i] if i < len(t_min) and t_min[i] is not None else 10
        )
        
        frost = AgriculturalIndices.frost_risk(
            t_min[i] if i < len(t_min) and t_min[i] is not None else 15
        )
        
        day_data = {
            "date": dates[i] if i < len(dates) else None,
            "weather_code": weather_code[i] if i < len(weather_code) else None,
            "weather_description": _get_weather_description(
                weather_code[i] if i < len(weather_code) else 0
            ),
            "temperature_max": t_max[i] if i < len(t_max) else None,
            "temperature_min": t_min[i] if i < len(t_min) else None,
            "precipitation": precip[i] if i < len(precip) else None,
            "wind_speed": wind[i] if i < len(wind) else None,
            "et0_fao": eto[i] if i < len(eto) else None,
            "uv_index": uv[i] if i < len(uv) else None,
            "sunrise": sunrise[i] if i < len(sunrise) else None,
            "sunset": sunset[i] if i < len(sunset) else None,
            # شاخص‌های محاسبه‌شده
            "gdd": round(gdd, 1),
            "frost_risk": frost,
        }
        days_data.append(day_data)
    
    return {"days": days_data}


def _calculate_summary(daily: Dict) -> Dict:
    """محاسبه آمار کلی"""
    t_max = [t for t in daily.get("temperature_2m_max", []) if t is not None]
    t_min = [t for t in daily.get("temperature_2m_min", []) if t is not None]
    precip = [p for p in daily.get("precipitation_sum", []) if p is not None]
    eto = [e for e in daily.get("et0_fao_evapotranspiration", []) if e is not None]
    
    total_gdd = sum(
        AgriculturalIndices.growing_degree_days(t_max[i], t_min[i])
        for i in range(min(len(t_max), len(t_min)))
    )
    
    return {
        "avg_max_temp": round(sum(t_max)/len(t_max), 1) if t_max else None,
        "avg_min_temp": round(sum(t_min)/len(t_min), 1) if t_min else None,
        "max_temp": max(t_max) if t_max else None,
        "min_temp": min(t_min) if t_min else None,
        "total_precipitation": round(sum(precip), 1) if precip else 0,
        "rainy_days": sum(1 for p in precip if p > 0),
        "total_eto": round(sum(eto), 1) if eto else 0,
        "total_gdd": round(total_gdd, 1),
        "avg_eto": round(sum(eto)/len(eto), 2) if eto else 0,
    }


def _get_weather_description(code: int) -> Dict:
    """تبدیل کد WMO به توضیح فارسی"""
    descriptions = {
        0: {"fa": "آسمان صاف", "icon": "☀️", "color": "#fbbf24"},
        1: {"fa": "عمدتاً صاف", "icon": "🌤️", "color": "#fcd34d"},
        2: {"fa": "نیمه ابری", "icon": "⛅", "color": "#94a3b8"},
        3: {"fa": "ابری", "icon": "☁️", "color": "#64748b"},
        45: {"fa": "مه", "icon": "🌫️", "color": "#94a3b8"},
        48: {"fa": "مه یخ‌زده", "icon": "🌫️", "color": "#93c5fd"},
        51: {"fa": "نم‌نم باران خفیف", "icon": "🌦️", "color": "#60a5fa"},
        53: {"fa": "نم‌نم باران", "icon": "🌦️", "color": "#3b82f6"},
        55: {"fa": "نم‌نم باران شدید", "icon": "🌧️", "color": "#2563eb"},
        61: {"fa": "باران خفیف", "icon": "🌧️", "color": "#3b82f6"},
        63: {"fa": "باران", "icon": "🌧️", "color": "#2563eb"},
        65: {"fa": "باران شدید", "icon": "🌧️", "color": "#1d4ed8"},
        71: {"fa": "برف خفیف", "icon": "🌨️", "color": "#dbeafe"},
        73: {"fa": "برف", "icon": "❄️", "color": "#bfdbfe"},
        75: {"fa": "برف شدید", "icon": "❄️", "color": "#93c5fd"},
        80: {"fa": "رگبار خفیف", "icon": "🌦️", "color": "#60a5fa"},
        81: {"fa": "رگبار", "icon": "🌧️", "color": "#3b82f6"},
        82: {"fa": "رگبار شدید", "icon": "⛈️", "color": "#1e40af"},
        95: {"fa": "رعد و برق", "icon": "⛈️", "color": "#4c1d95"},
        96: {"fa": "رعد و برق با تگرگ خفیف", "icon": "⛈️", "color": "#581c87"},
        99: {"fa": "رعد و برق با تگرگ شدید", "icon": "⛈️", "color": "#3b0764"},
    }
    return descriptions.get(code, {"fa": "نامشخص", "icon": "❓", "color": "#64748b"})
'''
    
    write_file(API_DIR / "modules" / "weather" / "router.py", content)


# ============================================================
# فایل 3: __init__.py
# ============================================================
def create_weather_init():
    print("\n📦 ایجاد weather/__init__.py...")
    content = '''# api/modules/weather/__init__.py
from . import router
'''
    write_file(API_DIR / "modules" / "weather" / "__init__.py", content)


# ============================================================
# فایل 4: به‌روزرسانی main.py
# ============================================================
def update_main():
    print("\n🔧 به‌روزرسانی main.py...")
    main_path = API_DIR / "main.py"
    
    if not main_path.exists():
        print("   ❌ main.py یافت نشد")
        return
    
    content = main_path.read_text(encoding="utf-8")
    
    if "weather_router" not in content:
        content = content.replace(
            "from api.scientific_core.router import router as scientific_router",
            "from api.scientific_core.router import router as scientific_router\nfrom api.modules.weather.router import router as weather_router"
        )
        content = content.replace(
            'app.include_router(scientific_router, prefix="/api/v1")',
            'app.include_router(scientific_router, prefix="/api/v1")\napp.include_router(weather_router, prefix="/api/v1")'
        )
        main_path.write_text(content, encoding="utf-8")
        print("   ✅ Weather router اضافه شد")


# ============================================================
# فایل 5: داشبورد فرانت‌اند
# ============================================================
def create_weather_dashboard():
    print("\n📊 ایجاد داشبورد هواشناسی...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import {
  ArrowRight, Cloud, Sun, Droplets, Wind, Thermometer, AlertTriangle,
  Loader2, MapPin, Calendar, TrendingUp, Activity, Zap, CloudRain,
  CloudSnow, Sunrise, Sunset, Eye, Navigation, CloudLightning,
  Gauge, Sprout, Shield, BarChart3, LineChart as LineChartIcon
} from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(m => m.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(m => m.Area), { ssr: false });
const ComposedChart = dynamic(() => import("recharts").then(m => m.ComposedChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });
const MapContainer = dynamic(() => import("react-leaflet").then(m => m.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then(m => m.TileLayer), { ssr: false });
const Marker = dynamic(() => import("react-leaflet").then(m => m.Marker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then(m => m.Popup), { ssr: false });
const CircleMarker = dynamic(() => import("react-leaflet").then(m => m.CircleMarker), { ssr: false });

const API_BASE = "http://localhost:8000/api/v1/weather";

export default function WeatherPage() {
  const [selectedCity, setSelectedCity] = useState("tehran");
  const [cities, setCities] = useState<any>({});
  const [forecast, setForecast] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [activeTab, setActiveTab] = useState<"forecast" | "map" | "alerts" | "agriculture">("forecast");

  useEffect(() => {
    loadCities();
  }, []);

  useEffect(() => {
    if (selectedCity) loadForecast();
  }, [selectedCity]);

  const loadCities = async () => {
    try {
      const res = await fetch(`${API_BASE}/cities`);
      if (res.ok) setCities(await res.json());
    } catch (e) {
      console.error("Failed to load cities");
    }
  };

  const loadForecast = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetch(`${API_BASE}/forecast/${selectedCity}?days=14`);
      if (!res.ok) throw new Error("خطا در دریافت پیش‌بینی");
      setForecast(await res.json());
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (code: number) => {
    if (code === 0 || code === 1) return <Sun className="h-8 w-8 text-yellow-400" />;
    if (code === 2 || code === 3) return <Cloud className="h-8 w-8 text-slate-400" />;
    if (code >= 45 && code <= 48) return <Eye className="h-8 w-8 text-slate-300" />;
    if (code >= 51 && code <= 67) return <CloudRain className="h-8 w-8 text-blue-400" />;
    if (code >= 71 && code <= 77) return <CloudSnow className="h-8 w-8 text-blue-200" />;
    if (code >= 80 && code <= 82) return <CloudRain className="h-8 w-8 text-blue-500" />;
    if (code >= 95) return <CloudLightning className="h-8 w-8 text-purple-500" />;
    return <Cloud className="h-8 w-8 text-slate-400" />;
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("fa-IR", { weekday: "short", month: "short", day: "numeric" });
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-500/20 border-red-500/50 text-red-300";
      case "high": return "bg-orange-500/20 border-orange-500/50 text-orange-300";
      case "medium": return "bg-amber-500/20 border-amber-500/50 text-amber-300";
      default: return "bg-blue-500/20 border-blue-500/50 text-blue-300";
    }
  };

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-sky-500 to-indigo-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-4">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-sky-500 to-indigo-600 shadow-2xl">
                <Cloud className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-sky-400 text-sm font-medium mb-1">هواشناسی کشاورزی هوشمند</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">پیش‌بینی و هشدار هواشناسی</h1>
                <p className="text-lg text-slate-300">
                  پیش‌بینی ۱۶ روزه، شاخص‌های کشاورزی، هشدارهای هوشمند و توصیه‌های آبیاری
                </p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 mt-4">
              {["Open-Meteo", "FAO-56 ETo", "GDD", "NOAA", "WMO"].map(s => (
                <span key={s} className="px-3 py-1 bg-sky-500/10 border border-sky-500/30 rounded-full text-xs text-sky-300">
                  {s}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </section>

      {/* City Selector */}
      <section className="container mx-auto px-6 py-6">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-4 flex flex-wrap items-center gap-4">
          <div className="flex items-center gap-2">
            <MapPin className="h-5 w-5 text-sky-400" />
            <span className="text-white font-bold">شهر:</span>
          </div>
          <select
            value={selectedCity}
            onChange={(e) => setSelectedCity(e.target.value)}
            className="flex-1 min-w-[200px] px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white"
          >
            {Object.entries(cities).map(([key, city]: any) => (
              <option key={key} value={key}>
                {city.name_fa} ({city.country})
              </option>
            ))}
          </select>
          
          {forecast && (
            <div className="flex items-center gap-2 text-sm text-slate-400">
              <Navigation className="h-4 w-4" />
              <span>{forecast.city.lat.toFixed(2)}°, {forecast.city.lon.toFixed(2)}°</span>
              <span className="mx-2">|</span>
              <span>ارتفاع: {forecast.city.elevation}m</span>
            </div>
          )}
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-4">
        <div className="flex gap-2 mb-6 flex-wrap">
          {[
            { id: "forecast", label: "پیش‌بینی", icon: Calendar },
            { id: "map", label: "نقشه", icon: MapPin },
            { id: "alerts", label: `هشدارها ${forecast?.alerts?.length ? `(${forecast.alerts.length})` : ""}`, icon: AlertTriangle },
            { id: "agriculture", label: "کشاورزی", icon: Sprout },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-5 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
                activeTab === tab.id
                  ? "bg-sky-600 text-white shadow-lg shadow-sky-500/30"
                  : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
            >
              <tab.icon className="h-5 w-5" />
              {tab.label}
            </button>
          ))}
        </div>

        {loading && (
          <div className="flex items-center justify-center py-20">
            <Loader2 className="h-12 w-12 animate-spin text-sky-400" />
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-500/20 border border-red-500/30 rounded-xl text-red-300">
            {error}
          </div>
        )}

        {!loading && !error && forecast && (
          <>
            {/* ============ FORECAST TAB ============ */}
            {activeTab === "forecast" && (
              <div className="space-y-6">
                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
                  <div className="bg-gradient-to-br from-red-900/30 to-red-800/20 border border-red-500/30 rounded-xl p-4">
                    <Thermometer className="h-5 w-5 text-red-400 mb-2" />
                    <p className="text-xs text-red-300">حداکثر دما</p>
                    <p className="text-2xl font-black text-white">{forecast.summary.max_temp?.toFixed(1)}°C</p>
                  </div>
                  <div className="bg-gradient-to-br from-blue-900/30 to-blue-800/20 border border-blue-500/30 rounded-xl p-4">
                    <Thermometer className="h-5 w-5 text-blue-400 mb-2" />
                    <p className="text-xs text-blue-300">حداقل دما</p>
                    <p className="text-2xl font-black text-white">{forecast.summary.min_temp?.toFixed(1)}°C</p>
                  </div>
                  <div className="bg-gradient-to-br from-sky-900/30 to-sky-800/20 border border-sky-500/30 rounded-xl p-4">
                    <CloudRain className="h-5 w-5 text-sky-400 mb-2" />
                    <p className="text-xs text-sky-300">کل بارش</p>
                    <p className="text-2xl font-black text-white">{forecast.summary.total_precipitation} mm</p>
                  </div>
                  <div className="bg-gradient-to-br from-emerald-900/30 to-emerald-800/20 border border-emerald-500/30 rounded-xl p-4">
                    <Droplets className="h-5 w-5 text-emerald-400 mb-2" />
                    <p className="text-xs text-emerald-300">ETo کل</p>
                    <p className="text-2xl font-black text-white">{forecast.summary.total_eto} mm</p>
                  </div>
                  <div className="bg-gradient-to-br from-amber-900/30 to-amber-800/20 border border-amber-500/30 rounded-xl p-4">
                    <Sprout className="h-5 w-5 text-amber-400 mb-2" />
                    <p className="text-xs text-amber-300">GDD کل</p>
                    <p className="text-2xl font-black text-white">{forecast.summary.total_gdd}</p>
                  </div>
                  <div className="bg-gradient-to-br from-purple-900/30 to-purple-800/20 border border-purple-500/30 rounded-xl p-4">
                    <CloudRain className="h-5 w-5 text-purple-400 mb-2" />
                    <p className="text-xs text-purple-300">روزهای بارانی</p>
                    <p className="text-2xl font-black text-white">{forecast.summary.rainy_days}</p>
                  </div>
                </div>

                {/* Temperature Chart */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-sky-400" />
                    روند دما و بارش
                  </h3>
                  <div className="h-72">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={forecast.forecast.days}>
                        <defs>
                          <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                            <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis 
                          dataKey="date" 
                          stroke="#64748b" 
                          fontSize={11}
                          tickFormatter={(v) => new Date(v).toLocaleDateString("fa-IR", { month: "short", day: "numeric" })}
                        />
                        <YAxis yAxisId="left" stroke="#ef4444" fontSize={11} label={{ value: "°C", angle: -90, position: "insideLeft", fill: "#ef4444" }} />
                        <YAxis yAxisId="right" orientation="right" stroke="#3b82f6" fontSize={11} label={{ value: "mm", angle: 90, position: "insideRight", fill: "#3b82f6" }} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }}
                          labelFormatter={(v) => new Date(v).toLocaleDateString("fa-IR")}
                        />
                        <Legend />
                        <Area yAxisId="left" type="monotone" dataKey="temperature_max" stroke="#ef4444" fill="url(#tempGrad)" name="حداکثر دما (°C)" />
                        <Line yAxisId="left" type="monotone" dataKey="temperature_min" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} name="حداقل دما (°C)" />
                        <Bar yAxisId="right" dataKey="precipitation" fill="#06b6d4" opacity={0.7} name="بارش (mm)" />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* ETo & GDD Chart */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Sprout className="h-5 w-5 text-emerald-400" />
                    تبخیر و تعرق (ETo) و درجه-روز رشد (GDD)
                  </h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <ComposedChart data={forecast.forecast.days}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis 
                          dataKey="date" 
                          stroke="#64748b" 
                          fontSize={11}
                          tickFormatter={(v) => new Date(v).toLocaleDateString("fa-IR", { month: "short", day: "numeric" })}
                        />
                        <YAxis stroke="#64748b" fontSize={11} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }}
                          labelFormatter={(v) => new Date(v).toLocaleDateString("fa-IR")}
                        />
                        <Legend />
                        <Bar dataKey="et0_fao" fill="#10b981" name="ETo (mm)" />
                        <Line type="monotone" dataKey="gdd" stroke="#f59e0b" strokeWidth={2} name="GDD" />
                      </ComposedChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                {/* Daily Forecast Cards */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Calendar className="h-5 w-5 text-sky-400" />
                    پیش‌بینی روزانه
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
                    {forecast.forecast.days.slice(0, 7).map((day: any, idx: number) => (
                      <motion.div
                        key={idx}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="bg-slate-800/50 border border-slate-700 rounded-xl p-4 text-center hover:border-sky-500/50 transition-colors"
                      >
                        <p className="text-xs text-slate-400 mb-2">{formatDate(day.date)}</p>
                        <div className="flex justify-center mb-2">{getWeatherIcon(day.weather_code)}</div>
                        <p className="text-xs text-slate-300 mb-2">{day.weather_description?.fa}</p>
                        <div className="space-y-1 text-xs">
                          <div className="flex justify-between">
                            <span className="text-red-400">↑{day.temperature_max?.toFixed(0)}°</span>
                            <span className="text-blue-400">↓{day.temperature_min?.toFixed(0)}°</span>
                          </div>
                          <div className="flex justify-between text-slate-400">
                            <span>💧{day.precipitation?.toFixed(1) || 0}</span>
                            <span>💨{day.wind_speed?.toFixed(0) || 0}</span>
                          </div>
                          <div className="pt-1 border-t border-slate-700 text-emerald-400">
                            ETo: {day.et0_fao?.toFixed(1) || 0}
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* ============ MAP TAB ============ */}
            {activeTab === "map" && (
              <div className="space-y-6">
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <MapPin className="h-5 w-5 text-sky-400" />
                    نقشه هواشناسی شهرها
                  </h3>
                  <div className="h-[600px] rounded-xl overflow-hidden">
                    <MapContainer
                      center={[32.5, 54.5]}
                      zoom={5}
                      style={{ height: "100%", width: "100%" }}
                      scrollWheelZoom={true}
                    >
                      <TileLayer
                        url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                        attribution="&copy; Esri"
                      />
                      
                      {/* شهرها */}
                      {Object.entries(cities).map(([key, city]: any) => {
                        const isSelected = key === selectedCity;
                        const cityForecast = key === selectedCity ? forecast : null;
                        const temp = cityForecast?.summary?.avg_max_temp;
                        
                        // رنگ بر اساس دما
                        const color = !temp ? "#64748b" :
                                     temp > 35 ? "#dc2626" :
                                     temp > 30 ? "#f97316" :
                                     temp > 25 ? "#f59e0b" :
                                     temp > 20 ? "#84cc16" :
                                     temp > 15 ? "#22c55e" :
                                     temp > 10 ? "#06b6d4" :
                                     temp > 5 ? "#3b82f6" :
                                     temp > 0 ? "#6366f1" : "#7c3aed";
                        
                        return (
                          <CircleMarker
                            key={key}
                            center={[city.lat, city.lon]}
                            radius={isSelected ? 15 : 10}
                            pathOptions={{
                              color: color,
                              fillColor: color,
                              fillOpacity: 0.7,
                              weight: isSelected ? 3 : 1,
                            }}
                          >
                            <Popup>
                              <div className="p-2 text-slate-900 min-w-[200px]">
                                <h4 className="font-bold text-lg mb-1">{city.name_fa}</h4>
                                <p className="text-xs text-slate-600 mb-2">{city.country}</p>
                                {cityForecast && (
                                  <>
                                    <div className="space-y-1 text-sm">
                                      <div className="flex justify-between">
                                        <span>حداکثر دما:</span>
                                        <span className="font-bold">{cityForecast.summary.max_temp?.toFixed(1)}°C</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span>حداقل دما:</span>
                                        <span className="font-bold">{cityForecast.summary.min_temp?.toFixed(1)}°C</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span>بارش کل:</span>
                                        <span className="font-bold">{cityForecast.summary.total_precipitation} mm</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span>ETo:</span>
                                        <span className="font-bold">{cityForecast.summary.total_eto} mm</span>
                                      </div>
                                      <div className="flex justify-between">
                                        <span>هشدارها:</span>
                                        <span className="font-bold text-red-500">{cityForecast.alerts?.length || 0}</span>
                                      </div>
                                    </div>
                                  </>
                                )}
                              </div>
                            </Popup>
                          </CircleMarker>
                        );
                      })}
                    </MapContainer>
                  </div>
                  
                  {/* Legend */}
                  <div className="mt-4 p-4 bg-slate-800/50 rounded-xl">
                    <p className="text-sm font-bold text-white mb-2">راهنمای رنگ دما:</p>
                    <div className="flex flex-wrap gap-3 text-xs">
                      {[
                        { color: "#7c3aed", label: "< 0°C" },
                        { color: "#6366f1", label: "0-5°C" },
                        { color: "#3b82f6", label: "5-10°C" },
                        { color: "#06b6d4", label: "10-15°C" },
                        { color: "#22c55e", label: "15-20°C" },
                        { color: "#84cc16", label: "20-25°C" },
                        { color: "#f59e0b", label: "25-30°C" },
                        { color: "#f97316", label: "30-35°C" },
                        { color: "#dc2626", label: "> 35°C" },
                      ].map(item => (
                        <div key={item.label} className="flex items-center gap-1">
                          <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                          <span className="text-slate-300">{item.label}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Cities Comparison Table */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">مقایسه شهرها</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-700">
                          <th className="text-right py-2 px-3 text-slate-300">شهر</th>
                          <th className="text-right py-2 px-3 text-slate-300">حداکثر دما</th>
                          <th className="text-right py-2 px-3 text-slate-300">حداقل دما</th>
                          <th className="text-right py-2 px-3 text-slate-300">بارش</th>
                          <th className="text-right py-2 px-3 text-slate-300">ETo</th>
                          <th className="text-right py-2 px-3 text-slate-300">هشدارها</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(cities).slice(0, 10).map(([key, city]: any) => (
                          <tr key={key} className="border-b border-slate-800 hover:bg-slate-800/50">
                            <td className="py-2 px-3 text-white font-bold">{city.name_fa}</td>
                            <td className="py-2 px-3 text-red-400">-</td>
                            <td className="py-2 px-3 text-blue-400">-</td>
                            <td className="py-2 px-3 text-sky-400">-</td>
                            <td className="py-2 px-3 text-emerald-400">-</td>
                            <td className="py-2 px-3">-</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* ============ ALERTS TAB ============ */}
            {activeTab === "alerts" && (
              <div className="space-y-6">
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-amber-400" />
                    هشدارهای فعال ({forecast.alerts.length})
                  </h3>
                  
                  {forecast.alerts.length === 0 ? (
                    <div className="text-center py-12">
                      <Shield className="h-16 w-16 text-emerald-400 mx-auto mb-4 opacity-50" />
                      <p className="text-slate-300">هیچ هشداری برای این منطقه فعال نیست</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {forecast.alerts.map((alert: any, idx: number) => (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: idx * 0.1 }}
                          className={`p-5 rounded-xl border-2 ${getSeverityColor(alert.severity)}`}
                        >
                          <div className="flex items-start gap-4">
                            <div className="text-4xl">{alert.icon}</div>
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-2 flex-wrap">
                                <h4 className="font-bold text-white text-lg">{alert.title}</h4>
                                <span className={`text-xs px-2 py-1 rounded-full ${
                                  alert.severity === "critical" ? "bg-red-500/30" :
                                  alert.severity === "high" ? "bg-orange-500/30" :
                                  "bg-amber-500/30"
                                }`}>
                                  {alert.severity === "critical" ? "بحرانی" :
                                   alert.severity === "high" ? "جدی" : "متوسط"}
                                </span>
                                <span className="text-xs text-slate-400">📅 {alert.date}</span>
                              </div>
                              <p className="text-sm text-slate-300 mb-3">{alert.description}</p>
                              <div className="bg-slate-900/50 rounded-lg p-3 border-l-4" style={{ borderColor: alert.color }}>
                                <p className="text-xs text-slate-400 mb-1">💡 اقدام پیشنهادی:</p>
                                <p className="text-sm text-white">{alert.action}</p>
                              </div>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Frost Risk Chart */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <CloudSnow className="h-5 w-5 text-blue-400" />
                    ریسک یخبندان
                  </h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={forecast.forecast.days}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                        <XAxis 
                          dataKey="date" 
                          stroke="#64748b" 
                          fontSize={11}
                          tickFormatter={(v) => new Date(v).toLocaleDateString("fa-IR", { month: "short", day: "numeric" })}
                        />
                        <YAxis stroke="#64748b" fontSize={11} />
                        <Tooltip 
                          contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }}
                          labelFormatter={(v) => new Date(v).toLocaleDateString("fa-IR")}
                        />
                        <Legend />
                        <Line type="monotone" dataKey="temperature_min" stroke="#3b82f6" strokeWidth={2} name="حداقل دما (°C)" />
                        <Line type="monotone" dataKey={[]} stroke="#ef4444" strokeDasharray="5 5" strokeWidth={2} name="آستانه یخبندان" />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}

            {/* ============ AGRICULTURE TAB ============ */}
            {activeTab === "agriculture" && (
              <div className="space-y-6">
                {/* Agricultural Indices */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gradient-to-br from-emerald-900/30 to-green-900/20 border border-emerald-500/30 rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Sprout className="h-8 w-8 text-emerald-400" />
                      <div>
                        <h3 className="text-xl font-bold text-white">شاخص‌های رشد گیاه</h3>
                        <p className="text-sm text-emerald-300">بر اساس FAO-56</p>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                        <span className="text-slate-300">GDD کل دوره:</span>
                        <span className="text-2xl font-black text-emerald-400">{forecast.summary.total_gdd}</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                        <span className="text-slate-300">میانگین روزانه GDD:</span>
                        <span className="text-xl font-bold text-emerald-400">
                          {(forecast.summary.total_gdd / forecast.forecast.days.length).toFixed(1)}
                        </span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                        <span className="text-slate-300">ETo کل:</span>
                        <span className="text-2xl font-black text-sky-400">{forecast.summary.total_eto} mm</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                        <span className="text-slate-300">میانگین ETo روزانه:</span>
                        <span className="text-xl font-bold text-sky-400">{forecast.summary.avg_eto} mm</span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gradient-to-br from-blue-900/30 to-cyan-900/20 border border-blue-500/30 rounded-2xl p-6">
                    <div className="flex items-center gap-3 mb-4">
                      <Droplets className="h-8 w-8 text-blue-400" />
                      <div>
                        <h3 className="text-xl font-bold text-white">توصیه‌های آبیاری</h3>
                        <p className="text-sm text-blue-300">بر اساس ETo و بارش</p>
                      </div>
                    </div>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                        <span className="text-slate-300">نیاز آبی کل:</span>
                        <span className="text-2xl font-black text-blue-400">{forecast.summary.total_eto} mm</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                        <span className="text-slate-300">بارش مؤثر:</span>
                        <span className="text-xl font-bold text-cyan-400">{forecast.summary.total_precipitation} mm</span>
                      </div>
                      <div className="flex justify-between items-center p-3 bg-slate-900/50 rounded-lg">
                        <span className="text-slate-300">نیاز آبیاری خالص:</span>
                        <span className="text-2xl font-black text-amber-400">
                          {Math.max(0, forecast.summary.total_eto - forecast.summary.total_precipitation * 0.7).toFixed(1)} mm
                        </span>
                      </div>
                      <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 rounded-lg">
                        <p className="text-xs text-emerald-300 mb-1">💡 توصیه:</p>
                        <p className="text-sm text-white">
                          {forecast.summary.total_eto - forecast.summary.total_precipitation * 0.7 > 0 
                            ? `آبیاری تکمیلی با حجم ${Math.round((forecast.summary.total_eto - forecast.summary.total_precipitation * 0.7) / forecast.forecast.days.length)} mm در روز`
                            : "بارش کافی است - آبیاری را کاهش دهید"}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Frost Risk by Day */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <CloudSnow className="h-5 w-5 text-blue-400" />
                    ریسک یخبندان روزانه
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-7 gap-3">
                    {forecast.forecast.days.slice(0, 7).map((day: any, idx: number) => (
                      <div
                        key={idx}
                        className="p-4 rounded-xl border-2 text-center"
                        style={{
                          borderColor: day.frost_risk.color,
                          backgroundColor: day.frost_risk.color + "20"
                        }}
                      >
                        <p className="text-xs text-slate-300 mb-2">{formatDate(day.date)}</p>
                        <p className="text-2xl font-black text-white mb-1">{day.temperature_min?.toFixed(1)}°C</p>
                        <p className="text-xs font-bold" style={{ color: day.frost_risk.color }}>
                          {day.frost_risk.risk}
                        </p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Agricultural Recommendations */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                    <Sprout className="h-5 w-5 text-emerald-400" />
                    توصیه‌های کشاورزی هوشمند
                  </h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
                      <h4 className="font-bold text-emerald-300 mb-2">🌱 زمان کاشت</h4>
                      <p className="text-sm text-slate-300">
                        {forecast.summary.min_temp > 5 
                          ? "شرایط دمایی برای کاشت بهاره مناسب است"
                          : "منتظر گرم‌تر شدن هوا باشید - ریسک یخبندان بالا"}
                      </p>
                    </div>
                    <div className="p-4 bg-sky-500/10 border border-sky-500/30 rounded-xl">
                      <h4 className="font-bold text-sky-300 mb-2">💧 آبیاری</h4>
                      <p className="text-sm text-slate-300">
                        {forecast.summary.total_precipitation > forecast.summary.total_eto * 0.7
                          ? "بارش کافی - آبیاری را کاهش دهید"
                          : "نیاز به آبیاری تکمیلی - صبح زود یا غروب"}
                      </p>
                    </div>
                    <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-xl">
                      <h4 className="font-bold text-amber-300 mb-2">🚜 عملیات زراعی</h4>
                      <p className="text-sm text-slate-300">
                        {forecast.forecast.days[0]?.wind_speed < 30
                          ? "شرایط برای سم‌پاشی و کوددهی مناسب است"
                          : "به دلیل وزش باد، عملیات سم‌پاشی را به تعویق بیندازید"}
                      </p>
                    </div>
                    <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-xl">
                      <h4 className="font-bold text-purple-300 mb-2">🌾 برداشت</h4>
                      <p className="text-sm text-slate-300">
                        {forecast.forecast.days.slice(0, 3).every((d: any) => d.precipitation < 5)
                          ? "هوا برای برداشت محصول مناسب است"
                          : "احتمال بارش - برداشت را برنامه‌ریزی کنید"}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Data Sources */}
                <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">📡 منابع داده</h3>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="font-bold text-white mb-1">Open-Meteo</p>
                      <p className="text-xs text-slate-400">پیش‌بینی ۱۶ روزه</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="font-bold text-white mb-1">FAO-56</p>
                      <p className="text-xs text-slate-400">ETo Penman-Monteith</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="font-bold text-white mb-1">NOAA</p>
                      <p className="text-xs text-slate-400">مدل‌های GFS</p>
                    </div>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                      <p className="font-bold text-white mb-1">WMO</p>
                      <p className="text-xs text-slate-400">استاندارد کدها</p>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "weather" / "page.tsx", content)


# ============================================================
# Main
# ============================================================
def main():
    print("🌦️ ماژول جامع هواشناسی کشاورزی")
    print("=" * 70)
    
    if not API_DIR.exists() or not WEB.exists():
        print("❌ دایرکتوری‌ها یافت نشد!")
        return 1
    
    create_weather_service()
    create_weather_router()
    create_weather_init()
    update_main()
    create_weather_dashboard()
    
    print("\n" + "=" * 70)
    print("✅ ماژول هواشناسی ایجاد شد!")
    print("\n🎯 ویژگی‌های پیاده‌سازی شده:")
    print("   📡 اتصال به Open-Meteo API (رایگان، بدون کلید)")
    print("   🌍 ۲۸ شهر (۲۰ ایران + ۸ جهان)")
    print("   📅 پیش‌بینی ۱۶ روزه")
    print("   🧮 شاخص‌های کشاورزی:")
    print("      • GDD (Growing Degree Days)")
    print("      • ETo (FAO-56 Penman-Monteith)")
    print("      • THI (Temperature-Humidity Index)")
    print("      • Frost Risk Assessment")
    print("   🚨 سیستم هشدار هوشمند:")
    print("      • یخبندان")
    print("      • موج گرم")
    print("      • بارش شدید")
    print("      • باد شدید")
    print("   🗺️ نقشه هواشناسی تعاملی")
    print("   📊 ۴ تب کامل:")
    print("      • پیش‌بینی")
    print("      • نقشه")
    print("      • هشدارها")
    print("      • کشاورزی")
    print("   💡 توصیه‌های آبیاری هوشمند")
    print("   📈 نمودارهای پیشرفته")
    print("")
    print("🚀 گام بعدی:")
    print("   1. نصب پکیج httpx (برای API calls):")
    print("      python -m pip install httpx")
    print("")
    print("   2. ری‌استارت سرور بک‌اند:")
    print("      uvicorn api.main:app --reload --port 8000")
    print("")
    print("   3. پاک‌سازی کش فرانت‌اند:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("")
    print("   4. اجرا:")
    print("      pnpm run dev -- -p 3001")
    print("")
    print("   5. مشاهده: http://localhost:3001/weather")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())