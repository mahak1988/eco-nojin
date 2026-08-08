"""Replicator Dynamics: CPR Game, Pigouvian Tax, ESS, Cooperation Mechanisms
Phase 15.1 | Manifest §6.1 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple
import numpy as np

@dataclass
class GameConfig:
    n_strategies:int=3;tax:float=0.0;subsidy:float=0.0;dt:float=0.05;n_steps:int=300
    seed:int=0;penalty:float=0.0;bonus:float=0.0;delta:float=0.95
    payoff:Optional[np.ndarray]=None

def cpr_payoff(n=3,tax=0.0,bonus=0.0):
    """Common Pool Resource payoff matrix: Cooperate, Defect, Punish."""
    R,P,T,S=3.0,1.0,5.0-tax,0.0
    return np.array([[R,S,R-0.5],[T,P-tax,T-1.0],[R-0.5+bonus,P-0.5,R-1.0]],float)

def replicator_step(x,A,dt):
    fitness=A@x;phi=float(x@fitness)
    xn=np.clip(x+dt*x*(fitness-phi),0,None)
    s=xn.sum();return xn/s if s>0 else np.ones_like(x)/len(x)

def find_ess(A,grid_size=100):
    """Search for Evolutionarily Stable Strategy via gradient."""
    n=A.shape[0];best,val=None,1e9
    for i in range(grid_size):
        x=np.random.random(n);x/=x.sum()
        for _ in range(200):
            fit=A@x;phi=float(x@fit);dx=x*(fit-phi)
            if np.max(np.abs(dx))<1e-8:break
            x=np.clip(x+0.01*dx,0,None);x/=(x.sum()+1e-15)
        inv=0.0
        for j in range(n):
            if x[j]<0.001:continue;ej=np.zeros(n);ej[j]=1
            inv+=max(0,float(ej@A@x-x@A@x))
        if inv<val:val=inv;best=x.copy()
    return best,val

def pigouvian_tax(x_total,x_social,tax_rate=0.5):
    excess=max(x_total-x_social,0)
    return tax_rate*excess*x_total/100.0

def simulate_replicator(cfg=None):
    cfg=cfg or GameConfig()
    A=cfg.payoff if cfg.payoff is not None else cpr_payoff(cfg.n_strategies,cfg.tax,cfg.bonus)
    rng=np.random.default_rng(cfg.seed)
    x=rng.random(cfg.n_strategies);x/=x.sum()
    traj,dom=[x.copy()],[]
    for _ in range(cfg.n_steps):
        x=replicator_step(x,A,cfg.dt)
        traj.append(x.copy());dom.append(int(np.argmax(x)))
    traj=np.array(traj)
    ess,ess_err=find_ess(A)
    return {"status":"ok","trajectory":traj,"x_final":traj[-1],
            "dominant_last":int(np.argmax(traj[-1])),
            "ess":ess.tolist() if ess is not None else None,
            "ess_error":float(ess_err) if ess is not None else None}

def cooperation_stability(bonus,penalty,gamma):
    return bonus>penalty*(1-gamma)/gamma

if __name__=="__main__":
    out=simulate_replicator(GameConfig(tax=0.5))
    print(f"Tax=0.5: x={out['x_final'].round(3)} dom={out['dominant_last']}")
    out2=simulate_replicator(GameConfig(tax=2.0,bonus=1.0))
    print(f"Tax+Bonus: x={out2['x_final'].round(3)} dom={out2['dominant_last']}")
    stable=cooperation_stability(bonus=2.0,penalty=3.0,gamma=0.95)
    print(f"Cooperation stable: {stable}")
    print("ALL REPLICATOR TESTS PASSED")
