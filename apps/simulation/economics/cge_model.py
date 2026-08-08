"""Small CGE Cobb-Douglas — phase 15.2. Manifest §6.2"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import numpy as np

@dataclass
class Sector:
    name: str; alpha_L: float = 0.4; alpha_K: float = 0.3; alpha_W: float = 0.3; A_tfp: float = 1.0

@dataclass
class CGEConfig:
    sectors: List[Sector] = field(default_factory=lambda: [
        Sector("agriculture", 0.35, 0.25, 0.40, 1.0),
        Sector("industry", 0.45, 0.40, 0.15, 1.2),
        Sector("services", 0.55, 0.35, 0.10, 1.1),
    ])
    L_bar: float = 100.0; K_bar: float = 200.0; W_bar: float = 50.0
    max_iter: int = 100; tol: float = 1e-6

def solve_cge(cfg=None):
    cfg = cfg or CGEConfig(); n = len(cfg.sectors); beta = np.ones(n)/n
    w_K, w_W = 1.0, 1.0; p = np.ones(n)
    for it in range(cfg.max_iter):
        L_d = K_d = W_d = 0.0; Y = np.zeros(n)
        for i, s in enumerate(cfg.sectors):
            cost = ((1/s.alpha_L)**s.alpha_L * (w_K/s.alpha_K)**s.alpha_K * (w_W/s.alpha_W)**s.alpha_W) / s.A_tfp
            p[i] = cost
            income = cfg.L_bar + w_K*cfg.K_bar + w_W*cfg.W_bar
            Y[i] = beta[i]*income / (p[i]+1e-15)
            L_d += s.alpha_L*p[i]*Y[i]; K_d += s.alpha_K*p[i]*Y[i]/(w_K+1e-15); W_d += s.alpha_W*p[i]*Y[i]/(w_W+1e-15)
        excess_K, excess_W = K_d-cfg.K_bar, W_d-cfg.W_bar
        w_K = max(0.01, w_K*(1+0.05*excess_K/(cfg.K_bar+1e-9)))
        w_W = max(0.01, w_W*(1+0.05*excess_W/(cfg.W_bar+1e-9)))
        if abs(excess_K)<cfg.tol*cfg.K_bar and abs(excess_W)<cfg.tol*cfg.W_bar: break
    return {"status":"ok", "w_K": w_K, "w_W": w_W, "prices": p.tolist(), "output": Y.tolist(),
            "sectors": [s.name for s in cfg.sectors], "iterations": it+1}

if __name__ == "__main__":
    print(solve_cge()); print("OK")
