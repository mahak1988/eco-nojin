"""Phase A — spectral indices and satellite→EcoCoin MRV bridge (offline)."""

from apps.satellite.mrv_bridge import mrv_from_bands, mrv_from_ndvi
from apps.satellite.processors.indices import (
    canopy_cover_from_ndvi,
    compute_all_indices,
    evi,
    ndvi,
    savi,
)


def test_ndvi_healthy_vegetation():
    v = ndvi(0.40, 0.08)
    assert 0.6 < v < 0.9


def test_ndvi_bare_soil_low():
    v = ndvi(0.15, 0.12)
    assert abs(v) < 0.25


def test_evi_and_savi_finite():
    assert -1.0 <= evi(0.35, 0.08, 0.04) <= 1.5
    assert -1.0 <= savi(0.35, 0.08) <= 1.5


def test_canopy_cover_clamped():
    assert canopy_cover_from_ndvi(0.0) == 0.0
    assert canopy_cover_from_ndvi(1.0) == 1.0
    mid = canopy_cover_from_ndvi(0.525)
    assert 0.4 < mid < 0.6


def test_compute_all_indices_keys():
    idx = compute_all_indices(0.08, 0.35, green=0.10, blue=0.05)
    assert "ndvi" in idx and "evi" in idx and "savi" in idx
    assert "canopy_cover" in idx and "ndwi" in idx


def test_mrv_from_ndvi_returns_mint_preview():
    out = mrv_from_ndvi(0.72, 0.75, measured_value=40.0, credit_type=0)
    assert out["mrv"]["quality_score"] >= 0.5
    assert out["mint_preview"]["ok"] is True
    assert out["mint_preview"]["mint_total"] > 0


def test_mrv_from_bands_pipeline():
    out = mrv_from_bands(
        0.08,
        0.35,
        green=0.10,
        model_yield_t_ha=4.2,
        field_yield_t_ha=4.0,
        measured_value=40.0,
    )
    assert "indices" in out and "mrv" in out and "mint_preview" in out
    assert out["mint_preview"]["quality_score"] == out["mrv"]["quality_score"]
