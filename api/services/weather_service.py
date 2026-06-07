# api/services/weather_service.py
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
