"""Saved Runs — Zero Trust: user_id locked to current_user."""
import uuid
from datetime import datetime
from fastapi import APIRouter,Depends,HTTPException,Query
from pydantic import BaseModel,Field
from sqlalchemy import desc,select
from sqlalchemy.ext.asyncio import AsyncSession
from apps.shared_core.database.session import get_db_session
from apps.shared_core.security import get_current_user
from apps.simulation.runs.models import SimulationRun
import logging
router=APIRouter(prefix="/api/v1/simulation/runs",tags=["Saved Runs"])
async def _ensure_table(db:AsyncSession):
    try:bind=db.get_bind();async with bind.begin() as conn:await conn.run_sync(SimulationRun.metadata.create_all)
    except Exception as e:logging.getLogger(__name__).debug("Table skip: %s",e)
class RunCreate(BaseModel):simulator_id:str;simulator_name:str="";parameters:dict=Field(default_factory=dict);metrics:dict=Field(default_factory=dict);advisory:dict=Field(default_factory=dict);scenario_name:str|None=None;note:str|None=Field(None,max_length=1000)
def _to_dict(r:SimulationRun)->dict:return{"id":r.id,"user_id":r.user_id,"simulator_id":r.simulator_id,"simulator_name":r.simulator_name,"parameters":r.parameters,"metrics":r.metrics,"advisory":r.advisory,"scenario_name":r.scenario_name,"note":r.note,"created_at":r.created_at.isoformat()if r.created_at else None}
@router.post("")
async def save_run(data:RunCreate,db:AsyncSession=Depends(get_db_session),current_user:dict=Depends(get_current_user))->dict:
    await _ensure_table(db);run=SimulationRun(id=str(uuid.uuid4()),user_id=current_user["id"],simulator_id=data.simulator_id,simulator_name=data.simulator_name,parameters=data.parameters,metrics=data.metrics,advisory=data.advisory,scenario_name=data.scenario_name,note=data.note,created_at=datetime.utcnow())
    db.add(run);await db.commit();return{"id":run.id,"status":"saved"}
@router.get("")
async def list_runs(simulator_id:str|None=Query(None),limit:int=Query(50,ge=1,le=200),db:AsyncSession=Depends(get_db_session),current_user:dict=Depends(get_current_user))->dict:
    q=select(SimulationRun).where(SimulationRun.user_id==current_user["id"]).order_by(desc(SimulationRun.created_at)).limit(limit)
    if simulator_id:q=q.where(SimulationRun.simulator_id==simulator_id)
    res=await db.execute(q);runs=res.scalars().all();return{"total":len(runs),"runs":[_to_dict(r)for r in runs]}
@router.get("/{run_id}")
async def get_run(run_id:str,db:AsyncSession=Depends(get_db_session),current_user:dict=Depends(get_current_user))->dict:
    await _ensure_table(db);run=await db.get(SimulationRun,run_id)
    if not run:raise HTTPException(404,"Run not found")
    if run.user_id!=current_user["id"]:raise HTTPException(403,"Not your run")
    return _to_dict(run)
@router.delete("/{run_id}")
async def delete_run(run_id:str,db:AsyncSession=Depends(get_db_session),current_user:dict=Depends(get_current_user))->dict:
    await _ensure_table(db);run=await db.get(SimulationRun,run_id)
    if not run:raise HTTPException(404,"Run not found")
    if run.user_id!=current_user["id"]:raise HTTPException(403,"Not your run")
    await db.delete(run);await db.commit();return{"status":"deleted","id":run_id}
class RunUpdate(BaseModel):advisory:dict|None=None;scenario_name:str|None=None;note:str|None=Field(None,max_length=1000)
@router.patch("/{run_id}")
async def update_run(run_id:str,data:RunUpdate,db:AsyncSession=Depends(get_db_session),current_user:dict=Depends(get_current_user))->dict:
    await _ensure_table(db);run=await db.get(SimulationRun,run_id)
    if not run:raise HTTPException(404,"Run not found")
    if run.user_id!=current_user["id"]:raise HTTPException(403,"Not your run")
    for f,v in data.model_dump(exclude_unset=True).items():setattr(run,f,v)
    await db.commit();return{"status":"updated","id":run_id}
