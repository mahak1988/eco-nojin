"""
Tests for simulation module | تست‌های simulation
===============================================
Run with: pytest apps/simulation/tests/test_simulation.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from apps.simulation.schemas import SimulationCreate, SimulationUpdate
from apps.simulation.service import SimulationService
from apps.shared_core.exceptions import NotFoundError


def test_module_imports():
    """Verify that the simulation module can be imported."""
    from apps.simulation import models, schemas, service, repository


def test_simulation_create_schema():
    """Test the SimulationCreate schema validates input."""
    from apps.simulation.schemas import SimulationCreate
    
    # Test valid data - schema only has name and description fields
    obj = SimulationCreate(name="Test Simulation", description="Test Desc")
    assert obj.name == "Test Simulation"
    assert obj.description == "Test Desc"


def test_simulation_response_schema():
    """Test the SimulationResponse schema serializes correctly."""
    from apps.simulation.schemas import SimulationResponse
    
    # Create a mock Simulation object with correct fields
    mock_sim = MagicMock()
    mock_sim.id = 1
    mock_sim.name = "Test Simulation"
    mock_sim.description = "Test Description"
    
    # Validate from ORM object
    response = SimulationResponse.model_validate(mock_sim)
    assert response.id == 1
    assert response.name == "Test Simulation"


@pytest.mark.asyncio
async def test_simulation_service_get_success():
    """Test getting a record via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock Simulation object
    mock_sim = MagicMock()
    mock_sim.id = 1
    mock_sim.name = "Test Simulation"
    
    # Setup repository mock
    mock_repo.get_by_id = AsyncMock(return_value=mock_sim)
    
    # Create service with mocked repository
    with patch.object(SimulationService, '__init__', lambda x, y: None):
        service = SimulationService.__new__(SimulationService)
        service.repo = mock_repo
        
        # Test get method
        result = await service.get(1)
        assert result == mock_sim
        mock_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_simulation_service_get_not_found():
    """Test that get raises NotFoundError when record doesn't exist."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Setup repository mock to return None
    mock_repo.get_by_id = AsyncMock(return_value=None)
    
    # Create service with mocked repository
    with patch.object(SimulationService, '__init__', lambda x, y: None):
        service = SimulationService.__new__(SimulationService)
        service.repo = mock_repo
        
        # Test get method raises NotFoundError
        with pytest.raises(NotFoundError) as exc_info:
            await service.get(999)
        
        assert "Simulation" in str(exc_info.value.message)
        assert "999" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_simulation_service_create():
    """Test creating a record via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock created Simulation object
    mock_sim = MagicMock()
    mock_sim.id = 1
    mock_sim.name = "New Simulation"
    
    # Setup repository mock
    mock_repo.create = AsyncMock(return_value=mock_sim)
    
    # Create service with mocked repository
    with patch.object(SimulationService, '__init__', lambda x, y: None):
        service = SimulationService.__new__(SimulationService)
        service.repo = mock_repo
        
        # Create schema object
        create_data = SimulationCreate(
            model_type="hydrology",
            name="New Simulation",
            parameters={}
        )
        
        # Test create method
        result = await service.create(create_data)
        assert result == mock_sim
        mock_repo.create.assert_called_once_with(create_data)


@pytest.mark.asyncio
async def test_simulation_service_update():
    """Test updating a record via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock existing and updated Simulation object
    mock_sim = MagicMock()
    mock_sim.id = 1
    mock_sim.name = "Updated Simulation"
    
    # Setup repository mocks
    mock_repo.get_by_id = AsyncMock(return_value=mock_sim)
    mock_repo.update = AsyncMock(return_value=mock_sim)
    
    # Create service with mocked repository
    with patch.object(SimulationService, '__init__', lambda x, y: None):
        service = SimulationService.__new__(SimulationService)
        service.repo = mock_repo
        
        # Create update schema
        update_data = SimulationUpdate(name="Updated Name")
        
        # Test update method
        result = await service.update(1, update_data)
        assert result == mock_sim


@pytest.mark.asyncio
async def test_simulation_service_update_no_changes():
    """Test that update returns early when no changes provided."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock existing Simulation object
    mock_sim = MagicMock()
    mock_sim.id = 1
    mock_sim.name = "Original Simulation"
    
    # Setup repository mock
    mock_repo.get_by_id = AsyncMock(return_value=mock_sim)
    
    # Create service with mocked repository
    with patch.object(SimulationService, '__init__', lambda x, y: None):
        service = SimulationService.__new__(SimulationService)
        service.repo = mock_repo
        
        # Create empty update schema (no fields set)
        update_data = SimulationUpdate()
        
        # Test update method returns early
        result = await service.update(1, update_data)
        assert result == mock_sim
        mock_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_simulation_service_delete():
    """Test deleting a record via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock existing Simulation object
    mock_sim = MagicMock()
    mock_sim.id = 1
    
    # Setup repository mocks
    mock_repo.get_by_id = AsyncMock(return_value=mock_sim)
    mock_repo.delete = AsyncMock(return_value=True)
    
    # Create service with mocked repository
    with patch.object(SimulationService, '__init__', lambda x, y: None):
        service = SimulationService.__new__(SimulationService)
        service.repo = mock_repo
        
        # Test delete method
        await service.delete(1)
        mock_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_simulation_service_list():
    """Test listing records via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock Simulation objects
    mock_sim1 = MagicMock()
    mock_sim1.id = 1
    mock_sim2 = MagicMock()
    mock_sim2.id = 2
    
    # Setup repository mock
    mock_repo.list = AsyncMock(return_value=([mock_sim1, mock_sim2], 2))
    
    # Create service with mocked repository
    with patch.object(SimulationService, '__init__', lambda x, y: None):
        service = SimulationService.__new__(SimulationService)
        service.repo = mock_repo
        
        # Test list method
        items, total = await service.list(skip=0, limit=10)
        assert len(items) == 2
        assert total == 2
        assert items[0] == mock_sim1
        assert items[1] == mock_sim2


@pytest.mark.asyncio
async def test_simulation_service_list_limit_cap():
    """Test that list caps the limit to prevent abuse."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Setup repository mock
    mock_repo.list = AsyncMock(return_value=([], 0))
    
    # Create service with mocked repository
    with patch.object(SimulationService, '__init__', lambda x, y: None):
        service = SimulationService.__new__(SimulationService)
        service.repo = mock_repo
        
        # Test with limit > 1000
        await service.list(skip=0, limit=5000)
        mock_repo.list.assert_called_once_with(skip=0, limit=1000)
