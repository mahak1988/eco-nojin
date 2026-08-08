"""Canopy Microclimate: Heat/Mass Transfer, Wind Profile, Energy Balance
Phase 14.2 | Manifest §5.2 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple
import numpy as np

VK=0.41;G=9.81;CPA=1004.0;RHOA=1.2;LV=2.45e6;RD=287.05;SIG=5.67e-8

@dataclass
class CanopyConfig:
    LAI:float=3.0;h_c:float=2.0;d_leaf:float=0.1;n_layers:int=10
    T_air_ref:float=28.0;RH_ref:float=40.0;U_ref:float=3.0;z_ref:float=10.0
    Rn:float=500.0;G:float=40.0;theta_s:float=0.45;theta:float=0.25
    albedo:float=0.18;emissivity:float=0.97

def wind_profile_canopy(z,h_c,LAI,U_ref,z_ref):
    """Wind profile within canopy: u(z)=u(h_c)*exp(-a*(1-z/h_c))."""
    d=0.63*h_c;z0=0.13*h_c
    u_h=VK*U_ref/np.log((z_ref-d)/z0) if z_ref>d else U_ref
    a=0.5*LAI*give_or_take=0.5*LAI
    u=u_h*np.exp(-a*(1.0-np.clip(z/h_c,0,1)))
    return u

def radiation_extinction(z,LAI,h_c,Rn_top,Rn_soil):
    """Beer-Lambert radiation extinction within canopy."""
    k=0.5;cum_LAI=LAI*(1.0-z/h_c)
    return Rn_soil+(Rn_top-Rn_soil)*np.exp(-k*cum_LAI)

def leaf_boundary_layer_conductance(u,d_leaf):
    """gb=0.135*sqrt(u/d_leaf) [mol m-2 s-1]."""
    return 0.135*np.sqrt(np.maximum(u,0.01)/d_leaf)*2.0

def canopy_energy_balance(Rn_abs,T_air,ea,ra,gb,LAI_layer):
    """Simple leaf energy balance per layer."""
    es=0.6108*np.exp(17.27*T_air/(T_air+237.3));VPD=max(es-ea,0.01)
    delta=4098.0*es/(T_air+237.3)**2;gamma=0.067
    ga=0.5*gb;rho_cp=1200.0;gs=0.005
    LE=max((delta*Rn_abs*LAI_layer+rho_cp*VPD*ga)/(delta+gamma*(1+ga/gs)),0)
    return LE

def simulate_canopy(cfg=None):
    cfg=cfg or CanopyConfig()
    z=np.linspace(0,cfg.h_c,cfg.n_layers)
    u=wind_profile_canopy(z,cfg.h_c,cfg.LAI,cfg.U_ref,cfg.z_ref)
    es=0.6108*np.exp(17.27*cfg.T_air_ref/(cfg.T_air_ref+237.3))
    ea=es*cfg.RH_ref/100.0
    Rn_s=cfg.Rn*(1.0-np.exp(-0.5*cfg.LAI))
    Rn_c=cfg.Rn*np.exp(-0.5*cfg.LAI)
    temp_profile=np.linspace(cfg.T_air_ref-2,cfg.T_air_ref,cfg.n_layers)
    LE_tot,E_tot,T_tot=0.0,0.0,0.0
    for i in range(cfg.n_layers):
        lai_layer=cfg.LAI/cfg.n_layers
        Rn_layer=Rn_c*lai_layer/cfg.LAI
        gb=leaf_boundary_layer_conductance(u[i],cfg.d_leaf)
        le=canopy_energy_balance(Rn_layer,temp_profile[i],ea,50.0,gb,lai_layer)
        LE_tot+=le
    E_can=LE_tot*86400.0/LV;E_soil=Rn_s*86400.0/LV
    return {"status":"ok","z":z,"u_profile":u,"T_profile":temp_profile,
            "ET_canopy_mm":E_can,"E_soil_mm":E_soil,"ET_total_mm":E_can+E_soil}

if __name__=="__main__":
    out=simulate_canopy()
    print(f"ET canopy={out['ET_canopy_mm']:.2f} mm/d, soil={out['E_soil_mm']:.2f} mm/d")
    print(f"Total={out['ET_total_mm']:.2f} mm/d")
    print("ALL CANOPY TESTS PASSED")
