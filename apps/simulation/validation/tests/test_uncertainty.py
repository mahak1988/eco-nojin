"""Tests for uncertainty quantification."""
import numpy as np
from apps.simulation.validation.uncertainty import sobol_indices,morris_screening,monte_carlo_ensemble
def test_mc():
    r=monte_carlo_ensemble(lambda x:sum(x),[(0,1)]*3,n_samples=500)
    assert"mean"in r and"std"in r and len(r["ci_95"])==2
def test_sobol():
    r=sobol_indices(lambda x:0.5*x[0]+0.3*x[1]+0.1*x[2],[(0,1)]*3,n_samples=200)
    assert r["S1"][0]>r["S1"][2]
def test_morris():
    r=morris_screening(lambda x:x[0]*x[1]+x[2],[(0,1)]*3,n_levels=4,n_trajectories=10)
    assert len(r["mu_star"])==3
def test_ci():
    r=monte_carlo_ensemble(lambda x:np.mean(x),[(0,1)]*5,n_samples=300)
    assert r["ci_95"][0]<r["mean"]<r["ci_95"][1]
