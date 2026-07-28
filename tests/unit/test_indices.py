"""Unit tests for Sentinel spectral indices."""

from apps.satellite.processors.indices import ndmi, ndvi, ndwi, smi


def test_ndvi_healthy_veg():
    # high NIR, low red
    v = ndvi(0.6, 0.08)
    assert v > 0.5


def test_ndvi_water_or_bare():
    v = ndvi(0.1, 0.12)
    assert abs(v) < 0.2


def test_ndwi_water():
    # green high relative to NIR for water surfaces (simplified)
    v = ndwi(0.25, 0.05)
    assert v > 0.3


def test_smi_range():
    s = smi(0.7, 0.2, lst_proxy=0.2)
    assert 0.0 <= s <= 1.0


def test_ndmi():
    v = ndmi(0.5, 0.2)
    assert v > 0
