"""
PINN for Richards Equation — فاز ۹.۱
Mixed-form Richards: ∂θ/∂t = ∇·[K(h)∇(h+z)] − S
Architecture: 8–12 hidden layers, tanh. PyTorch + AutoGrad.
Manifest §4.1  |  Target: apps/simulation/hydrology/pinn_richards.py
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple
import numpy as np
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    torch = nn = None  # type: ignore

@dataclass
class VGParams:
    alpha: float = 1.0
    n: float = 1.5
    theta_s: float = 0.45
    theta_r: float = 0.05
    l: float = 0.5
    ks: float = 1e-5

def vg_theta(h, p: VGParams):
    m = 1.0 - 1.0 / p.n
    if TORCH_AVAILABLE and isinstance(h, torch.Tensor):
        se = (1.0 + torch.clamp(p.alpha * torch.abs(h), min=0.0) ** p.n) ** (-m)
        return p.theta_r + (p.theta_s - p.theta_r) * se
    ah = np.clip(p.alpha * np.abs(h), 0.0, None)
    se = (1.0 + ah ** p.n) ** (-m)
    return p.theta_r + (p.theta_s - p.theta_r) * se

def vg_K(h, p: VGParams):
    m = 1.0 - 1.0 / p.n
    if TORCH_AVAILABLE and isinstance(h, torch.Tensor):
        se = torch.clamp((1.0 + torch.clamp(p.alpha * torch.abs(h), min=0.0) ** p.n) ** (-m), 1e-8, 1.0)
        term = 1.0 - (1.0 - se ** (1.0 / m)) ** m
        return p.ks * (se ** p.l) * (term ** 2)
    ah = np.clip(p.alpha * np.abs(h), 0.0, None)
    se = np.clip((1.0 + ah ** p.n) ** (-m), 1e-8, 1.0)
    term = 1.0 - (1.0 - se ** (1.0 / m)) ** m
    return p.ks * (se ** p.l) * (term ** 2)

if TORCH_AVAILABLE:
    class RichardsNet(nn.Module):
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

@dataclass
class PINNConfig:
    layers: List[int] = field(default_factory=lambda: [2, 64, 64, 64, 64, 64, 64, 64, 64, 1])
    epochs: int = 1000
    n_collocation: int = 2000
    n_bc: int = 200
    n_ic: int = 200
    z_max: float = 1.0
    t_max: float = 86400.0
    lr: float = 1e-3
    lambda_pde: float = 1.0
    lambda_bc: float = 10.0
    lambda_ic: float = 10.0
    device: str = "cpu"

class RichardsPINNTrainer:
    def __init__(self, vg: Optional[VGParams] = None, config: Optional[PINNConfig] = None):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch required")
        self.vg = vg or VGParams()
        self.cfg = config or PINNConfig()
        self.device = torch.device(self.cfg.device)
        self.net = RichardsNet(self.cfg.layers).to(self.device)
        self.opt = torch.optim.Adam(self.net.parameters(), lr=self.cfg.lr)
        self.history: List[Dict] = []

    def _pde_residual(self, z, t):
        h = self.net(torch.cat([z, t], dim=1))
        h_z = torch.autograd.grad(h, z, grad_outputs=torch.ones_like(h), create_graph=True)[0]
        theta = vg_theta(h, self.vg)
        theta_t = torch.autograd.grad(theta, t, grad_outputs=torch.ones_like(theta), create_graph=True, allow_unused=True)[0]
        if theta_t is None:
            theta_t = torch.zeros_like(h)
        K = vg_K(h, self.vg)
        flux = K * (h_z + 1.0)
        flux_z = torch.autograd.grad(flux, z, grad_outputs=torch.ones_like(flux), create_graph=True)[0]
        return theta_t - flux_z

    def train(self, h_ic: float = -5.0, h_top: float = -0.5, verbose: bool = True):
        c = self.cfg
        for ep in range(c.epochs):
            self.opt.zero_grad()
            z_c = (torch.rand(c.n_collocation, 1, device=self.device) * c.z_max).requires_grad_(True)
            t_c = (torch.rand(c.n_collocation, 1, device=self.device) * c.t_max).requires_grad_(True)
            loss_pde = torch.mean(self._pde_residual(z_c, t_c) ** 2)
            z_ic = torch.rand(c.n_ic, 1, device=self.device) * c.z_max
            loss_ic = torch.mean((self.net(torch.cat([z_ic, torch.zeros_like(z_ic)], 1)) - h_ic) ** 2)
            z_top = torch.zeros(c.n_bc, 1, device=self.device)
            t_bc = torch.rand(c.n_bc, 1, device=self.device) * c.t_max
            loss_bc = torch.mean((self.net(torch.cat([z_top, t_bc], 1)) - h_top) ** 2)
            loss = c.lambda_pde * loss_pde + c.lambda_ic * loss_ic + c.lambda_bc * loss_bc
            loss.backward(); self.opt.step()
            rec = {"epoch": ep, "loss": float(loss.item()), "pde": float(loss_pde.item()),
                   "ic": float(loss_ic.item()), "bc": float(loss_bc.item())}
            self.history.append(rec)
            if verbose and (ep % max(1, c.epochs // 10) == 0 or ep == c.epochs - 1):
                print(f"  ep {ep:4d}  loss={rec['loss']:.3e}")
        return self.history

    def evaluate(self, z: np.ndarray, t: float) -> np.ndarray:
        self.net.eval()
        with torch.no_grad():
            zt = torch.tensor(z, dtype=torch.float32, device=self.device).view(-1, 1)
            return self.net(torch.cat([zt, torch.full_like(zt, t)], 1)).cpu().numpy().ravel()

    def predict_h(self, z, t):
        return self.net(torch.cat([z, t], dim=1))

def residual_check_numpy(h_func, z, t, vg, dz=0.01, dt=60.0):
    theta = vg_theta(h_func(z, t), vg)
    theta_old = vg_theta(h_func(z, t - dt), vg)
    dtheta_dt = (theta - theta_old) / dt
    h, K = h_func(z, t), vg_K(h_func(z, t), vg)
    h_p, h_m = h_func(z + dz, t), h_func(z - dz, t)
    flux_p = 0.5 * (K + vg_K(h_p, vg)) * ((h_p - h) / dz + 1.0)
    flux_m = 0.5 * (K + vg_K(h_m, vg)) * ((h - h_m) / dz + 1.0)
    return dtheta_dt - (flux_p - flux_m) / dz

def run_pinn_richards_demo(epochs: int = 500, device: str = "cpu", verbose: bool = True) -> Dict:
    if not TORCH_AVAILABLE:
        return {"status": "torch_unavailable", "message": "Install PyTorch"}
    vg = VGParams(alpha=2.0, n=1.4, theta_s=0.42, theta_r=0.05, ks=5e-6)
    cfg = PINNConfig(layers=[2, 32, 32, 32, 32, 1], epochs=epochs, n_collocation=800,
                     n_bc=100, n_ic=100, t_max=21600.0, z_max=0.5, device=device, lr=2e-3)
    trainer = RichardsPINNTrainer(vg=vg, config=cfg)
    if verbose:
        print("Training Richards PINN …")
    hist = trainer.train(h_ic=-5.0, h_top=-0.5, verbose=verbose)
    z = np.linspace(0.0, 0.5, 50)
    h = trainer.evaluate(z, t=cfg.t_max)
    return {"status": "ok", "loss_history": hist, "z": z, "h_final": h, "theta_final": vg_theta(h, vg)}

if __name__ == "__main__":
    print("=== PINN Richards self-test ===")
    print(f"Torch available: {TORCH_AVAILABLE}")
    if TORCH_AVAILABLE:
        out = run_pinn_richards_demo(epochs=200, verbose=True)
        print(f"Status: {out['status']}  final loss: {out['loss_history'][-1]['loss']:.3e}")
    else:
        def h_lin(z, t): return -1.0 - 2.0 * z
        r = residual_check_numpy(h_lin, np.linspace(0.05, 0.95, 20), 100.0, VGParams())
        print(f"Numpy residual mean |r| = {np.mean(np.abs(r)):.3e}")
    print("OK")
