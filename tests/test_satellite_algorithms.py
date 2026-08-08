"""
تست‌های واحد برای ماژول‌های الگوریتم‌های ماهواره‌ای
"""

import sys
import os
# اضافه کردن مسیر اپلیکیشن به sys.path برای import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from apps.satellite.algorithms.extended_water_cloud_model import calculate_soil_moisture_ewcm
from apps.satellite.algorithms.prosail_inversion import invert_prosail

def test_ewcm_calculation():
    """تست تابع محاسبه رطوبت EWCM."""
    sig_vv = np.array([-12.0])
    sig_vh = np.array([-19.0])
    lai = 1.5
    vwc = 0.15
    freq = 5.405e9
    angle = 39.0

    vsm = calculate_soil_moisture_ewcm(sig_vv, sig_vh, lai, vwc, freq, angle)
    # بررسی اینکه خروجی عددی و در محدوده منطقی است
    assert isinstance(vsm[0], float)
    assert 0.0 <= vsm[0] <= 1.0
    print("Test 1 PASSED: EWCM calculation")

def test_prosail_inversion():
    """تست تابع حل معکوس PROSAIL."""
    obs_refl = np.array([0.06, 0.09, 0.13, 0.26, 0.36, 0.43, 0.49, 0.36, 0.16])
    soil_albedo = np.array([0.11, 0.13, 0.16, 0.21, 0.29, 0.36, 0.41, 0.31, 0.11])
    init_guess = [2.1, 41.0, 0.011]

    params = invert_prosail(obs_refl, soil_albedo, init_guess)
    # بررسی اینکه خروجی شامل کلیدهای صحیح است
    assert "LAI" in params
    assert "Cab" in params
    assert "Cw" in params
    # بررسی محدوده فیزیکی ساده
    assert 0.1 <= params["LAI"] <= 8
    assert 5 <= params["Cab"] <= 80
    assert 0.004 <= params["Cw"] <= 0.03
    print("Test 2 PASSED: PROSAIL inversion")

if __name__ == "__main__":
    import numpy as np
    test_ewcm_calculation()
    test_prosail_inversion()
    print("All tests passed!")