"""NDVI anomaly & Vegetation Condition Index (VCI) helpers — free, pure Python."""

from __future__ import annotations

from typing import Any


def compute_vci_series(mean_ndvi_values: list[float]) -> list[dict[str, Any]]:
    """VCI = (NDVI - NDVI_min) / (NDVI_max - NDVI_min) * 100 over the series window.

    Drought rule-of-thumb: VCI < 40 → stress; < 20 → severe (literature ranges).
    """
    vals = [float(v) for v in mean_ndvi_values if v is not None]
    if not vals:
        return []
    vmin = min(vals)
    vmax = max(vals)
    span = vmax - vmin
    out: list[dict[str, Any]] = []
    for v in vals:
        if span < 1e-6:
            vci = 50.0
        else:
            vci = (v - vmin) / span * 100.0
        if vci >= 40:
            label = "no_drought"
        elif vci >= 30:
            label = "mild"
        elif vci >= 20:
            label = "moderate"
        elif vci >= 10:
            label = "severe"
        else:
            label = "extreme"
        out.append({"ndvi": round(v, 4), "vci": round(vci, 2), "label": label})
    return out


def compute_anomaly(
    mean_ndvi_values: list[float],
) -> list[dict[str, Any]]:
    """Anomaly vs series mean (proxy when multi-year climatology unavailable)."""
    vals = [float(v) for v in mean_ndvi_values if v is not None]
    if not vals:
        return []
    mu = sum(vals) / len(vals)
    return [
        {
            "ndvi": round(v, 4),
            "baseline": round(mu, 4),
            "anomaly": round(v - mu, 4),
            "signal": (
                "greening"
                if v - mu > 0.05
                else ("browning" if v - mu < -0.05 else "near_normal")
            ),
        }
        for v in vals
    ]
