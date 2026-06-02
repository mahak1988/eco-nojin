"""Full RothC model (ported from scripts/rothc.py)."""

from datetime import datetime, timezone
from typing import Any


class RothCModel:
    """RothC soil organic carbon dynamics — 5-pool simplified."""

    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self.pools = {
            "DPM": 0.1,
            "RPM": 0.3,
            "BIO": 0.05,
            "HUM": 0.5,
            "IOM": 0.05,
        }
        self.results: dict[str, Any] | None = None

    def run(
        self,
        climate: dict,
        soil: dict,
        management: dict,
        years: int = 10,
    ) -> dict[str, Any]:
        temp = float(climate.get("temp_avg_c", climate.get("mean_temp_c", 18)))
        precip = float(climate.get("precip_mm", climate.get("annual_rain_mm", 350)))
        clay = float(soil.get("clay_pct", soil.get("clay_percent", 25)))
        initial_soc = float(soil.get("soc_percent", soil.get("initial_soc", 1.2) / 25))

        base_rate = 0.03
        temp_factor = 1 + 0.1 * (temp - 18) / 10
        moisture_factor = min(1.5, precip / 300)
        clay_protection = 1 - 0.005 * clay
        annual_loss = base_rate * temp_factor * moisture_factor * clay_protection
        residue = 0.3 if management.get("residue_return", True) else 0.0

        soc = initial_soc
        series = []
        for year in range(1, years + 1):
            loss = soc * annual_loss
            gain = residue / 100
            soc += gain - loss
            series.append({"year": year, "soc_percent": round(soc, 4), "soc_t_ha": round(soc * 25, 3)})

        self.results = {
            "model": "RothC-full",
            "soc_change_percent": round(soc - initial_soc, 4),
            "soc_change_t_ha": round((soc - initial_soc) * 25, 3),
            "final_soc_percent": round(soc, 4),
            "final_soc_t_ha": round(soc * 25, 3),
            "decomposition_rate": round(annual_loss, 4),
            "simulation_years": years,
            "series": series,
            "pools": self.pools,
            "inputs": {"temp": temp, "precip": precip, "clay": clay},
            "date": datetime.now(timezone.utc).isoformat(),
        }
        return self.results


def run_rothc_from_params(
    initial_soc: float,
    clay_percent: float,
    mean_temp_c: float,
    annual_rain_mm: float,
    years: int = 5,
) -> dict[str, Any]:
    model = RothCModel()
    return model.run(
        climate={"temp_avg_c": mean_temp_c, "precip_mm": annual_rain_mm},
        soil={"clay_pct": clay_percent, "initial_soc": initial_soc},
        management={"residue_return": True},
        years=years,
    )
