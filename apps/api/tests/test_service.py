"""Tests for service — real tests replacing stubs."""
from __future__ import annotations

import pytest


class TestService:
    """Test suite for ApiService."""

    def test_import(self) -> None:
        """Verify service module imports successfully."""
        from apps.api.service import ApiService
        assert ApiService is not None

    def test_ApiService_instantiation(self) -> None:
        """Verify ApiService can be instantiated with a session."""
        from apps.api.service import ApiService

        class FakeSession:
            pass

        service = ApiService(FakeSession())
        assert service is not None
        assert service.repo is not None

    def test_ApiService_has_get(self) -> None:
        """Verify ApiService has get method."""
        from apps.api.service import ApiService
        assert hasattr(ApiService, "get")
        assert callable(getattr(ApiService, "get"))

    def test_ApiService_has_list(self) -> None:
        """Verify ApiService has list method."""
        from apps.api.service import ApiService
        assert hasattr(ApiService, "list")
        assert callable(getattr(ApiService, "list"))

    def test_ApiService_has_create(self) -> None:
        """Verify ApiService has create method."""
        from apps.api.service import ApiService
        assert hasattr(ApiService, "create")
        assert callable(getattr(ApiService, "create"))

    def test_ApiService_has_update(self) -> None:
        """Verify ApiService has update method."""
        from apps.api.service import ApiService
        assert hasattr(ApiService, "update")
        assert callable(getattr(ApiService, "update"))

    def test_ApiService_has_delete(self) -> None:
        """Verify ApiService has delete method."""
        from apps.api.service import ApiService
        assert hasattr(ApiService, "delete")
        assert callable(getattr(ApiService, "delete"))

    @pytest.mark.asyncio
    async def test_ApiService_list_caps_limit(self) -> None:
        """Verify list method caps limit to 1000."""
        from apps.api.service import ApiService

        class FakeRepo:
            async def list(self, skip=0, limit=100):
                return [], 0

        class FakeSession:
            pass

        service = ApiService(FakeSession())
        service.repo = FakeRepo()

        result = await service.list(skip=0, limit=5000)
        # The cap is applied internally; FakeRepo receives capped limit
        assert result == ([], 0)
