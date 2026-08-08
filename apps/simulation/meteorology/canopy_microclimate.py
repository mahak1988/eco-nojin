"""Canopy microclimate — phase 14.2. Manifest §5.2"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

@dataclass
class CanopyParams:
    LAI: float = 3.0; h_canopy: float = 1.5; k_ext: float = 0.5
    z0: float = 0.1; d: float = 1.05; alpha_wind: float = 1.5; albedo: float = 0.2

@dataclass
class MeteoForcing:
    Rs: float = 600.0; Ta: float = 28.0; RH: float = 40.0; U_ref: float = 2.5; z_ref: float = 2.0

def saturation_vp(T_c):
    return 0.6108 * np.exp(17.27 * T_c / (T_c + 237.3))

def leaf_energy_balance(Rn_leaf, Ta, ea, ga, gs=0.01):
    rho_cp, gamma = 1200.0, 0.066; Tl = Ta
    for _ in range(8):
        es = saturation_vp(Tl)
        LE = (rho_cp/gamma)*(es-ea)/(1/max(gs,1e-6)+1/max(ga,1e-6))
        H = Rn_leaf - LE; Tl = Ta + H/(rho_cp*max(ga,1e-6))
    return {"T_leaf": Tl, "H": H, "LE": LE}

def simulate_canopy(params=None, met=None, n_layers=5):
    p = params or CanopyParams(); m = met or MeteoForcing()
    z_frac = np.linspace(0, 1, n_layers); z = p.h_canopy * (1 - z_frac)
    Rs_layer = m.Rs * np.exp(-p.k_ext * p.LAI * z_frac)
    U_h = max(m.U_ref * np.log(max(p.h_canopy-p.d,p.z0)/p.z0) / np.log(max(m.z_ref-p.d,p.z0)/p.z0), 0.1)
    U = U_h * np.exp(-p.alpha_wind * (1 - np.clip(z/p.h_canopy, 0, 1)))
    ea = saturation_vp(m.Ta)*(m.RH/100)
    T_leaf, H, LE = [], [], []
    for i in range(n_layers):
        Rn = Rs_layer[i]*(1-p.albedo)*0.5; ga = 0.01 + 0.05*U[i]
        bal = leaf_energy_balance(Rn, m.Ta, ea, ga)
        T_leaf.append(bal["T_leaf"]); H.append(bal["H"]); LE.append(bal["LE"])
    return {"status":"ok", "z": z, "Rs_layer": Rs_layer, "U": U,
            "T_leaf": np.array(T_leaf), "H": np.array(H), "LE": np.array(LE),
            "VPD": saturation_vp(m.Ta)-ea}

if __name__ == "__main__":
    out = simulate_canopy(); print(f"T_leaf={out['T_leaf']}"); print("OK")
