# api/modules/soil/schemas.py

from typing import List, Optional
from pydantic import BaseModel


class SoilLayerBase(BaseModel):
    depth_top_cm: float
    depth_bottom_cm: float
    bulk_density: Optional[float] = None
    field_capacity: Optional[float] = None
    wilting_point: Optional[float] = None
    saturated_hydraulic_conductivity: Optional[float] = None
    organic_carbon: Optional[float] = None


class SoilLayerCreate(SoilLayerBase):
    pass


class SoilLayerRead(SoilLayerBase):
    id: int

    class Config:
        from_attributes = True


class SoilProfileBase(BaseModel):
    name: str
    description: Optional[str] = None


class SoilProfileCreate(SoilProfileBase):
    project_id: int
    layers: List[SoilLayerCreate]


class SoilProfileRead(SoilProfileBase):
    id: int
    layers: List[SoilLayerRead]

    class Config:
        from_attributes = True