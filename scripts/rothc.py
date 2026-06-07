"""
04_rothc_model.py - RothC Soil Carbon Model
File: D:\econojin.com\scripts\models\soil_carbon\rothc.py
Run in IDLE: exec(open(r"D:\econojin.com\scripts\models\soil_carbon\rothc.py").read())
"""
import json
import os
import sys
from datetime import datetime

PROJECT_ROOT = r"D:\econojin.com"
sys.path.insert(0, PROJECT_ROOT)


class RothCModel:
    """RothC model for soil organic carbon dynamics"""

    def __init__(self, config=None):
        self.config = config or {}
        self.pools = {"DPM": 0.1, "RPM": 0.3, "BIO": 0.05, "HUM": 0.5, "IOM": 0.05}  # fractions
        self.results = None
        print(f"[INFO] RothC model initialized")

    def run(self, climate, soil, management, years=10):
        """Simulate SOC change over time"""
        print(f"[INFO] Running RothC for {years} years...")

        # Simplified RothC logic
        temp = climate.get("temp_avg_c", 18)
        precip = climate.get("precip_mm", 350)
        clay = soil.get("clay_pct", 25)
        initial_soc = soil.get("soc_percent", 1.2)

        # Decomposition rates (simplified)
        base_rate = 0.03  # per year
        temp_factor = 1 + 0.1 * (temp - 18) / 10
        moisture_factor = min(1.5, precip / 300)
        clay_protection = 1 - 0.005 * clay  # clay protects SOC

        annual_loss = base_rate * temp_factor * moisture_factor * clay_protection
        input_from_residue = management.get("residue_return", False) * 0.3  # tons C/ha/yr

        # Simple mass balance over years
        soc_change = 0
        for year in range(years):
            loss = initial_soc * annual_loss
            gain = input_from_residue
            soc_change += gain - loss
            initial_soc += (gain - loss) / 100  # convert to percent

        self.results = {
            "model": "RothC",
            "soc_change_percent": round(soc_change, 3),
            "soc_change_t_ha": round(soc_change * 25, 2),  # assuming 2.5M kg soil/ha
            "final_soc_percent": round(initial_soc, 2),
            "decomposition_rate": round(annual_loss, 4),
            "simulation_years": years,
            "inputs": {"temp": temp, "precip": precip, "clay": clay},
            "date": datetime.now().isoformat(),
        }
        print(f"[OK] SOC change: {self.results['soc_change_t_ha']} t C/ha over {years} years")
        return self.results

    def export(self, path):
        if not self.results:
            return False
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"[OK] Exported: {path}")
        return True


if __name__ == "__main__":
    print("=== RothC Sample Run ===\n")

    model = RothCModel()

    climate = {"temp_avg_c": 19, "precip_mm": 320}
    soil = {"clay_pct": 28, "soc_percent": 1.1, "bulk_density": 1.4}
    management = {"tillage": "reduced", "residue_return": True, "cover_crop": False}

    result = model.run(climate, soil, management, years=10)

    print(f"\n📊 Results:")
    print(f"   SOC Change: {result['soc_change_t_ha']} t C/ha")
    print(f"   Final SOC: {result['final_soc_percent']}%")
    print(f"   Decomposition Rate: {result['decomposition_rate']}/yr")

    output = os.path.join(PROJECT_ROOT, "data", "processed", "rothc_sample.json")
    model.export(output)

    print(f"\n[SUCCESS] RothC sample complete!")
