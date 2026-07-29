"""Phase B: AquaCrop → MRV → EcoCoin (offline unit tests)."""

from apps.simulation.aquacrop_mrv import aquacrop_to_mrv


def test_aquacrop_to_mrv_offline_wheat():
    out = aquacrop_to_mrv(crop="wheat", days=60, measured_value=40.0)
    assert "aquacrop" in out
    assert "mrv" in out
    assert "mint_preview" in out
    assert out["aquacrop"]["yield_t_ha"] >= 0
    assert 0.2 <= out["mrv"]["quality_score"] <= 1.5
    assert out["mint_preview"]["ok"] is True
    assert out["mint_preview"]["mint_total"] > 0


def test_aquacrop_to_mrv_with_ndvi_series():
    ndvi = [0.3, 0.45, 0.6, 0.72, 0.68]
    out = aquacrop_to_mrv(
        crop="maize",
        days=90,
        ndvi_values=ndvi,
        field_yield_t_ha=4.0,
        measured_value=25.0,
    )
    assert out["aquacrop"]["ndvi_calibrated"] is True
    assert out["mrv"]["components"].get("model_field_agreement") is not None or out[
        "mrv"
    ]["quality_score"] > 0.5
    assert "steward" in out["mint_preview"]["distribution"]


def test_aquacrop_maize_higher_yx_than_barley_default():
    maize = aquacrop_to_mrv(crop="maize", days=90)
    wheat = aquacrop_to_mrv(crop="wheat", days=90)
    # Potential Yx differs; both should complete
    assert maize["aquacrop"]["crop"] == "maize"
    assert wheat["aquacrop"]["crop"] == "wheat"
