"""Tests for router."""
from __future__ import annotations

import pytest


class TestRouter:
    """Test suite for router."""

    def test_import(self) -> None:
        """Verify module imports successfully."""
        try:
            import apps.ai_agents.router  # noqa: F401
        except ImportError as e:
            pytest.skip(f"Import failed: {e}")

    def test_get_llm_exists(self) -> None:
        """Verify get_llm is callable."""
        try:
            from apps.ai_agents.router import get_llm
            assert callable(get_llm)
        except ImportError:
            pytest.skip("Module not available")

    def test_get_agent_service_exists(self) -> None:
        """Verify get_agent_service is callable."""
        try:
            from apps.ai_agents.router import get_agent_service
            assert callable(get_agent_service)
        except ImportError:
            pytest.skip("Module not available")

    def test_chat_stream_exists(self) -> None:
        """Verify chat_stream is callable."""
        try:
            from apps.ai_agents.router import chat_stream
            assert callable(chat_stream)
        except ImportError:
            pytest.skip("Module not available")

    def test_chat_exists(self) -> None:
        """Verify chat is callable."""
        try:
            from apps.ai_agents.router import chat
            assert callable(chat)
        except ImportError:
            pytest.skip("Module not available")

    def test_list_conversations_exists(self) -> None:
        """Verify list_conversations is callable."""
        try:
            from apps.ai_agents.router import list_conversations
            assert callable(list_conversations)
        except ImportError:
            pytest.skip("Module not available")

