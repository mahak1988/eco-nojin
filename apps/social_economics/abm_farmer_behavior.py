"""
ماژول موتور ABM رفتار کشاورز - نسخه اولیه

این ماژول بخشی از تلاش برای پیاده‌سازی مرحله ۳ مانیفست Hydroma-Nojin است.
هدف: پیاده‌سازی یک مدل مبتنی بر عامل (ABM) برای شبیه‌سازی رفتار کشاورزان تحت تأثیر نظریه بازی.
این نسخه یک مدل ساده شده از بازی منابع مشترک (Common-Pool Resource Game) را پیاده‌سازی می‌کند.
"""

import numpy as np
from typing import List, Dict
import random


class FarmerAgent:
    """
    یک عامل کشاورز که در یک محیط ABM رفتار می‌کند.
    """

    def __init__(self, agent_id: int, initial_strategy: str = "cooperate"):
        self.id = agent_id
        self.strategy = initial_strategy  # "cooperate" یا "defect"
        self.water_withdrawal = 0.0 # میزان آبی که در دور فعلی برداشت می‌کند
        self.history = [] # تاریخچه استراتژی‌ها
        self.payoff = 0.0 # پرداختی/سود در دور فعلی

    def decide_withdrawal(self, total_others_withdrawal: float, resource_level: float, strategy: str) -> float:
        """
        تصمیم گیری در مورد میزان برداشت آب بر اساس استراتژی و وضعیت منبع.
        این تابع می‌تواند پیچیده‌تر شود.
        """
        # یک مدل ساده: همکار (cooperate) کمتر بر می‌دارد، تقلب‌کن (defect) بیشتر.
        base_withdrawal = 0.5 # میزان پایه
        if strategy == "defect":
            self.water_withdrawal = min(base_withdrawal * 1.5, resource_level * 0.8) # تا ۸۰٪ منبع
        else: # cooperate
            self.water_withdrawal = min(base_withdrawal, resource_level * 0.5) # تا ۵۰٪ منبع

        return self.water_withdrawal

    def update_strategy(self, neighbors_strategies: List[str], payoff_matrix: Dict):
        """
        به‌روزرسانی استراتژی بر اساس موفقیت همسایگان (الگوریتم دینامیک تکاملی).
        """
        # تعداد همسایگان با هر استراتژی
        defect_count = neighbors_strategies.count("defect")
        coop_count = neighbors_strategies.count("cooperate")

        # پرداختی متوسط همسایگان
        avg_payoff_defect = payoff_matrix["defect"]["defect"] * (defect_count / len(neighbors_strategies)) + \
                            payoff_matrix["defect"]["cooperate"] * (coop_count / len(neighbors_strategies))
        avg_payoff_coop = payoff_matrix["cooperate"]["defect"] * (defect_count / len(neighbors_strategies)) + \
                          payoff_matrix["cooperate"]["cooperate"] * (coop_count / len(neighbors_strategies))

        # تصمیم گیری: احتمال تغییر استراتژی بر اساس تفاوت پرداختی
        current_payoff = payoff_matrix[self.strategy]["defect"] * (defect_count / len(neighbors_strategies)) + \
                         payoff_matrix[self.strategy]["cooperate"] * (coop_count / len(neighbors_strategies))

        if self.strategy == "cooperate" and avg_payoff_defect > current_payoff:
            prob_change = min(1.0, (avg_payoff_defect - current_payoff) / 10.0) # تابع دلخواه
            if random.random() < prob_change:
                self.strategy = "defect"
        elif self.strategy == "defect" and avg_payoff_coop > current_payoff:
            prob_change = min(1.0, (avg_payoff_coop - current_payoff) / 10.0)
            if random.random() < prob_change:
                self.strategy = "cooperate"

        self.history.append(self.strategy)


class ABMFarmerSimulation:
    """
    شبیه‌سازی اصلی ABM برای کشاورزان.
    """

    def __init__(self, num_agents: int, initial_resource: float, payoff_matrix: Dict):
        self.agents = [FarmerAgent(i) for i in range(num_agents)]
        self.resource_level = initial_resource
        self.payoff_matrix = payoff_matrix
        self.history = []

    def step(self):
        """
        یک گام شبیه‌سازی: تصمیم گیری برداشت، به‌روزرسانی منبع، محاسبه پرداختی، به‌روزرسانی استراتژی.
        """
        total_withdrawal = 0.0
        payoffs = {}

        # مرحله ۱: تصمیم گیری هر عامل
        for agent in self.agents:
            others_total = sum(a.water_withdrawal for a in self.agents if a.id != agent.id)
            agent.decide_withdrawal(others_total, self.resource_level, agent.strategy)

        # مرحله ۲: به‌روزرسانی منابع
        total_withdrawal = sum(agent.water_withdrawal for agent in self.agents)
        # تصور کنیم یک مقدار بازیابی وجود دارد
        replenishment = 0.05 * self.resource_level
        self.resource_level = max(0, self.resource_level - total_withdrawal + replenishment)

        # مرحله ۳: محاسبه پرداختی
        for agent in self.agents:
            # مدل ساده: پرداختی وابسته به برداشت و سطح منبع
            agent.payoff = agent.water_withdrawal * (self.resource_level / (self.resource_level + 0.1)) - (agent.water_withdrawal**2) * 0.1
            payoffs[agent.id] = agent.payoff

        # مرحله ۴: به‌روزرسانی استراتژی
        for agent in self.agents:
            # فرض می‌کنیم همسایگان همه عوامل دیگر هستند (شبکه کامل)
            neighbors_strats = [a.strategy for a in self.agents if a.id != agent.id]
            agent.update_strategy(neighbors_strats, self.payoff_matrix)

        # ذخیره وضعیت
        coop_count = sum(1 for a in self.agents if a.strategy == "cooperate")
        defect_count = num_agents - coop_count
        self.history.append({
            "resource": self.resource_level,
            "cooperators": coop_count,
            "defectors": defect_count,
            "average_payoff": np.mean(list(payoffs.values()))
        })

    def run_simulation(self, num_steps: int):
        """
        اجرای شبیه‌سازی برای چندین گام.
        """
        for _ in range(num_steps):
            self.step()
        return self.history


# Example usage (can be removed or moved to a test file)
if __name__ == "__main__":
    print("Testing ABM Farmer Behavior...")
    num_agents = 20
    initial_resource = 10.0
    # Payoff Matrix for Prisoner's Dilemma style game
    # Row player vs Column player
    payoff_matrix = {
        "cooperate": {"cooperate": 3, "defect": 0},
        "defect": {"cooperate": 5, "defect": 1}
    }

    sim = ABMFarmerSimulation(num_agents, initial_resource, payoff_matrix)

    history = sim.run_simulation(10)
    for i, state in enumerate(history):
        print(f"Step {i+1}: Resource={state['resource']:.2f}, Coop={state['cooperators']}, Defect={state['defectors']}, AvgPayoff={state['average_payoff']:.2f}")