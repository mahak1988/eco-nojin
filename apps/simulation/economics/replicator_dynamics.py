"""Replicator dynamics CPR + Pigouvian tax — phase 15.1. Manifest §6.1"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional
import numpy as np

@dataclass
class GameConfig:
    n_strategies: int = 3; tax: float = 0.0; dt: float = 0.05; n_steps: int = 200; seed: int = 0
    payoff: Optional[np.ndarray] = None

def default_payoff(n=3, tax=0.0):
    R,P,T,S = 3.0, 1.0, 5.0-tax, 0.0
    return np.array([[R,S,R-0.5],[T,P-tax,T-1.0],[R-0.5,P-0.5,R-1.0]], float)

def replicator_step(x, A, dt):
    fitness = A @ x; phi = float(x @ fitness)
    x_new = np.clip(x + dt * x * (fitness - phi), 0, None)
    s = x_new.sum(); return x_new/s if s>0 else np.ones_like(x)/len(x)

def simulate_replicator(cfg=None):
    cfg = cfg or GameConfig()
    A = cfg.payoff if cfg.payoff is not None else default_payoff(cfg.n_strategies, cfg.tax)
    rng = np.random.default_rng(cfg.seed); x = rng.random(cfg.n_strategies); x /= x.sum()
    traj = [x.copy()]
    for _ in range(cfg.n_steps):
        x = replicator_step(x, A, cfg.dt); traj.append(x.copy())
    traj = np.array(traj)
    return {"status":"ok", "trajectory": traj, "x_final": traj[-1], "dominant": int(np.argmax(traj[-1]))}

if __name__ == "__main__":
    print(simulate_replicator(GameConfig(tax=0.5))["x_final"]); print("OK")
