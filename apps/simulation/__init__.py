"""
Econojin Simulation Engine
==========================
Comprehensive simulation platform with 24 scientific models across
agriculture, hydrology, carbon cycle, economics, ecosystem services,
energy, soil, water quality, biodiversity, and climate domains.

Each simulator inherits from the BaseSimulator abstract class and
provides:
- run() → executes the simulation with given parameters
- validate() → validates input parameters
- get_metadata() → returns simulator metadata
"""

__version__ = "1.0.0"

from apps.simulation.base import (
    BaseSimulator,
    SimulationResult,
    SimulationParameter,
    SimulationRegistry,
    SimulationStatus,
)

# Register all simulators
from apps.simulation.registry import register_all_simulators

__all__ = [
    "BaseSimulator",
    "SimulationResult",
    "SimulationParameter",
    "SimulationRegistry",
    "SimulationStatus",
    "register_all_simulators",
]