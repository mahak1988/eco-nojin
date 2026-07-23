"""
Tests for api module | تست‌های api
===============================================
Run with: pytest apps/api/tests/test_api.py -v
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.schemas import ApiCreate, ApiUpdate
from apps.api.service import ApiService
from apps.shared_core.exceptions import NotFoundError


def test_module_imports():
    """Verify that the api module can be imported."""
    from apps.api import models, schemas, service, repository


def test_api_create_schema():
    """Test the ApiCreate schema validates input."""
    from apps.api.schemas import ApiCreate
    
    # Test valid data
    obj = ApiCreate(name="test", description="desc")
    assert obj.name == "test"
    assert obj.description == "desc"
    
    # Test required fields
    with pytest.raises(ValueError):
        ApiCreate()  # Should fail without required fields


def test_api_response_schema():
    """Test the ApiResponse schema serializes correctly."""
    from apps.api.schemas import ApiResponse
    
    # Create a mock API object
    mock_api = MagicMock()
    mock_api.id = 1
    mock_api.name = "Test API"
    mock_api.description = "Test Description"
    
    # Validate from ORM object
    response = ApiResponse.model_validate(mock_api)
    assert response.id == 1
    assert response.name == "Test API"


@pytest.mark.asyncio
async def test_api_service_get_success():
    """Test getting a record via the service."""
    # Create mock session and repository
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock API object
    mock_api = MagicMock()
    mock_api.id = 1
    mock_api.name = "Test API"
    
    # Setup repository mock
    mock_repo.get_by_id = AsyncMock(return_value=mock_api)
    
    # Create service with mocked repository
    with patch.object(ApiService, '__init__', lambda x, y: None):
        service = ApiService.__new__(ApiService)
        service.repo = mock_repo
        
        # Test get method
        result = await service.get(1)
        assert result == mock_api
        mock_repo.get_by_id.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_api_service_get_not_found():
    """Test that get raises NotFoundError when record doesn't exist."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Setup repository mock to return None
    mock_repo.get_by_id = AsyncMock(return_value=None)
    
    # Create service with mocked repository
    with patch.object(ApiService, '__init__', lambda x, y: None):
        service = ApiService.__new__(ApiService)
        service.repo = mock_repo
        
        # Test get method raises NotFoundError
        with pytest.raises(NotFoundError) as exc_info:
            await service.get(999)
        
        assert "Api" in str(exc_info.value.message)
        assert "999" in str(exc_info.value.message)


@pytest.mark.asyncio
async def test_api_service_create():
    """Test creating a record via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock created API object
    mock_api = MagicMock()
    mock_api.id = 1
    mock_api.name = "New API"
    
    # Setup repository mock
    mock_repo.create = AsyncMock(return_value=mock_api)
    
    # Create service with mocked repository
    with patch.object(ApiService, '__init__', lambda x, y: None):
        service = ApiService.__new__(ApiService)
        service.repo = mock_repo
        
        # Create schema object
        create_data = ApiCreate(name="New API", description="Test")
        
        # Test create method
        result = await service.create(create_data)
        assert result == mock_api
        mock_repo.create.assert_called_once_with(create_data)


@pytest.mark.asyncio
async def test_api_service_update():
    """Test updating a record via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock existing and updated API object
    mock_api = MagicMock()
    mock_api.id = 1
    mock_api.name = "Updated API"
    
    # Setup repository mocks
    mock_repo.get_by_id = AsyncMock(return_value=mock_api)
    mock_repo.update = AsyncMock(return_value=mock_api)
    
    # Create service with mocked repository
    with patch.object(ApiService, '__init__', lambda x, y: None):
        service = ApiService.__new__(ApiService)
        service.repo = mock_repo
        
        # Create update schema
        update_data = ApiUpdate(name="Updated Name")
        
        # Test update method
        result = await service.update(1, update_data)
        assert result == mock_api


@pytest.mark.asyncio
async def test_api_service_update_no_changes():
    """Test that update returns early when no changes provided."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock existing API object
    mock_api = MagicMock()
    mock_api.id = 1
    mock_api.name = "Original API"
    
    # Setup repository mock
    mock_repo.get_by_id = AsyncMock(return_value=mock_api)
    
    # Create service with mocked repository
    with patch.object(ApiService, '__init__', lambda x, y: None):
        service = ApiService.__new__(ApiService)
        service.repo = mock_repo
        
        # Create empty update schema (no fields set)
        update_data = ApiUpdate()
        
        # Test update method returns early
        result = await service.update(1, update_data)
        assert result == mock_api
        mock_repo.update.assert_not_called()


@pytest.mark.asyncio
async def test_api_service_delete():
    """Test deleting a record via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock existing API object
    mock_api = MagicMock()
    mock_api.id = 1
    
    # Setup repository mocks
    mock_repo.get_by_id = AsyncMock(return_value=mock_api)
    mock_repo.delete = AsyncMock(return_value=True)
    
    # Create service with mocked repository
    with patch.object(ApiService, '__init__', lambda x, y: None):
        service = ApiService.__new__(ApiService)
        service.repo = mock_repo
        
        # Test delete method
        await service.delete(1)
        mock_repo.delete.assert_called_once_with(1)


@pytest.mark.asyncio
async def test_api_service_list():
    """Test listing records via the service."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Mock API objects
    mock_api1 = MagicMock()
    mock_api1.id = 1
    mock_api2 = MagicMock()
    mock_api2.id = 2
    
    # Setup repository mock
    mock_repo.list = AsyncMock(return_value=([mock_api1, mock_api2], 2))
    
    # Create service with mocked repository
    with patch.object(ApiService, '__init__', lambda x, y: None):
        service = ApiService.__new__(ApiService)
        service.repo = mock_repo
        
        # Test list method
        items, total = await service.list(skip=0, limit=10)
        assert len(items) == 2
        assert total == 2
        assert items[0] == mock_api1
        assert items[1] == mock_api2


@pytest.mark.asyncio
async def test_api_service_list_limit_cap():
    """Test that list caps the limit to prevent abuse."""
    mock_session = AsyncMock(spec=AsyncSession)
    mock_repo = AsyncMock()
    
    # Setup repository mock
    mock_repo.list = AsyncMock(return_value=([], 0))
    
    # Create service with mocked repository
    with patch.object(ApiService, '__init__', lambda x, y: None):
        service = ApiService.__new__(ApiService)
        service.repo = mock_repo
        
        # Test with limit > 1000
        await service.list(skip=0, limit=5000)
        mock_repo.list.assert_called_once_with(skip=0, limit=1000)

