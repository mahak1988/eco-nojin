"""
PINN Inverse Problem — فاز ۹.۳
Joint estimation of van Genuchten (α, n, Ks) + state via PyTorch AutoGrad.
Architecture: 8-layer tanh network. Manifest §4.1.3
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import numpy as np
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = nn = None  # type: ignore

@dataclass
class InverseConfig:
    layers: List[int] = field(default_factory=lambda: [2, 64, 64, 64, 64, 64, 64, 64, 1])
    epochs: int = 1500
    n_collocation: int = 1500
    lr_net: float = 1e-3
    lr_params: float = 5e-4
    lambda_pde: float = 1.0
    lambda_data: float = 20.0
    z_max: float = 0.6
    t_max: float = 86400.0
    device: str = "cpu"
    alpha_bounds: Tuple[float, float] = (0.5, 5.0)
    n_bounds: Tuple[float, float] = (1.15, 2.5)
    ks_bounds: Tuple[float, float] = (1e-7, 1e-4)

if TORCH_AVAILABLE:
    class InverseNet(nn.Module):
        def __init__(self, layers: List[int]):
            super().__init__()
            mods = []
            for i in range(len(layers) - 2):
                mods += [nn.Linear(layers[i], layers[i+1]), nn.Tanh()]
            mods.append(nn.Linear(layers[-2], layers[-1]))
            self.net = nn.Sequential(*mods)
            for m in self.net:
                if isinstance(m, nn.Linear):
                    nn.init.xavier_normal_(m.weight); nn.init.zeros_(m.bias)
        def forward(self, x):
            return self.net(x)

class InverseRichardsPINN:
    """Joint VG parameter + field estimation from (z,t,h) observations."""
    def __init__(self, config: Optional[InverseConfig] = None):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch required")
        self.cfg = config or InverseConfig()
        self.device = torch.device(self.cfg.device)
        self.net = InverseNet(self.cfg.layers).to(self.device)
        self.log_alpha = nn.Parameter(torch.tensor(0.0, device=self.device))
        self.raw_n = nn.Parameter(torch.tensor(0.5, device=self.device))
        self.log_ks = nn.Parameter(torch.tensor(-12.0, device=self.device))
        self.opt = torch.optim.Adam([
            {"params": self.net.parameters(), "lr": self.cfg.lr_net},
            {"params": [self.log_alpha, self.raw_n, self.log_ks], "lr": self.cfg.lr_params},
        ])
        self.history: List[Dict] = []

    def _params(self):
        alpha = torch.exp(self.log_alpha).clamp(*self.cfg.alpha_bounds)
        n = (1.0 + torch.nn.functional.softplus(self.raw_n)).clamp(*self.cfg.n_bounds)
        ks = torch.exp(self.log_ks).clamp(*self.cfg.ks_bounds)
        return alpha, n, ks

    def _vg_theta(self, h, alpha, n, theta_s=0.42, theta_r=0.05):
        m = 1.0 - 1.0 / n
        se = (1.0 + torch.clamp(alpha * torch.abs(h), min=0.0) ** n) ** (-m)
        return theta_r + (theta_s - theta_r) * se

    def _vg_K(self, h, alpha, n, ks, l=0.5):
        m = 1.0 - 1.0 / n
        se = torch.clamp((1.0 + torch.clamp(alpha * torch.abs(h), min=0.0) ** n) ** (-m), 1e-8, 1.0)
        term = 1.0 - (1.0 - se ** (1.0 / m)) ** m
        return ks * (se ** l) * (term ** 2)

    def _pde_residual(self, z, t, alpha, n, ks):
        h = self.net(torch.cat([z, t], dim=1))
        h_z = torch.autograd.grad(h, z, grad_outputs=torch.ones_like(h), create_graph=True)[0]
        theta = self._vg_theta(h, alpha, n)
        theta_t = torch.autograd.grad(theta, t, grad_outputs=torch.ones_like(theta), create_graph=True, allow_unused=True)[0]
        if theta_t is None:
            theta_t = torch.zeros_like(h)
        K = self._vg_K(h, alpha, n, ks)
        flux = K * (h_z + 1.0)
        flux_z = torch.autograd.grad(flux, z, grad_outputs=torch.ones_like(flux), create_graph=True)[0]
        return theta_t - flux_z

    def train(self, observations: List[Tuple[float, float, float]], verbose: bool = True) -> List[Dict]:
        cfg = self.cfg
        obs_z = torch.tensor([o[0] for o in observations], dtype=torch.float32, device=self.device).view(-1, 1)
        obs_t = torch.tensor([o[1] for o in observations], dtype=torch.float32, device=self.device).view(-1, 1)
        obs_h = torch.tensor([o[2] for o in observations], dtype=torch.float32, device=self.device).view(-1, 1)
        for ep in range(cfg.epochs):
            self.opt.zero_grad()
            alpha, n, ks = self._params()
            z_c = (torch.rand(cfg.n_collocation, 1, device=self.device) * cfg.z_max).requires_grad_(True)
            t_c = (torch.rand(cfg.n_collocation, 1, device=self.device) * cfg.t_max).requires_grad_(True)
            loss_pde = torch.mean(self._pde_residual(z_c, t_c, alpha, n, ks) ** 2)
            h_pred = self.net(torch.cat([obs_z, obs_t], dim=1))
            loss_data = torch.mean((h_pred - obs_h) ** 2)
            loss = cfg.lambda_pde * loss_pde + cfg.lambda_data * loss_data
            loss.backward(); self.opt.step()
            rec = {"epoch": ep, "loss": float(loss.item()), "pde": float(loss_pde.item()),
                   "data": float(loss_data.item()), "alpha": float(alpha.item()),
                   "n": float(n.item()), "ks": float(ks.item())}
            self.history.append(rec)
            if verbose and (ep % max(1, cfg.epochs // 10) == 0 or ep == cfg.epochs - 1):
                print(f"  ep {ep:4d}  loss={rec['loss']:.3e}  α={rec['alpha']:.3f}  n={rec['n']:.3f}  Ks={rec['ks']:.2e}")
        return self.history

    def estimated_params(self) -> Dict[str, float]:
        a, n, ks = self._params()
        return {"alpha": float(a.item()), "n": float(n.item()), "ks": float(ks.item())}

def generate_synthetic_observations(n_obs: int = 30, noise_std: float = 0.05, seed: int = 42):
    rng = np.random.default_rng(seed)
    obs = []
    for _ in range(n_obs):
        z, t = float(rng.uniform(0.05, 0.55)), float(rng.uniform(0, 86400))
        h = -0.8 - 1.5 * z + 0.3 * np.sin(2 * np.pi * t / 86400) * np.exp(-z) + rng.normal(0, noise_std)
        obs.append((z, t, float(h)))
    return obs

def run_inverse_demo(epochs: int = 600, verbose: bool = True) -> Dict:
    if not TORCH_AVAILABLE:
        return {"status": "torch_unavailable"}
    cfg = InverseConfig(epochs=epochs, layers=[2, 48, 48, 48, 48, 48, 48, 1])
    model = InverseRichardsPINN(cfg)
    if verbose:
        print("Training Inverse PINN …")
    hist = model.train(generate_synthetic_observations(), verbose=verbose)
    return {"status": "ok", "loss_history": hist, "estimated_params": model.estimated_params()}

if __name__ == "__main__":
    print("=== PINN Inverse self-test ===")
    print(f"Torch available: {TORCH_AVAILABLE}")
    if TORCH_AVAILABLE:
        out = run_inverse_demo(epochs=200, verbose=True)
        print(f"Status: {out['status']}  params: {out.get('estimated_params')}")
    print("OK")
