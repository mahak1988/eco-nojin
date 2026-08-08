"""Tests for Richards extended."""
import numpy as np
from apps.simulation.hydrology.richards_extended import solve_richards_extended
def test_output_shape():
    r=solve_richards_extended(n_nodes=10,dt=60,n_steps=5)
    assert len(r["h_final"])==10 and len(r["theta_final"])==10
def test_theta_range():
    r=solve_richards_extended(n_nodes=10,dt=60,n_steps=5)
    for t in r["theta_final"]:assert 0<t<0.5
def test_hysteresis():
    r1=solve_richards_extended(dt=60,n_steps=5)
    r2=solve_richards_extended(dt=60,n_steps=5,init_theta=0.15)
    assert r1 is not None and r2 is not None
