"""LLM chat — OpenAI or Azure OpenAI via HTTP."""

import logging

import httpx

from api.core.config import settings

logger = logging.getLogger(__name__)

SYSTEM_FA = """شما دستیار اکو نوژین هستید — پلتفرم کشاورزی پایدار، هواشناسی، GIS، EcoCoin و شبیه‌ساز علمی.
پاسخ‌ها کوتاه، دقیق و به فارسی باشد مگر کاربر انگلیسی بخواهد."""

SYSTEM_EN = """You are the Econojin assistant for sustainable agriculture, weather, GIS, EcoCoin, and scientific simulation.
Keep answers concise and helpful."""


async def chat_llm(message: str, locale: str = "fa", module: str = "general") -> str | None:
    if not settings.LLM_ENABLED:
        return None

    system = SYSTEM_EN if locale.startswith("en") else SYSTEM_FA
    user_content = f"[Module: {module}] {message}"

    if settings.AZURE_OPENAI_ENDPOINT and settings.AZURE_OPENAI_KEY:
        return await _azure_chat(system, user_content)
    if settings.OPENAI_API_KEY:
        return await _openai_chat(system, user_content)
    return None


async def _openai_chat(system: str, user: str) -> str | None:
    url = f"{settings.OPENAI_BASE_URL.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 800,
        "temperature": 0.4,
    }
    return await _post_chat(url, headers, payload)


async def _azure_chat(system: str, user: str) -> str | None:
    base = settings.AZURE_OPENAI_ENDPOINT.rstrip("/")
    deployment = settings.AZURE_OPENAI_DEPLOYMENT
    url = f"{base}/openai/deployments/{deployment}/chat/completions?api-version={settings.AZURE_OPENAI_API_VERSION}"
    headers = {
        "api-key": settings.AZURE_OPENAI_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_tokens": 800,
        "temperature": 0.4,
    }
    return await _post_chat(url, headers, payload)


async def _post_chat(url: str, headers: dict, payload: dict) -> str | None:
    try:
        async with httpx.AsyncClient(timeout=60) as client:
            res = await client.post(url, headers=headers, json=payload)
            res.raise_for_status()
            data = res.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.error("LLM request failed: %s", exc)
        return None
