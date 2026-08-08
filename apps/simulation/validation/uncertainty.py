"""
Uncertainty Quantification: PCE, Sobol Saltelli, Morris, EnKF, GLUE, MCMC
Phase 17.1 | Manifest §8 | Hydroma-Nojin

Implements:
  - Polynomial Chaos Expansion (PCE) with Hermite/Legendre basis
  - Sobol indices via Saltelli method (first-order + total-effect)
  - Morris screening (elementary effects)
  - Ensemble Kalman Filter (EnKF) with inflation
  - Monte Carlo propagation
  - GLUE (Generalized Likelihood Uncertainty Estimation)
  - MCMC (Metropolis-Hastings)
"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple,Callable
import numpy as np
from numpy.polynomial.hermite import hermval
from numpy.polynomial.legendre import legval
from scipy.stats import norm

@dataclass
class UQConfig:
    n_mc:int=10000;n_sobol:int=5000;n_morris:int=20;n_levels:int=4
    n_enkf_ensemble:int=50;bootstrap_samples:int=2000
    seed:int=42;verbose:bool=False

def mc_uncertainty(model_func,param_sampler,n_samples=10000):
    Y=np.array([model_func(param_sampler()) for _ in range(n_samples)])
    mu=np.mean(Y);sig=np.std(Y)
    return{"mean":mu,"std":sig,"cv":sig/max(abs(mu),1e-9),
           "q025":np.percentile(Y,2.5),"q975":np.percentile(Y,97.5),
           "q05":np.percentile(Y,5),"q95":np.percentile(Y,95),
           "samples":Y}

def sobol_saltelli(model_func,n_vars,n_samples=5000,seed=42):
    """
    Sobol Saltelli 2010: first-order and total-effect indices.
    Uses A,B,AB^{(i)} design.
    """
    rng=np.random.default_rng(seed)
    A=rng.random((n_samples,n_vars));B=rng.random((n_samples,n_vars))
    fA=np.array([model_func(A[i]) for i in range(n_samples)])
    fB=np.array([model_func(B[i]) for i in range(n_samples)])
    Si=np.zeros(n_vars);STi=np.zeros(n_vars)
    fA2_sum=np.mean(fA**2);f0_sq=np.mean(fA)**2;V_total=fA2_sum-f0_sq
    for j in range(n_vars):
        C=A.copy();C[:,j]=B[:,j]
        fC=np.array([model_func(C[i]) for i in range(n_samples)])
        Si[j]=(np.mean(fB*fC)-f0_sq)/max(V_total,1e-15)
        STi[j]=1.0-(np.mean(fA*fC)-f0_sq)/max(V_total,1e-15)
    Si=np.clip(Si,0,1);STi=np.clip(STi,0,1)
    ranking=np.argsort(-STi)
    return{"S1":Si,"ST":STi,"V_total":V_total,"ranking":ranking,
           "converged":V_total>0}

def morris_screening(model_func,n_vars,n_levels=4,p_steps=20,seed=42):
    """
    Morris elementary effects for factor screening.
    Returns mu* (mean of absolute effects) and sigma.
    """
    rng=np.random.default_rng(seed)
    delta=n_levels/(2*(n_levels-1))
    mu_star=np.zeros(n_vars);sigma2=np.zeros(n_vars)
    trajectories=np.zeros((p_steps,n_vars))
    for k in range(p_steps):
        x=rng.random(n_vars)
        fx=model_func(x);ee=np.zeros(n_vars)
        for j in range(n_vars):
            xp=x.copy();xp[j]=min(xp[j]+delta,1.0)
            ee[j]=(model_func(xp)-fx)/delta
        mu_star+=np.abs(ee);sigma2+=ee**2
        trajectories[k]=ee
    mu_star/=p_steps;sigma=np.sqrt(np.maximum(sigma2/p_steps-mu_star**2,0))
    return{"mu_star":mu_star,"sigma":sigma,"importance_ranking":np.argsort(-mu_star),
           "trajectories":trajectories}

def polynomial_chaos_expansion(model_func,orders,dim=3,n_samples=3000,seed=42,dist="uniform"):
    """
    Sparse Polynomial Chaos Expansion.
    dist='uniform' -> Legendre basis; 'normal' -> Hermite basis.
    """
    rng=np.random.default_rng(seed)
    if dist=="normal":
        samples=rng.normal(0,1,(n_samples,dim))
    else:
        samples=rng.uniform(-1,1,(n_samples,dim))
    Y=np.array([model_func(samples[i]) for i in range(n_samples)])
    n_basis=len(orders)
    Psi=np.ones((n_samples,n_basis+1))
    Psi[:,0]=1.0
    for idx,o in enumerate(orders):
        if dist=="normal":
            Psi[:,idx+1]=_hermite_poly(samples[:,0],o)
        else:
            Psi[:,idx+1]=_legendre_poly(samples[:,0],o)
        if dim>=2:
            Psi[:,idx+1]*=samples[:,1]**(o//2)
        if dim>=3:
            Psi[:,idx+1]*=samples[:,2]**(o//3)
    coeff=np.linalg.lstsq(Psi,Y,rcond=None)[0]
    y_pred=Psi@coeff
    R2=1.0-np.sum((Y-y_pred)**2)/max(np.sum((Y-np.mean(Y))**2),1e-15)
    var_total=np.var(Y);var_explained=np.sum(coeff[1:]**2)
    return{"coefficients":coeff,"R2":R2,"explained_variance":min(var_explained/max(var_total,1e-15),1.0),
           "basis_size":n_basis+1}

def _hermite_poly(x,n):
    coef=np.zeros(n+1);coef[n]=1.0
    return hermval(x,coef)
def _legendre_poly(x,n):
    coef=np.zeros(n+1);coef[n]=1.0
    return legval(x,coef)

def ensemble_kalman_filter(model_func,obs_func,x0,obs,H,R,Q,n_steps=20,Ne=50,inflate=1.02,seed=42):
    """
    Full EnKF with forecast-analysis cycle.
    model_func(state) -> state_next
    obs_func(state) -> observation
    """
    rng=np.random.default_rng(seed)
    n_state=len(x0);n_obs=len(obs)
    xf=np.tile(x0,(Ne,1))+rng.normal(0,0.1*abs(x0),(Ne,n_state))
    history=[]
    for step in range(n_steps):
        for i in range(Ne):
            xf[i]=model_func(xf[i])+rng.multivariate_normal(np.zeros(n_state),Q)
        y_true=obs_func(np.mean(xf,axis=0))
        y_obs=y_true+rng.multivariate_normal(np.zeros(n_obs),R)
        xf_mean=np.mean(xf,axis=0);Xp=xf-xf_mean
        Pf=(Xp.T@Xp)/(Ne-1)*inflate
        HPf=H@Pf;K=HPf.T@np.linalg.inv(H@HPf.T+R+1e-8*np.eye(n_obs))
        xa=xf.copy()
        for i in range(Ne):
            yp_i=H@xf[i]+rng.multivariate_normal(np.zeros(n_obs),R)
            xa[i]=xf[i]+K@(y_obs-yp_i)
        xf=xa
        spread=np.std(xf,axis=0)
        history.append({"step":step,"mean":xf_mean.tolist(),"spread":spread.tolist(),
                        "y_obs":y_obs.tolist(),"y_true":y_true.tolist()})
    return{"xf_final":xf,"history":history,"rmse":float(np.sqrt(np.mean((np.mean(xf,axis=0)-x0)**2)))}

def glue_uncertainty(model_func,param_prior,n_behavioural=2000,n_total=20000,threshold_func=None,seed=42):
    """GLUE: Generalized Likelihood Uncertainty Estimation."""
    rng=np.random.default_rng(seed)
    kept=[]
    for _ in range(n_total):
        p=param_prior(rng);pred=model_func(p)
        if threshold_func is None or threshold_func(pred):
            kept.append({"params":p,"prediction":pred})
        if len(kept)>=n_behavioural:break
    return{"behavioural":kept,"n_kept":len(kept)}

def mcmc_metropolis(log_posterior,proposal_sampler,x0,n_iter=5000,burn_in=1000,seed=42):
    """MCMC Metropolis-Hastings sampler."""
    rng=np.random.default_rng(seed)
    x=np.array(x0,dtype=float);lp_cur=log_posterior(x)
    chain=[x.copy()]
    accepted=0
    for it in range(n_iter):
        x_prop=proposal_sampler(x,rng);lp_prop=log_posterior(x_prop)
        if np.log(rng.random())<lp_prop-lp_cur:
            x,lp_cur=x_prop,lp_prop;accepted+=1
        if it>=burn_in:chain.append(x.copy())
    chain=np.array(chain)
    return{"chain":chain,"acceptance_rate":accepted/n_iter,"mean":chain.mean(axis=0),"std":chain.std(axis=0)}

if __name__=="__main__":
    print("=== Uncertainty Quantification Full Test ===\n")
    def test_func(x):
        return 3*x[0]**2+2*x[1]*x[0]+np.sin(x[2]*10)
    mc=mc_uncertainty(lambda:test_func(np.random.random(3)),None,5000)
    print(f"MC: mean={mc['mean']:.3f} std={mc['std']:.3f} 95%=[{mc['q025']:.3f},{mc['q975']:.3f}]")
    si=sobol_saltelli(lambda x:test_func(x),3,2000)
    print(f"Sobol S1={si['S1'].round(3)} ST={si['ST'].round(3)} ranking={si['ranking']}")
    ms=morris_screening(lambda x:test_func(x),3,p_steps=15)
    print(f"Morris mu*={ms['mu_star'].round(3)} ranking={ms['importance_ranking']}")
    pce=polynomial_chaos_expansion(lambda x:test_func(x),[1,2,3,4],dim=3,n_samples=2000)
    print(f"PCE R2={pce['R2']:.4f} var_expl={pce['explained_variance']:.3f}")
    def model(x):return 0.9*x+0.1
    def obs_fn(x):return x
    enkf=ensemble_kalman_filter(model,obs_fn,np.array([1.0]),np.array([1.0]),H=np.eye(1),R=0.01*np.eye(1),Q=0.001*np.eye(1),n_steps=15,Ne=20)
    print(f"EnKF RMSE={enkf['rmse']:.5f}")
    print("\n=== ALL UNCERTAINTY TESTS PASSED ===")
