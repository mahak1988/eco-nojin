from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
import logging
import re

from apps.shared_knowledge.knowledge.repository import KnowledgeRepository

logger = logging.getLogger(__name__)


class TemplateEngine:
    """موتور مدیریت و رندر قالب‌های پاسخ."""
    
    def __init__(self, session: AsyncSession):
        self.repo = KnowledgeRepository(session)
    
    async def get_response(
        self,
        agent_type: str,
        intent: str,
        variables: Optional[Dict[str, Any]] = None
    ) -> str:
        """دریافت پاسخ بر اساس قالب."""
        template = await self.repo.get_template(agent_type, intent)
        
        if not template:
            # fallback به قالب عمومی
            template = await self.repo.get_template("all", "fallback")
        
        if not template:
            return self._default_response(agent_type, intent)
        
        return self._render_template(template.template, variables or {})
    
    def _render_template(self, template: str, variables: Dict[str, Any]) -> str:
        """رندر قالب با متغیرها."""
        result = template
        
        # جایگزینی {variable} با مقدار
        for key, value in variables.items():
            placeholder = f"{{{key}}}"
            result = result.replace(placeholder, str(value))
        
        # حذف placeholderهای باقی‌مانده
        result = re.sub(r'\{[^}]+\}', '', result)
        
        return result.strip()
    
    def _default_response(self, agent_type: str, intent: str) -> str:
        """پاسخ پیش‌فرض در صورت نبود قالب."""
        defaults = {
            "financial": "من ایجنت تحلیلگر مالی هستم. لطفاً سوال مالی خود را مطرح کنید.",
            "support": "من ایجنت پشتیبانی هستم. چگونه می‌توانم کمک کنم؟",
            "admin": "من دستیار مدیریت پروژه هستم. چه کمکی نیاز دارید؟",
            "research": "من ایجنت محقق هستم. موضوع تحقیق خود را مشخص کنید.",
            "data_analyst": "من ایجنت تحلیلگر داده هستم. داده‌های خود را ارائه دهید.",
            "code_assistant": "من دستیار کدنویسی هستم. کد یا سوال خود را مطرح کنید."
        }
        
        return defaults.get(agent_type, "متأسفانه نمی‌توانم کمک کنم.")
    
    async def format_knowledge_response(
        self,
        agent_type: str,
        knowledge_context: str,
        user_query: str,
        rules_summary: str = ""
    ) -> str:
        """فرمت‌بندی پاسخ مبتنی بر دانش."""
        response_parts = []
        
        # header
        agent_names = {
            "financial": "تحلیلگر مالی",
            "support": "پشتیبانی",
            "admin": "کمک ادمین",
            "research": "محقق",
            "data_analyst": "تحلیلگر داده",
            "code_assistant": "دستیار کدنویسی"
        }
        
        agent_name = agent_names.get(agent_type, "ایجنت")
        response_parts.append(f"📚 پاسخ از دانش‌نامه {agent_name}:\n")
        
        # context
        if knowledge_context:
            response_parts.append(knowledge_context)
            response_parts.append("")
        
        # rules
        if rules_summary:
            response_parts.append(rules_summary)
            response_parts.append("")
        
        # footer
        response_parts.append("---")
        response_parts.append("💡 این پاسخ بر اساس دانش‌نامه داخلی تولید شده است.")
        response_parts.append("برای تحلیل عمیق‌تر، لطفاً با LLM آنلاین تعامل کنید.")
        
        return "\n".join(response_parts)