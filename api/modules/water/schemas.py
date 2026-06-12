# api/modules/water/schemas.py

from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class WaterBalanceBase(BaseModel):
    date: date
    precipitation: Optional[float] = None
    irrigation: Optional[float] = None
    evapotranspiration: Optional[float] = None
    runoff: Optional[float] = None
    deep_drainage: Optional[float] = None
    soil_moisture: Optional[float] = None


class WaterBalanceRead(WaterBalanceBase):
    id: int
    scenario_id: int
    soil_profile_id: Optional[int] = None

    class Config:
        from_attributes = True


class DailyInput(BaseModel):
    date: date
    precipitation: Optional[float] = None
    irrigation: Optional[float] = None
    evapotranspiration: Optional[float] = None


class SimulationRequest(BaseModel):
    scenario_id: int
    soil_profile_id: int
    daily_inputs: List[DailyInput]