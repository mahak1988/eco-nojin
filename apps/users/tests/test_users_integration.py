#!/usr/bin/env python3
"""
Integration tests for users module interacting with shared_core (e.g., security, config).
This test verifies that user registration and authentication work with the central security module.
"""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from apps.users.models import User
from apps.users.repository import UserRepository
from apps.users.schemas import UserCreate
from apps.users.service import UserService


class TestUserSharedCoreIntegration:
    """Integration tests for user service and shared security."""

    @pytest.fixture
    def mock_session(self):
        """Mock database session."""
        return AsyncMock(spec=AsyncSession)

    @pytest.fixture
    def mock_repo(self, mock_session):
        """Mock user repository."""
        repo = UserRepository(mock_session)
        repo.get_by_email = AsyncMock()
        repo.create = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repo):
        """UserService instance with mocked repository."""
        # UserService expects a session, but we inject the repo directly for easier mocking
        service_instance = UserService.__new__(UserService)  # Create without __init__
        service_instance.repo = mock_repo
        return service_instance

    @pytest.mark.asyncio
    async def test_register_user_hashes_password_via_shared_security(self, service, mock_repo):
        """
        Test that UserService.register_user calls the shared_core.security
        module's get_password_hash function correctly.
        """
        user_data = UserCreate(
            email="integration@test.com",
            password="a_secure_password_123!",
            full_name="Integration Test User",
        )

        # Mock repo calls
        mock_repo.get_by_email.return_value = None
        created_user_mock = User(
            id=999,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password="mock_hash",
        )
        mock_repo.create.return_value = created_user_mock

        # Patch the get_password_hash function from the shared module
        with patch("apps.users.service.get_password_hash") as mock_hash_func:
            mock_hash_func.return_value = "mock_hash_from_shared_core"

            result = await service.register_user(user_data)

            # Assertions
            assert result.email == user_data.email
            # Verify that the service called the shared security function
            mock_hash_func.assert_called_once_with(user_data.password)
            # Verify that the repo was called with the hashed password from the shared module
            mock_repo.create.assert_called_once()
            call_args = mock_repo.create.call_args[0][
                0
            ]  # Get the first positional argument (the User object)
            assert call_args.hashed_password == "mock_hash_from_shared_core"

    @pytest.mark.asyncio
    async def test_authenticate_user_verifies_password_via_shared_security(
        self, service, mock_repo
    ):
        """
        Test that UserService.authenticate_user calls the shared_core.security
        module's verify_password function correctly.
        """
        email = "auth@test.com"
        password = "correct_password"
        wrong_password = "wrong_password"

        # Mock repo to return a user with a known hashed password
        stored_hashed_password = "$2b$12$mocked_hashed_password"
        user_from_db = User(id=1, email=email, hashed_password=stored_hashed_password)
        mock_repo.get_by_email.return_value = user_from_db

        # Patch the verify_password function from the shared module
        with patch("apps.users.service.verify_password") as mock_verify_func:
            # Simulate successful verification
            mock_verify_func.return_value = True

            result = await service.authenticate_user(email, password)

            # Assertions
            assert result is not None
            assert result.email == email
            # Verify that the service called the shared security function with the correct arguments
            mock_verify_func.assert_called_once_with(password, stored_hashed_password)

        # Now test a failing verification
        with patch("apps.users.service.verify_password") as mock_verify_func:
            # Simulate failed verification
            mock_verify_func.return_value = False

            result = await service.authenticate_user(email, wrong_password)

            # Assertions
            assert result is None  # Should return None on failure
            # Verify that the service called the shared security function with the correct arguments
            mock_verify_func.assert_called_once_with(wrong_password, stored_hashed_password)
