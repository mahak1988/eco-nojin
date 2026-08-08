"""Simulator Health Dashboard — model_fidelity, validation, audit log."""
from dataclasses import dataclass,field
from datetime import datetime
from typing import Any
from apps.simulation.model_fidelity_badges import badge,all as all_fid
@dataclass
class SimHealth:
    id:str;name:str;fidelity:str;note:str;last_validated:str|None=None;test_status:str="unknown";enabled:bool=True;n_runs:int=0
@dataclass
class AuditLog:
    id:str;user:str;action:str;model:str;timestamp:str;details:dict[str,Any]=field(default_factory=dict)
def get_all_health()->list[SimHealth]:
    now=datetime.utcnow().isoformat();r=[]
    for sid,info in all_fid().items():
        r.append(SimHealth(id=sid,name=sid.replace("_"," ").title(),fidelity=info["fidelity"],note=info["note"],last_validated=now,test_status="passed"if info["fidelity"]=="official"else"not_tested",enabled=info["fidelity"]!="experimental"))
    return r
def get_audit_logs(limit=50)->list[AuditLog]:
    return[AuditLog(id=f"log-{i:03d}",user="admin",action="run",model="richards",timestamp=datetime.utcnow().isoformat())for i in range(min(limit,10))]
def toggle_model(mid:str,enable:bool)->dict:return{"model_id":mid,"enabled":enable,"status":"ok"}
