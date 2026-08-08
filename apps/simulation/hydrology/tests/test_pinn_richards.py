"""Tests for PINN Richards."""
import pytest
try:import torch;HAS=True
except:HAS=False
def test_import():
    from apps.simulation.hydrology.pinn_richards import PINN_M
    assert PINN_M is not None
@pytest.mark.skipif(not HAS,reason="no torch")
def test_forward():
    import torch
    from apps.simulation.hydrology.pinn_richards import PINN_M
    m=PINN_M();x=torch.linspace(0,1,10).reshape(-1,1);t=torch.ones_like(x)
    assert m(x,t).shape==(10,1)
