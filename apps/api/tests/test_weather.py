"""
Weather Module Tests
====================
Tests for climate alert evaluation and synthetic forecast generation.
"""

from datetime import date

from apps.weather.alerts import evaluate_alerts


class TestClimateAlerts:
    """Tests for evaluate_alerts function."""

    def test_empty_series(self) -> None:
        """Verify empty series returns no alerts."""
        assert evaluate_alerts([]) == []

    def test_frost_alert(self) -> None:
        """Verify frost alert triggered when tmin <= 0."""
        series = [
            {
                "date": "2024-01-15",
                "temp_min_c": -3,
                "temp_max_c": 5,
                "temp_mean_c": 1,
                "precip_mm": 0,
            }
        ]
        alerts = evaluate_alerts(series)
        frost = [a for a in alerts if a["type"] == "frost"]
        assert len(frost) == 1
        assert frost[0]["severity"] == "critical"  # tmin <= -2

    def test_frost_warning(self) -> None:
        """Verify frost warning when -2 < tmin <= 0."""
        series = [{"date": "2024-01-15", "temp_min_c": -1, "temp_max_c": 5}]
        alerts = evaluate_alerts(series)
        frost = [a for a in alerts if a["type"] == "frost"]
        assert len(frost) == 1
        assert frost[0]["severity"] == "warning"

    def test_heat_stress_alert(self) -> None:
        """Verify heat stress alert triggered when peak >= 38."""
        series = [{"date": "2024-07-15", "temp_max_c": 45, "precip_mm": 0}]
        alerts = evaluate_alerts(series)
        heat = [a for a in alerts if a["type"] == "heat_stress"]
        assert len(heat) == 1
        assert heat[0]["severity"] == "critical"  # peak >= 42

    def test_heat_stress_warning(self) -> None:
        """Verify heat stress warning when 38 <= peak < 42."""
        series = [{"date": "2024-07-15", "temp_max_c": 40, "precip_mm": 0}]
        alerts = evaluate_alerts(series)
        heat = [a for a in alerts if a["type"] == "heat_stress"]
        assert len(heat) == 1
        assert heat[0]["severity"] == "warning"

    def test_flood_alert(self) -> None:
        """Verify flood alert triggered when precip >= 40."""
        series = [{"date": "2024-06-15", "temp_max_c": 30, "precip_mm": 70}]
        alerts = evaluate_alerts(series)
        flood = [a for a in alerts if a["type"] == "flood"]
        assert len(flood) >= 1
        assert flood[0]["severity"] == "critical"  # precip >= 60

    def test_no_alerts_normal_conditions(self) -> None:
        """Verify no alerts for normal conditions."""
        series = [
            {
                "date": f"2024-01-{i:02d}",
                "temp_min_c": 10,
                "temp_max_c": 20,
                "temp_mean_c": 15,
                "precip_mm": 5,
            }
            for i in range(1, 5)
        ]
        alerts = evaluate_alerts(series)
        assert len(alerts) == 0

    def test_3day_flood_alert(self) -> None:
        """Verify 3-day rainfall sum flood alert."""
        series = []
        for i in range(5):
            series.append({"date": f"2024-06-{i + 10:02d}", "temp_max_c": 30, "precip_mm": 30})
        alerts = evaluate_alerts(series)
        three_day = [a for a in alerts if "3-day" in a["message"]]
        assert len(three_day) >= 1
        assert three_day[0]["severity"] == "critical"

    def test_dedup_alerts(self) -> None:
        """Verify duplicate alerts are removed."""
        row = {"date": "2024-06-15", "temp_max_c": 40, "precip_mm": 50}
        series = [row, row]
        alerts = evaluate_alerts(series)
        # Dedup based on (type, date, message[:40])
        assert len(alerts) == len({(a["type"], a.get("date"), a["message"][:40]) for a in alerts})


class TestSyntheticForecast:
    """Tests for synthetic forecast fallback."""

    def test_synthetic_forecast_basic(self) -> None:
        """Verify synthetic forecast returns expected structure."""
        from apps.weather.router import _synthetic_forecast

        result = _synthetic_forecast(lat=32.6, lon=51.7, days=7)
        assert result["provider"] == "synthetic-local"
        assert result["lat"] == 32.6
        assert result["lon"] == 51.7
        assert "daily" in result
        assert len(result["daily"]) == 7

    def test_synthetic_forecast_day_fields(self) -> None:
        """Verify each day has required fields."""
        from apps.weather.router import _synthetic_forecast

        result = _synthetic_forecast(lat=32.6, lon=51.7, days=3)
        for day in result["daily"]:
            assert "date" in day
            assert "temp_max_c" in day
            assert "temp_min_c" in day
            assert "precip_mm" in day
            assert "wind_m_s" in day
            assert "condition" in day

    def test_synthetic_climate_date_range(self) -> None:
        """Verify synthetic_climate returns correct date range."""
        from apps.weather.era5_chirps import synthetic_climate

        start = date(2024, 1, 1)
        end = date(2024, 1, 10)
        result = synthetic_climate(lat=32.6, lon=51.7, start=start, end=end)
        assert result["provider"] == "synthetic-climate"
        assert len(result["series"]) == 10
        assert result["series"][0]["date"] == "2024-01-01"
        assert result["series"][9]["date"] == "2024-01-10"
