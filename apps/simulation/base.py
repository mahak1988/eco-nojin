"""
Base Simulator Framework
========================
Abstract base class for all simulation models with parameter validation,
result serialization, and registry pattern.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Optional
import json
import uuid


class SimulationStatus(str, Enum):
    """Status of a simulation run."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SimulationParameter:
    """A single simulation parameter with metadata."""
    name: str
    label: str
    type: str  # "float", "int", "string", "select", "boolean"
    default: Any = None
    description: str = ""
    unit: str = ""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    options: list[str] = field(default_factory=list)  # for select type
    required: bool = True

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SimulationResult:
    """Result of a simulation run."""
    simulator_id: str
    simulator_name: str
    status: SimulationStatus
    run_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    parameters: dict[str, Any] = field(default_factory=dict)
    outputs: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    charts: dict[str, list] = field(default_factory=dict)  # chart data series
    error: Optional[str] = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


class SimulationRegistry:
    """Registry of all available simulators."""
    _simulators: dict[str, type["BaseSimulator"]] = {}

    @classmethod
    def register(cls, simulator_class: type["BaseSimulator"]) -> type["BaseSimulator"]:
        """Register a simulator class."""
        instance = simulator_class()
        cls._simulators[instance.id] = simulator_class
        return simulator_class

    @classmethod
    def get(cls, simulator_id: str) -> Optional[type["BaseSimulator"]]:
        return cls._simulators.get(simulator_id)

    @classmethod
    def list_all(cls) -> list[dict]:
        """List all registered simulators with metadata."""
        result = []
        for sid, sclass in cls._simulators.items():
            instance = sclass()
            meta = instance.get_metadata()
            meta["id"] = sid
            result.append(meta)
        return result

    @classmethod
    def get_parameters(cls, simulator_id: str) -> list[dict]:
        """Get parameters for a specific simulator."""
        sclass = cls.get(simulator_id)
        if sclass:
            instance = sclass()
            return [p.to_dict() for p in instance.get_parameters()]
        return []


class BaseSimulator(ABC):
    """Abstract base class for all simulation models."""

    @property
    @abstractmethod
    def id(self) -> str:
        """Unique identifier for this simulator."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass

    @property
    @abstractmethod
    def category(self) -> str:
        """Category: agriculture, hydrology, carbon, etc."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description."""
        pass

    @property
    @abstractmethod
    def version(self) -> str:
        """Version string."""
        pass

    @abstractmethod
    def get_parameters(self) -> list[SimulationParameter]:
        """Return list of required simulation parameters."""
        pass

    @abstractmethod
    async def run(self, parameters: dict[str, Any]) -> SimulationResult:
        """Execute the simulation with given parameters."""
        pass

    def validate(self, parameters: dict[str, Any]) -> list[str]:
        """Validate parameters. Returns list of error messages."""
        errors = []
        for param in self.get_parameters():
            value = parameters.get(param.name)
            if param.required and value is None:
                errors.append(f"{param.label} is required")
                continue
            if value is not None:
                if param.type == "float" or param.type == "int":
                    try:
                        v = float(value)
                        if param.min_value is not None and v < param.min_value:
                            errors.append(f"{param.label} must be >= {param.min_value}")
                        if param.max_value is not None and v > param.max_value:
                            errors.append(f"{param.label} must be <= {param.max_value}")
                    except (ValueError, TypeError):
                        errors.append(f"{param.label} must be a number")
                if param.type == "select" and param.options:
                    if str(value) not in param.options:
                        errors.append(f"{param.label} must be one of: {', '.join(param.options)}")
        return errors

    def get_metadata(self) -> dict:
        """Return metadata about this simulator."""
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "version": self.version,
            "parameters_count": len(self.get_parameters()),
        }