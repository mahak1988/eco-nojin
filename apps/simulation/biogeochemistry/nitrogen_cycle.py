"""Nitrogen cycle Monod kinetics — phase 6.2. Manifest §3.2"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

@dataclass
class NPools:
    N_org: float = 50.0; NH4: float = 5.0; NO3: float = 10.0; N2O: float = 0.0

@dataclass
class NParams:
    k_min: float = 0.02; k_nit: float = 0.2; k_denit: float = 0.05
    K_NH4: float = 2.0; K_NO3: float = 5.0; f_temp: float = 1.0; f_moist: float = 1.0
    leach_frac: float = 0.02; uptake_max: float = 1.5

def step_nitrogen(pools, p=None, dt=1.0, plant_demand=0.5):
    p = p or NParams(); f = p.f_temp * p.f_moist
    min_rate = p.k_min * f * pools.N_org
    nit = p.k_nit * f * pools.NH4 / (p.K_NH4 + pools.NH4 + 1e-9) * pools.NH4
    den = p.k_denit * f * pools.NO3 / (p.K_NO3 + pools.NO3 + 1e-9) * pools.NO3
    avail = pools.NH4 + pools.NO3
    uptake = min(plant_demand, p.uptake_max, avail) * dt
    leach = p.leach_frac * pools.NO3
    return NPools(max(pools.N_org - min_rate*dt, 0),
                  max(pools.NH4 + min_rate*dt - nit*dt - 0.5*uptake, 0),
                  max(pools.NO3 + nit*dt - den*dt - 0.5*uptake - leach*dt, 0),
                  max(pools.N2O + 0.01*den*dt, 0))

def simulate_n_cycle(n_days=30, p=None):
    pools = NPools(); hist = []
    for d in range(n_days):
        pools = step_nitrogen(pools, p, dt=1.0, plant_demand=0.8)
        hist.append((pools.N_org, pools.NH4, pools.NO3, pools.N2O))
    return {"status": "ok", "final": pools, "history": np.array(hist), "NO3_final": pools.NO3, "N2O_cum": pools.N2O}

if __name__ == "__main__":
    out = simulate_n_cycle(30); print(f"NO3={out['NO3_final']:.2f}"); print("OK")
