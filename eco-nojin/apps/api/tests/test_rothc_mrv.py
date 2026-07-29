"""Phase C: RothC → soil_soc EcoCoin MRV."""

from apps.simulation.rothc_mrv import rothc_to_mrv


def test_rothc_to_mrv_positive_input():
    out = rothc_to_mrv(years=10, c_input_t_ha_y=2.0, soc_t_ha=40.0)
    assert out["credit_type"] == 2
    assert out["rothc"]["model"] == "rothc_26_3"
    assert "mrv" in out and "mint_preview" in out
    assert out["mint_preview"]["credit_name"] == "soil_soc"


def test_rothc_with_lab_soc_improves_components():
    out = rothc_to_mrv(
        years=5,
        c_input_t_ha_y=1.5,
        lab_soc_final_t_ha=42.0,
    )
    assert out["mrv"]["inputs"].get("field_data_present") is True or "model_field_agreement" in out[
        "mrv"
    ].get("components", {})


def test_rothc_zero_input_no_crash():
    out = rothc_to_mrv(years=1, c_input_t_ha_y=0.0, soc_t_ha=40.0)
    assert out["mint_preview"]["ok"] is True
