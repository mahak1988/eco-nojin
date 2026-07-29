from apps.simulation.soil_suite import (
    evaluate_soil_series,
    run_nitrate_leaching,
    soil_catalog,
    soil_health_score,
    texture_hydrology,
)


def test_catalog_min_15():
    assert soil_catalog()["count"] >= 15


def test_leaching():
    r = run_nitrate_leaching({"days": 30, "rain_mm_day": 3, "et_mm_day": 1})
    assert r["leached_total_kg_ha"] >= 0
    assert len(r["series"]) >= 2


def test_texture():
    t = texture_hydrology({"sand_pct": 50, "clay_pct": 20})
    assert t["awc_mm"] > 0


def test_health():
    h = soil_health_score({})
    assert "score" in h


def test_kge_pbias():
    m = evaluate_soil_series([1, 2, 3, 4], [1.1, 2.1, 2.9, 3.8])
    assert m.get("kge") is not None or m.get("nse") is not None
