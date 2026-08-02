"""Phase 5 — offline E2E free science + MRV pipeline."""

from apps.simulation.science_pipeline_e2e import ISFAHAN_WHEAT, run_pipeline_sync


def test_e2e_isfahan_wheat_offline():
    out = run_pipeline_sync({"scenario_id": "isfahan-wheat", "use_live_ndvi": False})
    assert out["pipeline"] == "e2e_free_science_mrv_v1"
    assert out["cost"] == "zero"
    assert "ndvi" in out and out["ndvi"]["count"] > 0
    assert out["aquacrop"]["yield_t_ha"] is not None
    assert out["rothc"]["soc_final"] is not None
    assert out["mrv"]["assurance_level"] in ("L1", "L2", "L3")
    assert out["issuance"]["ok"] is True
    assert out["kpis"]["issuable"] is not None


def test_e2e_with_field_yield_raises_assurance():
    out = run_pipeline_sync(
        {
            "field_yield_t_ha": 4.0,
            "lab_soc_t_ha": 39.0,
        }
    )
    # triple-ish evidence → at least L2
    assert out["mrv"]["assurance_level"] in ("L2", "L3")


def test_isfahan_preset_coords():
    assert abs(ISFAHAN_WHEAT["lat"] - 32.65) < 0.01
    assert ISFAHAN_WHEAT["crop"] == "wheat"
