"""Data API Router — real-world climate/elevation/indicator data (no API keys)."""

from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from apps.simulation.data import service as data_service
from apps.simulation.data import world_bank
from apps.simulation.data.nasa_power import fetch_nasa_power_data
from apps.simulation.data.satellite import fetch_satellite_agro_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/data", tags=["Real-World Data"])


@router.get("/climate", summary="Daily climate series (NASA POWER / Open-Meteo, no key)")
async def climate(
    lat: float = Query(..., ge=-90, le=90, description="Latitude"),
    lon: float = Query(..., ge=-180, le=180, description="Longitude"),
    start: str | None = Query(None, description="YYYY-MM-DD (default: 90 days ago)"),
    end: str | None = Query(None, description="YYYY-MM-DD (default: today)"),
    source: str = Query("auto", description="auto | nasa | openmeteo"),
) -> dict[str, Any]:
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
        "latitude": lat,
        "longitude": lon,
        "start": start_d.isoformat(),
        "end": end_d.isoformat(),
        "source": source,
        "days": len(data),
        "daily": data,
    }


@router.get("/elevation", summary="Ground elevation (Open-Elevation, no key)")
async def elevation(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
) -> dict[str, Any]:
    elev = await data_service.get_elevation(lat, lon)
    if elev is None:
        raise HTTPException(502, "Could not fetch elevation")
    return {"latitude": lat, "longitude": lon, "elevation_m": elev}


@router.get("/indicators", summary="Agricultural indicators (World Bank, no key)")
async def indicators(
    country: str = Query(..., description="ISO2/ISO3 country code (e.g. IR, IRN)"),
    year_from: int = Query(2010, ge=1960, le=2025),
    year_to: int = Query(2023, ge=1960, le=2025),
) -> dict[str, Any]:
    data = await world_bank.get_indicators(country.upper(), year_from, year_to)
    return {"country": country.upper(), "indicators": data}


@router.get("/weather/real", summary="NASA POWER weather suggestion")
async def get_real_weather(lat: float, lon: float, days: int = 30) -> dict[str, Any]:
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y%m%d")

    data = await fetch_nasa_power_data(lat, lon, start_date, end_date)
    if data.get("status") == "error":
        return {
            "status": "error",
            "message": "NASA fetch failed; use defaults",
        }

    temps = list(data.get("temp_c", {}).values())
    precs = list(data.get("precip_mm", {}).values())

    avg_temp = sum(temps) / len(temps) if temps else 15.0
    total_precip = sum(precs) if precs else 250.0

    return {
        "status": "success",
        "suggested_params": {
            "fallback_et0": round(avg_temp * 0.3 + 2, 1),
            "fallback_precip": round(total_precip, 1),
        },
    }


@router.get("/satellite", summary="Synthetic satellite agro series")
async def get_satellite_data(lat: float, lon: float, days: int = 7) -> dict[str, Any]:
    data = await fetch_satellite_agro_data(lat, lon, days)
    if data.get("status") == "error":
        return {"status": "error", "message": data.get("message")}
    return data
