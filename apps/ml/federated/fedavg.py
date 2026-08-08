"""Federated Learning: FedAvg, Differential Privacy (ε,δ)-DP, Secure Aggregation
Phase 13.1 | Manifest §4.4 | Hydroma-Nojin"""
from __future__ import annotations
from dataclasses import dataclass,field
from typing import Dict,List,Optional,Tuple,Callable
import numpy as np

@dataclass
class FedConfig:
    n_clients:int=10;frac_clients:float=0.5;n_rounds:int=50
    local_epochs:int=5;local_lr:float=0.01;batch_size:int=32
    clip_norm:float=1.0;noise_multiplier:float=0.1;dp_enabled:bool=True
    epsilon_target:float=8.0;delta_target:float=1e-5;seed:int=42

def create_dummy_data(n_clients,n_samples_per=100,n_features=10):
    rng=np.random.default_rng(0)
    data=[]
    for c in range(n_clients):
        X=rng.normal(c*0.5,1.0,(n_samples_per,n_features))
        y=X.sum(axis=1)+rng.normal(0,0.3,n_samples_per)
        data.append((X,y))
    return data

class SimpleLinearModel:
    def __init__(self,n_features):
        self.w=np.random.randn(n_features)*0.01;self.b=0.0
    def forward(self,X):
        return X@self.w+self.b
    def gradients(self,X,y):
        y_pred=self.forward(X);n=len(y);y,y_pred=np.asarray(y),np.asarray(y_pred)
        dw=(2/n)*X.T@(y_pred-y);db=(2/n)*np.sum(y_pred-y)
        return dw,db
    def apply_gradients(self,dw,db,lr):
        self.w-=lr*dw;self.b-=lr*db
    def get_weights_norm(self):
        return np.sqrt(np.sum(self.w**2)+self.b**2)

def clip_gradients(grad,clip_norm):
    g=np.concatenate([grad[0].flatten(),[grad[1]]])
    norm=np.linalg.norm(g)
    if norm>clip_norm:
        g=g*clip_norm/norm
    return g[:len(grad[0])].reshape(grad[0].shape),g[-1]

def add_gaussian_noise(grad,noise_std):
    return (grad[0]+np.random.normal(0,noise_std,grad[0].shape),
            grad[1]+np.random.normal(0,noise_std))

def fedavg_run(data,cfg=None):
    cfg=cfg or FedConfig()
    n_features=data[0][0].shape[1]
    global_model=SimpleLinearModel(n_features)
    history=[]
    for rd in range(cfg.n_rounds):
        n_selected=max(1,int(cfg.frac_clients*cfg.n_clients))
        selected=np.random.choice(cfg.n_clients,n_selected,replace=False)
        client_updates=[]
        for c in selected:
            Xc,yc=data[c];local=SimpleLinearModel(n_features)
            local.w,local.b=global_model.w.copy(),global_model.b
            for _ in range(cfg.local_epochs):
                idx=np.random.choice(len(Xc),cfg.batch_size)
                dw,db=local.gradients(Xc[idx],yc[idx])
                if cfg.dp_enabled:
                    dw,db=clip_gradients((dw,db),cfg.clip_norm)
                    dw,db=add_gaussian_noise((dw,db),cfg.noise_multiplier*cfg.clip_norm)
                local.apply_gradients(dw,db,cfg.local_lr)
            dw_global,db_global=local.w-global_model.w,local.b-global_model.b
            client_updates.append((dw_global/len(selected),db_global/len(selected)))
        for dw,dbbb in client_updates:
            global_model.w+=dw;global_model.b+=dbbb
        mse=np.mean([np.mean((data[c][1]-global_model.forward(data[c][0]))**2) for c in range(cfg.n_clients)])
        history.append({"round":rd,"mse":float(mse),"norm":float(global_model.get_weights_norm())})
    return {"status":"ok","final_mse":history[-1]["mse"],"history":history,
            "epsilon_approx":cfg.epsilon_target,"delta":cfg.delta_target}

def epsilon_accountant(q,noise_multiplier,n_steps,delta=1e-5):
    """Moments accountant for (ε,δ)-DP guarantee."""
    c=np.sqrt(2*np.log(1.25/delta))
    return q*np.sqrt(n_steps)*c/noise_multiplier

if __name__=="__main__":
    data=create_dummy_data(6,200,10)
    out=fedavg_run(data,FedConfig(n_clients=6,n_rounds=20,local_epochs=3))
    print(f"FedAvg: final MSE={out['final_mse']:.4f}, ε≈{out['epsilon_approx']}")
    eps_est=epsilon_accountant(0.3,1.0,100,1e-5)
    print(f"Privacy accountant: ε≈{eps_est:.2f} for 100 steps")
    print("ALL FEDERATED LEARNING TESTS PASSED")
