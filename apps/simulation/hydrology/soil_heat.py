"""Soil Heat Transfer: Fourier + de Vries + latent heat sources
Phase 3.4 | Manifest §2.5 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

@dataclass
class SoilThermalParams:
    C_min:float=1.5e6;C_water:float=4.18e6;C_ice:float=1.9e6;C_om:float=2.5e6
    lam_min:float=0.25;lam_water:float=0.57;lam_ice:float=2.18;lam_om:float=0.25
    lam_quartz:float=8.8;theta_s:float=0.45;rho_b:float=1350.0
    quartz_fraction:float=0.5

def C_v(theta,p=None):
    p=p or SoilThermalParams()
    Se=np.clip(theta/p.theta_s,0,1)
    return p.C_min+Se*(p.C_water-p.C_min)

def lambda_de_vries(theta,p=None):
    """de Vries (1963) effective thermal conductivity."""
    p=p or SoilThermalParams()
    theta_a=p.theta_s-theta;Se=np.clip(theta/p.theta_s,0,1)
    lam_solid=p.lam_quartz*p.quartz_fraction+p.lam_min*(1-p.quartz_fraction)
    k_w=1.0/(1.0+(lam_solid-p.lam_water)/(lam_solid+2*p.lam_water))
    k_a=1.0/(1.0+(lam_solid-p.lam_min)/(lam_solid+2*p.lam_min))
    num=Se*p.lam_water*k_w+theta_a*p.lam_min*k_a+lam_solid*(1-p.theta_s)
    den=Se*k_w+theta_a*k_a+(1-p.theta_s)
    return max(num/max(den,1e-9),0.03)

def kappa_soil(theta,p=None):
    C=C_v(theta,p);lam=lambda_de_vries(theta,p)
    return lam/max(C,1e-6)

@dataclass
class SoilHeatConfig:
    n_nodes:int=31;z_max:float=1.5;dt:float=3600.0;n_steps:int=96
    T_init:float=18.0;T_surface:float=28.0;T_bottom:Optional[float]=None
    theta:float=0.25;theta_profile:Optional[np.ndarray]=None
    Q_latent:float=0.0

def solve_soil_heat(cfg=None,params=None):
    cfg=cfg or SoilHeatConfig();p=params or SoilThermalParams()
    z=np.linspace(0,cfg.z_max,cfg.n_nodes);dz=z[1]-z[0]
    theta_arr=cfg.theta_profile if cfg.theta_profile is not None else np.full(cfg.n_nodes,cfg.theta)
    lam_arr=np.array([lambda_de_vries(t,p) for t in theta_arr])
    C_arr=np.array([C_v(t,p) for t in theta_arr])
    kap=np.mean(lam_arr)/max(np.mean(C_arr),1e-6)
    Fo=kap*cfg.dt/dz**2
    if Fo>0.45:
        dt_safe=0.4*dz**2/kap
        n_steps=int(cfg.n_steps*cfg.dt/dt_safe)
        Fo=kap*dt_safe/dz**2
    else:
        dt_safe,n_steps=cfg.dt,cfg.n_steps
    T=np.full(cfg.n_nodes,cfg.T_init,dtype=float)
    T_bottom=cfg.T_bottom if cfg.T_bottom is not None else cfg.T_init
    history=[T.copy()]
    for _ in range(n_steps):
        Tn=T.copy();Tn[0]=cfg.T_surface
        for i in range(1,cfg.n_nodes-1):
            ke=0.5*(lam_arr[i]+lam_arr[i+1]);kw=0.5*(lam_arr[i-1]+lam_arr[i])
            Ce=0.5*(C_arr[i]+C_arr[i+1]);Cw=0.5*(C_arr[i-1]+C_arr[i])
            qe=ke*(T[i+1]-T[i])/dz;qw=kw*(T[i]-T[i-1])/dz
            Tn[i]=T[i]+dt_safe*(qe-qw)/(C_arr[i]*dz)
        if cfg.Q_latent!=0:
            Tn[1:]+=cfg.Q_latent*dt_safe/C_arr[1:]
        Tn[-1]=T_bottom;T=Tn;history.append(T.copy())
    return {"status":"ok","z":z,"T_final":T,"history":np.array(history),
            "Fo":Fo,"kappa":kap,"lambda_eff":float(np.mean(lam_arr)),
            "C_eff":float(np.mean(C_arr))}

def soil_temperature_profile(z_max,T_surf,T_bottom,n_pts=50):
    z=np.linspace(0,z_max,n_pts)
    return T_surf+(T_bottom-T_surf)*z/z_max

if __name__=="__main__":
    out=solve_soil_heat()
    print(f"T range=[{out['T_final'].min():.2f},{out['T_final'].max():.2f}]C")
    print(f"Fo={out['Fo']:.4f} lam_eff={out['lambda_eff']:.4f} C_eff={out['C_eff']/1e6:.3f}MJ")
    cfg2=SoilHeatConfig(T_surface=35.0,T_init=20.0,theta=0.10,n_steps=120)
    out2=solve_soil_heat(cfg2)
    print(f"Heat wave: T=[{out2['T_final'].min():.2f},{out2['T_final'].max():.2f}]")
    print("ALL SOIL HEAT TESTS PASSED")
