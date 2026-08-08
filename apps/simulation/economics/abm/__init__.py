"""ABM Wrapper for Eco Nozhin - Full Implementation"""

import logging
import math
import random
import time
from typing import Any

from apps.simulation.base import (
    BaseSimulator,
    SimulationParameter,
    SimulationRegistry,
    SimulationResult,
    SimulationStatus,
)

logger = logging.getLogger(__name__)


@SimulationRegistry.register
class ABMSimulator(BaseSimulator):
    @property
    def id(self) -> str:
        return "abm"

    @property
    def name(self) -> str:
        return "Agent-Based Economic Model"

    @property
    def category(self) -> str:
        return "economics"

    @property
    def description(self) -> str:
        return "Agent-based economic model for simulating individual agent behavior and market dynamics. Current skeleton implementation."

    @property
    def version(self) -> str:
        return "1.0.0-skeleton"

    def get_parameters(self) -> list[SimulationParameter]:
        return [
            SimulationParameter(
                name="num_agents",
                label="Number of Agents",
                type="int",
                default=100,
                min_value=10,
                max_value=1000,
                description="Number of economic agents in the simulation",
                required=True,
            ),
            SimulationParameter(
                name="market_type",
                label="Market Type",
                type="select",
                options=["perfect_competition", "monopoly", "oligopoly", "monopolistic"],
                default="perfect_competition",
                description="Type of market structure",
                required=True,
            ),
            SimulationParameter(
                name="agent_behavior",
                label="Agent Behavior",
                type="select",
                options=["rational", "bounded_rational", "adaptive_learning", "random"],
                default="rational",
                description="Behavioral model for agents",
                required=True,
            ),
            SimulationParameter(
                name="resource_availability",
                label="Resource Availability",
                type="float",
                default=1.0,
                min_value=0.1,
                max_value=5.0,
                description="Relative abundance of resources (1.0 = balanced)",
                required=True,
            ),
            SimulationParameter(
                name="price_volatility",
                label="Price Volatility",
                type="float",
                default=0.1,
                min_value=0.0,
                max_value=1.0,
                description="Degree of price volatility in the market",
                required=True,
            ),
            SimulationParameter(
                name="simulation_steps",
                label="Simulation Steps",
                type="int",
                default=50,
                min_value=10,
                max_value=200,
                description="Number of time steps to simulate",
                required=True,
            ),
        ]

    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        start = time.time()
        errors = self.validate(parameters)
        if errors:
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.FAILED,
                parameters=parameters,
                error="; ".join(errors),
            )

        try:
            # This is a skeleton - in the real implementation, we would run the ABM
            outputs = self._run_skeleton_simulation(parameters)
            elapsed = (time.time() - start) * 1000
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.COMPLETED,
                parameters=parameters,
                outputs=outputs,
                metrics=self._calculate_metrics(outputs),
                charts=self._generate_charts(outputs),
                execution_time_ms=elapsed,
            )
        except Exception as e:
            elapsed = (time.time() - start) * 1000
            return SimulationResult(
                simulator_id=self.id,
                simulator_name=self.name,
                status=SimulationStatus.FAILED,
                parameters=parameters,
                error=str(e),
                execution_time_ms=elapsed,
            )

    def _run_skeleton_simulation(self, params: dict[str, Any]) -> dict:
        """
        Skeleton implementation - this will be replaced with real ABM
        """
        num_agents = params.get("num_agents", 100)
        market_type = params.get("market_type", "perfect_competition")
        agent_behavior = params.get("agent_behavior", "rational")
        resource_availability = params.get("resource_availability", 1.0)
        price_volatility = params.get("price_volatility", 0.1)
        sim_steps = params.get("simulation_steps", 50)

        # Initialize agents with different characteristics
        agents = []
        for i in range(num_agents):
            agent = {
                "id": i,
                "wealth": random.uniform(1000, 10000),
                "risk_tolerance": random.uniform(0.1, 0.9),
                "strategy": agent_behavior,
            }
            agents.append(agent)

        # Simulate market dynamics over time
        price_history = []
        wealth_history = []
        trade_volume_history = []

        current_price = 100.0  # Starting price
        avg_wealth = sum([a["wealth"] for a in agents]) / len(agents)

        for step in range(sim_steps):
            # Market dynamics based on market type
            if market_type == "perfect_competition":
                # Prices move toward equilibrium based on supply/demand
                demand_shock = random.uniform(0.9, 1.1) * resource_availability
                supply_response = random.uniform(0.8, 1.2)

                # Price adjustment with volatility
                price_change = (demand_shock - supply_response) * (
                    1.0 + random.uniform(-price_volatility, price_volatility)
                )
                current_price = max(10.0, current_price * (1.0 + price_change * 0.1))

            elif market_type == "monopoly":
                # Monopolist sets prices higher
                current_price = max(10.0, current_price * (1.0 + random.uniform(0.02, 0.08)))

            elif market_type == "oligopoly":
                # Few firms compete strategically
                current_price = max(10.0, current_price * (1.0 + random.uniform(-0.03, 0.05)))

            else:  # monopolistic
                # Differentiated products with moderate competition
                current_price = max(10.0, current_price * (1.0 + random.uniform(-0.05, 0.05)))

            # Simulate trading activity
            trade_volume = random.uniform(0.1, 0.5) * num_agents * resource_availability

            # Update agent wealth based on market performance
            for agent in agents:
                # Random trading outcomes based on strategy and risk tolerance
                if agent_behavior == "rational":
                    profit_factor = 1.0 + (current_price - 100) / 1000 * agent["risk_tolerance"]
                elif agent_behavior == "bounded_rational":
                    profit_factor = 1.0 + random.uniform(-0.05, 0.1) * agent["risk_tolerance"]
                elif agent_behavior == "adaptive_learning":
                    profit_factor = 1.0 + random.uniform(-0.03, 0.08) * agent["risk_tolerance"]
                else:  # random
                    profit_factor = 1.0 + random.uniform(-0.1, 0.15) * agent["risk_tolerance"]

                agent["wealth"] *= profit_factor
                agent["wealth"] = max(100, agent["wealth"])  # Minimum wealth

            # Record history
            price_history.append(round(current_price, 2))
            avg_wealth = sum([a["wealth"] for a in agents]) / len(agents)
            wealth_history.append(round(avg_wealth, 2))
            trade_volume_history.append(round(trade_volume, 2))

        return {
            "series": [
                {
                    "key": "price",
                    "label": "Market Price",
                    "color": "#3b82f6",
                    "values": price_history,
                    "kind": "line",
                    "fill": False,
                },
                {
                    "key": "avg_wealth",
                    "label": "Average Wealth",
                    "color": "#10b981",
                    "values": wealth_history,
                    "kind": "line",
                    "fill": True,
                },
                {
                    "key": "trade_volume",
                    "label": "Trade Volume",
                    "color": "#f59e0b",
                    "values": trade_volume_history,
                    "kind": "line",
                    "fill": False,
                },
            ],
            "metrics": {
                "num_agents": num_agents,
                "market_type": market_type,
                "agent_behavior": agent_behavior,
                "initial_price": 100.0,
                "final_price": round(current_price, 2),
                "price_volatility_applied": price_volatility,
                "resource_availability": resource_availability,
                "price_return": round((current_price - 100.0) / 100.0 * 100, 2),
                "market_efficiency": round(
                    1.0 - price_volatility, 2
                ),  # Lower volatility = higher efficiency
            },
        }

    def _calculate_metrics(self, outputs: dict) -> dict[str, float]:
        return {
            k: float(v)
            for k, v in outputs.get("metrics", {}).items()
            if isinstance(v, (int, float))
        }

    def _generate_charts(self, outputs: dict) -> dict[str, list]:
        return {s["key"]: s["values"] for s in outputs.get("series", [])}


# Try to import from the wrapper, but provide a fallback to skeleton implementation
try:
    from .agent_model import AgentModel
    from .wrapper import ABMOutput, ABMWrapper
except ImportError:
    logger.warning("ABM wrapper not available, using skeleton implementation")

    # Provide skeleton classes to prevent import errors
    class ABMWrapper:
        pass

    class ABMOutput:
        pass

    class AgentModel:
        pass


__all__ = ["ABMOutput", "ABMSimulator", "ABMWrapper", "AgentModel"]
