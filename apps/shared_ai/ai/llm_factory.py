import os
import logging
from typing import Optional, Any, Literal
from dotenv import load_dotenv
from pathlib import Path

# بارگذاری .env در ابتدای فایل
load_dotenv(Path(__file__).parent.parent.parent.parent / ".env")

logger = logging.getLogger(__name__)

# ==========================================
# Provider Types
# ==========================================
LLMProvider = Literal["groq", "xai", "gemini", "openrouter", "ollama", "fake"]

# ==========================================
# Configuration
# ==========================================
DEFAULT_PROVIDER = os.getenv("LLM_PROVIDER", "xai")
DEFAULT_MODEL = os.getenv("LLM_MODEL", "")

PROVIDER_DEFAULTS = {
    "groq": "llama-3.3-70b-versatile",
    "xai": "grok-2",  # ✅ اصلاح شد از grok-2-latest به grok-2
    "gemini": "gemini-2.5-flash",
    "openrouter": "meta-llama/llama-4-maverick:free",
    "ollama": "llama3.1:8b",
    "fake": "fake"
}

# ==========================================
# LLM Factory
# ==========================================
class LLMFactory:
    """
    کارخانه چندگانه LLM.
    
    پشتیبانی از:
    - Groq (سریع‌ترین، Llama 3.3 70B)
    - xAI/Grok (مدل Grok 2)
    - Google Gemini (کیفیت بالا)
    - OpenRouter (تنوع مدل‌ها)
    - Ollama (محلی و آفلاین)
    - Fake (برای تست)
    """
    
    @staticmethod
    def create(
        provider: Optional[LLMProvider] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        **kwargs
    ) -> Any:
        """ساخت نمونه LLM."""
        provider = provider or DEFAULT_PROVIDER
        model = model or DEFAULT_MODEL or PROVIDER_DEFAULTS.get(provider, "fake")
        
        logger.info(f"🤖 Creating LLM: provider={provider}, model={model}")
        
        try:
            if provider == "groq":
                return LLMFactory._create_groq(model, temperature, **kwargs)
            elif provider == "xai":
                return LLMFactory._create_xai(model, temperature, **kwargs)
            elif provider == "gemini":
                return LLMFactory._create_gemini(model, temperature, **kwargs)
            elif provider == "openrouter":
                return LLMFactory._create_openrouter(model, temperature, **kwargs)
            elif provider == "ollama":
                return LLMFactory._create_ollama(model, temperature, **kwargs)
            elif provider == "fake":
                return LLMFactory._create_fake(model, temperature, **kwargs)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        except ImportError as e:
            logger.warning(f"⚠️ Provider {provider} not available: {e}")
            logger.info("🔄 Falling back to fake LLM")
            return LLMFactory._create_fake(model, temperature, **kwargs)
        except Exception as e:
            logger.error(f"❌ Failed to create LLM: {e}")
            logger.info("🔄 Falling back to fake LLM")
            return LLMFactory._create_fake(model, temperature, **kwargs)
    
    @staticmethod
    def _create_groq(model: str, temperature: float, **kwargs) -> Any:
        """ساخت Groq LLM."""
        from langchain_groq import ChatGroq
        
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set. Get one at https://console.groq.com")
        
        return ChatGroq(
            model=model,
            api_key=api_key,
            temperature=temperature,
            **kwargs
        )
    
    @staticmethod
    def _create_xai(model: str, temperature: float, **kwargs) -> Any:
        """ساخت xAI/Grok LLM."""
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise RuntimeError("XAI_API_KEY not set. Get one at https://console.x.ai")
        
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://api.x.ai/v1",
            temperature=temperature,
            default_headers={
                "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8000"),
                "X-Title": "Econojin API"
            },
            **kwargs
        )
    
    @staticmethod
    def _create_gemini(model: str, temperature: float, **kwargs) -> Any:
        """ساخت Google Gemini LLM."""
        from langchain_google_genai import ChatGoogleGenerativeAI
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not set. Get one at https://aistudio.google.com")
        
        return ChatGoogleGenerativeAI(
            model=model,
            google_api_key=api_key,
            temperature=temperature,
            **kwargs
        )
    
    @staticmethod
    def _create_openrouter(model: str, temperature: float, **kwargs) -> Any:
        """ساخت OpenRouter LLM."""
        from langchain_openai import ChatOpenAI
        
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set. Get one at https://openrouter.ai")
        
        return ChatOpenAI(
            model=model,
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
            temperature=temperature,
            default_headers={
                "HTTP-Referer": os.getenv("APP_URL", "http://localhost:8000"),
                "X-Title": "Econojin API"
            },
            **kwargs
        )
    
    @staticmethod
    def _create_ollama(model: str, temperature: float, **kwargs) -> Any:
        """ساخت Ollama LLM (محلی)."""
        from langchain_ollama import ChatOllama
        
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        
        return ChatOllama(
            model=model,
            base_url=base_url,
            temperature=temperature,
            timeout=120,
            **kwargs
        )
    
    @staticmethod
    def _create_fake(model: str, temperature: float, **kwargs) -> Any:
        """ساخت Fake LLM برای تست."""
        from langchain_core.language_models.fake_chat_models import FakeMessagesListChatModel
        from langchain_core.messages import AIMessage
        
        class FakeToolCallingModel(FakeMessagesListChatModel):
            def bind_tools(self, tools, **kwargs):
                return self
        
        return FakeToolCallingModel(
            responses=[
                AIMessage(content="این یک پاسخ آزمایشی است. لطفاً یکی از API Keyها را در فایل .env تنظیم کنید:")
            ]
        )
    
    @staticmethod
    def list_providers() -> dict:
        """لیست providerهای موجود و وضعیت آن‌ها."""
        providers = {
            "groq": {
                "name": "Groq",
                "status": "available" if os.getenv("GROQ_API_KEY") else "not_configured",
                "default_model": PROVIDER_DEFAULTS["groq"],
                "signup_url": "https://console.groq.com",
                "description": "سریع‌ترین، Llama 3.3 70B، رایگان"
            },
            "xai": {
                "name": "xAI (Grok)",
                "status": "available" if os.getenv("XAI_API_KEY") else "not_configured",
                "default_model": PROVIDER_DEFAULTS["xai"],
                "signup_url": "https://console.x.ai",
                "description": "مدل Grok 2، قدرتمند"
            },
            "gemini": {
                "name": "Google Gemini",
                "status": "available" if os.getenv("GOOGLE_API_KEY") else "not_configured",
                "default_model": PROVIDER_DEFAULTS["gemini"],
                "signup_url": "https://aistudio.google.com",
                "description": "کیفیت بالا، Gemini 2.5 Flash"
            },
            "openrouter": {
                "name": "OpenRouter",
                "status": "available" if os.getenv("OPENROUTER_API_KEY") else "not_configured",
                "default_model": PROVIDER_DEFAULTS["openrouter"],
                "signup_url": "https://openrouter.ai",
                "description": "دسترسی به 26+ مدل رایگان"
            },
            "ollama": {
                "name": "Ollama (Local)",
                "status": "available",
                "default_model": PROVIDER_DEFAULTS["ollama"],
                "signup_url": "https://ollama.com",
                "description": "محلی و آفلاین، بدون نیاز به API Key"
            },
            "fake": {
                "name": "Fake (Testing)",
                "status": "available",
                "default_model": "fake",
                "signup_url": None,
                "description": "برای تست بدون نیاز به API"
            }
        }
        return providers

# ============================================================
# Compatibility Aliases (Added by Phase 2 Fix)
# ============================================================

get_llm = LLMFactory().create
