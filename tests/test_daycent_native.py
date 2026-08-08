"""
تست‌های واحد برای ماژول daycent_native.py
"""

import sys
import os
# اضافه کردن مسیر اپلیکیشن به sys.path برای import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from apps.simulation.biogeochemistry.daycent_native import DayCentNative

def test_daycent_model_creation():
    """تست ایجاد مدل DayCent."""
    initial_pools = {
        "MET": 1.0,
        "STR": 2.0,
        "ACT": 0.5,
        "SLOW": 5.0,
        "PASS": 1.0,
        "DOC": 0.1,
        "BC": 0.5
    }
    model = DayCentNative(initial_pools)
    assert model.pools["MET"] == 1.0
    assert model.pools["STR"] == 2.0
    assert len(model.pools) == 7
    print("Test 1 PASSED: DayCentNative creation")

def test_daycent_model_step():
    """تست اجرای یک گام ساده از مدل."""
    initial_pools = {
        "MET": 10.0,
        "STR": 50.0,
        "ACT": 5.0,
        "SLOW": 100.0,
        "PASS": 20.0,
        "DOC": 2.0,
        "BC": 5.0
    }
    model = DayCentNative(initial_pools)

    # اجرای یک گام با شرایط مشخص
    temp, moisture, clay, o2, ph = 20, 0.3, 0.2, 0.2, 6.5
    model.step(temp, moisture, clay, o2, ph)

    # بررسی اینکه مقادیر کربن کاهش یافته‌اند (در شرایط عادی)
    # ممکن است برخی مقادیر بسیار کم تغییر کنند، بنابراین فقط یک مخزن اصلی چک می‌شود
    assert model.pools["MET"] <= 10.0
    assert model.pools["SLOW"] <= 100.0
    print("Test 2 PASSED: DayCentNative step execution")

if __name__ == "__main__":
    test_daycent_model_creation()
    test_daycent_model_step()
    print("All tests passed!")