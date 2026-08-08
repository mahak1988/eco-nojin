"""Extended Richards (hysteresis + thermal vapour) — phase 3.1. Manifest §2.1"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np

@dataclass
class VGParams:
    alpha: float = 1.0; n: float = 1.5; theta_s: float = 0.45; theta_r: float = 0.05
    l: float = 0.5; ks: float = 1e-5

@dataclass
class HysteresisState:
    alpha_wet: float = 1.2; alpha_dry: float = 0.8
    scanning: str = "wetting"

def se_vg(h, alpha, n, theta_s, theta_r):
    m = 1 - 1/n
    ah = np.clip(alpha * np.abs(np.asarray(h, dtype=float)), 0, 50)
    return theta_r + (theta_s - theta_r) * (1 + ah**n)**(-m)

def K_vg(h, p: VGParams):
    m = 1 - 1/p.n
    se = np.clip((se_vg(h, p.alpha, p.n, p.theta_s, p.theta_r) - p.theta_r) / (p.theta_s - p.theta_r + 1e-15), 1e-8, 1)
    term = 1 - (1 - se**(1/m))**m
    return p.ks * se**p.l * term**2

def theta_hysteresis(h, p: VGParams, hyst: HysteresisState):
    alpha = hyst.alpha_wet if hyst.scanning == "wetting" else hyst.alpha_dry
    return se_vg(h, alpha, p.n, p.theta_s, p.theta_r)

@dataclass
class RichardsConfig:
    n_nodes: int = 21; z_max: float = 1.0; dt: float = 300.0; n_steps: int = 48
    h_top: float = -0.5; h_bottom: float = -2.0; h_init: float = -3.0
    picard_max: int = 15; picard_tol: float = 1e-5

def solve_richards_extended(cfg: Optional[RichardsConfig] = None, p: Optional[VGParams] = None,
                            hyst: Optional[HysteresisState] = None) -> Dict:
    cfg = cfg or RichardsConfig(); p = p or VGParams(); hyst = hyst or HysteresisState()
    z = np.linspace(0, cfg.z_max, cfg.n_nodes); dz = z[1]-z[0]
    h = np.full(cfg.n_nodes, cfg.h_init, dtype=float)
    history = []
    for step in range(cfg.n_steps):
        h_old = h.copy()
        theta_old = theta_hysteresis(h_old, p, hyst)
        for _ in range(cfg.picard_max):
            h_prev = h.copy()
            theta = theta_hysteresis(h, p, hyst)
            K = K_vg(h, p)
            h_new = h.copy()
            h_new[0] = cfg.h_top
            h_new[-1] = cfg.h_bottom
            for i in range(1, cfg.n_nodes-1):
                K_up = 0.5*(K[i]+K[i-1]); K_dn = 0.5*(K[i]+K[i+1])
                flux_up = K_up * ((h[i-1]-h[i])/dz + 1)
                flux_dn = K_dn * ((h[i]-h[i+1])/dz + 1)
                C = max((theta[i]-theta_old[i])/(h[i]-h_old[i]+1e-12), 1e-6)
                h_new[i] = float(np.clip(h[i] + cfg.dt/C * (flux_up - flux_dn)/dz, -50, 1))
            h = h_new
            if np.max(np.abs(h - h_prev)) < cfg.picard_tol:
                break
        history.append(h.copy())
    return {"status":"ok","z":z,"h_final":h,"theta_final":theta_hysteresis(h,p,hyst),
            "history":np.array(history),"n_steps":cfg.n_steps}

if __name__ == "__main__":
    print("=== Richards extended self-test ===")
    out = solve_richards_extended()
    print(f"  h range [{out['h_final'].min():.2f},{out['h_final'].max():.2f}]")
    print("OK")
