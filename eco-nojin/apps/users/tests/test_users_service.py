#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for users service
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from apps.users.service import UserService
from apps.users.schemas import UserCreate, UserUpdate


class TestUserService:
    """Tests for UserService"""
    
    @pytest.fixture
    def mock_repository(self):
        """Mock user repository"""
        repo = AsyncMock()
        repo.get_by_email = AsyncMock()
        repo.create = AsyncMock()
        repo.update = AsyncMock()
        repo.delete = AsyncMock()
        return repo
    
    @pytest.fixture
    def service(self, mock_repository):
        """UserService instance with mock repository"""
        return UserService(mock_repository)
    
    @pytest.mark.asyncio
    async def test_create_user_success(self, service, mock_repository):
        """Test successful user creation"""
        user_data = UserCreate(
            email="test@example.com",
            password="securepassword123",
            full_name="Test User"
        )
        
        mock_repository.get_by_email.return_value = None
        mock_repository.create.return_value = MagicMock(id=1, email="test@example.com")
        
        result = await service.create_user(user_data)
        
        assert result is not None
        mock_repository.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_duplicate_email(self, service, mock_repository):
        """Test user creation with duplicate email"""
        user_data = UserCreate(
            email="existing@example.com",
            password="password123",
            full_name="Test User"
        )
        
        mock_repository.get_by_email.return_value = MagicMock(id=1)
        
        with pytest.raises(ValueError, match="already exists"):
            await service.create_user(user_data)
    
    @pytest.mark.asyncio
    async def test_get_user_by_id(self, service, mock_repository):
        """Test getting user by ID"""
        mock_user = MagicMock(id=1, email="test@example.com")
        mock_repository.get_by_id.return_value = mock_user
        
        result = await service.get_user_by_id(1)
        
        assert result is not None
        assert result.id == 1
        mock_repository.get_by_id.assert_called_once_with(1)
