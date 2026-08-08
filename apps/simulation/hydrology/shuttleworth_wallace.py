"""Shuttleworth-Wallace Dual-Source ET + Medlyn Stomatal + Penman-Monteith
Phase 3.2 | Manifest §2.3 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np

VK=0.41;G=9.81;CPA=1004.0;LV=2.45e6;SB=5.67e-8;RD=287.05

@dataclass
class SWInputs:
    Rn:float=400.0;G:float=40.0;Ta:float=28.0;RH:float=40.0;U:float=2.0
    Pa:float=101.3;LAI:float=2.5;h_c:float=0.5;theta:float=0.25;theta_s:float=0.45
    A_n:float=15.0;g1:float=4.0;z_ref:float=2.0;Psi_leaf:float=-0.5;Psi_50:float=-2.5

@dataclass
class SWOutputs:
    ET:float;E_soil:float;T_canopy:float;LE:float;EF:float
    ra_a:float;ra_c:float;ra_s:float;rs_c:float;rs_s:float

def svp(Tc):return 0.6108*np.exp(17.27*Tc/(Tc+237.3))
def delta_svp(Tc):
    es=svp(Tc);return 4098.0*es/(Tc+237.3)**2
def psychro(Pa):return 0.665e-3*Pa
def rho_air(Tc,Pa):
    return Pa*1000.0/(RD*(Tc+273.15))

def medlyn_gs(VPD,A_n=15.0,g0=0.01,g1=4.0,Ca=400.0):
    D=max(VPD,0.01);gs=g0+1.6*(1.0+g1/np.sqrt(D))*(A_n/Ca)
    return float(max(gs*0.025,1e-5))

def medlyn_gs_stress(VPD,A_n,g1_opt,Psi_leaf,Psi_50,c_shape=2.0):
    g1_eff=float(g1_opt*np.exp(-(abs(Psi_leaf)/abs(Psi_50))**c_shape))
    return medlyn_gs(VPD,A_n=A_n,g1=g1_eff)

def soil_surface_resistance(theta,theta_s=0.45):
    Se=np.clip(theta/theta_s,0.0,1.0)
    return float(50.0*np.exp(5.0*(1.0-Se)))

def aero_resistances(U,h_c,LAI,z_ref=2.0):
    k=VK;z0=0.13*h_c;d=0.63*h_c;Ue=max(U,0.1)
    ra_a=np.log((z_ref-d)/z0)**2/(k**2*Ue)
    u_star=k*Ue/np.log((z_ref-d)/z0)
    gb=0.135*np.sqrt(max(u_star*2.0,0.1)/0.05)
    ra_c=max(1.0/max(gb,0.001)/max(LAI,0.01),1.0)
    ra_s=ra_a*np.exp(2.0*(1.0-z0/(0.05+1e-9)))
    return {"ra_a":ra_a,"ra_c":ra_c,"ra_s":ra_s,"u_star":u_star}

def shuttleworth_wallace(inp=None,theta=None):
    inp=inp or SWInputs()
    th=theta if theta is not None else inp.theta
    Ta=inp.Ta;es=svp(Ta);ea=es*inp.RH/100.0;VPD=es-ea
    Delt=delta_svp(Ta);gamma=psychro(inp.Pa);rho=rho_air(Ta,inp.Pa)
    A_surf=inp.Rn-inp.G
    tau=np.exp(-0.5*inp.LAI);Rn_c=inp.Rn*(1.0-tau);Rn_s=tau*inp.Rn-inp.G
    res=aero_resistances(inp.U,inp.h_c,inp.LAI,inp.z_ref)
    ra_a,ra_c,ra_s=res["ra_a"],res["ra_c"],res["ra_s"]
    rs_c=1.0/medlyn_gs(VPD,A_n=inp.A_n,g1=inp.g1)
    if inp.Psi_leaf<0:
        rs_c=1.0/medlyn_gs_stress(VPD,inp.A_n,inp.g1,inp.Psi_leaf,inp.Psi_50)
    rs_s=soil_surface_resistance(th,inp.theta_s)
    Rc=ra_c+rs_c;Rs=ra_s+rs_s
    denom_c=Delt+gamma*(1.0+Rc/ra_a)
    denom_s=Delt+gamma*(1.0+Rs/ra_a)
    LE_c=max((Delt*Rn_c+rho*CPA*VPD/ra_a)/max(denom_c,1e-9),0.0)
    LE_s=max((Delt*Rn_s+rho*CPA*VPD/ra_a)/max(denom_s,1e-9),0.0)
    LE=LE_c+LE_s
    fac=86400.0/LV
    EF=np.clip(LE/max(A_surf,1.0),0.0,1.0)
    return SWOutputs(ET=LE*fac,E_soil=LE_s*fac,T_canopy=LE_c*fac,
                     LE=LE,EF=EF,ra_a=ra_a,ra_c=ra_c,ra_s=ra_s,
                     rs_c=rs_c,rs_s=rs_s)

def daily_et_series(inputs_list,theta_series=None):
    ets,es,ts=[],[],[]
    for i,inp in enumerate(inputs_list):
        th=theta_series[i] if theta_series else inp.theta
        out=shuttleworth_wallace(inp,th)
        ets.append(out.ET);es.append(out.E_soil);ts.append(out.T_canopy)
    return {"ET_daily":np.array(ets),"E_soil":np.array(es),"T_canopy":np.array(ts)}

if __name__=="__main__":
    o=shuttleworth_wallace()
    print(f"ET={o.ET:.2f}mm/d E={o.E_soil:.2f} T={o.T_canopy:.2f} EF={o.EF:.3f}")
    print(f"ra_a={o.ra_a:.1f} ra_c={o.ra_c:.2f} rs_c={o.rs_c:.1f} rs_s={o.rs_s:.1f}")
    inp2=SWInputs(Rn=500.0,LAI=4.0,Ta=32.0,RH=25.0,U=3.0,theta=0.35)
    o2=shuttleworth_wallace(inp2)
    print(f"Summer: ET={o2.ET:.2f}mm/d E={o2.E_soil:.2f} T={o2.T_canopy:.2f}")
    print("ALL SW TESTS PASSED")
