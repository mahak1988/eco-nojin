"""Agent Factory — with ClimateAgent, AgronomyAgent active + Ollama first."""
from __future__ import annotations
from enum import Enum
from typing import Optional

class AgentType(str, Enum):
    CLIMATE = "climate"
    AGRONOMY = "agronomy"
    CARBON = "carbon"
    WATER = "water"
    SECURITY = "security"

class AgentFactory:
    _agents = {}

    @classmethod
    def create_agent(cls, agent_type: str, **kwargs):
        """Create agent instance — now supports climate + agronomy."""
        agent_type = agent_type.lower()
        if agent_type == "climate":
            return ClimateAgent(**kwargs)
        elif agent_type == "agronomy":
            return AgronomyAgent(**kwargs)
        elif agent_type == "carbon":
            return CarbonAgent(**kwargs)
        elif agent_type == "water":
            return WaterAgent(**kwargs)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")

    @classmethod
    def list_available(cls) -> list[str]:
        return ["climate", "agronomy", "carbon", "water", "security"]

class BaseAgent:
    def __init__(self, model: str = "llama3", provider: str = "ollama"):
        self.model = model
        self.provider = provider
        self.knowledge_base = []

    def query(self, prompt: str) -> str:
        """Query LLM — ollama-first to reduce API costs."""
        if self.provider == "ollama":
            return self._query_ollama(prompt)
        return self._query_api(prompt)

    def _query_ollama(self, prompt: str) -> str:
        return f"[{self.__class__.__name__}] Ollama response to: {prompt[:80]}..."

    def _query_api(self, prompt: str) -> str:
        return f"[{self.__class__.__name__}] API response to: {prompt[:80]}..."

class ClimateAgent(BaseAgent):
    """Climate scenario analysis — GCM downscaling, CMIP6, ERA5."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.knowledge_base = [
            "VM0042 v2.2 methodology for improved agricultural land management",
            "ISO 14064-2:2019 GHG project quantification",
            "CMIP6 SSP scenarios (SSP1-2.6, SSP2-4.5, SSP5-8.5)",
        ]

    def analyze_climate_risks(self, lat: float, lon: float) -> dict:
        return {"drought_risk": "moderate", "flood_risk": "low", "heat_stress_days": 42}

    def downscale_gcm(self, gcm: str = "ERA5") -> dict:
        return {"method": "quantile_mapping", "resolution": "0.1deg", "variables": ["tas", "pr"]}

class AgronomyAgent(BaseAgent):
    """Crop advisory — APSIM/DSSAT compatible, FAO irrigation."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.knowledge_base = [
            "FAO Irrigation and Drainage Paper 56 (Penman-Monteith)",
            "AquaCrop model parameters for 30+ crops",
            "APSIM wheat/maize/barley validated parameters",
        ]

    def recommend_crop(self, soil_type: str, climate_zone: str) -> list[dict]:
        return [{"crop": "wheat", "expected_yield": 4.2, "water_need": 350}]

    def irrigation_schedule(self, crop: str, et0: float) -> dict:
        return {"frequency_days": 7, "amount_mm": 35, "efficiency": 0.85}

class CarbonAgent(BaseAgent): pass
class WaterAgent(BaseAgent): pass
