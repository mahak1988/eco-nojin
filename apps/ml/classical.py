"""
Pure-Python classical ML (no sklearn required).

- LinearRegression (OLS via normal equations with regularization)
- LogisticRegression (batch GD, multi-class one-vs-rest for 3 risk levels)
- ZScoreAnomalyDetector
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


def _dot(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


def _mat_vec(A: list[list[float]], v: list[float]) -> list[float]:
    return [_dot(row, v) for row in A]


def _transpose(A: list[list[float]]) -> list[list[float]]:
    return [list(col) for col in zip(*A)]


def _add_ridge(XtX: list[list[float]], lam: float) -> list[list[float]]:
    n = len(XtX)
    out = [row[:] for row in XtX]
    for i in range(n):
        out[i][i] += lam
    return out


def _solve_linear(A: list[list[float]], b: list[float]) -> list[float]:
    """Gaussian elimination with partial pivoting."""
    n = len(b)
    M = [A[i][:] + [b[i]] for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        M[col], M[pivot] = M[pivot], M[col]
        if abs(M[col][col]) < 1e-12:
            continue
        div = M[col][col]
        M[col] = [v / div for v in M[col]]
        for r in range(n):
            if r == col:
                continue
            factor = M[r][col]
            M[r] = [rv - factor * cv for rv, cv in zip(M[r], M[col])]
    return [M[i][n] for i in range(n)]


def sigmoid(z: float) -> float:
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)


@dataclass
class LinearModel:
    weights: list[float]  # includes bias as last
    feature_means: list[float]
    feature_stds: list[float]
    target_mean: float = 0.0
    target_std: float = 1.0
    name: str = "linear"

    def predict(self, x: list[float]) -> float:
        xn = [
            (xi - m) / (s if s > 1e-9 else 1.0)
            for xi, m, s in zip(x, self.feature_means, self.feature_stds)
        ]
        xn = xn + [1.0]
        y_n = _dot(self.weights, xn)
        return y_n * self.target_std + self.target_mean


@dataclass
class LogisticModel:
    """Binary or one-vs-rest multiclass."""

    weights: list[list[float]]  # C x (d+1)
    classes: list[str]
    feature_means: list[float]
    feature_stds: list[float]
    name: str = "logistic"

    def predict_proba(self, x: list[float]) -> dict[str, float]:
        xn = [
            (xi - m) / (s if s > 1e-9 else 1.0)
            for xi, m, s in zip(x, self.feature_means, self.feature_stds)
        ]
        xn = xn + [1.0]
        if len(self.classes) == 2:
            z = _dot(self.weights[0], xn)
            p1 = sigmoid(z)
            return {self.classes[0]: 1.0 - p1, self.classes[1]: p1}
        # softmax of OVR scores
        scores = [_dot(w, xn) for w in self.weights]
        m = max(scores)
        exps = [math.exp(s - m) for s in scores]
        s = sum(exps) or 1.0
        return {c: e / s for c, e in zip(self.classes, exps)}

    def predict(self, x: list[float]) -> str:
        proba = self.predict_proba(x)
        return max(proba.items(), key=lambda kv: kv[1])[0]


@dataclass
class ZScoreDetector:
    means: list[float]
    stds: list[float]
    threshold: float = 3.0
    name: str = "zscore_anomaly"

    def score(self, x: list[float]) -> dict[str, Any]:
        z = []
        for xi, m, s in zip(x, self.means, self.stds):
            z.append(abs(xi - m) / (s if s > 1e-9 else 1.0))
        max_z = max(z) if z else 0.0
        return {
            "max_z": round(max_z, 4),
            "z_per_feature": [round(v, 4) for v in z],
            "is_anomaly": max_z >= self.threshold,
            "threshold": self.threshold,
        }


def fit_linear(X: list[list[float]], y: list[float], ridge: float = 1e-2) -> LinearModel:
    n, d = len(X), len(X[0])
    means = [sum(X[i][j] for i in range(n)) / n for j in range(d)]
    stds = []
    for j in range(d):
        var = sum((X[i][j] - means[j]) ** 2 for i in range(n)) / max(n - 1, 1)
        stds.append(math.sqrt(var))
    y_mean = sum(y) / n
    y_var = sum((yi - y_mean) ** 2 for yi in y) / max(n - 1, 1)
    y_std = math.sqrt(y_var) or 1.0

    Xn = []
    for row in X:
        rn = [(row[j] - means[j]) / (stds[j] if stds[j] > 1e-9 else 1.0) for j in range(d)]
        rn.append(1.0)
        Xn.append(rn)
    yn = [(yi - y_mean) / y_std for yi in y]

    Xt = _transpose(Xn)
    XtX = [[_dot(Xt[i], Xt[j]) for j in range(d + 1)] for i in range(d + 1)]
    XtX = _add_ridge(XtX, ridge)
    Xty = [_dot(Xt[i], yn) for i in range(d + 1)]
    w = _solve_linear(XtX, Xty)
    return LinearModel(
        weights=w, feature_means=means, feature_stds=stds, target_mean=y_mean, target_std=y_std
    )


def fit_logistic(
    X: list[list[float]],
    y: list[str],
    classes: list[str] | None = None,
    lr: float = 0.15,
    epochs: int = 400,
) -> LogisticModel:
    n, d = len(X), len(X[0])
    classes = classes or sorted(set(y))
    means = [sum(X[i][j] for i in range(n)) / n for j in range(d)]
    stds = []
    for j in range(d):
        var = sum((X[i][j] - means[j]) ** 2 for i in range(n)) / max(n - 1, 1)
        stds.append(math.sqrt(var))
    Xn = []
    for row in X:
        rn = [(row[j] - means[j]) / (stds[j] if stds[j] > 1e-9 else 1.0) for j in range(d)]
        rn.append(1.0)
        Xn.append(rn)

    if len(classes) == 2:
        # positive = classes[1]
        ybin = [1.0 if yi == classes[1] else 0.0 for yi in y]
        w = [0.0] * (d + 1)
        for _ in range(epochs):
            grad = [0.0] * (d + 1)
            for i in range(n):
                p = sigmoid(_dot(w, Xn[i]))
                err = p - ybin[i]
                for j in range(d + 1):
                    grad[j] += err * Xn[i][j]
            for j in range(d + 1):
                w[j] -= lr * grad[j] / n
        return LogisticModel(weights=[w], classes=classes, feature_means=means, feature_stds=stds)

    # one-vs-rest
    weights: list[list[float]] = []
    for c in classes:
        ybin = [1.0 if yi == c else 0.0 for yi in y]
        w = [0.0] * (d + 1)
        for _ in range(epochs):
            grad = [0.0] * (d + 1)
            for i in range(n):
                p = sigmoid(_dot(w, Xn[i]))
                err = p - ybin[i]
                for j in range(d + 1):
                    grad[j] += err * Xn[i][j]
            for j in range(d + 1):
                w[j] -= lr * grad[j] / n
        weights.append(w)
    return LogisticModel(weights=weights, classes=classes, feature_means=means, feature_stds=stds)


def fit_zscore(X: list[list[float]], threshold: float = 3.0) -> ZScoreDetector:
    n, d = len(X), len(X[0])
    means = [sum(X[i][j] for i in range(n)) / n for j in range(d)]
    stds = []
    for j in range(d):
        var = sum((X[i][j] - means[j]) ** 2 for i in range(n)) / max(n - 1, 1)
        stds.append(math.sqrt(var) or 1.0)
    return ZScoreDetector(means=means, stds=stds, threshold=threshold)


@dataclass
class ModelBundle:
    yield_regressor: LinearModel
    risk_classifier: LogisticModel
    anomaly: ZScoreDetector
    metrics: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "yield_regressor": asdict(self.yield_regressor),
            "risk_classifier": asdict(self.risk_classifier),
            "anomaly": asdict(self.anomaly),
            "metrics": self.metrics,
        }

    @staticmethod
    def from_dict(d: dict[str, Any]) -> ModelBundle:
        return ModelBundle(
            yield_regressor=LinearModel(**d["yield_regressor"]),
            risk_classifier=LogisticModel(**d["risk_classifier"]),
            anomaly=ZScoreDetector(**d["anomaly"]),
            metrics=d.get("metrics") or {},
        )


def save_bundle(bundle: ModelBundle, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(bundle.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")


def load_bundle(path: Path) -> ModelBundle | None:
    if not path.is_file():
        return None
    try:
        return ModelBundle.from_dict(json.loads(path.read_text(encoding="utf-8")))
    except Exception:
        return None
