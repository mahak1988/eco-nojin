"""
LLM Provider implementations for Econojin AI Agents.

This module contains direct provider implementations as an alternative
to the centralized LLMFactory, allowing for more granular control.
"""

from abc import ABC, abstractmethod
from typing import Optional, Any, AsyncGenerator, Dict, List
import os
import logging

logger = logging.getLogger(__name__)


class BaseLLMProvider(ABC):
    """پایه‌گذار مشترک برای تمام ارائه‌دهندگان LLM."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "", temperature: float = 0.7):
        self.api_key = api_key or self._get_api_key()
        self.model = model or self._get_default_model()
        self.temperature = temperature
        self._client = None
    
    @abstractmethod
    def _get_api_key(self) -> Optional[str]:
        """دریافت API key از environment."""
        pass
    
    @abstractmethod
    def _get_default_model(self) -> str:
        """مدل پیش‌فرض این provider."""
        pass
    
    @abstractmethod
    def _initialize_client(self) -> Any:
        """راه‌اندازی کلاینت."""
        pass
    
    @property
    def client(self) -> Any:
        """دریافت کلاینت (lazy initialization)."""
        if self._client is None:
            self._client = self._initialize_client()
        return self._client
    
    @abstractmethod
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """ارسال پیام و دریافت پاسخ."""
        pass
    
    @abstractmethod
    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        """Streaming پاسخ."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """بررسی در دسترس بودن provider."""
        return self.api_key is not None


class GroqProvider(BaseLLMProvider):
    """Groq provider - سریع‌ترین گزینه."""
    
    def _get_api_key(self) -> Optional[str]:
        return os.getenv("GROQ_API_KEY")
    
    def _get_default_model(self) -> str:
        return "llama-3.3-70b-versatile"
    
    def _initialize_client(self) -> Any:
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=self.model,
            api_key=self.api_key,
            temperature=self.temperature
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        response = await self.client.ainvoke(lc_messages)
        return response.content
    
    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        async for chunk in self.client.astream(lc_messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    def is_available(self) -> bool:
        return self.api_key is not None


class XAIProvider(BaseLLMProvider):
    """xAI/Grok provider."""
    
    def _get_api_key(self) -> Optional[str]:
        return os.getenv("XAI_API_KEY")
    
    def _get_default_model(self) -> str:
        return "grok-2"
    
    def _initialize_client(self) -> Any:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url="https://api.x.ai/v1",
            temperature=self.temperature,
            default_headers={
                "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8000"),
                "X-Title": "Econojin API"
            }
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        response = await self.client.ainvoke(lc_messages)
        return response.content
    
    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        async for chunk in self.client.astream(lc_messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    def is_available(self) -> bool:
        return self.api_key is not None


class GeminiProvider(BaseLLMProvider):
    """Google Gemini provider."""
    
    def _get_api_key(self) -> Optional[str]:
        return os.getenv("GOOGLE_API_KEY")
    
    def _get_default_model(self) -> str:
        return "gemini-2.5-flash"
    
    def _initialize_client(self) -> Any:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=self.model,
            google_api_key=self.api_key,
            temperature=self.temperature
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        response = await self.client.ainvoke(lc_messages)
        return response.content
    
    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        async for chunk in self.client.astream(lc_messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    def is_available(self) -> bool:
        return self.api_key is not None


class OllamaProvider(BaseLLMProvider):
    """Ollama provider - محلی و آفلاین."""
    
    def _get_api_key(self) -> Optional[str]:
        return None  # نیازی به API key ندارد
    
    def _get_default_model(self) -> str:
        return "llama3.1:8b"
    
    def _initialize_client(self) -> Any:
        from langchain_ollama import ChatOllama
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        return ChatOllama(
            model=self.model,
            base_url=base_url,
            temperature=self.temperature,
            timeout=120
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        response = await self.client.ainvoke(lc_messages)
        return response.content
    
    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        async for chunk in self.client.astream(lc_messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    def is_available(self) -> bool:
        # بررسی دسترسی به سرور Ollama
        import aiohttp
        import asyncio
        
        async def check():
            try:
                base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"{base_url}/api/tags") as resp:
                        return resp.status == 200
            except:
                return False
        
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(check())


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter provider - دسترسی به 26+ مدل."""
    
    def _get_api_key(self) -> Optional[str]:
        return os.getenv("OPENROUTER_API_KEY")
    
    def _get_default_model(self) -> str:
        return "meta-llama/llama-4-maverick:free"
    
    def _initialize_client(self) -> Any:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=self.model,
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=self.temperature,
            default_headers={
                "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8000"),
                "X-Title": "Econojin API"
            }
        )
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        response = await self.client.ainvoke(lc_messages)
        return response.content
    
    async def chat_stream(self, messages: List[Dict], **kwargs) -> AsyncGenerator[str, None]:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        lc_messages = []
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                lc_messages.append(SystemMessage(content=content))
            elif role == "user":
                lc_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                lc_messages.append(AIMessage(content=content))
        
        async for chunk in self.client.astream(lc_messages):
            if hasattr(chunk, 'content') and chunk.content:
                yield chunk.content
    
    def is_available(self) -> bool:
        return self.api_key is not None


# ============================================================
# Provider Registry
# ============================================================

PROVIDER_REGISTRY = {
    "groq": GroqProvider,
    "xai": XAIProvider,
    "gemini": GeminiProvider,
    "ollama": OllamaProvider,
    "openrouter": OpenRouterProvider,
}


def get_provider(provider_name: str, model: Optional[str] = None, temperature: float = 0.7) -> BaseLLMProvider:
    """دریافت نمونه provider."""
    if provider_name not in PROVIDER_REGISTRY:
        raise ValueError(f"Unknown provider: {provider_name}. Available: {list(PROVIDER_REGISTRY.keys())}")
    
    provider_class = PROVIDER_REGISTRY[provider_name]
    return provider_class(model=model, temperature=temperature)


def list_available_providers() -> List[str]:
    """لیست providerهای در دسترس."""
    available = []
    for name, provider_class in PROVIDER_REGISTRY.items():
        try:
            provider = provider_class()
            if provider.is_available():
                available.append(name)
        except:
            pass
    return available
