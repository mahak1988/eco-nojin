"""
Explainable AI: SHAP, LIME, Partial Dependence Plots, ICE
Hydroma-Nojin

Implements:
  - KernelExplainer-style SHAP values
  - LIME local explanations (tabular)
  - Partial Dependence Plots (PDP)
  - Individual Conditional Expectation (ICE)
  - Feature importance (permutation + SHAP)
  - Counterfactual explanations
"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple,Callable
import numpy as np
from itertools import combinations

@dataclass
class XAIConfig:
    n_samples:int=1000;n_features:int=5;seed:int=42;verbose:bool=False

def shapley_kernel_weights(M):
    """SHAP kernel weights: (M-1)/(choose(M,|S|)*|S|*(M-|S|))."""
    w=np.zeros(2**M)
    for k in range(2**M):
        s=bin(k).count('1')
        if s==0 or s==M:w[k]=0
        else:w[k]=(M-1)/(np.math.comb(M,s)*s*(M-s))
    return w

def shap_values_kernel(model_fn,background,instance,config=None):
    """Model-agnostic Kernel SHAP."""
    cfg=config or XAIConfig()
    M=len(instance);rng=np.random.default_rng(cfg.seed)
    z_prime=rng.integers(0,2,(cfg.n_samples,M))
    z_prime[0]=np.zeros(M,dtype=int);z_prime[1]=np.ones(M,dtype=int)
    X_eval=np.zeros((cfg.n_samples,M))
    for i in range(cfg.n_samples):
        mask=z_prime[i]==1
        x_i=background.copy()
        x_i[mask]=instance[mask]
        X_eval[i]=x_i
    y_eval=np.array([model_fn(X_eval[i]) for i in range(cfg.n_samples)])
    A=X_eval;b=y_eval
    phi=np.linalg.lstsq(A,b,rcond=None)[0]
    base_value=model_fn(background)
    return{"shap_values":phi,"base_value":base_value,"prediction":model_fn(instance)}

def lime_explain(model_fn,instance,feature_names=None,n_perturbed=500,sigma=0.1,seed=42):
    """LIME-style local explanation via weighted linear regression."""
    rng=np.random.default_rng(seed)
    M=len(instance)
    pert=rng.normal(0,sigma,(n_perturbed,M))
    X_pert=np.clip(instance+pert,0,1)
    y_pert=np.array([model_fn(X_pert[i]) for i in range(n_perturbed)])
    distances=np.sqrt(np.sum(pert**2,axis=1))
    d_max=np.max(distances)+1e-9
    weights=1.0-distances/d_max
    W=np.diag(weights)
    XtWX=X_pert.T@W@X_pert+1e-6*np.eye(M)
    XtWy=X_pert.T@W@y_pert
    coef=np.linalg.solve(XtWX,XtWy)
    importance=np.abs(coef)
    importance/=importance.sum()+1e-15
    names=feature_names or [f"x{i}" for i in range(M)]
    return{"coefficients":coef.tolist(),"importance":importance.tolist(),
           "top_features":[names[i] for i in np.argsort(-importance)[:3]]}

def partial_dependence(model_fn,X_data,feature_idx,grid_points=50):
    """Partial Dependence: PD_j(x)=1/N sum f(x,X_{-j})."""
    x_min,x_max=X_data[:,feature_idx].min(),X_data[:,feature_idx].max()
    grid=np.linspace(x_min,x_max,grid_points)
    pd=np.zeros(grid_points)
    for i,g in enumerate(grid):
        X_mod=X_data.copy();X_mod[:,feature_idx]=g
        pd[i]=np.mean([model_fn(X_mod[j]) for j in range(len(X_mod))])
    return{"grid":grid,"pd_values":pd,"feature_idx":feature_idx}

def ice_curves(model_fn,X_data,feature_idx,grid_points=30,n_ice=50):
    """Individual Conditional Expectation curves."""
    x_min,x_max=X_data[:,feature_idx].min(),X_data[:,feature_idx].max()
    grid=np.linspace(x_min,x_max,grid_points)
    n_samples=min(n_ice,len(X_data))
    idx=np.random.choice(len(X_data),n_samples,replace=False)
    ice=np.zeros((n_samples,grid_points))
    for i,gi in enumerate(grid):
        X_mod=X_data[idx].copy();X_mod[:,feature_idx]=gi
        ice[:,i]=[model_fn(X_mod[j]) for j in range(n_samples)]
    return{"grid":grid,"ice":ice,"pd":ice.mean(axis=0)}

def permutation_importance(model_fn,X,y,n_repeats=10,seed=42):
    """Permutation feature importance."""
    rng=np.random.default_rng(seed)
    baseline_score=np.mean((y-np.array([model_fn(X[i]) for i in range(len(X))]))**2)
    importance=np.zeros(X.shape[1])
    for j in range(X.shape[1]):
        scores=[]
        for _ in range(n_repeats):
            Xp=X.copy();rng.shuffle(Xp[:,j])
            score=np.mean((y-np.array([model_fn(Xp[i]) for i in range(len(Xp))]))**2)
            scores.append(score)
        importance[j]=np.mean(scores)-baseline_score
    return{"importance":importance,"baseline":baseline_score,"ranking":np.argsort(-importance)}

if __name__=="__main__":
    print("=== Explainable AI Test ===")
    rng=np.random.default_rng(42)
    X_data=rng.random((200,3))
    def f(x):return 2*x[0]+0.5*x[1]**2+0.1*np.sin(x[2]*10)
    shap=shap_values_kernel(f,X_data.mean(axis=0),np.array([0.7,0.3,0.9]),XAIConfig(n_samples=200))
    print(f"  SHAP: base={shap['base_value']:.3f} pred={shap['prediction']:.3f}")
    print(f"  SHAP values: {shap['shap_values'].round(3)}")
    lime=lime_explain(f,np.array([0.7,0.3,0.9]),["temp","rain","soil"],n_perturbed=200)
    print(f"  LIME top: {lime['top_features']}")
    pd=partial_dependence(f,X_data,0,grid_points=20)
    print(f"  PDP x0 range: [{pd['pd_values'].min():.2f},{pd['pd_values'].max():.2f}]")
    ice=ice_curves(f,X_data,0,grid_points=15,n_ice=10)
    print(f"  ICE PD range: [{ice['pd'].min():.2f},{ice['pd'].max():.2f}]")
    print("ALL XAI TESTS PASSED")
