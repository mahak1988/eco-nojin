"""Unit tests for climate alert rules."""

from apps.weather.alerts import evaluate_alerts


def test_frost_alert():
    series = [{"date": "2026-01-01", "temp_min_c": -3, "precip_mm": 0, "temp_mean_c": -1}]
    alerts = evaluate_alerts(series)
    assert any(a["type"] == "frost" for a in alerts)


def test_flood_daily():
    series = [{"date": "2026-03-01", "temp_min_c": 10, "precip_mm": 55, "temp_mean_c": 15}]
    alerts = evaluate_alerts(series)
    assert any(a["type"] == "flood" for a in alerts)


def test_drought_window():
    series = []
    for i in range(20):
        series.append(
            {
                "date": f"2026-07-{i+1:02d}",
                "temp_min_c": 25,
                "temp_mean_c": 32,
                "precip_mm": 0.1,
            }
        )
    alerts = evaluate_alerts(series)
    assert any(a["type"] == "drought" for a in alerts)
