"""
03_aquacrop_model.py - AquaCrop Model Implementation
File: D:\econojin.com\scripts\models\soil_carbon\aquacrop.py
Run in IDLE: exec(open(r"D:\econojin.com\scripts\models\soil_carbon\aquacrop.py").read())
"""
import json
import os
import sys
from datetime import datetime

PROJECT_ROOT = r"D:\econojin.com"
sys.path.insert(0, PROJECT_ROOT)


class AquaCropModel:
    """AquaCrop model for crop yield simulation"""

    def __init__(self, config=None):
        self.config = config or {}
        self.results = None
        self.status = "initialized"
        print(f"[INFO] AquaCrop model initialized")

    def run(self, weather, soil, crop):
        """Run crop yield simulation"""
        print(f"[INFO] Running AquaCrop simulation...")

        # Simple empirical model (placeholder for real AquaCrop)
        temp_avg = weather.get("temp_avg_c", 20)
        precip = weather.get("precip_mm", 300)
        soil_water = soil.get("field_capacity", 0.3) * 0.8
        growing_days = crop.get("growing_days", 120)

        # Yield calculation (simplified)
        base_yield = 3000  # kg/ha
        temp_factor = 1.0 if 15 <= temp_avg <= 25 else 0.8
        water_factor = min(1.0, precip / 400)
        soil_factor = min(1.0, soil_water / 0.25)

        yield_kg_ha = base_yield * temp_factor * water_factor * soil_factor
        biomass = yield_kg_ha * 3.5  # Harvest index ~0.29
        wp = yield_kg_ha / max(precip, 1)  # Water productivity

        self.results = {
            "model": "AquaCrop",
            "yield_kg_ha": round(yield_kg_ha, 1),
            "biomass_kg_ha": round(biomass, 1),
            "water_productivity_kg_m3": round(wp, 2),
            "inputs": {"temp_avg": temp_avg, "precip_mm": precip, "soil_fc": soil_water},
            "simulation_date": datetime.now().isoformat(),
        }
        self.status = "completed"
        print(f"[OK] Yield: {self.results['yield_kg_ha']} kg/ha")
        return self.results

    def export(self, path):
        """Export results to JSON file"""
        if not self.results:
            print("[WARN] No results to export")
            return False
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        print(f"[OK] Exported: {path}")
        return True


# Sample execution
if __name__ == "__main__":
    print("=== AquaCrop Sample Run ===\n")

    model = AquaCropModel()

    # Sample inputs for pilot area (Iran central)
    weather = {"temp_avg_c": 22, "precip_mm": 280, "et0_mm": 450}
    soil = {"field_capacity": 0.32, "wilting_point": 0.15, "texture": "loam"}
    crop = {"species": "wheat", "growing_days": 120, "planting_date": "2024-03-15"}

    result = model.run(weather, soil, crop)

    print(f"\n📊 Results:")
    print(f"   Yield: {result['yield_kg_ha']} kg/ha")
    print(f"   Biomass: {result['biomass_kg_ha']} kg/ha")
    print(f"   Water Productivity: {result['water_productivity_kg_m3']} kg/m³")

    # Export
    output = os.path.join(PROJECT_ROOT, "data", "processed", "aquacrop_sample.json")
    model.export(output)

    print(f"\n[SUCCESS] Sample run complete!")
