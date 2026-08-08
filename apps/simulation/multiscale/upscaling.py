"""
Multiscale Upscaling + GWR — فاز ۱۶.۱

Techniques:
  - Effective parameter homogenisation (arithmetic / harmonic / geometric)
  - Geographically Weighted Regression (GWR) for spatial coefficient surfaces

Manifest §7.2
Target: apps/simulation/multiscale/upscaling.py
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import numpy as np

def arithmetic_mean(values: np.ndarray, weights: Optional[np.ndarray] = None) -> float:
    if weights is None:
        return float(np.mean(values))
    return float(np.average(values, weights=weights))

def harmonic_mean(values: np.ndarray, weights: Optional[np.ndarray] = None) -> float:
    v = np.asarray(values, dtype=float)
    v = np.clip(v, 1e-15, None)
    if weights is None:
        return float(len(v) / np.sum(1.0 / v))
    return float(np.sum(weights) / np.sum(weights / v))

def geometric_mean(values: np.ndarray) -> float:
    v = np.asarray(values, dtype=float)
    v = np.clip(v, 1e-15, None)
    return float(np.exp(np.mean(np.log(v))))

def effective_conductivity(K: np.ndarray, direction: str = "isotropic") -> float:
    if direction == "horizontal":
        return arithmetic_mean(K)
    if direction == "vertical":
        return harmonic_mean(K)
    return geometric_mean(K)

@dataclass
class GWRResult:
    coefficients: np.ndarray
    predictions: np.ndarray
    bandwidth: float

def _gaussian_kernel(d: np.ndarray, bandwidth: float) -> np.ndarray:
    return np.exp(-0.5 * (d / bandwidth) ** 2)

def gwr_fit(coords: np.ndarray, X: np.ndarray, y: np.ndarray, bandwidth: float = 1.0) -> GWRResult:
    n, p = X.shape
    X_des = np.column_stack([np.ones(n), X])
    coefs = np.zeros((n, p + 1))
    preds = np.zeros(n)
    for i in range(n):
        d = np.sqrt(np.sum((coords - coords[i]) ** 2, axis=1))
        w = _gaussian_kernel(d, bandwidth)
        W = np.diag(w)
        XtW = X_des.T @ W
        try:
            beta = np.linalg.solve(XtW @ X_des, XtW @ y)
        except np.linalg.LinAlgError:
            beta = np.linalg.lstsq(XtW @ X_des, XtW @ y, rcond=None)[0]
        coefs[i] = beta
        preds[i] = X_des[i] @ beta
    return GWRResult(coefficients=coefs, predictions=preds, bandwidth=bandwidth)

def upscale_grid(field: np.ndarray, factor: int = 2, method: str = "mean") -> np.ndarray:
    ny, nx = field.shape
    ny2, nx2 = ny // factor, nx // factor
    out = np.zeros((ny2, nx2))
    for i in range(ny2):
        for j in range(nx2):
            block = field[i*factor:(i+1)*factor, j*factor:(j+1)*factor]
            if method == "mean":
                out[i, j] = np.mean(block)
            elif method == "min":
                out[i, j] = np.min(block)
            elif method == "max":
                out[i, j] = np.max(block)
            elif method == "harmonic":
                out[i, j] = harmonic_mean(block.ravel())
            else:
                out[i, j] = np.mean(block)
    return out

if __name__ == "__main__":
    print("=== Upscaling / GWR self-test ===")
    K = np.array([1.0, 2.0, 4.0, 8.0])
    print(f"  arithmetic={arithmetic_mean(K):.3f}  harmonic={harmonic_mean(K):.3f}  geometric={geometric_mean(K):.3f}")
    rng = np.random.default_rng(0)
    coords = rng.random((30, 2)) * 10
    X = rng.random((30, 2))
    y = 1.0 + 2.0 * X[:, 0] - 0.5 * X[:, 1] + rng.normal(0, 0.1, 30)
    gwr = gwr_fit(coords, X, y, bandwidth=3.0)
    print(f"  GWR pred RMSE={np.sqrt(np.mean((gwr.predictions - y)**2)):.4f}")
    grid = rng.random((16, 16))
    up = upscale_grid(grid, factor=4, method="mean")
    print(f"  upscale 16x16 → {up.shape}")
    print("OK")
