"""
Federated Averaging (FedAvg) + Differential Privacy — فاز ۱۳.۱

Privacy-preserving collaborative training across farms / edge devices
without sharing raw data.

Features:
  - Classic FedAvg (McMahan et al., 2017)
  - Client sampling
  - (ε, δ)-Differential Privacy via Gaussian mechanism on updates
  - Optional FedProx-style proximal term

Manifest refs: §4.4
Target path: apps/ml/federated/fedavg.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

import numpy as np


@dataclass
class DPConfig:
    """(ε, δ)-DP parameters for the Gaussian mechanism."""
    epsilon: float = 1.0
    delta: float = 1e-5
    clip_norm: float = 1.0
    noise_multiplier: Optional[float] = None

    def sigma(self) -> float:
        if self.noise_multiplier is not None:
            return self.noise_multiplier * self.clip_norm
        return self.clip_norm * np.sqrt(2.0 * np.log(1.25 / self.delta)) / max(self.epsilon, 1e-9)


@dataclass
class FedAvgConfig:
    n_rounds: int = 20
    local_epochs: int = 3
    learning_rate: float = 0.05
    client_fraction: float = 1.0
    batch_size: int = 16
    seed: int = 42
    dp: Optional[DPConfig] = None
    proximal_mu: float = 0.0


@dataclass
class ClientUpdate:
    client_id: str
    delta: np.ndarray
    n_samples: int


class SimpleLinearModel:
    def __init__(self, n_features: int, seed: int = 0):
        rng = np.random.default_rng(seed)
        self.w = rng.normal(0, 0.1, size=n_features)
        self.b = 0.0

    def params(self) -> np.ndarray:
        return np.concatenate([self.w, [self.b]])

    def set_params(self, p: np.ndarray):
        self.w = p[:-1].copy()
        self.b = float(p[-1])

    def predict(self, X: np.ndarray) -> np.ndarray:
        return X @ self.w + self.b

    def loss_grad(self, X: np.ndarray, y: np.ndarray) -> Tuple[float, np.ndarray]:
        pred = self.predict(X)
        err = pred - y
        loss = 0.5 * np.mean(err ** 2)
        grad_w = (X.T @ err) / len(y)
        grad_b = np.mean(err)
        return float(loss), np.concatenate([grad_w, [grad_b]])


def clip_l2(vec: np.ndarray, max_norm: float) -> np.ndarray:
    n = np.linalg.norm(vec)
    if n > max_norm:
        return vec * (max_norm / n)
    return vec


class FederatedServer:
    def __init__(self, model: SimpleLinearModel, config: Optional[FedAvgConfig] = None):
        self.model = model
        self.cfg = config or FedAvgConfig()
        self.rng = np.random.default_rng(self.cfg.seed)
        self.history: List[Dict] = []

    def select_clients(self, client_ids: List[str]) -> List[str]:
        n = max(1, int(len(client_ids) * self.cfg.client_fraction))
        return list(self.rng.choice(client_ids, size=n, replace=False))

    def aggregate(self, updates: List[ClientUpdate]) -> np.ndarray:
        total = sum(u.n_samples for u in updates)
        if total == 0:
            return self.model.params()
        agg = np.zeros_like(self.model.params())
        for u in updates:
            weight = u.n_samples / total
            delta = u.delta
            if self.cfg.dp is not None:
                delta = clip_l2(delta, self.cfg.dp.clip_norm)
            agg += weight * delta
        if self.cfg.dp is not None:
            sigma = self.cfg.dp.sigma()
            noise = self.rng.normal(0.0, sigma, size=agg.shape)
            agg = agg + noise
        return self.model.params() + agg


class FederatedClient:
    def __init__(self, client_id: str, X: np.ndarray, y: np.ndarray):
        self.client_id = client_id
        self.X = X
        self.y = y
        self.n = len(y)

    def local_train(self, global_params: np.ndarray, n_features: int, cfg: FedAvgConfig) -> ClientUpdate:
        model = SimpleLinearModel(n_features)
        model.set_params(global_params.copy())
        global_ref = global_params.copy()
        idx = np.arange(self.n)
        for _ in range(cfg.local_epochs):
            np.random.shuffle(idx)
            for start in range(0, self.n, cfg.batch_size):
                batch = idx[start:start + cfg.batch_size]
                loss, grad = model.loss_grad(self.X[batch], self.y[batch])
                if cfg.proximal_mu > 0:
                    prox = cfg.proximal_mu * (model.params() - global_ref)
                    grad = grad + prox
                new_p = model.params() - cfg.learning_rate * grad
                model.set_params(new_p)
        delta = model.params() - global_params
        return ClientUpdate(self.client_id, delta, self.n)


def run_fedavg(
    clients: List[FederatedClient],
    n_features: int,
    config: Optional[FedAvgConfig] = None,
    eval_fn: Optional[Callable[[np.ndarray], float]] = None,
    verbose: bool = True,
) -> Dict:
    cfg = config or FedAvgConfig()
    model = SimpleLinearModel(n_features, seed=cfg.seed)
    server = FederatedServer(model, cfg)
    client_ids = [c.client_id for c in clients]
    client_map = {c.client_id: c for c in clients}

    for rnd in range(cfg.n_rounds):
        selected = server.select_clients(client_ids)
        updates = []
        for cid in selected:
            upd = client_map[cid].local_train(model.params(), n_features, cfg)
            updates.append(upd)
        new_params = server.aggregate(updates)
        model.set_params(new_params)
        rec = {"round": rnd, "n_clients": len(selected)}
        if eval_fn is not None:
            rec["eval_loss"] = eval_fn(model.params())
        server.history.append(rec)
        if verbose and (rnd % max(1, cfg.n_rounds // 5) == 0 or rnd == cfg.n_rounds - 1):
            msg = f"  round {rnd:3d}  clients={len(selected)}"
            if "eval_loss" in rec:
                msg += f"  loss={rec['eval_loss']:.4f}"
            print(msg)

    privacy = None
    if cfg.dp is not None:
        privacy = {
            "epsilon": cfg.dp.epsilon,
            "delta": cfg.dp.delta,
            "sigma": cfg.dp.sigma(),
            "clip_norm": cfg.dp.clip_norm,
            "note": "Per-round Gaussian noise; compose carefully for total budget",
        }

    return {"status": "ok", "params": model.params(), "history": server.history, "privacy": privacy}


def make_synthetic_clients(
    n_clients: int = 5,
    n_samples: int = 80,
    n_features: int = 4,
    seed: int = 0,
) -> Tuple[List[FederatedClient], np.ndarray, np.ndarray]:
    rng = np.random.default_rng(seed)
    true_w = rng.normal(0, 1, size=n_features)
    clients = []
    all_X, all_y = [], []
    for i in range(n_clients):
        local_w = true_w + rng.normal(0, 0.15, size=n_features)
        X = rng.normal(0, 1, size=(n_samples, n_features))
        y = X @ local_w + rng.normal(0, 0.3, size=n_samples)
        clients.append(FederatedClient(f"farm_{i}", X, y))
        all_X.append(X)
        all_y.append(y)
    return clients, np.vstack(all_X), np.concatenate(all_y)


def run_fedavg_demo(with_dp: bool = True, verbose: bool = True) -> Dict:
    clients, X_all, y_all = make_synthetic_clients()
    n_features = X_all.shape[1]

    def eval_loss(params: np.ndarray) -> float:
        m = SimpleLinearModel(n_features)
        m.set_params(params)
        pred = m.predict(X_all)
        return float(0.5 * np.mean((pred - y_all) ** 2))

    dp = DPConfig(epsilon=2.0, delta=1e-5, clip_norm=0.5) if with_dp else None
    cfg = FedAvgConfig(n_rounds=15, local_epochs=2, learning_rate=0.08, client_fraction=0.8, dp=dp, proximal_mu=0.01)
    if verbose:
        print(f"Running FedAvg{' + DP' if with_dp else ''} …")
    result = run_fedavg(clients, n_features, cfg, eval_fn=eval_loss, verbose=verbose)
    if verbose and result["privacy"]:
        print(f"  DP: ε={result['privacy']['epsilon']}, σ={result['privacy']['sigma']:.4f}")
    return result


if __name__ == "__main__":
    print("=== FedAvg + DP self-test ===")
    out = run_fedavg_demo(with_dp=True, verbose=True)
    print(f"Status: {out['status']}")
    if out["history"]:
        print(f"Final eval loss: {out['history'][-1].get('eval_loss', 'n/a')}")
    print("OK")
