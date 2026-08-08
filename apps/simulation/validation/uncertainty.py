"""Uncertainty Quantification — phase 17-18. PCE, Sobol, Morris, EnKF + NSE/RMSE/KGE."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Sequence, Tuple
import numpy as np

def nse(obs, sim):
    obs, sim = np.asarray(obs, float), np.asarray(sim, float)
    d = np.sum((obs - np.mean(obs))**2)
    return float("nan") if d < 1e-15 else float(1 - np.sum((obs-sim)**2)/d)

def rmse(obs, sim):
    return float(np.sqrt(np.mean((np.asarray(obs,float)-np.asarray(sim,float))**2)))

def kge(obs, sim):
    obs, sim = np.asarray(obs, float), np.asarray(sim, float)
    if len(obs) < 2: return float("nan")
    r = np.corrcoef(obs, sim)[0,1]
    a = np.std(sim)/(np.std(obs)+1e-15); b = np.mean(sim)/(np.mean(obs)+1e-15)
    return float(1 - np.sqrt((r-1)**2+(a-1)**2+(b-1)**2))

def pbias(obs, sim):
    obs, sim = np.asarray(obs, float), np.asarray(sim, float)
    return float(100*np.sum(sim-obs)/(np.sum(obs)+1e-15))

def r_squared(obs, sim):
    obs, sim = np.asarray(obs, float), np.asarray(sim, float)
    ss_tot = np.sum((obs-np.mean(obs))**2)
    return float("nan") if ss_tot < 1e-15 else float(1-np.sum((obs-sim)**2)/ss_tot)

def compute_all_metrics(obs, sim):
    return {"NSE": nse(obs,sim), "RMSE": rmse(obs,sim), "KGE": kge(obs,sim),
            "PBIAS": pbias(obs,sim), "R2": r_squared(obs,sim), "n": float(len(obs))}

@dataclass
class ParameterSpec:
    name: str; low: float; high: float; dist: str = "uniform"

def sample_parameters(specs, n, seed=None):
    rng = np.random.default_rng(seed); d = len(specs); U = rng.random((n,d)); X = np.zeros_like(U); names=[]
    for j,s in enumerate(specs):
        names.append(s.name)
        if s.dist == "loguniform":
            X[:,j] = np.exp(np.log(s.low)+(np.log(s.high)-np.log(s.low))*U[:,j])
        else:
            X[:,j] = s.low+(s.high-s.low)*U[:,j]
    return X, names

def _u2p(u, specs):
    x = np.zeros_like(u)
    for j,s in enumerate(specs):
        if s.dist=="loguniform": x[j]=np.exp(np.log(s.low)+(np.log(s.high)-np.log(s.low))*u[j])
        else: x[j]=s.low+(s.high-s.low)*u[j]
    return x

@dataclass
class MorrisResult:
    mu: np.ndarray; mu_star: np.ndarray; sigma: np.ndarray; names: List[str]

def morris_screening(model, specs, n_trajectories=20, n_levels=4, seed=42):
    rng = np.random.default_rng(seed); d=len(specs); p=n_levels
    delta = p/(2*(p-1)) if p>1 else 0.5; ees=np.zeros((n_trajectories,d))
    for t in range(n_trajectories):
        x = rng.integers(0,p,size=d).astype(float)/max(p-1,1)
        order = rng.permutation(d); y0=model(_u2p(x,specs))
        for j in order:
            x_new=x.copy(); step = delta if x[j]+delta<=1 else -delta
            x_new[j]=np.clip(x[j]+step,0,1); y1=model(_u2p(x_new,specs))
            ees[t,j]=(y1-y0)/(step+1e-15); x,y0=x_new,y1
    return MorrisResult(np.mean(ees,0), np.mean(np.abs(ees),0), np.std(ees,0,ddof=1), [s.name for s in specs])

@dataclass
class SobolResult:
    S1: np.ndarray; ST: np.ndarray; names: List[str]; n_base: int

def sobol_indices(model, specs, n_base=512, seed=42):
    rng=np.random.default_rng(seed); d=len(specs)
    A,B=rng.random((n_base,d)),rng.random((n_base,d))
    YA=np.array([model(_u2p(A[i],specs)) for i in range(n_base)])
    YB=np.array([model(_u2p(B[i],specs)) for i in range(n_base)])
    var_Y=np.var(YA,ddof=1); S1=np.zeros(d); ST=np.zeros(d)
    if var_Y<1e-15: return SobolResult(S1,ST,[s.name for s in specs],n_base)
    for j in range(d):
        ABj=A.copy(); ABj[:,j]=B[:,j]
        YAB=np.array([model(_u2p(ABj[i],specs)) for i in range(n_base)])
        S1[j]=float(np.clip(np.mean(YB*(YAB-YA))/var_Y,0,1))
        ST[j]=float(np.clip(0.5*np.mean((YA-YAB)**2)/var_Y,0,1))
    return SobolResult(S1,ST,[s.name for s in specs],n_base)

def _legendre(n,x):
    if n==0: return np.ones_like(x)
    if n==1: return x.copy()
    a,b=np.ones_like(x),x.copy()
    for k in range(2,n+1):
        a,b=b,((2*k-1)*x*b-(k-1)*a)/k
    return b

def _multi_indices(d, order):
    idx=[]
    def rec(pref, rd, ro):
        if rd==1:
            for a in range(ro+1): idx.append(pref+[a]); return
        for a in range(ro+1): rec(pref+[a], rd-1, ro-a)
    rec([], d, order); return np.array(idx, dtype=int)

@dataclass
class PCEResult:
    coefficients: np.ndarray; multi_indices: np.ndarray; mean: float; variance: float
    sobol_s1: Optional[np.ndarray]=None; names: Optional[List[str]]=None

def pce_fit(X_phys, y, specs, order=3):
    n,d=X_phys.shape; Xi=np.zeros_like(X_phys)
    for j,s in enumerate(specs):
        Xi[:,j]=np.clip(2*(X_phys[:,j]-s.low)/(s.high-s.low+1e-15)-1,-1,1)
    multi=_multi_indices(d,order); Psi=np.ones((n,len(multi)))
    for k,alpha in enumerate(multi):
        for j in range(d):
            if alpha[j]>0: Psi[:,k]*=_legendre(int(alpha[j]),Xi[:,j])
    coef,_,_,_=np.linalg.lstsq(Psi,y,rcond=None)
    mean=float(coef[0]); var=float(np.sum(coef[1:]**2)) if len(coef)>1 else 0.0
    s1=np.zeros(d)
    if var>1e-15:
        for j in range(d):
            mask=(multi[:,j]>0)&(np.sum(multi,1)==multi[:,j])
            s1[j]=float(np.sum(coef[mask]**2)/var)
    return PCEResult(coef, multi, mean, var, s1, [s.name for s in specs])

def pce_predict(result, X_phys, specs):
    n,d=X_phys.shape; Xi=np.zeros_like(X_phys)
    for j,s in enumerate(specs):
        Xi[:,j]=np.clip(2*(X_phys[:,j]-s.low)/(s.high-s.low+1e-15)-1,-1,1)
    yhat=np.zeros(n)
    for k,alpha in enumerate(result.multi_indices):
        term=np.ones(n)
        for j in range(d):
            if alpha[j]>0: term*=_legendre(int(alpha[j]),Xi[:,j])
        yhat+=result.coefficients[k]*term
    return yhat

@dataclass
class EnKFConfig:
    n_ensemble: int=50; inflation: float=1.02; obs_noise_std: float=0.1; seed: Optional[int]=42

@dataclass
class EnKFState:
    ensemble: np.ndarray; mean: np.ndarray; spread: np.ndarray

def enkf_update(ensemble, observation, H=None, R=None, config=None):
    cfg=config or EnKFConfig(); n_ens,n_state=ensemble.shape; n_obs=len(observation)
    rng=np.random.default_rng(cfg.seed)
    if H is None:
        H=np.zeros((n_obs,n_state)); H[:,:n_obs]=np.eye(n_obs)
    if R is None: R=(cfg.obs_noise_std**2)*np.eye(n_obs)
    x_mean=np.mean(ensemble,0); A=(ensemble-x_mean)*cfg.inflation
    Y=(H@ensemble.T).T; y_mean=np.mean(Y,0); AY=Y-y_mean
    Pxy=(A.T@AY)/(n_ens-1); Pyy=(AY.T@AY)/(n_ens-1)+R
    K=Pxy@np.linalg.inv(Pyy)
    obs_pert=observation+rng.normal(0,cfg.obs_noise_std,size=(n_ens,n_obs))
    analysis=ensemble+(K@(obs_pert-Y).T).T
    return EnKFState(analysis, np.mean(analysis,0), np.std(analysis,0,ddof=1))

def enkf_forecast(ensemble, forward, process_noise_std=0.0, seed=None):
    rng=np.random.default_rng(seed); forecast=np.array([forward(ensemble[i]) for i in range(len(ensemble))])
    if process_noise_std>0: forecast+=rng.normal(0,process_noise_std,forecast.shape)
    return forecast

@dataclass
class UQReport:
    morris: Optional[MorrisResult]=None; sobol: Optional[SobolResult]=None
    pce: Optional[PCEResult]=None; metrics: Optional[Dict[str,float]]=None

def run_uq_pipeline(model, specs, obs=None, sim=None, n_morris=15, n_sobol=256, n_pce=200, pce_order=2, seed=42):
    report=UQReport()
    report.morris=morris_screening(model,specs,n_trajectories=n_morris,seed=seed)
    report.sobol=sobol_indices(model,specs,n_base=n_sobol,seed=seed+1)
    X,_=sample_parameters(specs,n_pce,seed=seed+2)
    y=np.array([model(X[i]) for i in range(n_pce)])
    report.pce=pce_fit(X,y,specs,order=pce_order)
    if obs is not None and sim is not None: report.metrics=compute_all_metrics(obs,sim)
    return report

def batch_metric_evaluation(obs_list, sim_list):
    n=len(obs_list); out={k:np.zeros(n) for k in ("NSE","RMSE","KGE","PBIAS","R2")}
    for i,(o,s) in enumerate(zip(obs_list,sim_list)):
        m=compute_all_metrics(o,s)
        for k in out: out[k][i]=m[k]
    return out

def synthetic_farm_batch(n_farms=1000, n_days=30, seed=0):
    rng=np.random.default_rng(seed); obs_list,sim_list=[],[]
    for _ in range(n_farms):
        base=rng.uniform(2,8)
        obs=base+0.5*np.sin(np.linspace(0,4*np.pi,n_days))+rng.normal(0,0.2,n_days)
        sim=obs+rng.normal(0,0.3,n_days); obs_list.append(obs); sim_list.append(sim)
    return obs_list, sim_list

def run_uncertainty_demo(verbose=True):
    specs=[ParameterSpec("x1",-np.pi,np.pi),ParameterSpec("x2",-np.pi,np.pi),ParameterSpec("x3",-np.pi,np.pi)]
    def model(x): return float(np.sin(x[0])+7*np.sin(x[1])**2+0.1*x[2]**4*np.sin(x[0]))
    if verbose: print("Running UQ (Morris+Sobol+PCE+EnKF) …")
    report=run_uq_pipeline(model,specs,n_morris=12,n_sobol=128,n_pce=150,pce_order=2,seed=7)
    ens=np.random.default_rng(1).normal(0,1,(40,4))
    enkf=enkf_update(ens,np.array([0.5,-0.2]),config=EnKFConfig(seed=1))
    obs=np.linspace(1,5,50); sim=obs+np.random.default_rng(0).normal(0,0.15,50)
    metrics=compute_all_metrics(obs,sim)
    o,s=synthetic_farm_batch(500,20)
    batch=batch_metric_evaluation(o,s)
    out={"status":"ok","morris_mu_star":report.morris.mu_star.tolist(),
         "sobol_S1":report.sobol.S1.tolist(),"pce_mean":report.pce.mean,
         "pce_var":report.pce.variance,"enkf_mean":enkf.mean.tolist(),
         "metrics":metrics,"batch_nse_mean":float(np.nanmean(batch["NSE"]))}
    if verbose:
        print(f"  Morris μ*={out['morris_mu_star']}")
        print(f"  Sobol S1={out['sobol_S1']}")
        print(f"  PCE mean={out['pce_mean']:.4f} var={out['pce_var']:.4f}")
        print(f"  NSE={metrics['NSE']:.3f} KGE={metrics['KGE']:.3f} batchNSE={out['batch_nse_mean']:.3f}")
    return out

if __name__ == "__main__":
    print("=== Uncertainty self-test ===")
    print(run_uncertainty_demo(verbose=True)["status"]); print("OK")
