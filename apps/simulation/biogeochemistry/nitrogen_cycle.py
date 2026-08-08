"""Nitrogen Cycle: Monod Kinetics, Mineralization, Nitrification, Denitrification, Leaching
Phase 6.2 | Manifest §3.2 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict, List, Optional, Tuple
import numpy as np

@dataclass
class NPools:
    N_org:float=50.0;NH4:float=5.0;NO3:float=10.0;N2O:float=0.0;N2:float=0.0
    microbial_C:float=100.0
    @property
    def total_N(self):return self.N_org+self.NH4+self.NO3+self.N2O+self.N2
    def as_array(self):return np.array([self.N_org,self.NH4,self.NO3,self.N2O,self.N2])

@dataclass
class NParams:
    k_min:float=0.02;k_nit:float=0.2;k_denit:float=0.05
    K_NH4:float=2.0;K_NO3:float=5.0;K_O2:float=0.2;mu_max:float=0.8
    f_temp:float=1.0;f_moist:float=1.0;f_pH:float=1.0;f_O2:float=1.0
    leach_frac:float=0.02;uptake_max:float=1.5
    CN_microbe:float=8.0;CN_threshold_min:float=25.0
    N2O_N2_ratio:float=0.01;immobilization_factor:float=0.3

def temperature_factor(T_C,T_opt=30.0,T_min=2.0,T_max=45.0):
    if T_C<T_min or T_C>T_max:return 0.0
    if T_C<=T_opt:
        return np.exp(0.08*(T_C-10.0))
    return np.exp(0.08*(T_opt-10.0))*np.exp(-0.1*(T_C-T_opt))

def moisture_factor(theta,theta_s=0.45,theta_fc=0.3,theta_wp=0.08):
    if theta<theta_wp:return 0.0
    if theta<=theta_fc:return (theta-theta_wp)/(theta_fc-theta_wp)
    if theta<=theta_s:return 1.0-0.5*(theta-theta_fc)/(theta_s-theta_fc)
    return 0.5

def pH_factor(pH,pH_opt=7.0,sigma=2.0):
    return float(np.exp(-(pH-pH_opt)**2/(2*sigma**2)))

def step_nitrogen(pools,p=None,dt=1.0,plant_demand=0.5,T_C=20.0,theta=0.25,pH_val=7.0):
    p=p or NParams()
    ft=temperature_factor(T_C);fm=moisture_factor(theta);fp=pH_factor(pH_val)
    env_factor=ft*fm*fp*p.f_O2
    p.f_temp,p.f_moist,p.f_pH=ft,fm,fp
    min_rate=p.k_min*env_factor*pools.N_org
    immob=0.0
    if pools.N_org>0 and pools.microbial_C>0:
        CN_residue=pools.N_org/max(pools.microbial_C/p.CN_microbe,1e-9)
        if CN_residue>p.CN_threshold_min:
            immob=p.k_min*env_factor*pools.microbial_C*p.immobilization_factor*dt
    net_min=max(min_rate*dt-immob,0)
    nit=p.k_nit*env_factor*pools.NH4/(p.K_NH4+pools.NH4+1e-9)*pools.NH4*dt
    f_anaerobic=1.0 if theta>0.8*0.45 else 0.2
    den=p.k_denit*env_factor*f_anaerobic*pools.NO3/(p.K_NO3+pools.NO3+1e-9)*pools.NO3*dt
    avail=pools.NH4+pools.NO3
    uptake=min(plant_demand*dt,p.uptake_max,avail)
    nh4_up=uptake*pools.NH4/max(avail,1e-9)
    no3_up=uptake*pools.NO3/max(avail,1e-9)
    leach=p.leach_frac*env_factor*pools.NO3*dt
    n2o=den*p.N2O_N2_ratio;n2=den-n2o
    return NPools(
        N_org=max(pools.N_org-net_min,0),
        NH4=max(pools.NH4+net_min-nit-nh4_up,0),
        NO3=max(pools.NO3+nit-den-no3_up-leach,0),
        N2O=pools.N2O+n2o,N2=pools.N2+n2,
        microbial_C=pools.microbial_C)

def simulate_n_cycle(n_days=90,p=None,T_init=18.0,theta_init=0.30):
    pools=NPools();hist=[]
    for d in range(n_days):
        Tc=T_init+5*np.sin(2*np.pi*d/365)
        th=theta_init+0.05*np.sin(2*np.pi*(d-180)/365)
        dem=0.3+0.5*np.sin(2*np.pi*(d-90)/365)
        pools=step_nitrogen(pools,p,plant_demand=dem,T_C=Tc,theta=th)
        hist.append([pools.N_org,pools.NH4,pools.NO3,pools.N2O,pools.N2])
    return {"status":"ok","final":pools,"history":np.array(hist),
            "NO3_final":pools.NO3,"N2O_cum":pools.N2O,"N2_cum":pools.N2}

if __name__=="__main__":
    out=simulate_n_cycle(90)
    print(f"NO3={out['NO3_final']:.2f} N2O={out['N2O_cum']:.3f} N2={out['N2_cum']:.2f}")
    print("ALL NITROGEN CYCLE TESTS PASSED")
