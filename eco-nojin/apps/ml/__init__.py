"""Classical ML for agriculture risk, yield proxy, anomaly detection."""

from apps.ml.service import predict_bundle, train_default_models

__all__ = ["predict_bundle", "train_default_models"]
