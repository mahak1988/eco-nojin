"""
Agent Tool Registry
====================
Tool calling framework for AI agents.
"""

from typing import Callable, Any
import logging

logger = logging.getLogger("econojin")


class AgentToolRegistry:
    """Registry of tools available to AI agents."""
    
    _tools: dict[str, Callable] = {}
    
    @classmethod
    def register(cls, name: str) -> Callable:
        """Register a tool function by name."""
        def decorator(fn: Callable) -> Callable:
            cls._tools[name] = fn
            logger.info(f"Registered agent tool: {name}")
            return fn
        return decorator
    
    @classmethod
    def get(cls, name: str) -> Callable | None:
        """Get a tool by name."""
        return cls._tools.get(name)
    
    @classmethod
    def list_tools(cls) -> list[str]:
        """List all registered tool names."""
        return list(cls._tools.keys())
    
    @classmethod
    def execute(cls, name: str, *args: Any, **kwargs: Any) -> Any:
        """Execute a tool by name."""
        tool = cls.get(name)
        if tool is None:
            raise ValueError(f"Tool '{name}' not found. Available: {cls.list_tools()}")
        return tool(*args, **kwargs)


# Tool definitions
@AgentToolRegistry.register("get_weather_data")
async def get_weather_data(latitude: float, longitude: float, days: int = 7) -> dict:
    """Get weather forecast for a location."""
    from apps.simulation.climate import ClimateSimulator
    sim = ClimateSimulator()
    return await sim.run({"latitude": latitude, "longitude": longitude, "days": days})


@AgentToolRegistry.register("get_crop_recommendation")
async def get_crop_recommendation(
    province: str,
    soil_type: str,
    water_availability: float,
) -> dict:
    """Get crop recommendation based on location and conditions."""
    # Simplified recommendation logic
    crops = {
        "water_high": ["rice", "cotton"],
        "water_medium": ["wheat", "maize"],
        "water_low": ["tomato", "sorghum"],
    }
    
    if water_availability > 500:
        recommended = crops["water_high"]
    elif water_availability > 300:
        recommended = crops["water_medium"]
    else:
        recommended = crops["water_low"]
    
    return {"province": province, "recommended_crops": recommended}


@AgentToolRegistry.register("calculate_irrigation")
async def calculate_irrigation(
    crop: str,
    soil_moisture: float,
    evapotranspiration: float,
    area_ha: float,
) -> dict:
    """Calculate irrigation requirements."""
    from apps.simulation.agriculture.aquacrop import FAO_CROP_DATA
    
    crop_data = FAO_CROP_DATA.get(crop, FAO_CROP_DATA["wheat"])
    water_needed = evapotranspiration * area_ha * 1000  # mm to liters
    
    return {
        "crop": crop,
        "water_needed_m3": water_needed,
        "soil_moisture_status": "adequate" if soil_moisture > 0.5 else "low",
    }


@AgentToolRegistry.register("analyze_financial")
async def analyze_financial(
    revenue: float,
    costs: list[float],
    period_months: int = 12,
) -> dict:
    """Analyze financial performance."""
    total_costs = sum(costs)
    profit = revenue - total_costs
    roi = (profit / total_costs * 100) if total_costs > 0 else 0
    
    return {
        "revenue": revenue,
        "total_costs": total_costs,
        "profit": profit,
        "roi_percent": roi,
        "period_months": period_months,
    }