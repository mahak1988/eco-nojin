"""Fetcher produces consistent index series."""

from datetime import date, timedelta

from apps.satellite.fetchers.sentinel2 import fetch_indices, synthetic_series


def test_synthetic_series_length():
    end = date(2026, 7, 1)
    start = end - timedelta(days=30)
    rows = synthetic_series(32.65, 51.67, start, end, step_days=5)
    assert len(rows) >= 5
    for r in rows:
        assert -1 <= r.ndvi <= 1
        assert 0 <= r.smi <= 1


def test_fetch_indices_offline():
    rows = fetch_indices(32.65, 51.67, date.today() - timedelta(days=60), date.today())
    assert len(rows) > 0
    last = rows[-1].to_dict()
    assert "ndvi" in last
    assert "ndwi" in last
    assert "smi" in last
    assert -1.0 <= last["ndvi"] <= 1.0
    assert 0.0 <= last["smi"] <= 1.0
    assert last["provider"] in ("synthetic-s2", "planetary-computer-stac")
