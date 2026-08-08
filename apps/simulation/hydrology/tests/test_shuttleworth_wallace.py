"""Tests for Shuttleworth-Wallace."""
import pytest
from apps.simulation.hydrology.shuttleworth_wallace import shuttleworth_wallace_et
def test_et():
    r=shuttleworth_wallace_et(Rn=500,G=40,Ta=25,ea=1.2,u=2,LAI=3)
    assert r["ET_total"]>0
    assert r["ET_soil"]+r["ET_canopy"]==pytest.approx(r["ET_total"],0.02)
def test_lai():
    r1=shuttleworth_wallace_et(Rn=500,G=40,Ta=25,ea=1.2,u=2,LAI=1)
    r2=shuttleworth_wallace_et(Rn=500,G=40,Ta=25,ea=1.2,u=2,LAI=5)
    assert r2["ET_canopy"]>r1["ET_canopy"]
