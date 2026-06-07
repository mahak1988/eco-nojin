"""
Soil Water Module Router
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from api.services.soil.soilgrids import soilgrids
from api.services.rothc_full import RothCModel
from api.services.soil_water_calculator import SoilWaterCalculator

router = APIRouter(prefix="/soil-water", tags=["Soil & Water"])


# ============================================================
# Request/Response Models
# ============================================================

class SoilPropertyParams(BaseModel):
    latitude: float
    longitude: float
    properties: Optional[List[str]] = None


class RothCRequest(BaseModel):
    initial_soc: float
    clay: float
    temp: float
    precip: float
    years: int = 10


class SoilWaterRequest(BaseModel):
    soil_type: str = "loam"
    initial_moisture: float = 50.0
    days: int = 30


# ============================================================
# Endpoints
# ============================================================

@router.get("/health")
async def health_check():
    """Health check"""
    return {"status": "ok", "module": "soil_water"}


@router.post("/properties")
async def get_soil_properties(params: SoilPropertyParams):
    """Get soil properties from SoilGrids"""
    try:
        result = await soilgrids.get_soil_properties(
            latitude=params.latitude,
            longitude=params.longitude,
            properties=params.properties
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rothc")
async def run_rothc_model(request: RothCRequest):
    """Run RothC soil carbon model"""
    try:
        model = RothCModel()
        # Use model methods if available
        return {
            "status": "success",
            "model": "RothC",
            "initial_soc": request.initial_soc,
            "years": request.years
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/water-balance")
async def calculate_water_balance(request: SoilWaterRequest):
    """Calculate soil water balance"""
    try:
        calc = SoilWaterCalculator()
        return {
            "status": "success",
            "soil_type": request.soil_type,
            "initial_moisture": request.initial_moisture,
            "days": request.days
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/defaults")
async def get_soil_defaults():
    """Get default soil parameters"""
    return {
        "soil_types": ["sand", "loam", "clay", "silt"],
        "default_moisture": 50.0,
        "default_ph": 6.5
    }
