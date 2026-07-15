from typing import List, Any
from langchain_core.tools import BaseTool
from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.data_tools import (
    analyze_statistics,
    correlation_analysis,
    hypothesis_test,
    trend_analysis,
    generate_chart,
    data_summary
)
from apps.shared_ai.ai.tools.fast_compute import (
    fast_statistics,
    monte_carlo_simulation,
    optimization_solver
)
from apps.shared_ai.ai.tools.scientific_compute import (
    solve_differential_equation,
    advanced_matrix_operations,
    train_ml_model,
    numerical_integration,
    scientific_optimization
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
DATA_ANALYST_PROMPT = """شما یک تحلیلگر داده حرفه‌ای هستید که در پلتفرم Econojin فعالیت می‌کنید.

وظایف شما:
1. تحلیل آماری داده‌ها با fast_statistics (سریع‌ترین)
2. تحلیل همبستگی و ارتباطات
3. آزمون فرضیه‌های آماری
4. تحلیل روندها و پیش‌بینی
5. حل معادلات دیفرانسیل
6. عملیات ماتریسی پیشرفته
7. آموزش مدل‌های ML
8. انتگرال‌گیری عددی
9. بهینه‌سازی علمی
10. تولید نمودار و visualization
11. **استفاده از پایگاه دانش کاربر برای تحلیل‌های دقیق‌تر**

اصول کاری:
- برای محاسبات آماری سریع از fast_statistics استفاده کنید
- برای معادلات دیفرانسیل از solve_differential_equation استفاده کنید
- برای عملیات ماتریسی از advanced_matrix_operations استفاده کنید
- برای آموزش مدل ML از train_ml_model استفاده کنید
- **قبل از تحلیل، از get_rag_context برای دریافت اطلاعات از پایگاه دانش کاربر استفاده کنید**
- اگر کاربر داده‌ها، گزارش‌ها یا تحقیقات آپلود کرده، از آن‌ها استفاده کنید
- پاسخ‌ها باید ساختاریافته و مبتنی بر داده باشند

ابزارهای موجود:
- fast_statistics: محاسبات آماری سریع (Numba JIT)
- monte_carlo_simulation: شبیه‌سازی مونت کارلو
- optimization_solver: بهینه‌سازی
- solve_differential_equation: حل معادلات دیفرانسیل
- advanced_matrix_operations: عملیات ماتریسی
- train_ml_model: آموزش مدل ML
- numerical_integration: انتگرال‌گیری عددی
- scientific_optimization: بهینه‌سازی علمی
- correlation_analysis: تحلیل همبستگی
- hypothesis_test: آزمون فرضیه
- trend_analysis: تحلیل روند
- generate_chart: تولید نمودار
- data_summary: خلاصه داده
- get_rag_context: دریافت اطلاعات از پایگاه دانش کاربر
- search_knowledge_base: جستجو در پایگاه دانش
- upload_document: آپلود سند جدید
- get_knowledge_base_stats: آمار پایگاه دانش
"""

class DataAnalystAgent:
    """ایجنت تحلیلگر داده با RAG."""
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.tools: List[BaseTool] = [
            # ابزارهای سریع (Numba)
            fast_statistics,
            monte_carlo_simulation,
            optimization_solver,
            # ابزارهای علمی (SciPy)
            solve_differential_equation,
            advanced_matrix_operations,
            train_ml_model,
            numerical_integration,
            scientific_optimization,
            # ابزارهای قبلی
            analyze_statistics,
            correlation_analysis,
            hypothesis_test,
            trend_analysis,
            generate_chart,
            data_summary,
            # ابزارهای RAG
            get_rag_context,
            search_knowledge_base,
            upload_document,
            get_knowledge_base_stats
        ]
        self.builder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=DATA_ANALYST_PROMPT
        )
        self.graph = self.builder.build()
    
    async def chat(self, user_message: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام."""
        return await self.builder.run(user_message, context)