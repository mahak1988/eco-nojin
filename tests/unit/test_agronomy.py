from apps.crops.agronomy_services import disease_rules, rotation_plan, yield_prediction
from apps.planting.season import season_plan
from apps.weather.alerts import evaluate_alerts


def test_rotation():
    r = rotation_plan("wheat", 3)
    assert len(r["sequence"]) == 3


def test_yield():
    y = yield_prediction("wheat", area_ha=2, water_stress=0.1)
    assert y["total_t"] > 0


def test_disease():
    assert len(disease_rules("wheat")) >= 1


def test_season():
    s = season_plan("wheat")
    assert "stages" in s


def test_heat_alert():
    series = [{"date": "2026-07-01", "temp_max_c": 43, "temp_min_c": 28, "precip_mm": 0}]
    a = evaluate_alerts(series)
    assert any(x["type"] == "heat_stress" for x in a)
