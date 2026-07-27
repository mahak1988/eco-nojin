"""NDVI helpers."""

from __future__ import annotations


def ndvi_from_bands(nir: float, red: float) -> float:
    denom = nir + red
    if abs(denom) < 1e-10:
        return 0.0
    return (nir - red) / denom


def classify_ndvi(v: float) -> str:
    if v < 0.1:
        return "bare_or_water"
    if v < 0.3:
        return "sparse"
    if v < 0.5:
        return "moderate"
    if v < 0.7:
        return "healthy"
    return "dense"
