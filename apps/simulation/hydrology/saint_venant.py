"""Saint-Venant 1-D + SCS-CN runoff — phase 3.3. Manifest §2.4"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

CN_TABLE = {"row_crop": 78, "small_grain": 72, "pasture": 61, "forest": 55, "bare": 86, "urban": 90}

@dataclass
class SVConfig:
    n_cells: int = 30; dx: float = 100.0; dt: float = 10.0; n_steps: int = 100
    n_manning: float = 0.03; S0: float = 0.001; width: float = 5.0; mode: str = "kinematic"

def scs_cn_runoff(P_mm, CN=78.0):
    S = 25400 / CN - 254; Ia = 0.2 * S
    if P_mm <= Ia: return 0.0
    return (P_mm - Ia)**2 / (P_mm - Ia + S)

def manning_Q(A, R, S, n):
    return (1/n) * A * R**(2/3) * np.sqrt(max(S, 1e-8))

def solve_saint_venant(cfg=None, Q_bc=2.0):
    cfg = cfg or SVConfig()
    A = np.full(cfg.n_cells, 0.5); Q = np.zeros(cfg.n_cells); history_Q = []
    for step in range(cfg.n_steps):
        for i in range(cfg.n_cells):
            h = A[i] / cfg.width
            R = h * cfg.width / (cfg.width + 2*h + 1e-9)
            Q[i] = manning_Q(A[i], R, cfg.S0, cfg.n_manning)
        Q[0] = Q_bc; A_new = A.copy()
        for i in range(1, cfg.n_cells):
            A_new[i] = max(A[i] - cfg.dt/cfg.dx * (Q[i] - Q[i-1]), 0.01)
        A = A_new; history_Q.append(Q.copy())
    return {"status": "ok", "Q_final": Q, "A_final": A, "history_Q": np.array(history_Q),
            "CN_runoff_example_mm": scs_cn_runoff(40, CN_TABLE["row_crop"])}

if __name__ == "__main__":
    out = solve_saint_venant(); print(f"Q mean={out['Q_final'].mean():.3f}"); print("OK")
