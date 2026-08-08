"""k-ε RANS boundary layer — phase 14.1. Manifest §5.1"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

@dataclass
class KEpsilonParams:
    kappa: float = 0.41; C_mu: float = 0.09; z0: float = 0.05; u_star: float = 0.3

@dataclass
class ProfileConfig:
    z_max: float = 100.0; n_nodes: int = 40; U_ref: float = 5.0; z_ref: float = 10.0

def log_wind_profile(z, p, U_ref, z_ref):
    z = np.maximum(z, p.z0*1.01)
    u_star = p.kappa * U_ref / np.log(z_ref / p.z0)
    return (u_star / p.kappa) * np.log(z / p.z0)

def tke_dissipation_profile(z, p, u_star=None):
    z = np.maximum(z, p.z0*1.01); us = u_star if u_star is not None else p.u_star
    k = np.full_like(z, us**2 / np.sqrt(p.C_mu))
    eps = us**3 / (p.kappa * z)
    return {"k": k, "eps": eps, "nu_t": p.C_mu * k**2 / (eps+1e-15), "u_star": us}

def solve_boundary_layer(cfg=None, params=None):
    cfg = cfg or ProfileConfig(); p = params or KEpsilonParams()
    z = np.linspace(p.z0*2, cfg.z_max, cfg.n_nodes)
    U = log_wind_profile(z, p, cfg.U_ref, cfg.z_ref)
    us = p.kappa * cfg.U_ref / np.log(cfg.z_ref / p.z0)
    turb = tke_dissipation_profile(z, p, u_star=us)
    return {"status":"ok", "z": z, "U": U, **turb}

if __name__ == "__main__":
    out = solve_boundary_layer(); print(f"u*={out['u_star']:.3f}"); print("OK")
