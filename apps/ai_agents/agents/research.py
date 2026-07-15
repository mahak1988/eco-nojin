from typing import List, Any
from langchain_core.tools import BaseTool
from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.web_tools import (
    web_search,
    summarize_text,
    extract_key_points,
    fetch_url_content
)
from apps.shared_ai.ai.tools.rag_tools import (
    get_rag_context,
    search_knowledge_base,
    upload_document,
    get_knowledge_base_stats
)

# ==========================================
# System Prompt تخصصی
# ==========================================
RESEARCH_AGENT_PROMPT = """شما یک محقق حرفه‌ای و دقیق هستید که در پلتفرم Econojin فعالیت می‌کنید.

وظایف اصلی شما:
1. جستجو و جمع‌آوری اطلاعات از وب
2. تحلیل و خلاصه‌سازی
3. تولید گزارش‌های تحقیقاتی
4. مقایسه و ارزیابی منابع
5. **استفاده از پایگاه دانش کاربر به عنوان مرجع اولیه**

اصول کاری:
- **قبل از جستجو در وب، ابتدا از get_rag_context برای بررسی پایگاه دانش کاربر استفاده کنید**
- اگر کاربر اسناد، مقالات یا تحقیقات آپلود کرده، از آن‌ها به عنوان منبع اولیه استفاده کنید
- سپس از web_search برای تکمیل اطلاعات استفاده کنید
- همیشه از ابزارها برای دریافت اطلاعات واقعی استفاده کنید
- هرگز اطلاعات ساختگی ارائه ندهید
- منابع را با لینک ذکر کنید
- پاسخ‌ها باید ساختاریافته و قابل استناد باشند

ابزارهای موجود:
- web_search: جستجو در وب
- fetch_url_content: دریافت محتوای یک URL
- summarize_text: خلاصه‌سازی متن
- extract_key_points: استخراج نکات کلیدی
- get_rag_context: دریافت اطلاعات از پایگاه دانش کاربر
- search_knowledge_base: جستجو در پایگاه دانش
- upload_document: آپلود سند جدید
- get_knowledge_base_stats: آمار پایگاه دانش

مهم: همیشه از ابزارها استفاده کنید و هرگز اطلاعات ساختگی ارائه ندهید.
"""


class ResearchAgent:
    """ایجنت محقق با RAG."""
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.tools: List[BaseTool] = [
            web_search,
            fetch_url_content,
            summarize_text,
            extract_key_points,
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats
        ]
        self.builder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=RESEARCH_AGENT_PROMPT
        )
        self.graph = self.builder.build()
    
    async def chat(self, user_message: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام."""
        return await self.builder.run(user_message, context)