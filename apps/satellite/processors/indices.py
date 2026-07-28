"""Spectral indices for Sentinel-2 reflectance (0–1 scaled bands)."""

from __future__ import annotations

from typing import Iterable


def _safe_div(a: float, b: float) -> float:
    if abs(b) < 1e-9:
        return 0.0
    return a / b


def ndvi(nir: float, red: float) -> float:
    return _safe_div(nir - red, nir + red)


def ndwi(green: float, nir: float) -> float:
    return _safe_div(green - nir, green + nir)


def ndmi(nir: float, swir1: float) -> float:
    return _safe_div(nir - swir1, nir + swir1)


def evi(nir: float, red: float, blue: float = 0.05) -> float:
    """Enhanced Vegetation Index."""
    return 2.5 * _safe_div(nir - red, nir + 6 * red - 7.5 * blue + 1)


def smi(ndvi_v: float, ndwi_v: float, lst_proxy: float = 0.5) -> float:
    veg = max(0.0, min(1.0, (ndvi_v + 1) / 2))
    water = max(0.0, min(1.0, (ndwi_v + 1) / 2))
    dryness = max(0.0, min(1.0, lst_proxy))
    raw = 0.45 * water + 0.35 * veg + 0.20 * (1.0 - dryness)
    return max(0.0, min(1.0, raw))


def batch_ndvi(nir: Iterable[float], red: Iterable[float]) -> list[float]:
    return [ndvi(n, r) for n, r in zip(nir, red)]
