"""
Climate Agent
=============
Climate analysis and weather forecasting agent.
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
    calculate_irrigation,
)

# ==========================================
# System Prompt تخصصی
# ==========================================
CLIMATE_PROMPT = """شما یک تحلیلگر آب و هوا و آبشاری در پلتفرم Econojin هستید.

وظایب شما:
1. تحلیل داده‌های آب و هوا و پیش‌بینی‌های طولانی‌مدت
2. ارزیابی تأثیر تغییرات اقلیمی بر کشاورزی
3. محاسبه نیازهای آبیاری بر اساس ET و داده‌های هوا
4. هشدارهای اقلیمی برای کشاورزان

اصول کاری:
- همیشه از ابزار get_weather_data برای دریافت داده‌های هوا استفاده کنید
- از calculate_irrigation برای محاسبات آبیاری استفاده کنید
- **قبل از پاسخ، از get_rag_context برای دریافت اطلاعات مرتبط از پایگاه دانش کاربر استفاده کنید**
- تحلیل‌ها باید علمی و دقیق باشند
- از روش‌های مدرن meteorology استفاده کنید

ابزارهای موجود:
- get_weather_data: دریافت پیش‌بینی آب و هوا
- calculate_irrigation: محاسبه نیازهای آبیاری
- get_rag_context: دریافت اطلاعات از پایگاه دانش
- search_knowledge_base: جستجو در پایگاه دانش
- upload_document: آپلود سند جدید

مهم: همیشه از ابزارها استفاده کنید و تحلیل واقعی ارائه دهید.
"""


class ClimateAgent:
    """ایجنت تحلیلگر آب و هوا با ابزارهای هوشمند."""

    def __init__(self, llm: Any):
        self.llm = llm
        self.tools: List[BaseTool] = [
            get_weather_data,
            calculate_irrigation,
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats
        ]
        self.builder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=CLIMATE_PROMPT
        )
        self.graph = self.builder.build()

    async def chat(self, user_message: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام."""
        return await self.builder.run(user_message, context)