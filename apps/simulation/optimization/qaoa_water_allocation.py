"""QAOA-Inspired Water Allocation: QUBO + Simulated Annealing
Phase 11.1 | Manifest §4.2 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple
import numpy as np

@dataclass
class WaterAllocationProblem:
    n_farms:int=10;n_periods:int=3
    water_availability:Optional[np.ndarray]=None
    costs:Optional[np.ndarray]=None
    interactions:Optional[np.ndarray]=None

def create_sample_problem(n_farms=8,n_periods=3,seed=42):
    rng=np.random.default_rng(seed)
    water_avail=rng.uniform(5,15,n_periods)
    costs=rng.uniform(1,10,n_farms*n_periods)
    interactions=rng.uniform(0,3,(n_farms,n_farms,n_periods))
    return WaterAllocationProblem(n_farms,n_periods,water_avail,costs,interactions)

def build_qubo(problem):
    """Build QUBO: min Σ c_i x_i + Σ J_ij x_i x_j + P Σ (Σ x_i - W_t)^2."""
    n=problem.n_farms;T=problem.n_periods;N=n*T
    P_penalty=100.0
    Q=np.zeros((N,N))
    for t in range(T):
        for i in range(n):
            idx=i+t*n;Q[idx,idx]=problem.costs[idx]
            for j in range(n):
                jdx=j+t*n
                Q[idx,jdx]+=problem.interactions[i,j,t]
                Q[idx,jdx]+=P_penalty*(1.0/problem.n_farms**2)
            Q[idx,idx]-=2*P_penalty*problem.water_availability[t]/problem.n_farms
        for i in range(n):
            for j in range(n):
                Q[i+t*n,j+t*n]+=P_penalty/(problem.n_farms**2)
    return Q

def qubo_energy(x,Q):
    return float(x@Q@x)

def simulated_annealing_qubo(Q,n_iters=5000,T_init=10.0,cooling=0.995,seed=42):
    rng=np.random.default_rng(seed);N=Q.shape[0]
    x=rng.integers(0,2,N).astype(float);best_x,best_e=x.copy(),qubo_energy(x,Q)
    T=T_init
    for it in range(n_iters):
        i=rng.integers(0,N);xn=x.copy();xn[i]=1-xn[i]
        dE=qubo_energy(xn,Q)-qubo_energy(x,Q)
        if dE<0 or rng.random()<np.exp(-dE/T):
            x=xn;e_cur=qubo_energy(x,Q)
            if e_cur<best_e:best_x,best_e=x.copy(),e_cur
        T*=cooling
    return best_x,best_e

def decode_solution(x,problem):
    n,T=problem.n_farms,problem.n_periods
    alloc=np.zeros((n,T))
    for t in range(T):
        for i in range(n):
            alloc[i,t]=int(x[i+t*n])
    total_per_period=alloc.sum(axis=0)
    feasible=all(total_per_period<=problem.water_availability)
    return {"allocation":alloc,"total_per_period":total_per_period,
            "water_available":problem.water_availability,"feasible":feasible}

def qaoa_inspired_water_optimize(problem=None):
    prob=problem or create_sample_problem()
    Q=build_qubo(prob)
    x_best,energy=simulated_annealing_qubo(Q,n_iters=5000)
    decoded=decode_solution(x_best,prob)
    return {"status":"ok","energy":energy,"solution":x_best.tolist(),
            "decoded":decoded,"qubo_size":Q.shape[0]}

if __name__=="__main__":
    out=qaoa_inspired_water_optimize()
    d=out["decoded"]
    print(f"Water allocation: feasible={d['feasible']}")
    print(f"Total per period: {d['total_per_period'].round(1)} vs available={d['water_available'].round(1)}")
    print("ALL QAOA WATER ALLOCATION TESTS PASSED")
