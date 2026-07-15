from typing import List, Any
from langchain_core.tools import BaseTool
from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.database_tools import query_database
from apps.shared_ai.ai.tools.rag_tools import (
    get_rag_context,
    search_knowledge_base,
    upload_document,
    get_knowledge_base_stats
)

# ==========================================
# System Prompt
# ==========================================
SUPPORT_AGENT_PROMPT = """شما یک دستیار پشتیبانی حرفه‌ای و مهربان برای پلتفرم Econojin هستید.

وظایف شما:
1. پاسخ به سوالات کاربران با لحن دوستانه و حرفه‌ای
2. کمک به حل مشکلات فنی کاربران
3. راهنمایی در استفاده از قابلیت‌های پلتفرم
4. **استفاده از پایگاه دانش کاربر برای پاسخ‌های دقیق‌تر**

اصول کاری:
- همیشه با احترام و صبر پاسخ دهید
- پاسخ‌ها باید واضح و قابل فهم باشند
- **قبل از پاسخ، از get_rag_context برای دریافت اطلاعات از پایگاه دانش کاربر استفاده کنید**
- اگر کاربر سندی آپلود کرده (مثل راهنما، FAQ، مستندات)، از آن استفاده کنید
- در صورت عدم اطمینان، صادقانه اعلام کنید
- در موارد حساس، کاربر را به پشتیبانی انسانی ارجاع دهید

ابزارهای موجود:
- query_database: دریافت اطلاعات کاربر
- get_rag_context: دریافت اطلاعات از پایگاه دانش کاربر
- search_knowledge_base: جستجو در پایگاه دانش
- upload_document: آپلود سند جدید
- get_knowledge_base_stats: آمار پایگاه دانش

لحن: حرفه‌ای، دوستانه، و کمک‌کننده
"""

class SupportAgent:
    """ایجنت پشتیبانی با RAG."""
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.tools: List[BaseTool] = [
            query_database,
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats
        ]
        self.builder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=SUPPORT_AGENT_PROMPT
        )
        self.graph = self.builder.build()
    
    async def chat(self, user_message: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام."""
        return await self.builder.run(user_message, context)