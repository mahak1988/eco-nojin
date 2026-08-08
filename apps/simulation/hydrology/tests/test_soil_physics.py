"""Tests for soil physics."""
from apps.simulation.hydrology.soil_physics import van_genuchten_theta,hydraulic_conductivity
def test_vg_sat():
    t=van_genuchten_theta(h=0,theta_s=0.45,theta_r=0.05,alpha=2,n=2)
    assert abs(t-0.45)<0.01
def test_vg_dry():
    t=van_genuchten_theta(h=-1000,theta_s=0.45,theta_r=0.05,alpha=2,n=2)
    assert abs(t-0.05)<0.02
def test_K():
    K=hydraulic_conductivity(theta=0.35,Ks=1e-5,theta_s=0.45,theta_r=0.05,n=2)
    assert 0<K<=1e-5
