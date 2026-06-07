from api.services.ai.ai_service import AIService, ai_service
"""
AI Module Router - سرویس هوش مصنوعی
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any, Optional

router = APIRouter(prefix="/ai", tags=["AI"])


class SoilAnalysisRequest(BaseModel):
    ph: Optional[float] = 7.0
    organic_carbon: Optional[float] = 2.0
    nitrogen: Optional[float] = 0.1


class WeatherAnalysisRequest(BaseModel):
    temperature: float
    humidity: float
    rainfall: float


class VegetationRequest(BaseModel):
    ndvi: float
    evi: float


class FarmPlanRequest(BaseModel):
    area_ha: float
    crop_type: str
    soil_data: Dict[str, Any]
    weather_data: Dict[str, Any]


class ChatRequest(BaseModel):
    message: str


@router.post("/analyze/soil")
async def analyze_soil(req: SoilAnalysisRequest):
    return ai_service.analyze_soil_conditions(req.dict())


@router.post("/analyze/weather")
async def analyze_weather(req: WeatherAnalysisRequest):
    return ai_service.analyze_weather_conditions(req.dict())


@router.post("/analyze/vegetation")
async def analyze_vegetation(req: VegetationRequest):
    return ai_service.analyze_vegetation(req.ndvi, req.evi)


@router.post("/analyze/farm-plan")
async def farm_plan(req: FarmPlanRequest):
    return ai_service.generate_farm_plan(req.area_ha, req.crop_type, req.soil_data, req.weather_data)


@router.post("/chat")
async def chat(req: ChatRequest):
    return {"response": ai_service.chat_response(req.message)}
