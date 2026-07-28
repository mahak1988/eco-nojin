"""Public AI agent meta endpoints (no auth) + feedback stub."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/ai-agents", tags=["AI Agents Public"])

_FEEDBACK: list[dict] = []


class FeedbackIn(BaseModel):
    conversation_id: int | None = None
    rating: int = Field(..., ge=1, le=5)
    comment: str = ""


@router.get("/providers")
async def providers():
    return {
        "providers": [
            {"id": "fake", "name": "Fake/local", "status": "always"},
            {"id": "openai", "name": "OpenAI", "status": "key-required"},
            {"id": "groq", "name": "Groq", "status": "key-required"},
            {"id": "gemini", "name": "Google Gemini", "status": "key-required"},
            {"id": "ollama", "name": "Ollama local", "status": "optional"},
            {"id": "openrouter", "name": "OpenRouter", "status": "key-required"},
            {"id": "xai", "name": "xAI", "status": "key-required"},
        ]
    }


@router.get("/history")
async def history_stub():
    return {"data": [], "message": "Use authenticated /ai-agents/conversations for real history"}


@router.post("/feedback")
async def feedback(body: FeedbackIn):
    row = body.model_dump()
    _FEEDBACK.append(row)
    return {"ok": True, "stored": len(_FEEDBACK)}


@router.post("/rag/query")
async def rag_query(q: str = ""):
    return {
        "query": q,
        "hits": [],
        "answer": "RAG corpus not indexed in this environment; use authenticated chat with docs when available.",
        "engine": "stub",
    }
