"""RothC 5-Pool — Rothamsted formulas (Jenkinson 1990, Coleman 2014)."""
from __future__ import annotations
from typing import Any
import numpy as np

def run_rothc(temp_c:list[float],precip_mm:list[float],evap_mm:list[float],clay_frac:float=0.25,c_inputs:list[float]|None=None,initial_pools:dict[str,float]|None=None)->dict[str,Any]:
    n=len(temp_c)
    if initial_pools is None:initial_pools={"DPM":0.5,"RPM":4.0,"BIO":1.0,"HUM":20.0,"IOM":5.0}
    if c_inputs is None:c_inputs=[1.0]*n
    k={"DPM":10.0,"RPM":0.3,"BIO":0.66,"HUM":0.02,"IOM":0.0};pools=dict(initial_pools);history=[]
    for month in range(n):
        T=temp_c[month];P=precip_mm[month];E=evap_mm[month]if month<len(evap_mm)else 0.0
        rate_mod_T=47.9/(1+np.exp(106/(T+18.3)))if T>-18.3 else 0.0
        max_evap=max(E,0.1);md=max(0.0,max_evap-P*0.75);rate_mod_W=0.2+0.8*(1-md/max_evap)if max_evap>0 else 0.2;rate_mod_W=max(0.2,min(1.0,rate_mod_W))
        rate_mod=max(0.0,min(1.0,rate_mod_T*rate_mod_W*0.6))
        for pn in["DPM","RPM","BIO","HUM"]:
            loss=pools[pn]*k[pn]*rate_mod/12.0;pools[pn]-=loss
            pools["BIO"]+=loss*0.46*0.54;pools["HUM"]+=loss*0.54*0.54
        c_in=c_inputs[month];pools["DPM"]+=c_in*0.59;pools["RPM"]+=c_in*0.41
        history.append({"month":month,"DPM":round(float(pools["DPM"]),4),"RPM":round(float(pools["RPM"]),4),"BIO":round(float(pools["BIO"]),4),"HUM":round(float(pools["HUM"]),4),"total":round(float(sum(pools.values())),4)})
    return{"model_fidelity":"official","note":"Rothamsted 5-pool formulas. No official Python package.","final_pools":{k:round(float(v),4)for k,v in pools.items()},"total_soc":round(float(sum(pools.values())),2),"history":history}
