"""
Spectral indices for Sentinel-2 reflectance (0–1 scaled bands).

Standard public formulas (Huete, Gao, Rouse, etc.) — domain science, not proprietary.
Aligned with OpenFarm / AGRS / NASA Harvest common practice.
"""

from __future__ import annotations

from typing import Any, Iterable, Optional


def _safe_div(a: float, b: float) -> float:
    if abs(b) < 1e-9:
        return 0.0
    return a / b


def ndvi(nir: float, red: float) -> float:
    """Normalized Difference Vegetation Index."""
    return _safe_div(nir - red, nir + red)


def ndwi(green: float, nir: float) -> float:
    """McFeeters NDWI (water / moisture stress proxy)."""
    return _safe_div(green - nir, green + nir)


def ndmi(nir: float, swir1: float) -> float:
    """Normalized Difference Moisture Index."""
    return _safe_div(nir - swir1, nir + swir1)


def evi(nir: float, red: float, blue: float = 0.05) -> float:
    """Enhanced Vegetation Index (Huete)."""
    return 2.5 * _safe_div(nir - red, nir + 6 * red - 7.5 * blue + 1)


def savi(nir: float, red: float, L: float = 0.5) -> float:
    """Soil-Adjusted Vegetation Index (Huete 1988). L typically 0.5."""
    return _safe_div((nir - red) * (1.0 + L), nir + red + L)


def msavi(nir: float, red: float) -> float:
    """Modified SAVI (Qi et al.) — self-adjusting L."""
    # MSAVI2 form
    term = (2 * nir + 1) ** 2 - 8 * (nir - red)
    if term < 0:
        term = 0.0
    return 0.5 * (2 * nir + 1 - term**0.5)


def smi(ndvi_v: float, ndwi_v: float, lst_proxy: float = 0.5) -> float:
    veg = max(0.0, min(1.0, (ndvi_v + 1) / 2))
    water = max(0.0, min(1.0, (ndwi_v + 1) / 2))
    dryness = max(0.0, min(1.0, lst_proxy))
    raw = 0.45 * water + 0.35 * veg + 0.20 * (1.0 - dryness)
    return max(0.0, min(1.0, raw))


def canopy_cover_from_ndvi(
    ndvi_v: float,
    ndvi_min: float = 0.15,
    ndvi_max: float = 0.90,
) -> float:
    """
    Linear NDVI → fractional green canopy cover (0–1).
    Common first-order proxy for AquaCrop CC calibration (literature standard).
    """
    if ndvi_max <= ndvi_min:
        return 0.0
    cc = (ndvi_v - ndvi_min) / (ndvi_max - ndvi_min)
    return max(0.0, min(1.0, cc))


def compute_all_indices(
    red: float,
    nir: float,
    green: Optional[float] = None,
    blue: Optional[float] = None,
    swir1: Optional[float] = None,
) -> dict[str, float]:
    """Compute available indices from reflectance bands in [0, 1]."""
    out: dict[str, float] = {
        "ndvi": round(ndvi(nir, red), 6),
        "savi": round(savi(nir, red), 6),
        "msavi": round(msavi(nir, red), 6),
        "evi": round(evi(nir, red, blue if blue is not None else 0.05), 6),
    }
    out["canopy_cover"] = round(canopy_cover_from_ndvi(out["ndvi"]), 6)
    if green is not None:
        out["ndwi"] = round(ndwi(green, nir), 6)
        out["smi"] = round(smi(out["ndvi"], out["ndwi"]), 6)
    if swir1 is not None:
        out["ndmi"] = round(ndmi(nir, swir1), 6)
    return out


def batch_ndvi(nir: Iterable[float], red: Iterable[float]) -> list[float]:
    return [ndvi(n, r) for n, r in zip(nir, red)]


def indices_from_mean_reflectance(bands: dict[str, float]) -> dict[str, Any]:
    """
    bands keys: red/B04, nir/B08, optional green/B03, blue/B02, swir1/B11.
    """
    red = float(bands.get("red") or bands.get("B04") or 0.0)
    nir = float(bands.get("nir") or bands.get("B08") or 0.0)
    green = bands.get("green") or bands.get("B03")
    blue = bands.get("blue") or bands.get("B02")
    swir1 = bands.get("swir1") or bands.get("B11")
    g = float(green) if green is not None else None
    b = float(blue) if blue is not None else None
    s = float(swir1) if swir1 is not None else None
    return {
        "bands_used": {"red": red, "nir": nir, "green": g, "blue": b, "swir1": s},
        "indices": compute_all_indices(red, nir, g, b, s),
        "sentinel2_hint": "B04=red, B08=nir, B03=green, B02=blue, B11=swir1",
    }
