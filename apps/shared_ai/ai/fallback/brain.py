from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from apps.shared_ai.ai.fallback.knowledge_base import KnowledgeBaseEngine
from apps.shared_ai.ai.fallback.rules_engine import RulesEngine
from apps.shared_ai.ai.fallback.templates import TemplateEngine
from apps.shared_knowledge.knowledge.repository import KnowledgeRepository

logger = logging.getLogger(__name__)


class FallbackBrain:
    """
    مغز مرکزی سیستم Fallback.
    
    در صورت عدم دسترسی به LLM خارجی، این سیستم:
    1. دانش‌نامه داخلی را جستجو می‌کند
    2. قوانین کسب‌وکار را اعمال می‌کند
    3. قالب مناسب را انتخاب می‌کند
    4. پاسخ نهایی را تولید می‌کند
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.knowledge_engine = KnowledgeBaseEngine(session)
        self.rules_engine = RulesEngine(session)
        self.template_engine = TemplateEngine(session)
        self.memory_repo = KnowledgeRepository(session)
    
    async def generate_response(
        self,
        agent_type: str,
        user_message: str,
        user_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """تولید پاسخ در حالت offline."""
        logger.info(f"🧠 FallbackBrain processing for {agent_type}")
        
        context = context or {}
        context["query"] = user_message
        
        try:
            # 1. شناسایی intent
            intent = self._detect_intent(user_message, agent_type)
            logger.info(f"📋 Detected intent: {intent}")
            
            # 2. جستجوی دانش
            knowledge_context = await self.knowledge_engine.get_context_for_agent(
                agent_type, user_message
            )
            
            # 3. ارزیابی قوانین
            rules_summary = await self.rules_engine.get_actions_summary(
                agent_type, context
            )
            
            # 4. ذخیره در حافظه
            await self._save_to_memory(agent_type, user_id, user_message, intent)
            
            # 5. تولید پاسخ
            if knowledge_context:
                response = await self.template_engine.format_knowledge_response(
                    agent_type=agent_type,
                    knowledge_context=knowledge_context,
                    user_query=user_message,
                    rules_summary=rules_summary
                )
            else:
                # استفاده از template
                response = await self.template_engine.get_response(
                    agent_type, intent, context
                )
            
            logger.info(f"✅ Fallback response generated ({len(response)} chars)")
            return response
        
        except Exception as e:
            logger.error(f"❌ FallbackBrain error: {e}")
            return await self.template_engine.get_response(agent_type, "fallback", {})
    
    def _detect_intent(self, message: str, agent_type: str) -> str:
        """شناسایی intent پیام کاربر."""
        message_lower = message.lower()
        
        # greeting detection
        greetings = ["سلام", "درود", "hello", "hi", "صبح بخیر", "عصر بخیر"]
        if any(g in message_lower for g in greetings):
            return "greeting"
        
        # agent-specific intents
        if agent_type == "financial":
            if any(w in message_lower for w in ["تحلیل", "نسبت", "سود", "زیان"]):
                return "analysis_request"
            if any(w in message_lower for w in ["پیشنهاد", "توصیه"]):
                return "recommendation"
        
        elif agent_type == "support":
            if any(w in message_lower for w in ["مشکل", "خطا", "کار نمی‌کند"]):
                return "issue_report"
            if any(w in message_lower for w in ["چگونه", "راهنما"]):
                return "how_to"
        
        elif agent_type == "admin":
            if any(w in message_lower for w in ["گزارش", "وضعیت"]):
                return "status_report"
            if any(w in message_lower for w in ["اولویت", "تسک"]):
                return "task_management"
        
        elif agent_type == "research":
            if any(w in message_lower for w in ["تحقیق", "جستجو", "منبع"]):
                return "research_request"
        
        elif agent_type == "data_analyst":
            if any(w in message_lower for w in ["تحلیل", "آمار", "نمودار"]):
                return "data_analysis"
        
        elif agent_type == "code_assistant":
            if any(w in message_lower for w in ["باگ", "خطا", "debug"]):
                return "bug_report"
            if any(w in message_lower for w in ["تست", "unit test"]):
                return "test_generation"
        
        return "general_query"
    
    async def _save_to_memory(
        self,
        agent_type: str,
        user_id: int,
        message: str,
        intent: str
    ):
        """ذخیره تعامل در حافظه."""
        try:
            await self.memory_repo.save_memory(
                agent_type=agent_type,
                user_id=user_id,
                memory_type="interaction",
                content=f"Intent: {intent} | Message: {message[:200]}",
                importance=0.5
            )
        except Exception as e:
            logger.warning(f"⚠️ Failed to save memory: {e}")
    
    async def seed_knowledge_if_needed(self):
        """بارگذاری دانش‌نامه در صورت نیاز."""
        from apps.shared_knowledge.knowledge.seed_data import seed_knowledge_base
        await seed_knowledge_base(self.session)