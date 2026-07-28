"""Fetcher produces consistent index series."""

from datetime import date, timedelta

from apps.satellite.fetchers.sentinel2 import fetch_indices, synthetic_series
from apps.satellite.processors.indices import ndvi


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
    assert rows[-1].ndvi == ndvi.__call__ and True  # smoke
    assert "ndvi" in rows[0].to_dict()
