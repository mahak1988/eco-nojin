"""
Ordinary Kriging for precipitation (CHIRPS / GPM style grids or station data).

Implements:
  - Experimental variogram
  - Theoretical models (spherical, exponential, gaussian)
  - Ordinary Kriging system of equations (§1.2.4 style)
  - Simple interface for gridded satellite precipitation downscaling / gap-filling

References: classic geostatistics (Cressie, Goovaerts) + remote-sensing precip literature.
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Tuple, Dict, List, Callable
from dataclasses import dataclass
from enum import Enum
from scipy.optimize import minimize
from scipy.spatial.distance import cdist


class VariogramModel(str, Enum):
    SPHERICAL = "spherical"
    EXPONENTIAL = "exponential"
    GAUSSIAN = "gaussian"
    LINEAR = "linear"


@dataclass
class VariogramParams:
    nugget: float = 0.0
    sill: float = 1.0
    range_: float = 10.0  # effective range
    model: VariogramModel = VariogramModel.SPHERICAL


def theoretical_variogram(
    h: np.ndarray,
    params: VariogramParams,
) -> np.ndarray:
    """
    γ(h) for common models.
    """
    nugget, sill, a = params.nugget, params.sill, params.range_
    c = sill - nugget  # partial sill
    h = np.asarray(h, dtype=float)
    gamma = np.zeros_like(h)

    if params.model == VariogramModel.SPHERICAL:
        mask = h <= a
        gamma[mask] = nugget + c * (1.5 * (h[mask] / a) - 0.5 * (h[mask] / a) ** 3)
        gamma[~mask] = sill
    elif params.model == VariogramModel.EXPONENTIAL:
        # effective range ≈ 3a
        gamma = nugget + c * (1.0 - np.exp(-3.0 * h / a))
    elif params.model == VariogramModel.GAUSSIAN:
        # effective range ≈ √3 a
        gamma = nugget + c * (1.0 - np.exp(-3.0 * (h / a) ** 2))
    elif params.model == VariogramModel.LINEAR:
        gamma = nugget + (sill - nugget) * np.minimum(h / a, 1.0)
    else:
        raise ValueError(f"Unknown model {params.model}")
    return gamma


def experimental_variogram(
    coords: np.ndarray,
    values: np.ndarray,
    n_lags: int = 15,
    max_dist: Optional[float] = None,
    min_pairs: int = 5,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute experimental (empirical) semivariogram.

    Returns
    -------
    lag_centers, gamma, counts
    """
    coords = np.asarray(coords)
    values = np.asarray(values).ravel()
    n = len(values)
    if coords.ndim != 2 or coords.shape[0] != n:
        raise ValueError("coords must be (n, 2)")

    dist = cdist(coords, coords)
    iu = np.triu_indices(n, k=1)
    d = dist[iu]
    v = 0.5 * (values[:, None] - values[None, :]) ** 2
    g = v[iu]

    if max_dist is None:
        max_dist = np.percentile(d, 75)

    bins = np.linspace(0, max_dist, n_lags + 1)
    lag_c = 0.5 * (bins[:-1] + bins[1:])
    gamma = np.full(n_lags, np.nan)
    counts = np.zeros(n_lags, dtype=int)

    for i in range(n_lags):
        mask = (d >= bins[i]) & (d < bins[i + 1])
        counts[i] = mask.sum()
        if counts[i] >= min_pairs:
            gamma[i] = np.mean(g[mask])

    valid = ~np.isnan(gamma)
    return lag_c[valid], gamma[valid], counts[valid]


def fit_variogram(
    lag: np.ndarray,
    gamma: np.ndarray,
    model: VariogramModel = VariogramModel.SPHERICAL,
    nugget_bounds: Tuple[float, float] = (0.0, None),
) -> VariogramParams:
    """
    Least-squares fit of theoretical model to experimental variogram.
    """
    lag = np.asarray(lag)
    gamma = np.asarray(gamma)
    sill0 = np.nanmax(gamma) if len(gamma) else 1.0
    range0 = np.nanmax(lag) * 0.6 if len(lag) else 10.0

    def loss(x):
        p = VariogramParams(nugget=x[0], sill=x[1], range_=x[2], model=model)
        pred = theoretical_variogram(lag, p)
        return np.sum((pred - gamma) ** 2)

    x0 = [0.0, sill0, range0]
    bounds = [
        (nugget_bounds[0], nugget_bounds[1] if nugget_bounds[1] is not None else sill0),
        (1e-8, None),
        (1e-3, None),
    ]
    res = minimize(loss, x0, bounds=bounds, method="L-BFGS-B")
    return VariogramParams(
        nugget=float(res.x[0]),
        sill=float(res.x[1]),
        range_=float(res.x[2]),
        model=model,
    )


def ordinary_kriging(
    train_coords: np.ndarray,
    train_values: np.ndarray,
    query_coords: np.ndarray,
    params: VariogramParams,
    max_points: Optional[int] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Ordinary Kriging.

    Solves the system:
        [ Γ   1 ] [ λ ]   [ γ ]
        [ 1ᵀ  0 ] [ μ ] = [ 1 ]

    where Γij = γ(|xi - xj|), γi = γ(|x0 - xi|)

    Returns
    -------
    estimates, kriging_variance
    """
    train_coords = np.asarray(train_coords, dtype=float)
    train_values = np.asarray(train_values, dtype=float).ravel()
    query_coords = np.asarray(query_coords, dtype=float)
    n = len(train_values)

    if query_coords.ndim == 1:
        query_coords = query_coords.reshape(1, -1)

    estimates = np.zeros(len(query_coords))
    variances = np.zeros(len(query_coords))

    # pre-compute train-train distances & gamma matrix
    dist_tt = cdist(train_coords, train_coords)
    gamma_tt = theoretical_variogram(dist_tt, params)

    for i, q in enumerate(query_coords):
        dist_tq = cdist(q.reshape(1, -1), train_coords).ravel()

        # optional neighbourhood
        if max_points is not None and n > max_points:
            idx = np.argsort(dist_tq)[:max_points]
            d_tq = dist_tq[idx]
            vals = train_values[idx]
            g_tt = gamma_tt[np.ix_(idx, idx)]
            m = max_points
        else:
            idx = np.arange(n)
            d_tq = dist_tq
            vals = train_values
            g_tt = gamma_tt
            m = n

        gamma_tq = theoretical_variogram(d_tq, params)

        # build OK system (m+1)
        A = np.ones((m + 1, m + 1))
        A[:m, :m] = g_tt
        A[m, m] = 0.0
        b = np.ones(m + 1)
        b[:m] = gamma_tq

        try:
            sol = np.linalg.solve(A, b)
        except np.linalg.LinAlgError:
            # singular → fall back to nearest neighbour
            estimates[i] = vals[np.argmin(d_tq)]
            variances[i] = params.sill
            continue

        lam = sol[:m]
        mu = sol[m]
        estimates[i] = np.dot(lam, vals)
        # kriging variance
        variances[i] = np.dot(lam, gamma_tq) + mu

    return estimates, variances


def kriging_precipitation(
    station_coords: np.ndarray,
    station_precip: np.ndarray,
    target_coords: np.ndarray,
    model: VariogramModel = VariogramModel.SPHERICAL,
    fit: bool = True,
    params: Optional[VariogramParams] = None,
    max_points: Optional[int] = 50,
) -> Dict[str, np.ndarray]:
    """
    High-level routine for precipitation (CHIRPS/GPM style).

    Parameters
    ----------
    station_coords : (n, 2) lon/lat or projected
    station_precip : (n,) precipitation values [mm]
    target_coords  : (m, 2) locations to estimate
    """
    if fit or params is None:
        lag, gamma, _ = experimental_variogram(station_coords, station_precip)
        if len(lag) < 3:
            # not enough pairs → pure IDW-like fallback
            params = VariogramParams(nugget=0.0, sill=np.var(station_precip) + 1e-6, range_=np.max(cdist(station_coords, station_coords))/2)
        else:
            params = fit_variogram(lag, gamma, model=model)

    est, var = ordinary_kriging(
        station_coords, station_precip, target_coords, params, max_points=max_points
    )
    # precipitation cannot be negative
    est = np.maximum(est, 0.0)

    return {
        "estimate": est,
        "variance": var,
        "params": params,
        "std": np.sqrt(np.maximum(var, 0.0)),
    }


# ---------------------------------------------------------------------------
# Grid helpers (for satellite product gap-filling / downscaling)
# ---------------------------------------------------------------------------

def make_grid(xmin: float, xmax: float, ymin: float, ymax: float, res: float) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return xx, yy, coords (N,2) for a regular grid."""
    xs = np.arange(xmin, xmax + res / 2, res)
    ys = np.arange(ymin, ymax + res / 2, res)
    xx, yy = np.meshgrid(xs, ys)
    coords = np.column_stack([xx.ravel(), yy.ravel()])
    return xx, yy, coords


if __name__ == "__main__":
    # Synthetic demo
    rng = np.random.default_rng(42)
    n_stat = 30
    coords = rng.uniform(0, 100, size=(n_stat, 2))
    # true field with spatial structure
    true = 20 + 10 * np.sin(coords[:, 0] / 20) + 5 * np.cos(coords[:, 1] / 15)
    precip = true + rng.normal(0, 1.5, n_stat)

    # target grid
    xx, yy, target = make_grid(0, 100, 0, 100, 5.0)

    result = kriging_precipitation(coords, precip, target, model=VariogramModel.SPHERICAL)
    print("Kriging precip demo")
    print(f"  fitted params: nugget={result['params'].nugget:.3f}, "
          f"sill={result['params'].sill:.3f}, range={result['params'].range_:.1f}")
    print(f"  estimate range: {result['estimate'].min():.2f} … {result['estimate'].max():.2f}")
    print(f"  mean kriging std: {result['std'].mean():.2f}")
