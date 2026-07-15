from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from apps.shared_core.database.session import get_db_session
from apps.shared_ai.ai.llm_factory import LLMFactory
from apps.users.dependencies import get_current_user
from apps.users.models import User
from apps.ai_agents.service import AIAgentService
from apps.ai_agents.schemas import (
    ChatRequest,
    ChatResponse,
    ConversationCreate,
    ConversationResponse,
    ConversationDetail,
    MessageResponse
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai-agents", tags=["AI Agents"])

# ==========================================
# LLM Dependency
# ==========================================
def get_llm():
    """دریافت نمونه LLM از Factory."""
    return LLMFactory.create()

def get_agent_service(
    session: AsyncSession = Depends(get_db_session)
) -> AIAgentService:
    """Dependency برای AIAgentService."""
    return AIAgentService(session=session, llm=get_llm())

# ==========================================
# Streaming Endpoint
# ==========================================
@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    agent_service: AIAgentService = Depends(get_agent_service)
):
    """
    ارسال پیام به ایجنت و دریافت پاسخ به صورت streaming (SSE).
    
    این endpoint پاسخ را به صورت real-time ارسال می‌کند (مانند ChatGPT).
    
    فرمت پاسخ:
    - data: {"conversation_id": 123}
    - data: {"content": "chunk of text"}
    - data: {"content": "more text"}
    - data: {"done": true, "used_fallback": false}
    """
    async def event_generator():
        try:
            async for chunk in agent_service.chat_stream(
                user_id=current_user.id,
                request=request
            ):
                yield chunk
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"data: {{\"error\": \"{str(e)}\"}}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # برای nginx
        }
    )

# ==========================================
# Non-Streaming Endpoint (existing)
# ==========================================
@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    agent_service: AIAgentService = Depends(get_agent_service)
):
    """ارسال پیام به ایجنت و دریافت پاسخ (non-streaming)."""
    try:
        result = await agent_service.chat(
            user_id=current_user.id,
            request=request
        )
        
        return ChatResponse(
            conversation_id=result["conversation_id"],
            assistant_message=result["assistant_message"],
            messages=[
                MessageResponse.model_validate(m)
                for m in result["messages"]
            ],
            used_fallback=result.get("used_fallback", False)
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="خطا در پردازش درخواست"
        )

# ==========================================
# Other Endpoints (existing)
# ==========================================
@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    agent_type: str = None,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    agent_service: AIAgentService = Depends(get_agent_service)
):
    """دریافت لیست مکالمات کاربر."""
    conversations = await agent_service.get_user_conversations(
        user_id=current_user.id,
        agent_type=agent_type,
        limit=limit
    )
    return [ConversationResponse(**c) for c in conversations]

@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    agent_service: AIAgentService = Depends(get_agent_service)
):
    """دریافت جزئیات یک مکالمه با تمام پیام‌ها."""
    conv = await agent_service.get_conversation_detail(
        conversation_id=conversation_id,
        user_id=current_user.id
    )
    
    if not conv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="مکالمه یافت نشد"
        )
    
    msg_count = await agent_service.conversation_repo.get_message_count(conversation_id)
    
    return ConversationDetail(
        id=conv.id,
        user_id=conv.user_id,
        agent_type=conv.agent_type,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=msg_count,
        messages=[
            MessageResponse.model_validate(m)
            for m in conv.messages
        ]
    )

@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: ConversationCreate,
    current_user: User = Depends(get_current_user),
    agent_service: AIAgentService = Depends(get_agent_service)
):
    """ایجاد مکالمه جدید."""
    conv = await agent_service.create_conversation(
        user_id=current_user.id,
        agent_type=request.agent_type,
        title=request.title
    )
    return ConversationResponse(
        id=conv.id,
        user_id=conv.user_id,
        agent_type=conv.agent_type,
        title=conv.title,
        created_at=conv.created_at,
        updated_at=conv.updated_at,
        message_count=0
    )

@router.get("/types")
async def list_agent_types():
    """دریافت لیست انواع ایجنت‌های موجود."""
    return {
        "agents": [
            {
                "type": "financial",
                "name": "تحلیلگر مالی",
                "description": "تحلیل داده‌های مالی و ارائه گزارش‌های استراتژیک",
                "capabilities": [
                    "اجرای کوئری SQL روی دیتابیس",
                    "تحلیل روندها و الگوهای مالی",
                    "محاسبات آماری سریع (Numba JIT)",
                    "شبیه‌سازی مونت کارلو",
                    "بهینه‌سازی پورتفوی"
                ]
            },
            {
                "type": "support",
                "name": "پشتیبانی",
                "description": "پاسخ به سوالات و حل مشکلات کاربران",
                "capabilities": [
                    "پاسخ به سوالات عمومی",
                    "راهنمایی در استفاده از پلتفرم",
                    "حل مشکلات فنی"
                ]
            },
            {
                "type": "admin",
                "name": "کمک ادمین",
                "description": "مدیریت پروژه، گزارش‌گیری و پشتیبانی تصمیم‌گیری",
                "capabilities": [
                    "گزارش‌گیری از وضعیت پروژه",
                    "تحلیل معیارهای کلیدی (KPIs)",
                    "اولویت‌بندی تسک‌ها",
                    "پشتیبانی تصمیم‌گیری استراتژیک"
                ]
            },
            {
                "type": "research",
                "name": "محقق",
                "description": "جستجو در وب، خلاصه‌سازی مقالات و تولید گزارش‌های تحقیقاتی",
                "capabilities": [
                    "جستجو در وب و یافتن منابع معتبر",
                    "خلاصه‌سازی متون طولانی",
                    "استخراج نکات کلیدی",
                    "تولید گزارش‌های تحقیقاتی"
                ]
            },
            {
                "type": "data_analyst",
                "name": "تحلیلگر داده",
                "description": "تحلیل آماری، تولید نمودار و آزمون فرضیه‌ها",
                "capabilities": [
                    "محاسبات آماری سریع (Numba JIT)",
                    "تحلیل همبستگی بین متغیرها",
                    "آزمون فرضیه‌ها (t-test, ANOVA)",
                    "حل معادلات دیفرانسیل (SciPy)",
                    "عملیات ماتریسی پیشرفته",
                    "آموزش مدل‌های ML",
                    "تولید نمودار"
                ]
            },
            {
                "type": "code_assistant",
                "name": "دستیار کدنویسی",
                "description": "تحلیل کد، شناسایی باگ، تولید تست و مستندات",
                "capabilities": [
                    "تحلیل ساختاری کد با AST",
                    "شناسایی باگ‌های رایج",
                    "محاسبه پیچیدگی الگوریتمی",
                    "تولید تست واحد",
                    "تبدیل بین زبان‌ها",
                    "تولید مستندات"
                ]
            }
        ]
    }

@router.get("/llm/providers")
async def list_llm_providers():
    """دریافت لیست ارائه‌دهندگان LLM."""
    return LLMFactory.list_providers()

@router.get("/llm/current")
async def get_current_llm():
    """دریافت اطلاعات LLM فعلی."""
    import os
    
    provider = os.getenv("LLM_PROVIDER", "xai")
    model = os.getenv("LLM_MODEL", "")
    
    from apps.shared_ai.ai.llm_factory import PROVIDER_DEFAULTS
    model = model or PROVIDER_DEFAULTS.get(provider, "unknown")
    
    return {
        "provider": provider,
        "model": model,
        "status": "active"
    }