from typing import Optional, Dict, Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import json

from apps.ai_agents.repository import ConversationRepository, MessageRepository
from apps.ai_agents.models import Conversation, Message
from apps.ai_agents.schemas import ChatRequest
from apps.ai_agents.agents.financial import FinancialAnalystAgent
from apps.ai_agents.agents.support import SupportAgent
from apps.ai_agents.agents.admin import AdminAssistantAgent
from apps.ai_agents.agents.research import ResearchAgent
from apps.ai_agents.agents.data_analyst import DataAnalystAgent
from apps.ai_agents.agents.code_assistant import CodeAssistantAgent
from apps.shared_ai.ai.fallback.brain import FallbackBrain

logger = logging.getLogger(__name__)


class AgentFactory:
    """کارخانه ساخت ایجنت‌ها."""
    
    @staticmethod
    def create_agent(agent_type: str, llm: Any):
        """ساخت ایجنت بر اساس نوع."""
        if agent_type == "financial":
            return FinancialAnalystAgent(llm)
        elif agent_type == "support":
            return SupportAgent(llm)
        elif agent_type == "admin":
            return AdminAssistantAgent(llm)
        elif agent_type == "research":
            return ResearchAgent(llm)
        elif agent_type == "data_analyst":
            return DataAnalystAgent(llm)
        elif agent_type == "code_assistant":
            return CodeAssistantAgent(llm)
        else:
            raise ValueError(f"Unknown agent type: {agent_type}")


class AIAgentService:
    """سرویس اصلی مدیریت ایجنت‌ها و مکالمات."""
    
    def __init__(self, session: AsyncSession, llm: Any):
        self.session = session
        self.llm = llm
        self.conversation_repo = ConversationRepository(session)
        self.message_repo = MessageRepository(session)
        self.fallback_brain = FallbackBrain(session)
    
    async def create_conversation(
        self,
        user_id: int,
        agent_type: str,
        title: Optional[str] = None
    ) -> Conversation:
        """ایجاد مکالمه جدید."""
        conv = await self.conversation_repo.create({
            "user_id": user_id,
            "agent_type": agent_type,
            "title": title or f"مکالمه جدید با ایجنت {agent_type}"
        })
        logger.info(f"✅ Created conversation {conv.id} for user {user_id}")
        return conv
    
    async def get_user_conversations(
        self,
        user_id: int,
        agent_type: Optional[str] = None,
        limit: int = 50
    ):
        """دریافت مکالمات کاربر."""
        conversations = await self.conversation_repo.get_user_conversations(
            user_id=user_id,
            agent_type=agent_type,
            limit=limit
        )
        
        result = []
        for conv in conversations:
            msg_count = await self.conversation_repo.get_message_count(conv.id)
            result.append({
                "id": conv.id,
                "user_id": conv.user_id,
                "agent_type": conv.agent_type,
                "title": conv.title,
                "created_at": conv.created_at,
                "updated_at": conv.updated_at,
                "message_count": msg_count
            })
        
        return result
    
    async def get_conversation_detail(
        self,
        conversation_id: int,
        user_id: int
    ) -> Optional[Conversation]:
        """دریافت جزئیات مکالمه."""
        conv = await self.conversation_repo.get_with_messages(conversation_id)
        
        if not conv:
            return None
        
        if conv.user_id != user_id:
            logger.warning(f"⚠️ Unauthorized access attempt to conversation {conversation_id}")
            return None
        
        return conv
    
    async def chat(
        self,
        user_id: int,
        request: ChatRequest
    ) -> Dict[str, Any]:
        """پردازش پیام کاربر و دریافت پاسخ از ایجنت (non-streaming)."""
        conversation_id = request.conversation_id
        
        if conversation_id:
            conv = await self.conversation_repo.get_by_id(conversation_id)
            if not conv or conv.user_id != user_id:
                raise ValueError("مکالمه یافت نشد یا دسترسی غیرمجاز")
        else:
            conv = await self.create_conversation(
                user_id=user_id,
                agent_type=request.agent_type
            )
            conversation_id = conv.id
        
        user_message = await self.message_repo.create_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        
        history = await self.message_repo.get_conversation_messages(
            conversation_id=conversation_id,
            limit=20
        )
        
        context = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "agent_type": request.agent_type,
            "history": [
                {"role": m.role, "content": m.content}
                for m in history
            ]
        }
        
        assistant_response = None
        used_fallback = False
        
        try:
            agent = AgentFactory.create_agent(request.agent_type, self.llm)
            assistant_response = await agent.chat(
                user_message=request.message,
                context=context
            )
            
            if not assistant_response or "خطایی رخ داد" in assistant_response:
                raise Exception("LLM returned error")
        
        except Exception as e:
            logger.warning(f"⚠️ LLM failed, using fallback: {e}")
            used_fallback = True
            assistant_response = await self.fallback_brain.generate_response(
                agent_type=request.agent_type,
                user_message=request.message,
                user_id=user_id,
                context=context
            )
        
        assistant_message = await self.message_repo.create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=assistant_response,
            metadata_json={"used_fallback": used_fallback}
        )
        
        await self.conversation_repo.update(conv, {"title": conv.title})
        
        all_messages = await self.message_repo.get_conversation_messages(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "assistant_message": assistant_response,
            "messages": all_messages,
            "used_fallback": used_fallback
        }
    
    async def chat_stream(
        self,
        user_id: int,
        request: ChatRequest
    ) -> AsyncGenerator[str, None]:
        """
        پردازش پیام کاربر و streaming پاسخ (SSE).
        
        Yields:
            str: هر chunk از پاسخ در فرمت SSE
        """
        conversation_id = request.conversation_id
        
        # ایجاد یا دریافت مکالمه
        if conversation_id:
            conv = await self.conversation_repo.get_by_id(conversation_id)
            if not conv or conv.user_id != user_id:
                yield f"data: {json.dumps({'error': 'مکالمه یافت نشد'})}\n\n"
                return
        else:
            conv = await self.create_conversation(
                user_id=user_id,
                agent_type=request.agent_type
            )
            conversation_id = conv.id
        
        # ارسال conversation_id به کلاینت
        yield f"data: {json.dumps({'conversation_id': conversation_id})}\n\n"
        
        # ذخیره پیام کاربر
        await self.message_repo.create_message(
            conversation_id=conversation_id,
            role="user",
            content=request.message
        )
        
        # دریافت context
        history = await self.message_repo.get_conversation_messages(
            conversation_id=conversation_id,
            limit=20
        )
        
        context = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "agent_type": request.agent_type,
            "history": [
                {"role": m.role, "content": m.content}
                for m in history
            ]
        }
        
        # streaming از ایجنت
        full_response = ""
        used_fallback = False
        llm_failed = False
        
        try:
            agent = AgentFactory.create_agent(request.agent_type, self.llm)
            
            async for chunk in agent.builder.run_stream(request.message, context):
                # بررسی خطا در chunk
                if "❌ خطا" in chunk or "Error code:" in chunk:
                    llm_failed = True
                    break
                
                full_response += chunk
                # ✅ استفاده از json.dumps به جای repr
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
            
            # اگر LLM خطا داد یا پاسخ خالی بود
            if llm_failed or not full_response or "خطایی رخ داد" in full_response:
                raise Exception("LLM returned error or empty response")
        
        except Exception as e:
            logger.warning(f"⚠️ LLM failed in streaming, using fallback: {e}")
            used_fallback = True
            
            # streaming از fallback
            fallback_response = await self.fallback_brain.generate_response(
                agent_type=request.agent_type,
                user_message=request.message,
                user_id=user_id,
                context=context
            )
            
            full_response = fallback_response
            
            # ارسال fallback به صورت chunk
            chunk_size = 50
            for i in range(0, len(fallback_response), chunk_size):
                chunk = fallback_response[i:i+chunk_size]
                yield f"data: {json.dumps({'content': chunk}, ensure_ascii=False)}\n\n"
        
        # ذخیره پاسخ کامل
        await self.message_repo.create_message(
            conversation_id=conversation_id,
            role="assistant",
            content=full_response,
            metadata_json={"used_fallback": used_fallback, "streaming": True}
        )
        
        await self.conversation_repo.update(conv, {"title": conv.title})
        
        # ارسال پایان stream
        yield f"data: {json.dumps({'done': True, 'used_fallback': used_fallback})}\n\n"