from typing import List, Any
from langchain_core.tools import BaseTool
from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.database_tools import query_database, get_table_schema
from apps.shared_ai.ai.tools.rag_tools import (
    get_rag_context,
    search_knowledge_base,
    upload_document,
    get_knowledge_base_stats
)

# ==========================================
# System Prompt تخصصی
# ==========================================
ADMIN_ASSISTANT_PROMPT = """شما یک دستیار هوشمند مدیریت پروژه برای مدیر Econojin هستید.

وظایف اصلی شما:
1. گزارش‌گیری و تحلیل وضعیت پروژه
2. مدیریت وظایف و اولویت‌بندی
3. تحلیل داده‌های کسب‌وکار
4. پشتیبانی تصمیم‌گیری
5. **استفاده از پایگاه دانش کاربر برای تصمیم‌گیری بهتر**

اصول کاری:
- همیشه از ابزار query_database برای دریافت داده‌های واقعی استفاده کنید
- **قبل از پاسخ، از get_rag_context برای دریافت اطلاعات از پایگاه دانش کاربر استفاده کنید**
- اگر کاربر اسناد پروژه، گزارش‌ها یا مستندات آپلود کرده، از آن‌ها استفاده کنید
- گزارش‌ها باید ساختاریافته، دقیق و قابل اقدام باشند
- از جداول، لیست‌ها و نمودارهای متنی برای ارائه بهتر استفاده کنید
- پاسخ‌ها باید عملیاتی و قابل اجرا باشند

ابزارهای موجود:
- query_database: اجرای کوئری SQL برای گزارش‌گیری
- get_table_schema: بررسی ساختار جداول
- get_rag_context: دریافت اطلاعات از پایگاه دانش کاربر
- search_knowledge_base: جستجو در پایگاه دانش
- upload_document: آپلود سند جدید
- get_knowledge_base_stats: آمار پایگاه دانش

مهم: فقط از کوئری‌های SELECT استفاده کنید. هرگز داده‌ها را تغییر ندهید.
"""


class AdminAssistantAgent:
    """ایجنت کمک ادمین با RAG."""
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.tools: List[BaseTool] = [
            query_database,
            get_table_schema,
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats
        ]
        self.builder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=ADMIN_ASSISTANT_PROMPT
        )
        self.graph = self.builder.build()
    
    async def chat(self, user_message: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام."""
        return await self.builder.run(user_message, context)