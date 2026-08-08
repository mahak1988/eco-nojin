"""Shuttleworth-Wallace dual-source ET — phase 3.2. Manifest §2.3"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

@dataclass
class SWInputs:
    Rn: float = 400.0; G: float = 40.0; Ta: float = 28.0; RH: float = 40.0
    U: float = 2.0; Pa: float = 101.3; LAI: float = 2.5; h_c: float = 0.5

@dataclass
class SWOutputs:
    ET: float; E_soil: float; T_canopy: float; ra: float; rs: float; rss: float

def medlyn_gs(VPD, A_n=15.0, g0=0.01, g1=4.0):
    gs = g0 + 1.6 * (1 + g1 / np.sqrt(max(VPD, 0.1))) * (A_n / 1000)
    return max(gs * 0.025, 1e-4)

def aero_resistances(U, h_c, LAI):
    z0, d = 0.13 * h_c, 0.63 * h_c
    raa = np.log((2 - d) / z0)**2 / (0.41**2 * max(U, 0.1))
    return {"raa": raa, "rca": raa / max(LAI, 0.5), "rsa": raa * 2}

def soil_surface_resistance(theta=0.2, theta_s=0.45):
    return 50 * np.exp(5 * (1 - theta / theta_s))

def shuttleworth_wallace(inp=None, theta=0.25):
    inp = inp or SWInputs()
    es = 0.6108 * np.exp(17.27 * inp.Ta / (inp.Ta + 237.3))
    ea = es * inp.RH / 100; VPD = es - ea
    delta = 4098 * es / (inp.Ta + 237.3)**2; gamma = 0.665e-3 * inp.Pa
    Rn_c = inp.Rn * (1 - np.exp(-0.5 * inp.LAI)); Rn_s = inp.Rn - Rn_c - inp.G
    res = aero_resistances(inp.U, inp.h_c, inp.LAI)
    rs = 1.0 / medlyn_gs(VPD); rss = soil_surface_resistance(theta)
    Ra, Rc, Rs = res["raa"], res["rca"] + rs, res["rsa"] + rss
    Ga = 1 / (Ra + 1e-9); rho_cp = 1200
    LE_c = max((delta * Rn_c + rho_cp * VPD * Ga) / (delta + gamma * (1 + Rc * Ga)), 0)
    LE_s = max((delta * Rn_s + rho_cp * VPD * Ga) / (delta + gamma * (1 + Rs * Ga)), 0)
    fac = 86400 / 2.45e6
    return SWOutputs(ET=(LE_c+LE_s)*fac, E_soil=LE_s*fac, T_canopy=LE_c*fac, ra=res["raa"], rs=rs, rss=rss)

if __name__ == "__main__":
    o = shuttleworth_wallace(); print(f"ET={o.ET:.2f} mm/d"); print("OK")
