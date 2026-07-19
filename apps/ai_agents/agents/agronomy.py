"""
Agronomy Agent
==============
Smart farming and crop advisory agent.
"""

from typing import List, Any
from langchain_core.tools import BaseTool
from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.rag_tools import (
    get_rag_context,
    search_knowledge_base,
    upload_document,
    get_knowledge_base_stats
)
from apps.ai_agents.tools.registry import (
    get_weather_data,
    get_crop_recommendation,
    calculate_irrigation,
)

# ==========================================
# System Prompt تخصصی
# ==========================================
AGRONOMY_PROMPT = """شما یک مشاور کشاورزی هوشمند در پلتفرم Econojin هستید.

وظایب شما:
1. توصیه کشت بهینه بر اساس شرایط آب و هوا و خاک
2. محاسبه آبیاری و نیازهای آبی محصولات
3. بررسی داده‌های آب و هوا برای تصمیم‌گیری کشاورزی
4. ارائه مشاوره در مورد بذر، کود و سمپاشی

اصول کاری:
- همیشه از ابزارهای get_weather_data و get_crop_recommendation استفاده کنید
- برای محاسبه آبیاری از calculate_irrigation استفاده کنید
- **قبل از پاسخ، از get_rag_context برای دریافت اطلاعات مرتبط از پایگاه دانش کاربر استفاده کنید**
- اگر کاربر سندی آپلود کرده، حتماً از آن استفاده کنید
- پاسخ‌ها باید علمی و عملی باشند

ابزارهای موجود:
- get_weather_data: دریافت پیش‌بینی آب و هوا
- get_crop_recommendation: توصیه کشت بر اساس شرایط
- calculate_irrigation: محاسبه نیازهای آبیاری
- get_rag_context: دریافت اطلاعات از پایگاه دانش
- search_knowledge_base: جستجو در پایگاه دانش
- upload_document: آپلود سند جدید

مهم: همیشه از ابزارها استفاده کنید و مشاوره واقعی ارائه دهید.
"""


class AgronomyAgent:
    """ایجنت مشاور کشاورزی با ابزارهای هوشمند."""

    def __init__(self, llm: Any):
        self.llm = llm
        self.tools: List[BaseTool] = [
            get_weather_data,
            get_crop_recommendation,
            calculate_irrigation,
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats
        ]
        self.builder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=AGRONOMY_PROMPT
        )
        self.graph = self.builder.build()

    async def chat(self, user_message: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام."""
        return await self.builder.run(user_message, context)