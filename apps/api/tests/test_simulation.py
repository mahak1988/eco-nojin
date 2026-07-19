"""
Simulation Framework Tests
==========================
Tests for base simulator and AquaCrop implementation.
"""

import pytest
from apps.simulation.base import (
    BaseSimulator, SimulationParameter, SimulationResult,
    SimulationStatus, SimulationRegistry
)
from apps.simulation.agriculture.aquacrop import AquaCropSimulator


@pytest.mark.asyncio
async def test_simulation_parameter_creation():
    """Test simulation parameter creation and to_dict."""
    param = SimulationParameter(
        name="test_param",
        label="Test Parameter",
        type="float",
        default=10.0,
        description="A test parameter",
        unit="kg",
        min_value=0.0,
        max_value=100.0,
        required=True,
    )
    assert param.name == "test_param"
    assert param.type == "float"
    
    param_dict = param.to_dict()
    assert param_dict["name"] == "test_param"
    assert param_dict["default"] == 10.0


@pytest.mark.asyncio
async def test_simulation_result_creation():
    """Test simulation result creation and serialization."""
    result = SimulationResult(
        simulator_id="test_sim",
        simulator_name="Test Simulator",
        status=SimulationStatus.COMPLETED,
        outputs={"yield": 5.0},
        metrics={"water_use": 100.0},
    )
    
    assert result.simulator_id == "test_sim"
    assert result.status == SimulationStatus.COMPLETED
    
    result_dict = result.to_dict()
    assert result_dict["simulator_id"] == "test_sim"
    
    result_json = result.to_json()
    assert '"simulator_id": "test_sim"' in result_json


@pytest.mark.asyncio
async def test_simulation_status_enum():
    """Test simulation status enum values."""
    assert SimulationStatus.PENDING == "pending"
    assert SimulationStatus.RUNNING == "running"
    assert SimulationStatus.COMPLETED == "completed"
    assert SimulationStatus.FAILED == "failed"


@pytest.mark.asyncio
async def test_registry_registration():
    """Test simulator registry registration and retrieval."""
    # Test AquaCrop is registered
    sim_class = SimulationRegistry.get("aquacrop")
    assert sim_class is not None
    
    # Create instance
    sim = sim_class()
    assert sim.id == "aquacrop"
    assert sim.name == "AquaCrop (FAO Crop Water Productivity Model)"
    assert sim.category == "agriculture"


@pytest.mark.asyncio
async def test_registry_list_all():
    """Test listing all simulators."""
    simulators = SimulationRegistry.list_all()
    assert len(simulators) >= 1
    
    # Find aquacrop in the list
    aquacrop_found = any(s["id"] == "aquacrop" for s in simulators)
    assert aquacrop_found


@pytest.mark.asyncio
async def test_registry_get_parameters():
    """Test getting parameters for a simulator."""
    params = SimulationRegistry.get_parameters("aquacrop")
    assert len(params) >= 1
    
    # Check first parameter structure
    first_param = params[0]
    assert "name" in first_param
    assert "label" in first_param
    assert "type" in first_param


@pytest.mark.asyncio
async def test_aquacrop_parameters():
    """Test AquaCrop simulator parameters."""
    sim = AquaCropSimulator()
    params = sim.get_parameters()
    
    param_names = [p.name for p in params]
    assert "crop" in param_names
    assert "planting_date" in param_names
    assert "harvest_date" in param_names
    assert "field_capacity" in param_names
    assert "wilting_point" in param_names


@pytest.mark.asyncio
async def test_aquacrop_validation():
    """Test AquaCrop parameter validation."""
    sim = AquaCropSimulator()
    
    # Valid parameters
    valid_params = {
        "crop": "wheat",
        "planting_date": "2025-03-15",
        "harvest_date": "2025-07-15",
        "field_capacity": 200.0,
        "wilting_point": 80.0,
        "total_irrigation": 300.0,
        "rainfall": 200.0,
        "et0": 5.0,
    }
    errors = sim.validate(valid_params)
    assert len(errors) == 0
    
    # Invalid parameters - missing required
    invalid_params = {"crop": "wheat"}
    errors = sim.validate(invalid_params)
    assert len(errors) > 0


@pytest.mark.asyncio
async def test_aquacrop_run():
    """Test AquaCrop simulator execution."""
    sim = AquaCropSimulator()
    
    params = {
        "crop": "wheat",
        "planting_date": "2025-03-15",
        "harvest_date": "2025-07-15",
        "field_capacity": 200.0,
        "wilting_point": 80.0,
        "total_irrigation": 300.0,
        "rainfall": 200.0,
        "et0": 5.0,
    }
    
    result = await sim.run(params)
    
    assert result.status == SimulationStatus.COMPLETED
    assert result.simulator_id == "aquacrop"
    assert "yield_kg_per_ha" in result.outputs
    assert "water_use_efficiency" in result.metrics
    assert result.execution_time_ms >= 0


@pytest.mark.asyncio
async def test_aquacrop_metadata():
    """Test AquaCrop simulator metadata."""
    sim = AquaCropSimulator()
    meta = sim.get_metadata()
    
    assert meta["id"] == "aquacrop"
    assert meta["category"] == "agriculture"
    assert meta["parameters_count"] >= 1