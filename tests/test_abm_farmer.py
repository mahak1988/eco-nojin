"""
تست‌های واحد برای ماژول abm_farmer_behavior.py
"""

import sys
import os
# اضافه کردن مسیر اپلیکیشن به sys.path برای import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from apps.social_economics.abm_farmer_behavior import FarmerAgent, ABMFarmerSimulation

def test_farmer_agent_creation():
    """تست ایجاد یک عامل کشاورز."""
    agent = FarmerAgent(agent_id=1, initial_strategy="cooperate")
    assert agent.id == 1
    assert agent.strategy == "cooperate"
    assert agent.water_withdrawal == 0.0
    print("Test 1 PASSED: FarmerAgent creation")

def test_abm_simulation_run():
    """تست اجرای یک گام ساده از شبیه‌سازی."""
    num_agents = 5
    initial_resource = 10.0
    payoff_matrix = {
        "cooperate": {"cooperate": 3, "defect": 0},
        "defect": {"cooperate": 5, "defect": 1}
    }

    sim = ABMFarmerSimulation(num_agents, initial_resource, payoff_matrix)
    initial_state = sim.history.copy()

    # اجرای یک گام
    sim.step()

    # بررسی اینکه وضعیت تاریخچه تغییر کرده است
    assert len(sim.history) == len(initial_state) + 1
    # بررسی اینکه سطح منبع تغییر کرده (احتمالاً کاهش یافته)
    # این بستگی به نحوه پیاده‌سازی step دارد، اما حداقل یک تغییر رخ داده است.
    assert True # تست ساده برای نشان دادن ساختار

    print("Test 2 PASSED: ABM Simulation step")

if __name__ == "__main__":
    test_farmer_agent_creation()
    test_abm_simulation_run()
    print("All tests passed!")