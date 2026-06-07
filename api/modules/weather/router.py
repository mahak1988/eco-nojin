from api.services.weather.open_meteo import open_meteo, OpenMeteoService
# api/modules/weather/router.py
from api.core.schemas import SuccessResponse, IDResponse, StatsResponse, PaginatedResponse
from datetime import datetime, timedelta
from typing import Dict, Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from api.services.weather_service import (
    CITIES_DATABASE,
    AgriculturalIndices,
    OpenMeteoService,
    WeatherAlerts,
    get_all_cities,
)

router = APIRouter(prefix="/weather", tags=["Weather"])


class CityInput(BaseModel):
    city_key: Optional[str] = None
    lat: Optional[float] = None
    lon: Optional[float] = None


@router.get("/cities", response_model=Dict[str, Any])
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


@router.get("/forecast/{city_key}", response_model=Dict[str, Any])
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


@router.get("/forecast/coordinates", response_model=Dict[str, Any])
async def get_forecast_by_coords(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    days: int = Query(7, ge=1, le=16),
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


@router.get("/historical/{city_key}", response_model=Dict[str, Any])
async def get_historical(city_key: str, days_back: int = Query(30, ge=7, le=365)):
    """داده‌های تاریخی"""
    if city_key not in CITIES_DATABASE:
        raise HTTPException(404, f"شهر یافت نشد: {city_key}")

    city = CITIES_DATABASE[city_key]
    end_date = datetime.utcnow().date() - timedelta(days=2)
    start_date = end_date - timedelta(days=days_back)

    historical = await OpenMeteoService.get_historical(
        city["lat"], city["lon"], start_date.isoformat(), end_date.isoformat()
    )

    if "error" in historical:
        raise HTTPException(500, historical["error"])

    return {
        "city": city["name_fa"],
        "period": f"{start_date} to {end_date}",
        "data": historical.get("daily", {}),
    }


@router.get("/compare", response_model=Dict[str, Any])
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
        results.append(
            {
                "key": key,
                "name_fa": city["name_fa"],
                "today_max": daily.get("temperature_2m_max", [None])[0],
                "today_min": daily.get("temperature_2m_min", [None])[0],
                "today_precip": daily.get("precipitation_sum", [None])[0],
                "today_eto": daily.get("et0_fao_evapotranspiration", [None])[0],
                "alerts_count": len(WeatherAlerts.generate_alerts(forecast)),
            }
        )

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
            t_min[i] if i < len(t_min) and t_min[i] is not None else 10,
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
        "avg_max_temp": round(sum(t_max) / len(t_max), 1) if t_max else None,
        "avg_min_temp": round(sum(t_min) / len(t_min), 1) if t_min else None,
        "max_temp": max(t_max) if t_max else None,
        "min_temp": min(t_min) if t_min else None,
        "total_precipitation": round(sum(precip), 1) if precip else 0,
        "rainy_days": sum(1 for p in precip if p > 0),
        "total_eto": round(sum(eto), 1) if eto else 0,
        "total_gdd": round(total_gdd, 1),
        "avg_eto": round(sum(eto) / len(eto), 2) if eto else 0,
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
