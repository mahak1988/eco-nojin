from fastapi import APIRouter, Body, Request
from pydantic import BaseModel, Field

router = APIRouter(tags=["AI"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    locale: str = Field(default="fa")
    module: str = Field(default="general")


class ChatResponse(BaseModel):
    reply: str
    agent: str
    suggestions: list[str] = []


KNOWLEDGE_FA = {
    "کشاورز": "می‌توانید از پنل کشاورزان ثبت‌نام و مزرعه خود را مدیریت کنید.",
    "هواشناسی": "ماژول هواشناسی پیش‌بینی ۷ روزه و هشدار یخبندان دارد.",
    "ecocoin": "EcoCoin با فرمول ماینر طبیعی از اقدامات سبز محاسبه می‌شود.",
    "شبیه": "شبیه‌ساز RothC و AquaCrop در /api/v1/simulation در دسترس است.",
}

KNOWLEDGE_EN = {
    "farmer": "Use the Farmers panel to register and manage your farm profile.",
    "weather": "Weather module provides 7-day forecast and frost alerts.",
    "ecocoin": "EcoCoin uses the natural miner formula from green actions.",
    "simulation": "RothC and AquaCrop simulators are at /api/v1/simulation.",
}


def _build_reply(message: str, locale: str, module: str) -> ChatResponse:
    msg = message.lower()
    kb = KNOWLEDGE_EN if locale.startswith("en") else KNOWLEDGE_FA
    hints = []
    for key, text in kb.items():
        if key in msg or key in module.lower():
            hints.append(text)
    if locale.startswith("en"):
        reply = (
            f"[Econojin Agent · {module}] I received your question about: «{message[:120]}». "
            + (hints[0] if hints else "Explore modules from the dashboard or run a simulation.")
        )
        suggestions = ["Run RothC simulation", "Check weather forecast", "Mine EcoCoin"]
    else:
        reply = (
            f"[ایجنت اکو نوژین · {module}] پرسش شما: «{message[:120]}» — "
            + (hints[0] if hints else "از داشبورد ماژول‌ها یا شبیه‌ساز علمی استفاده کنید.")
        )
        suggestions = ["شبیه‌سازی RothC", "پیش‌بینی هواشناسی", "ماینینگ EcoCoin"]
    return ChatResponse(reply=reply, agent="EconojinOrchestrator", suggestions=suggestions)


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request):
    from api.services.llm import chat_llm

    orch = getattr(request.app.state, "orchestrator", None)
    if orch:
        await orch.process_request(req.message, {"locale": req.locale, "module": req.module})

    llm_reply = await chat_llm(req.message, req.locale, req.module)
    if llm_reply:
        base = _build_reply(req.message, req.locale, req.module)
        return ChatResponse(
            reply=llm_reply,
            agent="OpenAI/Azure",
            suggestions=base.suggestions,
        )
    return _build_reply(req.message, req.locale, req.module)
