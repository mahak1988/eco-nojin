"""Soil chemistry: CEC, SAR/ESP, isotherms — phase 6.3. Manifest §3.3-3.4"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
import numpy as np

@dataclass
class SoilChemState:
    Ca: float = 5.0; Mg: float = 2.0; Na: float = 1.0; K: float = 0.5
    CEC: float = 15.0; EC: float = 1.5

def sar(Na, Ca, Mg): return Na / np.sqrt((Ca + Mg) / 2 + 1e-15)
def esp(Na, CEC): return 100 * Na / (CEC + 1e-15)
def gapon_exchange(Na_sol, Ca_sol, K_g=0.015): return K_g * Na_sol / np.sqrt(max(Ca_sol, 1e-9))
def langmuir(C, Qmax=10.0, KL=0.5): return Qmax * KL * C / (1 + KL * C)
def freundlich(C, KF=2.0, n=0.6): return KF * C ** n
def sips(C, Qmax=10.0, Ks=0.5, n=0.8): return Qmax * (Ks * C)**n / (1 + (Ks * C)**n)
def lime_requirement(pH, target=6.5, buffer=1.0): return max(0.0, (target - pH) * buffer * 2.0)

def assess_sodicity(state):
    s, e = sar(state.Na, state.Ca, state.Mg), esp(state.Na, state.CEC)
    class_ = "normal"
    if s > 13 or e > 15: class_ = "sodic"
    elif state.EC > 4 and s > 13: class_ = "saline-sodic"
    elif state.EC > 4: class_ = "saline"
    return {"SAR": s, "ESP": e, "EC": state.EC, "class": class_, "lime_t_ha": lime_requirement(7.0 - 0.1*e)}

if __name__ == "__main__":
    print(assess_sodicity(SoilChemState(Na=3.0, Ca=4.0, Mg=1.5, CEC=12, EC=2.0))); print("OK")
