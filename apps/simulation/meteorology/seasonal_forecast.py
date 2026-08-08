"""Seasonal forecast HMM + quantile downscaling — phase 14.3. Manifest §5.3"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Tuple
import numpy as np

class GaussianHMM:
    def __init__(self, n_states=3, seed=42):
        self.n_states = n_states
        rng = np.random.default_rng(seed)
        self.pi = np.ones(n_states)/n_states
        self.A = rng.random((n_states, n_states)); self.A /= self.A.sum(1, keepdims=True)
        self.mu = np.linspace(-1, 1, n_states); self.var = np.ones(n_states)

    def _emit(self, x):
        return np.exp(-0.5*(x-self.mu)**2/(self.var+1e-9))/np.sqrt(2*np.pi*(self.var+1e-9))

    def fit(self, series, n_iter=30):
        x = np.asarray(series, float); T, N = len(x), self.n_states
        for _ in range(n_iter):
            alpha = np.zeros((T,N)); alpha[0]=self.pi*self._emit(x[0]); alpha[0]/=alpha[0].sum()+1e-15
            for t in range(1,T):
                alpha[t]=self._emit(x[t])*(alpha[t-1]@self.A); alpha[t]/=alpha[t].sum()+1e-15
            beta=np.zeros((T,N)); beta[-1]=1.0
            for t in range(T-2,-1,-1):
                beta[t]=self.A@(self._emit(x[t+1])*beta[t+1]); beta[t]/=beta[t].sum()+1e-15
            gamma=alpha*beta; gamma/=gamma.sum(1,keepdims=True)+1e-15
            self.pi=gamma[0]
            for i in range(N):
                self.mu[i]=np.sum(gamma[:,i]*x)/(gamma[:,i].sum()+1e-15)
                self.var[i]=max(np.sum(gamma[:,i]*(x-self.mu[i])**2)/(gamma[:,i].sum()+1e-15),1e-4)
            xi=np.zeros((N,N))
            for t in range(T-1):
                num=np.outer(alpha[t], self._emit(x[t+1])*beta[t+1])*self.A
                xi+=num/(num.sum()+1e-15)
            self.A=xi/(xi.sum(1,keepdims=True)+1e-15)
        return self

    def sample(self, n, seed=None):
        rng=np.random.default_rng(seed); states=np.zeros(n,int); obs=np.zeros(n)
        states[0]=rng.choice(self.n_states,p=self.pi)
        obs[0]=rng.normal(self.mu[states[0]], np.sqrt(self.var[states[0]]))
        for t in range(1,n):
            states[t]=rng.choice(self.n_states,p=self.A[states[t-1]])
            obs[t]=rng.normal(self.mu[states[t]], np.sqrt(self.var[states[t]]))
        return states, obs

def quantile_map(sim, obs):
    sim, obs = np.asarray(sim,float), np.asarray(obs,float)
    qs = np.argsort(np.argsort(sim))/max(len(sim)-1,1)
    obs_sorted=np.sort(obs)
    idx=np.clip((qs*(len(obs_sorted)-1)).astype(int),0,len(obs_sorted)-1)
    return obs_sorted[idx]

def seasonal_forecast_demo():
    rng=np.random.default_rng(0)
    truth=np.array([0]*40+[1]*30+[2]*30+[1]*20)
    series=np.array([rng.normal([-0.5,0.2,1.0][s],0.3) for s in truth])
    hmm=GaussianHMM(3,1).fit(series,25)
    _, forecast=hmm.sample(60,2)
    return {"status":"ok", "forecast_mean": float(np.mean(forecast)), "mu": hmm.mu.tolist(), "A": hmm.A.tolist()}

if __name__ == "__main__":
    print(seasonal_forecast_demo()); print("OK")
