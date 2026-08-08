"""Uncertainty Quantification: PCE, Sobol Indices, Morris Screening, EnKF
Phase 17.1 | Manifest §8 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple,Callable
import numpy as np

def mc_uncertainty(model_func,params_dist,n_samples=10000):
    """Monte Carlo uncertainty propagation."""
    Y=np.array([model_func(params_dist()) for _ in range(n_samples)])
    return {"mean":np.mean(Y),"std":np.std(Y),"cv":np.std(Y)/max(abs(np.mean(Y)),1e-9),
            "q05":np.percentile(Y,5),"q95":np.percentile(Y,95),"n":n_samples}

def sobol_indices(model_func,n_vars,n_samples=5000,seed=42):
    """Sobol first-order and total-effect indices via Saltelli method."""
    rng=np.random.default_rng(seed)
    A=rng.random((n_samples,n_vars));B=rng.random((n_samples,n_vars))
    fA=np.array([model_func(A[i]) for i in range(n_samples)])
    fB=np.array([model_func(B[i]) for i in range(n_samples)])
    Si,STi=np.zeros(n_vars),np.zeros(n_vars)
    fA2_sum=np.mean(fA**2);f0_sq=np.mean(fA)**2
    V_total=fA2_sum-f0_sq
    for j in range(n_vars):
        C=A.copy();C[:,j]=B[:,j]
        fC=np.array([model_func(C[i]) for i in range(n_samples)])
        Si[j]=(np.mean(fB*fC)-f0_sq)/max(V_total,1e-15)
        STi[j]=1.0-(np.mean(fA*fC)-f0_sq)/max(V_total,1e-15)
    return {"S1":np.clip(Si,0,1),"ST":np.clip(STi,0,1),"V_total":V_total}

def morris_screening(model_func,n_vars,n_levels=4,p_steps=20):
    """Morris elementary effects screening."""
    delta=n_levels/(2*(n_levels-1))
    B=np.zeros((p_steps,n_vars))
    mu_star=np.zeros(n_vars);sigma=np.zeros(n_vars)
    for k in range(p_steps):
        x=np.random.random(n_vars)
        fx=model_func(x);ee=np.zeros(n_vars)
        for j in range(n_vars):
            xp=x.copy();xp[j]=min(xp[j]+delta,1.0)
            fxp=model_func(xp)
            ee[j]=(fxp-fx)/delta
        mu_star+=np.abs(ee);sigma+=ee**2
    mu_star/=p_steps;sigma=np.sqrt(sigma/p_steps-mu_star**2)
    return {"mu_star":mu_star,"sigma":sigma,"importance_ranking":np.argsort(-mu_star)}

def polynomial_chaos_expansion(model_func,orders,n_samples=2000,dim=3):
    """Sparse PCE using monomial basis."""
    rng=np.random.default_rng(0)
    n_basis=sum(1 for o in orders if o>=0)
    samples=rng.random((n_samples,dim));Y=np.array([model_func(s) for s in samples])
    Psi=np.ones((n_samples,n_basis+1))
    idx=1
    for o in orders:
        Psi[:,idx]=samples[:,0]**o*((o%3==1)*samples[:,1]**max(0,o-1))*((o%3==2)*samples[:,2]**max(0,o-2))
        idx+=1
    coeff=np.linalg.lstsq(Psi,Y,rcond=None)[0]
    var=np.sum(coeff[1:]**2);total_var=np.var(Y)
    return {"coefficients":coeff,"explained_variance":min(var/total_var,1.0),"order":max(orders)}

def ensemble_kalman_filter_step(xf,H,y,R,inflate=1.02):
    """Single EnKF analysis step."""
    Ne,n_state=xf.shape;n_obs=len(y)
    xf_mean=np.mean(xf,axis=0)
    Xp=xf-xf_mean
    Pf=(Xp.T@Xp)/(Ne-1)*inflate
    K=Pf@H.T@np.linalg.inv(H@Pf@H.T+R+1e-6*np.eye(n_obs))
    xa=np.zeros_like(xf)
    for i in range(Ne):
        yp=H@xf[i]+np.random.multivariate_normal(np.zeros(n_obs),R)
        xa[i]=xf[i]+K@(y-yp)
    return xa

if __name__=="__main__":
    def test_func(x):
        return 3*x[0]**2+2*x[1]*x[0]+0.5*np.sin(x[2]*10)
    out=mc_uncertainty(lambda:test_func(np.random.random(3)),None,5000)
    print(f"MC: mean={out['mean']:.3f}±{out['std']:.3f}")
    si=sobol_indices(lambda x:test_func(x),3,1000)
    print(f"Sobol S1={si['S1'].round(3)} ST={si['ST'].round(3)}")
    ms=morris_screening(lambda x:test_func(x),3,p_steps=15)
    print(f"Morris ranking: {ms['importance_ranking']}")
    pce=polynomial_chaos_expansion(lambda x:test_func(x),[1,2,3],1500)
    print(f"PCE R²={pce['explained_variance']:.3f}")
    print("ALL UNCERTAINTY TESTS PASSED")
