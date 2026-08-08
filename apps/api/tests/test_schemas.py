"""Tests for schemas — real tests replacing stubs."""

from __future__ import annotations

from datetime import datetime

import pytest


class TestSchemas:
    """Test suite for Pydantic schemas."""

    def test_import(self) -> None:
        """Verify schemas module imports successfully."""
        from apps.api.schemas import ApiBase, ApiCreate, ApiListResponse, ApiResponse, ApiUpdate

        assert ApiBase is not None
        assert ApiCreate is not None
        assert ApiUpdate is not None
        assert ApiResponse is not None
        assert ApiListResponse is not None

    def test_ApiBase_fields(self) -> None:
        """Verify ApiBase has name and description fields."""
        from apps.api.schemas import ApiBase

        obj = ApiBase(name="test", description="desc")
        assert obj.name == "test"
        assert obj.description == "desc"

    def test_ApiBase_name_required(self) -> None:
        """Verify name is required."""
        from apps.api.schemas import ApiBase

        with pytest.raises(Exception):
            ApiBase(description="no name")

    def test_ApiBase_name_min_length(self) -> None:
        """Verify name has min_length=1."""
        from apps.api.schemas import ApiBase

        with pytest.raises(Exception):
            ApiBase(name="")

    def test_ApiUpdate_fields(self) -> None:
        """Verify ApiUpdate has optional fields."""
        from apps.api.schemas import ApiUpdate

        obj = ApiUpdate()
        assert obj.name is None
        assert obj.description is None
        assert obj.is_active is None

    def test_ApiUpdate_partial(self) -> None:
        """Verify ApiUpdate accepts partial data."""
        from apps.api.schemas import ApiUpdate

        obj = ApiUpdate(name="updated")
        assert obj.name == "updated"
        assert obj.description is None

    def test_ApiListResponse_fields(self) -> None:
        """Verify ApiListResponse has required fields."""
        from apps.api.schemas import ApiListResponse

        obj = ApiListResponse(items=[], total=0, skip=0, limit=100)
        assert obj.items == []
        assert obj.total == 0
        assert obj.skip == 0
        assert obj.limit == 100

    def test_ApiCreate_instantiation(self) -> None:
        """Verify ApiCreate can be instantiated."""
        from apps.api.schemas import ApiCreate

        obj = ApiCreate(name="test", description="desc")
        assert obj.name == "test"
        assert obj.description == "desc"

    def test_ApiResponse_with_id(self) -> None:
        """Verify ApiResponse requires id, is_active, timestamps."""
        from apps.api.schemas import ApiResponse

        obj = ApiResponse(
            id=1,
            name="test",
            description="desc",
            is_active=True,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        assert obj.id == 1
        assert obj.is_active is True
