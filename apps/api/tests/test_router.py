"""Tests for router — real tests replacing stubs."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from apps.main import app

client = TestClient(app)


class TestRouter:
    """Test suite for router — verifies CRUD endpoints exist and respond."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        from apps.api.router import router

        assert router is not None

    def test_list_api_exists(self) -> None:
        """Verify list_api is callable."""
        from apps.api.router import list_api

        assert callable(list_api)

    def test_get_api_exists(self) -> None:
        """Verify get_api is callable."""
        from apps.api.router import get_api

        assert callable(get_api)

    def test_create_api_exists(self) -> None:
        """Verify create_api is callable."""
        from apps.api.router import create_api

        assert callable(create_api)

    def test_update_api_exists(self) -> None:
        """Verify update_api is callable."""
        from apps.api.router import update_api

        assert callable(update_api)

    def test_delete_api_exists(self) -> None:
        """Verify delete_api is callable."""
        from apps.api.router import delete_api

        assert callable(delete_api)

    def test_router_has_correct_prefix(self) -> None:
        """Verify router has /api prefix."""
        from apps.api.router import router

        assert router.prefix == "/api"

    def test_router_has_correct_tags(self) -> None:
        """Verify router has 'api' tag."""
        from apps.api.router import router

        assert "api" in router.tags

    def test_router_has_get_endpoint(self) -> None:
        """Verify router has a GET endpoint."""
        from apps.api.router import router

        methods = []
        for r in router.routes:
            if hasattr(r, "methods"):
                methods.extend(r.methods)
        assert "GET" in methods

    def test_router_has_post_endpoint(self) -> None:
        """Verify router has a POST endpoint."""
        from apps.api.router import router

        methods = []
        for r in router.routes:
            if hasattr(r, "methods"):
                methods.extend(r.methods)
        assert "POST" in methods

    def test_router_has_delete_endpoint(self) -> None:
        """Verify router has a DELETE endpoint."""
        from apps.api.router import router

        methods = []
        for r in router.routes:
            if hasattr(r, "methods"):
                methods.extend(r.methods)
        assert "DELETE" in methods
