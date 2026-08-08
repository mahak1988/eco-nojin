"""Data Fusion STARFM + Kalman — phase 1.3. Manifest §1.3"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional
import numpy as np

@dataclass
class STARFMConfig:
    window: int = 7; n_candidates: int = 20; spectral_tol: float = 0.05

def _weight(s_diff, t_diff, d_spatial):
    eps = 1e-6
    return 1.0 / ((abs(s_diff)+eps)*(abs(t_diff)+eps)*(d_spatial+1.0)**2)

def starfm_fuse(fine_t0, coarse_t0, coarse_tk, cfg=None):
    cfg = cfg or STARFMConfig()
    fine_t0, coarse_t0, coarse_tk = map(lambda a: np.asarray(a, float), (fine_t0, coarse_t0, coarse_tk))
    multi = fine_t0.ndim == 3
    if not multi:
        fine_t0, coarse_t0, coarse_tk = fine_t0[...,None], coarse_t0[...,None], coarse_tk[...,None]
    H, W, B = fine_t0.shape; out = np.zeros_like(fine_t0); half = cfg.window // 2
    for i in range(H):
        for j in range(W):
            i0, i1 = max(0, i-half), min(H, i+half+1)
            j0, j1 = max(0, j-half), min(W, j+half+1)
            for b in range(B):
                cand = []
                for ii in range(i0, i1):
                    for jj in range(j0, j1):
                        s_diff = fine_t0[ii,jj,b] - coarse_t0[ii,jj,b]
                        t_diff = coarse_tk[ii,jj,b] - coarse_t0[ii,jj,b]
                        w = _weight(s_diff, t_diff, np.hypot(ii-i, jj-j))
                        pred = fine_t0[ii,jj,b] + (coarse_tk[ii,jj,b] - coarse_t0[ii,jj,b])
                        cand.append((w, pred))
                if not cand:
                    out[i,j,b] = fine_t0[i,j,b] + (coarse_tk[i,j,b]-coarse_t0[i,j,b])
                else:
                    cand = sorted(cand, key=lambda x: -x[0])[:cfg.n_candidates]
                    ws, ps = np.array([c[0] for c in cand]), np.array([c[1] for c in cand])
                    out[i,j,b] = np.sum(ws*ps)/(np.sum(ws)+1e-15)
    return out if multi else out[...,0]

@dataclass
class KalmanState:
    x: np.ndarray; P: np.ndarray

def kalman_update(state, z, H=None, R=None, Q=None):
    n = len(state.x)
    H = np.eye(n) if H is None else H
    R = np.eye(len(z))*0.01 if R is None else R
    Q = np.eye(n)*0.001 if Q is None else Q
    x_pred, P_pred = state.x.copy(), state.P + Q
    y = z - H @ x_pred; S = H @ P_pred @ H.T + R
    K = P_pred @ H.T @ np.linalg.inv(S)
    return KalmanState(x_pred + K@y, (np.eye(n)-K@H)@P_pred)

def demo_data_fusion():
    rng = np.random.default_rng(0); H,W = 12,12
    fine = 0.3 + 0.1*rng.random((H,W))
    coarse0 = fine + rng.normal(0,0.02,(H,W))
    coarse1 = coarse0 + 0.05 + rng.normal(0,0.01,(H,W))
    fused = starfm_fuse(fine, coarse0, coarse1, STARFMConfig(window=5, n_candidates=8))
    return {"status":"ok", "fused_mean": float(np.mean(fused)), "fused_std": float(np.std(fused))}

if __name__ == "__main__":
    print(demo_data_fusion()); print("OK")
