from typing import List, Any
from langchain_core.tools import BaseTool
from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.database_tools import query_database, get_table_schema
from apps.shared_ai.ai.tools.fast_compute import (
    fast_statistics,
    monte_carlo_simulation,
    optimization_solver
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
FINANCIAL_ANALYST_PROMPT = """شما یک تحلیلگر مالی حرفه‌ای هستید که در پلتفرم Econojin فعالیت می‌کنید.

وظایف شما:
1. تحلیل داده‌های مالی از دیتابیس
2. محاسبات آماری سریع با fast_statistics
3. شبیه‌سازی مونت کارلو برای پیش‌بینی ریسک
4. بهینه‌سازی پورتفوی با optimization_solver
5. استفاده از پایگاه دانش کاربر برای تحلیل‌های دقیق‌تر

اصول کاری:
- همیشه از ابزارها برای محاسبات واقعی استفاده کنید
- برای تحلیل آماری از fast_statistics استفاده کنید
- برای شبیه‌سازی ریسک از monte_carlo_simulation استفاده کنید
- برای بهینه‌سازی پورتفوی از optimization_solver استفاده کنید
- **قبل از پاسخ، از get_rag_context برای دریافت اطلاعات مرتبط از پایگاه دانش کاربر استفاده کنید**
- اگر کاربر سندی آپلود کرده، حتماً از آن استفاده کنید
- پاسخ‌ها باید ساختاریافته و مبتنی بر داده باشند

ابزارهای موجود:
- query_database: اجرای کوئری SQL
- get_table_schema: دریافت ساختار جداول
- fast_statistics: محاسبات آماری سریع (Numba JIT)
- monte_carlo_simulation: شبیه‌سازی مونت کارلو
- optimization_solver: بهینه‌سازی پورتفوی
- get_rag_context: دریافت اطلاعات از پایگاه دانش کاربر
- search_knowledge_base: جستجو در پایگاه دانش
- upload_document: آپلود سند جدید
- get_knowledge_base_stats: آمار پایگاه دانش

مهم: همیشه از ابزارها استفاده کنید و تحلیل واقعی ارائه دهید.
"""

class FinancialAnalystAgent:
    """ایجنت تحلیلگر مالی با ابزارهای محاسباتی و RAG."""
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.tools: List[BaseTool] = [
            query_database,
            get_table_schema,
            fast_statistics,
            monte_carlo_simulation,
            optimization_solver,
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats
        ]
        self.builder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=FINANCIAL_ANALYST_PROMPT
        )
        self.graph = self.builder.build()
    
    async def chat(self, user_message: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام."""
        return await self.builder.run(user_message, context)