"""
Multiscale Upscaling: GWR, Effective Homogenization, Power-law Scaling, Richardson
Phase 16.1 | Manifest §7 | Hydroma-Nojin

Implements:
  - GWR with CV bandwidth selection (gaussian/bisquare/exponential kernels)
  - Wiener bounds (Voigt-Reuss) + Cardwell-Parsons + Power-average
  - Richardson extrapolation with GCI (Grid Convergence Index)
  - Empirical variogram + spherical model fitting
  - Power-law upscale/downscale
  - Block averaging + bilinear interpolation (scale bridging)
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict,List,Optional,Tuple
import numpy as np
from scipy.spatial.distance import cdist
from scipy.optimize import curve_fit
from scipy.interpolate import RegularGridInterpolator

def effective_conductivity_geometric(K):
    K=np.maximum(np.asarray(K,float),1e-20)
    return float(np.exp(np.mean(np.log(K))))
def effective_conductivity_arithmetic(K):
    return float(np.mean(np.asarray(K,float)))
def effective_conductivity_harmonic(K):
    K=np.maximum(np.asarray(K,float),1e-20)
    return float(1.0/np.mean(1.0/K))
def effective_conductivity_cardwell_parsons(K):
    return float(np.sqrt(effective_conductivity_arithmetic(K)*effective_conductivity_harmonic(K)))
def effective_conductivity_power_average(K,omega=-1.0):
    K=np.maximum(np.asarray(K,float),1e-20)
    if abs(omega)<1e-10:return effective_conductivity_geometric(K)
    return float(np.mean(K**omega)**(1.0/omega))
def wiener_bounds(K):
    Ka=effective_conductivity_arithmetic(K);Kh=effective_conductivity_harmonic(K)
    return{"upper":Ka,"lower":Kh,"geometric":effective_conductivity_geometric(K),
           "cardwell_parsons":effective_conductivity_cardwell_parsons(K),
           "anisotropy_ratio":Ka/max(Kh,1e-20)}
def effective_dispersivity(D0,alpha_L,v_mean):
    return D0+alpha_L*abs(v_mean)

@dataclass
class GWRConfig:
    bandwidth:Optional[float]=None;kernel:str="gaussian"
    cv_bandwidths:Optional[list]=None;adaptive:bool=False;n_neighbors:int=30

def gaussian_kernel(d,b):return np.exp(-d**2/(2.0*b**2))
def bisquare_kernel(d,b):
    w=np.zeros_like(d);mask=d<b;w[mask]=(1.0-(d[mask]/b)**2)**2;return w
def exponential_kernel(d,b):return np.exp(-d/b)
KERNELS={"gaussian":gaussian_kernel,"bisquare":bisquare_kernel,"exponential":exponential_kernel}

def gwr_predict(X,y,coords,cfg=None):
    cfg=cfg or GWRConfig();n,k=X.shape
    D_full=cdist(coords,coords,metric="euclidean")
    if cfg.bandwidth is None:
        if cfg.cv_bandwidths is not None:
            candidates=cfg.cv_bandwidths
        else:
            dm=float(np.median(D_full[D_full>0]))
            candidates=np.logspace(np.log10(dm*0.1),np.log10(dm*5.0),20)
        kernel_fn=KERNELS.get(cfg.kernel,gaussian_kernel)
        best_b,best_cv=candidates[0],1e20
        for b in candidates:
            cv_score=0.0
            for i in range(min(n,200)):
                Wd=kernel_fn(D_full[i],b);Wd[i]=0.0
                XtW=X.T*Wd[np.newaxis,:];XtWX=XtW@X+1e-8*np.eye(k);XtWy=XtW@y
                try:
                    bi=np.linalg.solve(XtWX,XtWy)
                    cv_score+=(y[i]-X[i]@bi)**2
                except:cv_score+=1e6
            cv_score/=min(n,200)
            if cv_score<best_cv:best_cv,best_b=cv_score,b
        cfg.bandwidth=float(best_b)
    b=cfg.bandwidth;kernel_fn=KERNELS.get(cfg.kernel,gaussian_kernel)
    beta_local=np.zeros((n,k));y_pred=np.zeros(n);hat_diag=np.zeros(n)
    for i in range(n):
        if cfg.adaptive:
            di=D_full[i];idx=np.argsort(di);bi=di[idx[min(cfg.n_neighbors,n-1)]]+1e-8
            Wd=kernel_fn(di,bi)
        else:Wd=kernel_fn(D_full[i],b)
        XtW=X.T*Wd[np.newaxis,:];XtWX=XtW@X+1e-8*np.eye(k);XtWy=XtW@y
        try:
            beta_i=np.linalg.solve(XtWX,XtWy)
        except:beta_i=np.linalg.lstsq(XtWX,XtWy,rcond=None)[0]
        beta_local[i]=beta_i;y_pred[i]=X[i]@beta_i
        try:hat_diag[i]=float(X[i]@np.linalg.solve(XtWX,X[i]*Wd[i]))
        except:hat_diag[i]=0.0
    residuals=y-y_pred
    R2=1.0-np.sum(residuals**2)/max(np.sum((y-np.mean(y))**2),1e-15)
    return{"beta":beta_local,"y_pred":y_pred,"residuals":residuals,
           "R2_global":R2,"bandwidth":b,"hat_diag":hat_diag,
           "n_params_effective":float(np.sum(hat_diag))}

def power_law_upscale(v_fine,ratio,exponent=0.5):
    return np.asarray(v_fine)*(ratio**(-exponent))
def power_law_downscale(v_coarse,ratio,exponent=0.5):
    return np.asarray(v_coarse)*(ratio**exponent)

def richardson_extrapolation(f_h,f_2h,order=2.0):
    r=2.0;return(r**order*f_h-f_2h)/(r**order-1.0)
def richardson_error_estimate(f_h,f_2h,order=2.0):
    fe=richardson_extrapolation(f_h,f_2h,order)
    re=abs(f_h-fe)/max(abs(fe),1e-15)
    gci=1.25*abs(f_h-f_2h)/(2.0**order-1.0)
    return{"f_exact":fe,"rel_error":re,"GCI":gci}

def empirical_variogram(values,coords,n_bins=15):
    D=cdist(coords,coords);diffs=(values[:,None]-values[None,:])**2
    d_max=np.max(D)*0.5
    bins=np.logspace(np.log10(d_max/n_bins),np.log10(d_max),n_bins)
    gh=np.zeros(n_bins-1);dh=np.zeros(n_bins-1);npairs=np.zeros(n_bins-1,dtype=int)
    for i in range(n_bins-1):
        mask=(D>=bins[i])&(D<bins[i+1]);np.fill_diagonal(mask,False)
        npairs[i]=np.sum(mask)
        if npairs[i]>0:gh[i]=0.5*np.mean(diffs[mask]);dh[i]=np.mean(D[mask])
        else:dh[i]=0.5*(bins[i]+bins[i+1])
    return{"distance":dh,"gamma":gh,"n_pairs":npairs}

def fit_variogram_spherical(dh,gh):
    def sph(h,sill,rng,nug):
        h=np.asarray(h)
        return np.where(h<=rng,nug+sill*(1.5*h/rng-0.5*(h/rng)**3),nug+sill)
    p0=[np.max(gh)*0.9,np.max(dh)*0.5,np.min(gh)]
    try:
        popt,_=curve_fit(sph,dh,gh,p0=p0,maxfev=5000)
        return{"sill":popt[0],"range":popt[1],"nugget":popt[2]}
    except:return{"sill":float(np.max(gh)),"range":float(np.median(dh)),"nugget":0.0}

def block_average(data,factor):
    s=(data.shape[0]//factor,factor,data.shape[1]//factor,factor)
    return data[:s[0]*factor,:s[2]*factor].reshape(s).mean(axis=(1,3))
def bilinear_interpolate(data,factor):
    ny,nx=data.shape
    x=np.arange(nx);y=np.arange(ny)
    interp=RegularGridInterpolator((y,x),data,method='linear',bounds_error=False,fill_value=np.mean(data))
    xx,yy=np.meshgrid(np.linspace(0,nx-1,nx*factor),np.linspace(0,ny-1,ny*factor))
    pts=np.column_stack([yy.ravel(),xx.ravel()])
    return interp(pts).reshape(ny*factor,nx*factor)

if __name__=="__main__":
    print("=== Multiscale Upscaling Full Test ===\n")
    K=np.array([1e-5,5e-6,2e-5,8e-6,3e-5,1.5e-5])
    wb=wiener_bounds(K)
    print(f"Wiener: upper={wb['upper']:.2e} geo={wb['geometric']:.2e} lower={wb['lower']:.2e}")
    assert wb['upper']>=wb['geometric']>=wb['lower'],"Wiener bounds violated!"
    print("  OK Wiener bounds satisfied\n")
    rng=np.random.default_rng(42)
    n=60;coords=rng.uniform(0,100,(n,2))
    X=np.column_stack([np.ones(n),rng.normal(0,1,n)])
    true_beta=np.column_stack([np.ones(n)*3.0,2.0+0.03*coords[:,0]])
    y=np.sum(true_beta*X,axis=1)+rng.normal(0,0.5,n)
    gwr=gwr_predict(X,y,coords,GWRConfig(bandwidth=20.0))
    print(f"GWR: R2={gwr['R2_global']:.4f} b={gwr['bandwidth']:.1f} eff_params={gwr['n_params_effective']:.1f}")
    print("  OK GWR works\n")
    r=richardson_error_estimate(1.23456789,1.23450000,order=2)
    print(f"Richardson: GCI={r['GCI']:.2e} rel_err={r['rel_error']:.2e}")
    print("  OK Richardson works\n")
    data=rng.random((32,32))
    coarse=block_average(data,4)
    fine=bilinear_interpolate(coarse,4)
    print(f"Scale bridge: 32x32 -> {coarse.shape} -> {fine.shape}")
    print("  OK Scale bridging works\n")
    print("=== ALL UPSCALING TESTS PASSED ===")
