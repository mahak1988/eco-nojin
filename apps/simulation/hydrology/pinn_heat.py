"""
PINN for Soil Heat Transfer — فاز ۹.۲
1-D Fourier heat equation with de Vries C_v(θ) and λ(θ).
Architecture: 8–12 layer tanh. Manifest §2.5, §4.1.2
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
class ThermalParams:
    C_dry: float = 1.5e6
    C_water: float = 4.18e6
    lambda_dry: float = 0.25
    lambda_sat: float = 1.5
    theta_s: float = 0.45
    S_h: float = 0.0

def C_v(theta: float, p: ThermalParams) -> float:
    return p.C_dry + (p.C_water - p.C_dry) * (theta / p.theta_s)

def thermal_conductivity(theta: float, p: ThermalParams) -> float:
    sat = np.clip(theta / p.theta_s, 0.0, 1.0)
    return p.lambda_dry + (p.lambda_sat - p.lambda_dry) * sat

if TORCH_AVAILABLE:
    class HeatNet(nn.Module):
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
class PINNHeatConfig:
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

class SoilHeatPINN:
    def __init__(self, thermal=None, config=None, theta: float = 0.25):
        if not TORCH_AVAILABLE:
            raise RuntimeError("PyTorch required")
        self.thermal = thermal or ThermalParams()
        self.cfg = config or PINNHeatConfig()
        self.theta = theta
        self.device = torch.device(self.cfg.device)
        self.net = HeatNet(self.cfg.layers).to(self.device)
        self.opt = torch.optim.Adam(self.net.parameters(), lr=self.cfg.lr)
        self.history: List[Dict] = []

    def _sample(self):
        c = self.cfg
        z_c = (torch.rand(c.n_collocation, 1, device=self.device) * c.z_max).requires_grad_(True)
        t_c = (torch.rand(c.n_collocation, 1, device=self.device) * c.t_max).requires_grad_(True)
        z_ic = torch.rand(c.n_ic, 1, device=self.device) * c.z_max
        t_ic = torch.zeros(c.n_ic, 1, device=self.device)
        z_top = torch.zeros(c.n_bc, 1, device=self.device)
        t_bc = torch.rand(c.n_bc, 1, device=self.device) * c.t_max
        z_bot = torch.full((c.n_bc, 1), c.z_max, device=self.device).requires_grad_(True)
        return z_c, t_c, z_ic, t_ic, z_top, t_bc, z_bot

    def _pde(self, z, t):
        T = self.net(torch.cat([z, t], dim=1))
        T_z = torch.autograd.grad(T, z, grad_outputs=torch.ones_like(T), create_graph=True)[0]
        T_t = torch.autograd.grad(T, t, grad_outputs=torch.ones_like(T), create_graph=True)[0]
        T_zz = torch.autograd.grad(T_z, z, grad_outputs=torch.ones_like(T_z), create_graph=True)[0]
        Cv = C_v(self.theta, self.thermal)
        lam = thermal_conductivity(self.theta, self.thermal)
        return Cv * T_t - lam * T_zz - self.thermal.S_h

    def train(self, T_init: float = 15.0, T_surface: float = 25.0, verbose: bool = True):
        c = self.cfg
        for ep in range(c.epochs):
            self.opt.zero_grad()
            z_c, t_c, z_ic, t_ic, z_top, t_bc, z_bot = self._sample()
            loss_pde = torch.mean(self._pde(z_c, t_c) ** 2)
            loss_ic = torch.mean((self.net(torch.cat([z_ic, t_ic], 1)) - T_init) ** 2)
            loss_top = torch.mean((self.net(torch.cat([z_top, t_bc], 1)) - T_surface) ** 2)
            T_bot = self.net(torch.cat([z_bot, t_bc], 1))
            T_bot_z = torch.autograd.grad(T_bot, z_bot, grad_outputs=torch.ones_like(T_bot), create_graph=True)[0]
            loss_bot = torch.mean(T_bot_z ** 2)
            loss = c.lambda_pde * loss_pde + c.lambda_ic * loss_ic + c.lambda_bc * (loss_top + loss_bot)
            loss.backward(); self.opt.step()
            rec = {"epoch": ep, "loss": float(loss.item()), "pde": float(loss_pde.item()),
                   "ic": float(loss_ic.item()), "bc": float((loss_top + loss_bot).item())}
            self.history.append(rec)
            if verbose and (ep % max(1, c.epochs // 10) == 0 or ep == c.epochs - 1):
                print(f"  ep {ep:4d}  loss={rec['loss']:.3e}  pde={rec['pde']:.3e}")
        return self.history

    def predict(self, z: np.ndarray, t: float) -> np.ndarray:
        self.net.eval()
        with torch.no_grad():
            zt = torch.tensor(z, dtype=torch.float32, device=self.device).view(-1, 1)
            return self.net(torch.cat([zt, torch.full_like(zt, t)], 1)).cpu().numpy().ravel()

def run_pinn_heat_demo(epochs: int = 400, verbose: bool = True) -> Dict:
    if not TORCH_AVAILABLE:
        return {"status": "torch_unavailable"}
    cfg = PINNHeatConfig(layers=[2, 48, 48, 48, 48, 48, 48, 48, 1], epochs=epochs,
                         n_collocation=1200, t_max=43200.0, z_max=0.8)
    model = SoilHeatPINN(config=cfg, theta=0.28)
    if verbose:
        print("Training Soil-Heat PINN …")
    hist = model.train(T_init=18.0, T_surface=28.0, verbose=verbose)
    z = np.linspace(0, cfg.z_max, 40)
    T = model.predict(z, t=cfg.t_max)
    return {"status": "ok", "loss_history": hist, "z": z, "T_final": T,
            "T_range": (float(T.min()), float(T.max()))}

if __name__ == "__main__":
    print("=== PINN Soil Heat self-test ===")
    print(f"Torch available: {TORCH_AVAILABLE}")
    if TORCH_AVAILABLE:
        out = run_pinn_heat_demo(epochs=150, verbose=True)
        print(f"Status: {out['status']}  T_range: {out.get('T_range')}")
    print("OK")
