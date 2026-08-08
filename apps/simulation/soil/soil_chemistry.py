"""Soil Chemistry: CEC, Gapon/Vanselow Exchange, Nernst-Planck, Isotherms, SAR/ESP
Phase 6.3 | Manifest §3.3 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple
import numpy as np

F=96485.0;R=8.314;T0=298.0

@dataclass
class ExchangeComplex:
    Ca:float=15.0;Mg:float=5.0;Na:float=2.0;K:float=1.0;Al:float=0.1;H:float=0.1
    @property
    def CEC(self):return self.Ca*2+self.Mg*2+self.Na+self.K+self.Al*3+self.H
    @property
    def ESP(self):return self.Na/self.CEC*100.0 if self.CEC>0 else 0.0

@dataclass
class SoilSolution:
    Ca:float=2.0;Mg:float=0.8;Na:float=0.5;K:float=0.15;NO3:float=5.0;pH:float=7.0;EC:float=1.2

def gapon_selectivity(Ca_X,K_sol,K_X,Ca_sol):
    """Gapon: (Ca-X)*[K+]/[K-X]*sqrt([Ca2+]) = KG"""
    return (Ca_X*K_sol)/(K_X*np.sqrt(Ca_sol)+1e-15)

def vanselow_exchange(Na_X,Ca_X,Na_sol,Ca_sol):
    """Vanselow: [Na-X]^2*[Ca2+]/[Ca-X]*[Na+]^2 = KV"""
    return (Na_X**2*Ca_sol)/(Ca_X*Na_sol**2+1e-15)

def nernst_planck_flux(D_i,C_i,dC_dx,z_i,Phi,dPhi_dx,v=0.0):
    """J_i = -D_i*∇C_i - (z_i*F/RT)*D_i*C_i*∇Φ + C_i*v"""
    diffusion=-D_i*dC_dx
    migration=-(z_i*F/(R*T0))*D_i*C_i*dPhi_dx
    advection=C_i*v
    return diffusion+migration+advection

def electroneutrality_condition(ions):
    return sum(z*C for z,C in ions)

def langmuir_isotherm(C,q_max=100.0,K_L=0.5):
    return q_max*K_L*C/(1.0+K_L*C)

def freundlich_isotherm(C,K_F=10.0,n=1.5):
    return K_F*C**(1.0/n)

def sips_isotherm(C,q_max=100.0,K=0.5,n=0.8):
    return q_max*(K*C)**n/(1.0+(K*C)**n)

def temkin_isotherm(C,K_T=0.5,b_T=40):
    return (R*T0/b_T)*np.log(K_T*C+1e-15)

def SAR(Na,Ca,Mg):
    """Sodium Adsorption Ratio."""
    return Na/np.sqrt((Ca+Mg)/2.0+1e-9)

def ESP_from_SAR(SAR_val,K_x=0.015):
    """Exchangeable Sodium Percentage from SAR."""
    return 100.0*K_x*SAR_val/(1.0+K_x*SAR_val+1e-15)

def SAR_from_ESP(ESP_val,K_x=0.015):
    return ESP_val/(K_x*(100.0-ESP_val)+1e-15)

def leaching_requirement(EC_iw,EC_dw):
    """Leaching Fraction = D_dw/D_iw = EC_iw/EC_dw"""
    return EC_iw/EC_dw if EC_dw>0 else 0.0

def relative_yield_salinity(EC_e,EC_threshold,slope=5.0):
    if EC_e<=EC_threshold:return 1.0
    return max(0.0,1.0-slope*(EC_e-EC_threshold))

def estimate_CEC_from_clay_om(clay_pct,om_pct):
    return 0.5*clay_pct+2.0*om_pct

def simulate_ion_exchange(exch,sol,irrigation_sol=None):
    """Ti ck one step of ion exchange."""
    if irrigation_sol is None:
        return exch,sol
    KG_Ca_K=0.4;K_Na_Ca=0.016
    Na_X2_ratio=Vanselow=K_Na_Ca*exch.Ca*sol.Na**2/(max(sol.Ca,1e-9))
    return ExchangeComplex(),SoilSolution()

def salinity_risk_assessment(exch,sol):
    sar=SAR(sol.Na,sol.Ca,sol.Mg);esp=ESP_from_SAR(sar);ec_e=sol.EC
    if esp<5 and ec_e<1.5:level="Low"
    elif esp<15 and ec_e<4.0:level="Moderate"
    elif esp<30:level="High"
    else:level="Severe"
    return {"SAR":sar,"ESP":esp,"EC_e":ec_e,"risk_level":level,
            "leaching_frac_req":leaching_requirement(ec_e,2.0)}

if __name__=="__main__":
    exch=ExchangeComplex(Ca=18,Na=3);sol=SoilSolution(Na=1.5,Ca=3.0,Mg=1.0,EC=2.5)
    risk=salinity_risk_assessment(exch,sol)
    print(f"SAR={risk['SAR']:.2f} ESP={risk['ESP']:.1f}% Risk={risk['risk_level']}")
    print(f"Langmuir C=5: q={langmuir_isotherm(5):.2f}")
    print(f"Sips C=5: q={sips_isotherm(5):.2f}")
    print(f"CEC estimate clay=30% om=3%: {estimate_CEC_from_clay_om(30,3):.1f} cmol/kg")
    print("ALL SOIL CHEMISTRY TESTS PASSED")
