"""Scenario API — Zero Trust auth: Depends(get_current_user) on all write/private endpoints."""
from __future__ import annotations
import logging, uuid
from datetime import datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from apps.shared_core.database.session import get_db_session
from apps.shared_core.security import get_current_user
from apps.simulation.registry import SimulationRegistry
from apps.simulation.scenario.models import PRESET_SCENARIOS, ComparisonSession, ModelChain, Scenario, ScenarioResult
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/simulation", tags=["Scenario & Comparison"])
class ScenarioCreate(BaseModel):
    name:str=Field(...,min_length=1,max_length=255);description:str|None=None;simulator_id:str
    base_params:dict[str,Any]=Field(default_factory=dict);scenario_params:dict[str,Any]=Field(default_factory=dict)
    category:str|None=None;is_preset:bool=False
class ScenarioResponse(BaseModel):
    id:str;name:str;description:str|None;simulator_id:str
    base_params:dict[str,Any];scenario_params:dict[str,Any]
    category:str|None;is_preset:bool;created_at:str;model_fidelity:str="simplified"
FIDELITY={"aquacrop":"official","rothc":"official"}
def _fid(s:str)->str:return FIDELITY.get(s,"simplified")
@router.post("/scenarios",response_model=ScenarioResponse,status_code=201)
async def create_scenario(data:ScenarioCreate,db:AsyncSession=Depends(get_db_session),current_user:dict=Depends(get_current_user))->ScenarioResponse:
    sim=SimulationRegistry.get(data.simulator_id)
    if not sim:raise HTTPException(404,f"Simulator '{data.simulator_id}' not found")
    s=Scenario(id=uuid.uuid4(),user_id=current_user["id"],name=data.name,description=data.description,simulator_id=data.simulator_id,base_params=data.base_params,scenario_params=data.scenario_params,category=data.category,is_preset=data.is_preset)
    db.add(s);await db.commit();await db.refresh(s)
    return ScenarioResponse(id=str(s.id),name=s.name,description=s.description,simulator_id=s.simulator_id,base_params=s.base_params,scenario_params=s.scenario_params,category=s.category,is_preset=s.is_preset,created_at=s.created_at.isoformat(),model_fidelity=_fid(data.simulator_id))
@router.get("/scenarios",response_model=list[ScenarioResponse])
async def list_scenarios(simulator_id:str|None=Query(None),category:str|None=Query(None),db:AsyncSession=Depends(get_db_session),current_user:dict=Depends(get_current_user))->list[ScenarioResponse]:
    q=select(Scenario).where(Scenario.user_id==current_user["id"]).order_by(Scenario.created_at.desc())
    if simulator_id:q=q.where(Scenario.simulator_id==simulator_id)
    if category:q=q.where(Scenario.category==category)
    res=await db.execute(q);sc=res.scalars().all()
    return[ScenarioResponse(id=str(x.id),name=x.name,description=x.description,simulator_id=x.simulator_id,base_params=x.base_params,scenario_params=x.scenario_params,category=x.category,is_preset=x.is_preset,created_at=x.created_at.isoformat(),model_fidelity=_fid(x.simulator_id))for x in sc]
@router.delete("/scenarios/{scenario_id}",status_code=204)
async def delete_scenario(scenario_id:str,db:AsyncSession=Depends(get_db_session),current_user:dict=Depends(get_current_user))->None:
    res=await db.execute(select(Scenario).where(Scenario.id==uuid.UUID(scenario_id)))
    s=res.scalar_one_or_none()
    if not s:raise HTTPException(404,"Scenario not found")
    if s.user_id!=current_user["id"]:raise HTTPException(403,"Not your scenario")
    await db.delete(s);await db.commit()
# Public presets (no auth needed)
@router.get("/presets/{simulator_id}")
async def get_preset_scenarios(simulator_id:str)->dict:return{"simulator_id":simulator_id,"scenarios":PRESET_SCENARIOS.get(simulator_id,[])}
@router.get("/presets")
async def get_all_presets()->list[dict]:return[{"simulator_id":k,"scenarios":v}for k,v in PRESET_SCENARIOS.items()]
