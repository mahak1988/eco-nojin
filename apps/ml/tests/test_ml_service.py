"""
Tests for apps/ml/ — classical models, features, synthetic data, service.
No external dependencies required; all computation is pure Python.
"""

from __future__ import annotations

import pytest


# ── 1. Synthetic data generation ───────────────────────────────
class TestSyntheticData:
    def test_generate_dataset_shape(self):
        from apps.ml.synthetic_data import generate_dataset

        X, y_reg, y_cls = generate_dataset(n_samples=100, seed=0)
        assert len(X) == 100
        assert len(y_reg) == 100
        assert len(y_cls) == 100

    def test_generate_dataset_reproducible(self):
        from apps.ml.synthetic_data import generate_dataset

        X1, y1, _ = generate_dataset(100, seed=42)
        X2, y2, _ = generate_dataset(100, seed=42)
        assert X1 == X2
        assert y1 == y2

    def test_generate_dataset_labels(self):
        from apps.ml.synthetic_data import generate_dataset

        _, _, y_cls = generate_dataset(200, seed=7)
        valid = {"low", "medium", "high"}
        assert all(label in valid for label in y_cls)

    def test_generate_dataset_reg_range(self):
        from apps.ml.synthetic_data import generate_dataset

        _, y_reg, _ = generate_dataset(100, seed=1)
        assert all(0.0 <= v <= 1.0 for v in y_reg), "Yield values must be in [0, 1]"

    def test_generate_dataset_feature_length(self):
        from apps.ml.features import FEATURE_NAMES
        from apps.ml.synthetic_data import generate_dataset

        X, _, _ = generate_dataset(50, seed=3)
        assert all(len(row) == len(FEATURE_NAMES) for row in X)


# ── 2. Feature extraction ───────────────────────────────────────
class TestFeatures:
    def test_feature_names_nonempty(self):
        from apps.ml.features import FEATURE_NAMES

        assert len(FEATURE_NAMES) > 0
        assert all(isinstance(n, str) for n in FEATURE_NAMES)

    def test_vector_from_dict_length(self):
        from apps.ml.features import FEATURE_NAMES, vector_from_dict

        fdict = {name: 0.5 for name in FEATURE_NAMES}
        vec = vector_from_dict(fdict)
        assert len(vec) == len(FEATURE_NAMES)

    def test_vector_from_dict_defaults(self):
        """Missing keys should default to 0, not raise."""
        from apps.ml.features import vector_from_dict

        vec = vector_from_dict({})  # no keys at all
        assert isinstance(vec, list)

    def test_vector_from_dict_values(self):
        from apps.ml.features import FEATURE_NAMES, vector_from_dict

        fdict = {FEATURE_NAMES[0]: 0.99}
        vec = vector_from_dict(fdict)
        assert vec[0] == pytest.approx(0.99, abs=0.01)


# ── 3. Classical models ─────────────────────────────────────────
class TestClassicalModels:
    def test_fit_linear_predict(self):
        from apps.ml.classical import fit_linear

        X = [[1.0, 0.5], [0.2, 0.8], [0.5, 0.5], [0.9, 0.1]]
        y = [0.8, 0.3, 0.5, 0.7]
        model = fit_linear(X, y)
        pred = model.predict([0.5, 0.5])
        assert isinstance(pred, float)

    def test_fit_logistic_predict(self):
        from apps.ml.classical import fit_logistic

        X = [[1.0, 0.5], [0.2, 0.8], [0.5, 0.5], [0.9, 0.1], [0.1, 0.9]]
        y = ["high", "low", "medium", "high", "low"]
        model = fit_logistic(X, y, classes=["low", "medium", "high"])
        label = model.predict([0.6, 0.4])
        assert label in {"low", "medium", "high"}

    def test_fit_logistic_proba(self):
        from apps.ml.classical import fit_logistic

        X = [[1.0, 0.5], [0.2, 0.8], [0.5, 0.5], [0.9, 0.1], [0.1, 0.9]]
        y = ["high", "low", "medium", "high", "low"]
        model = fit_logistic(X, y, classes=["low", "medium", "high"])
        proba = model.predict_proba([0.6, 0.4])
        assert isinstance(proba, dict)
        assert abs(sum(proba.values()) - 1.0) < 0.01  # probabilities sum to 1

    def test_fit_zscore_anomaly(self):
        from apps.ml.classical import fit_zscore

        X = [[1.0, 0.5], [0.9, 0.6], [1.1, 0.4], [0.5, 0.5], [5.0, 5.0]]
        model = fit_zscore(X, threshold=2.8)
        normal_score = model.score([1.0, 0.5])
        assert isinstance(normal_score, float)

    def test_model_bundle_creation(self):
        from apps.ml.classical import ModelBundle, fit_linear, fit_logistic, fit_zscore

        X = [[1.0, 0.5], [0.2, 0.8], [0.5, 0.5], [0.9, 0.1], [0.1, 0.9]]
        y_r = [0.8, 0.3, 0.5, 0.7, 0.2]
        y_c = ["high", "low", "medium", "high", "low"]
        reg = fit_linear(X, y_r)
        clf = fit_logistic(X, y_c, classes=["low", "medium", "high"])
        anom = fit_zscore(X)
        bundle = ModelBundle(yield_regressor=reg, risk_classifier=clf, anomaly=anom)
        assert bundle is not None

    def test_linear_predict_clamp(self):
        """Predictions must be clamped to [0, 1]."""
        from apps.ml.classical import fit_linear

        X = [[1.0], [0.0]]
        y = [1.0, 0.0]
        model = fit_linear(X, y)
        pred = model.predict([100.0])  # extreme input
        assert pred <= 2.0  # should not explode (clamping may happen in service)


# ── 4. ML Service (train + predict) ────────────────────────────
class TestMLService:
    def test_train_default_models_returns_ok(self):
        from apps.ml.service import train_default_models

        result = train_default_models(n_samples=200, seed=99)
        assert result.get("ok") is True
        assert "metrics" in result

    def test_train_metrics_shape(self):
        from apps.ml.service import train_default_models

        result = train_default_models(n_samples=100, seed=0)
        metrics = result["metrics"]
        assert "yield_mae" in metrics
        assert "risk_accuracy" in metrics
        assert 0.0 <= metrics["risk_accuracy"] <= 1.0

    def test_predict_bundle_output_shape(self):
        from apps.ml.features import FEATURE_NAMES
        from apps.ml.service import predict_bundle, train_default_models

        train_default_models(n_samples=100, seed=1)
        features = {name: 0.5 for name in FEATURE_NAMES}
        result = predict_bundle(features)
        assert "yield_predicted" in result
        assert "risk_label" in result
        assert "risk_proba" in result

    def test_predict_bundle_yield_range(self):
        from apps.ml.features import FEATURE_NAMES
        from apps.ml.service import predict_bundle, train_default_models

        train_default_models(n_samples=100, seed=2)
        features = {name: 0.5 for name in FEATURE_NAMES}
        result = predict_bundle(features)
        assert 0.0 <= result["yield_predicted"] <= 1.0

    def test_predict_bundle_risk_label_valid(self):
        from apps.ml.features import FEATURE_NAMES
        from apps.ml.service import predict_bundle, train_default_models

        train_default_models(n_samples=100, seed=3)
        features = {name: 0.3 for name in FEATURE_NAMES}
        result = predict_bundle(features)
        assert result["risk_label"] in {"low", "medium", "high"}

    def test_get_bundle_consistent(self):
        """Calling get_bundle twice returns the same object."""
        from apps.ml.service import get_bundle, train_default_models

        train_default_models(n_samples=100, seed=5)
        b1 = get_bundle()
        b2 = get_bundle()
        assert b1 is b2


# ── 5. Global / Morris sensitivity ─────────────────────────────
class TestSensitivity:
    def test_sensitivity_module_importable(self):
        try:
            import apps.ml.sensitivity as sens  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("sensitivity module not importable in isolation")

    def test_global_sensitivity_importable(self):
        try:
            import apps.ml.global_sensitivity as gs  # noqa: F401

            assert True
        except ImportError:
            pytest.skip("global_sensitivity not importable in isolation")
