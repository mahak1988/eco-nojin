"""Soil Heat Transfer (Fourier + de Vries) — phase 3.4. Manifest §2.5"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

@dataclass
class SoilThermalParams:
    C_dry: float = 1.5e6; C_water: float = 4.18e6
    lambda_dry: float = 0.25; lambda_sat: float = 1.8; theta_s: float = 0.45

def C_v(theta, p): return p.C_dry + (p.C_water - p.C_dry) * np.clip(theta / p.theta_s, 0, 1)
def lambda_th(theta, p):
    s = np.clip(theta / p.theta_s, 0, 1)
    return p.lambda_dry + (p.lambda_sat - p.lambda_dry) * s

@dataclass
class SoilHeatConfig:
    n_nodes: int = 21; z_max: float = 1.0; dt: float = 3600.0; n_steps: int = 48
    T_init: float = 18.0; T_surface: float = 28.0; T_bottom: Optional[float] = None; theta: float = 0.25

def solve_soil_heat(cfg=None, params=None):
    cfg = cfg or SoilHeatConfig(); p = params or SoilThermalParams()
    z = np.linspace(0, cfg.z_max, cfg.n_nodes); dz = z[1] - z[0]
    Cv, lam = C_v(cfg.theta, p), lambda_th(cfg.theta, p); kappa = lam / Cv
    Fo = kappa * cfg.dt / dz**2
    if Fo > 0.5:
        dt = 0.4 * dz**2 / kappa; n_steps = int(cfg.n_steps * cfg.dt / dt); Fo = kappa * dt / dz**2
    else:
        dt, n_steps = cfg.dt, cfg.n_steps
    T = np.full(cfg.n_nodes, cfg.T_init, dtype=float); history = [T.copy()]
    for _ in range(n_steps):
        Tn = T.copy(); Tn[0] = cfg.T_surface
        for i in range(1, cfg.n_nodes - 1):
            Tn[i] = T[i] + Fo * (T[i+1] - 2*T[i] + T[i-1])
        Tn[-1] = Tn[-2] if cfg.T_bottom is None else cfg.T_bottom
        T = Tn; history.append(T.copy())
    return {"status": "ok", "z": z, "T_final": T, "history": np.array(history), "Fo": Fo, "kappa": kappa}

if __name__ == "__main__":
    out = solve_soil_heat()
    print(f"Soil heat T range [{out['T_final'].min():.2f}, {out['T_final'].max():.2f}]"); print("OK")
