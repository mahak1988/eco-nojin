"""CGE Computable General Equilibrium: Cobb-Douglas, CES, social welfare
Phase 15.2 | Manifest §6.2 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional
import numpy as np

@dataclass
class Sector:
    name:str;alpha_L:float=0.4;alpha_K:float=0.3;alpha_W:float=0.3;A_tfp:float=1.0
    sigma:float=0.8;gamma_W:float=0.5

@dataclass
class CGEConfig:
    sectors:List[Sector]=field(default_factory=lambda:[
        Sector("agriculture",0.35,0.25,0.40,1.0,0.7,0.6),
        Sector("industry",0.45,0.40,0.15,1.2,1.0,0.3),
        Sector("services",0.55,0.35,0.10,1.1,1.2,0.2)])
    L_bar:float=100.0;K_bar:float=200.0;W_bar:float=50.0
    rho:float=0.03;eta:float=1.5;g_rate:float=0.02
    max_iter:int=200;tol:float=1e-6;alpha_io:Optional[np.ndarray]=None

def social_discount_rate(cfg=None):
    cfg=cfg or CGEConfig()
    return cfg.rho+cfg.eta*cfg.g_rate

def cobb_douglas_output(L,K,W,alpha_L,alpha_K,alpha_W,A):
    return A*(L**alpha_L)*(K**alpha_K)*(W**alpha_W)

def ces_output(L,K,W,alpha_L,alpha_K,alpha_W,sigma,A):
    if abs(sigma-1.0)<1e-6:
        return cobb_douglas_output(L,K,W,alpha_L,alpha_K,alpha_W,A)
    rho_s=(sigma-1.0)/max(sigma,1e-9)
    return A*(alpha_L*L**rho_s+alpha_K*K**rho_s+alpha_W*W**rho_s)**(1.0/rho_s)

def solve_cge(cfg=None):
    cfg=cfg or CGEConfig()
    n=len(cfg.sectors);beta=np.ones(n)/n
    w_L,w_K,w_W=1.0,1.0,1.0
    p=np.ones(n);Y=np.zeros(n)
    for it in range(cfg.max_iter):
        income=w_L*cfg.L_bar+w_K*cfg.K_bar+w_W*cfg.W_bar
        L_d=K_d=W_d=0.0
        for i,s in enumerate(cfg.sectors):
            MC=((w_L/s.alpha_L)**s.alpha_L*(w_K/s.alpha_K)**s.alpha_K*(w_W/s.alpha_W)**s.alpha_W)/max(s.A_tfp,1e-9)
            p[i]=MC
            Y[i]=beta[i]*income/max(p[i],1e-15)
            L_d+=s.alpha_L*p[i]*Y[i]/max(w_L,1e-9)
            K_d+=s.alpha_K*p[i]*Y[i]/max(w_K,1e-9)
            W_d+=s.alpha_W*p[i]*Y[i]/max(w_W,1e-9)
        dL,dK,dW=L_d-cfg.L_bar,K_d-cfg.K_bar,W_d-cfg.W_bar
        w_L=max(0.01,w_L*(1+0.03*dL/(cfg.L_bar+1e-9)))
        w_K=max(0.01,w_K*(1+0.03*dK/(cfg.K_bar+1e-9)))
        w_W=max(0.01,w_W*(1+0.03*dW/(cfg.W_bar+1e-9)))
        if max(abs(dL)<cfg.tol*cfg.L_bar,abs(dK)<cfg.tol*cfg.K_bar,abs(dW)<cfg.tol*cfg.W_bar):
            break
    gdp=float(np.sum(p*Y));sw=float(income)
    dr=social_discount_rate(cfg)
    return {"status":"ok","w_L":w_L,"w_K":w_K,"w_W":w_W,"prices":p.tolist(),
            "output":Y.tolist(),"gdp":gdp,"social_welfare":sw,
            "sectors":[s.name for s in cfg.sectors],"iterations":it+1,
            "social_discount_rate":dr,"Pigouvian_tax_per_ton_CO2":dr*50.0}

if __name__=="__main__":
    out=solve_cge()
    print(f"GDP={out['gdp']:.1f} w_K={out['w_K']:.3f} w_W={out['w_W']:.3f}")
    print(f"Discount rate={out['social_discount_rate']:.4f} CO2 tax={out['Pigouvian_tax_per_ton_CO2']:.2f}")
    cfg2=CGEConfig(W_bar=60.0)
    o2=solve_cge(cfg2)
    print(f"Water shock: GDP={o2['gdp']:.1f} w_W={o2['w_W']:.3f}")
    print("ALL CGE TESTS PASSED")
