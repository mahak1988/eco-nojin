"""Tests for LLM Providers."""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import os

from apps.ai_agents.providers.llm_providers import (
    GroqProvider,
    XAIProvider,
    GeminiProvider,
    OllamaProvider,
    OpenRouterProvider,
    get_provider,
    list_available_providers
)


class TestGroqProvider:
    """تست‌های Groq Provider."""
    
    def test_groq_initialization(self):
        """بررسی راه‌اندازی Groq."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            provider = GroqProvider(model="llama-3.3-70b-versatile")
            assert provider.model == "llama-3.3-70b-versatile"
            assert provider.temperature == 0.7
            assert provider.is_available()
    
    def test_groq_no_api_key(self):
        """بررسی عدم وجود API key."""
        with patch.dict(os.environ, {}, clear=True):
            if "GROQ_API_KEY" in os.environ:
                del os.environ["GROQ_API_KEY"]
            provider = GroqProvider()
            assert not provider.is_available()


class TestXAIProvider:
    """تست‌های xAI Provider."""
    
    def test_xai_initialization(self):
        """بررسی راه‌اندازی xAI."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test_key"}):
            provider = XAIProvider(model="grok-2")
            assert provider.model == "grok-2"
            assert provider.is_available()


class TestGeminiProvider:
    """تست‌های Gemini Provider."""
    
    def test_gemini_initialization(self):
        """بررسی راه‌اندازی Gemini."""
        with patch.dict(os.environ, {"GOOGLE_API_KEY": "test_key"}):
            provider = GeminiProvider(model="gemini-2.5-flash")
            assert provider.model == "gemini-2.5-flash"
            assert provider.is_available()


class TestOllamaProvider:
    """تست‌های Ollama Provider."""
    
    def test_ollama_initialization(self):
        """بررسی راه‌اندازی Ollama."""
        # Ollama نیاز به API key ندارد
        provider = OllamaProvider(model="llama3.1:8b")
        assert provider.model == "llama3.1:8b"
        # is_available بررسی می‌کند که سرور در دسترس باشد


class TestOpenRouterProvider:
    """تست‌های OpenRouter Provider."""
    
    def test_openrouter_initialization(self):
        """بررسی راه‌اندازی OpenRouter."""
        with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test_key"}):
            provider = OpenRouterProvider(model="meta-llama/llama-4-maverick:free")
            assert provider.is_available()


class TestProviderRegistry:
    """تست‌های Provider Registry."""
    
    def test_get_provider_groq(self):
        """دریافت Groq provider از registry."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            provider = get_provider("groq")
            assert isinstance(provider, GroqProvider)
    
    def test_get_provider_xai(self):
        """دریافت xAI provider از registry."""
        with patch.dict(os.environ, {"XAI_API_KEY": "test_key"}):
            provider = get_provider("xai")
            assert isinstance(provider, XAIProvider)
    
    def test_get_provider_invalid(self):
        """دریافت provider نامعتبر."""
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider("invalid_provider")


class TestListAvailableProviders:
    """تست‌های لیست providerهای در دسترس."""
    
    def test_list_providers(self):
        """بررسی لیست providerها."""
        # بدون تنظیم API keyها، باید لیست خالی یا فقط ollama برگرداند
        providers = list_available_providers()
        assert isinstance(providers, list)
        # Ollama ممکن است در دسترس باشد اگر سرور اجرا باشد
        # بقیه providerها نیاز به API key دارند


@pytest.mark.asyncio
class TestAsyncChat:
    """تست‌های چت غیرهمگام."""
    
    async def test_groq_chat_mock(self):
        """تست چت Groq با mock."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            with patch.object(GroqProvider, '_initialize_client') as mock_init:
                mock_client = AsyncMock()
                mock_client.ainvoke = AsyncMock(return_value=Mock(content="Test response"))
                mock_init.return_value = mock_client
                
                provider = GroqProvider()
                messages = [{"role": "user", "content": "Hello"}]
                response = await provider.chat(messages)
                
                assert response == "Test response"
                mock_client.ainvoke.assert_called_once()
    
    async def test_groq_chat_stream_mock(self):
        """تست streaming چت Groq با mock."""
        with patch.dict(os.environ, {"GROQ_API_KEY": "test_key"}):
            with patch.object(GroqProvider, '_initialize_client') as mock_init:
                mock_client = AsyncMock()
                
                async def mock_stream():
                    yield Mock(content="Hello ")
                    yield Mock(content="world!")
                
                mock_client.astream = mock_stream
                mock_init.return_value = mock_client
                
                provider = GroqProvider()
                messages = [{"role": "user", "content": "Say hello"}]
                
                chunks = []
                async for chunk in provider.chat_stream(messages):
                    chunks.append(chunk)
                
                assert len(chunks) == 2
                assert chunks[0] == "Hello "
                assert chunks[1] == "world!"
