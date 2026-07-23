from apps.simulation.data.satellite import fetch_satellite_agro_data
from apps.simulation.data.nasa_power import fetch_nasa_power_data
"""
Data API Router — real-world climate/elevation/indicator data (no API keys).
"""
from datetime import date, timedelta
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from apps.simulation.data import service as data_service
from apps.simulation.data import world_bank

router = APIRouter(prefix="/api/v1/data", tags=["🌍 Real-World Data"])


@router.get("/climate", summary="Daily climate series (NASA POWER / Open-Meteo, no key)")
async def climate(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    start: Optional[str] = Query(None, description="YYYY-MM-DD (default: 90 days ago)"),
    end: Optional[str] = Query(None, description="YYYY-MM-DD (default: today)"),
    source: str = Query("auto", description="auto | nasa | openmeteo"),
):
    try:
        end_d = date.fromisoformat(end) if end else date.today()
        start_d = date.fromisoformat(start) if start else (end_d - timedelta(days=90))
    except ValueError:
        raise HTTPException(400, "Invalid date format (use YYYY-MM-DD)")
    if (end_d - start_d).days > 3650:
        raise HTTPException(400, "Range too large (max 10 years)")

    data = await data_service.get_climate_series(lat, lon, start_d, end_d, source)
    if not data:
        raise HTTPException(502, "Could not fetch climate data from any source")
    return {
        "latitude": lat, "longitude": lon,
        "start": start_d.isoformat(), "end": end_d.isoformat(),
        "source": source, "days": len(data), "daily": data,
    }


@router.get("/elevation", summary="Ground elevation (Open-Elevation, no key)")
async def elevation(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    elev = await data_service.get_elevation(lat, lon)
    if elev is None:
        raise HTTPException(502, "Could not fetch elevation")
    return {"latitude": lat, "longitude": lon, "elevation_m": elev}


@router.get("/indicators", summary="Agricultural indicators (World Bank, no key)")
async def indicators(
    country: str = Query(..., description="ISO2/ISO3 country code (e.g. IR, IRN)"),
    year_from: int = Query(2010, ge=1960, le=2025),
    year_to: int = Query(2023, ge=1960, le=2025),
):
    data = await world_bank.get_indicators(country.upper(), year_from, year_to)
    return {"country": country.upper(), "indicators": data}

@router.get("/weather/real", summary="دریافت دادهٔ واقعی آب‌وهوا از NASA POWER")
async def get_real_weather(lat: float, lon: float, days: int = 30):
    from datetime import datetime, timedelta
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")
    
    data = await fetch_nasa_power_data(lat, lon, start_date, end_date)
    if data.get("status") == "error":
        return {"status": "error", "message": "خطا در دریافت داده از ناسا. از دادهٔ پیش‌فرض استفاده شد."}
    
    # محاسبهٔ میانگین برای پر کردن خودکار فرم
    temps = list(data.get("temp_c", {}).values())
    precs = list(data.get("precip_mm", {}).values())
    
    avg_temp = sum(temps) / len(temps) if temps else 15.0
    total_precip = sum(precs) if precs else 250.0
    
    return {
        "status": "success",
        "suggested_params": {
            "fallback_et0": round(avg_temp * 0.3 + 2, 1), # تخمین ساده ET0
            "fallback_precip": round(total_precip, 1)
        }
    }

@router.get("/satellite", summary="دریافت داده‌های ماهواره‌ای کشاورزی (رطوبت خاک و تبخیر-تعرق)")
async def get_satellite_data(lat: float, lon: float, days: int = 7):
    data = await fetch_satellite_agro_data(lat, lon, days)
    if data.get("status") == "error":
        return {"status": "error", "message": data.get("message")}
    return data
