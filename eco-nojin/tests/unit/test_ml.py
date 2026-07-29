from apps.ml.classical import fit_linear, fit_logistic, fit_zscore
from apps.ml.service import predict_bundle, train_default_models
from apps.ml.synthetic_data import generate_dataset


def test_synthetic_shapes():
    X, y, c = generate_dataset(50, seed=1)
    assert len(X) == 50
    assert len(X[0]) == 10
    assert len(y) == 50
    assert set(c) <= {"low", "medium", "high"}


def test_linear_fit_predict():
    X, y, _ = generate_dataset(100, seed=2)
    m = fit_linear(X, y)
    p = m.predict(X[0])
    assert 0.0 <= p <= 1.5


def test_logistic_classes():
    X, _, c = generate_dataset(120, seed=3)
    m = fit_logistic(X, c, classes=["low", "medium", "high"])
    label = m.predict(X[0])
    assert label in {"low", "medium", "high"}
    proba = m.predict_proba(X[0])
    assert abs(sum(proba.values()) - 1.0) < 0.05


def test_zscore():
    X, _, _ = generate_dataset(80, seed=4)
    z = fit_zscore(X)
    s = z.score(X[0])
    assert "is_anomaly" in s


def test_train_and_predict():
    r = train_default_models(n_samples=300, seed=7)
    assert r["ok"] is True
    pred = predict_bundle(
        {
            "et0_mm_day": 6.0,
            "rain_mm_day": 0.2,
            "mean_ndvi": 0.25,
            "mean_canopy": 0.3,
            "soil_moisture": 15.0,
            "air_temp_c": 39.0,
            "irrigation_need_mm": 300.0,
            "yield_relative_proxy": 0.4,
            "runoff_mm_year": 20.0,
            "soc_delta": -1.0,
        }
    )
    assert "yield_relative_pred" in pred
    assert pred["risk_label"] in {"low", "medium", "high"}
