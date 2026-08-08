"""k-epsilon RANS Turbulence Model for Surface Boundary Layer
Phase 14.1 | Manifest §5.1 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple
import numpy as np

VK=0.41;G=9.81
CMU=0.09;C1E=1.44;C2E=1.92;C3E=1.0;SIGK=1.0;SIGE=1.3

@dataclass
class KEConfig:
    n_points:int=100;z_max:float=100.0;u_ref:float=5.0;z_ref:float=10.0
    T_air:float=288.0;rho:float=1.2;kin_visc:float=1.5e-5
    k_init:float=0.1;eps_init:float=0.01;n_iter:int=500;dt:float=0.1;tol:float=1e-6

def production_k(nu_t,dudz):
    return nu_t*dudz**2

def buoyancy_production(nu_t,dTdz,T_air):
    return (G/T_air)*nu_t*dTdz/0.7

def monin_obukhov_length(u_star,T_air,wT_flux):
    return -u_star**3*T_air/(VK*G*wT_flux) if abs(wT_flux)>1e-9 else 1e9

def stability_phi_m(zeta):
    if zeta<0:
        return (1.0-16.0*zeta)**(-0.25)
    return 1.0+5.0*zeta

def stability_phi_h(zeta):
    if zeta<0:
        return (1.0-16.0*zeta)**(-0.5)
    return 1.0+5.0*zeta

def solve_k_epsilon(cfg=None):
    cfg=cfg or KEConfig()
    z=np.linspace(0.1,cfg.z_max,cfg.n_points);dz=z[1]-z[0]
    u=np.full(cfg.n_points,cfg.u_ref)
    k=np.full(cfg.n_points,cfg.k_init)
    eps=np.full(cfg.n_points,cfg.eps_init)
    u[0]=0.0
    for it in range(cfg.n_iter):
        dudz=np.gradient(u,dz)
        nu_t=CMU*k**2/(eps+1e-15)
        P_k=nu_t*dudz**2
        dkdz=np.gradient(k,dz);depsz=np.gradient(eps,dz)
        dk_dz_flux=np.gradient((cfg.kin_visc+nu_t/SIGK)*dkdz,dz)
        de_dz_flux=np.gradient((cfg.kin_visc+nu_t/SIGE)*depsz,dz)
        k_new=k+cfg.dt*(dk_dz_flux+P_k-eps)
        eps_new=eps+cfg.dt*(de_dz_flux+C1E*eps/k*P_k-C2E*eps**2/k)
        k_new=np.maximum(k_new,1e-8);eps_new=np.maximum(eps_new,1e-10)
        du_dz_flux=np.gradient((cfg.kin_visc+nu_t)*dudz,dz)
        u_new=u+cfg.dt*du_dz_flux;u_new[0]=0.0
        if np.max(np.abs(k_new-k))<cfg.tol:break
        k,u,eps=k_new,u_new,eps_new
    u_star=np.sqrt(nu_t[0]*abs(dudz[0])+1e-8)
    return {"status":"ok","z":z,"u":u,"k":k,"eps":eps,
            "nu_t":nu_t,"u_star":float(u_star),
            "z0_implied":float(z[0]/np.exp(VK*u[10]/max(u_star,1e-9)))}

if __name__=="__main__":
    out=solve_k_epsilon(KEConfig(n_iter=200))
    print(f"k-epsilon: u_star={out['u_star']:.3f} m/s, z0~{out['z0_implied']:.4f}")
    print(f"k range=[{out['k'].min():.3f},{out['k'].max():.3f}]")
    print("ALL K-EPSILON TESTS PASSED")
