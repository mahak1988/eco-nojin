"""Drought Domain Router.

این ماژول endpointهای API خشکسالی را تعریف می‌کند.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from datetime import datetime
from .schemas.drought_schemas import (
    DroughtIndexResponse, 
    SPEIRequest, 
    CHIRPSRequest
)
from .services.drought_service import DroughtService
from .repositories.drought_repository import DroughtRepository


router = APIRouter(prefix="/drought", tags=["Drought"])


def get_drought_service() -> DroughtService:
    """Dependency Injection برای DroughtService"""
    repo = DroughtRepository()
    return DroughtService(repo)


@router.get("/index", response_model=List[DroughtIndexResponse])
async def get_drought_index(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
    start_date: datetime = Query(...),
    end_date: datetime = Query(...),
    service: DroughtService = Depends(get_drought_service)
):
    """دریافت شاخص‌های خشکسالی"""
    # TODO: اتصال به service
    return []


@router.post("/spei")
async def calculate_spei(
    request: SPEIRequest,
    service: DroughtService = Depends(get_drought_service)
):
    """محاسبه شاخص SPEI"""
    # TODO: پیاده‌سازی
    return {"status": "not_implemented"}


@router.get("/early-warning/{lat}/{lon}")
async def get_early_warning(
    lat: float,
    lon: float,
    service: DroughtService = Depends(get_drought_service)
):
    """دریافت هشدار زودهنگام خشکسالی"""
    return await service.get_early_warning(lat, lon)
