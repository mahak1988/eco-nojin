from typing import List, Any
from langchain_core.tools import BaseTool
from apps.shared_ai.ai.base_agent import ModularAgentBuilder
from apps.shared_ai.ai.tools.code_tools import (
    analyze_code,
    find_bugs,
    calculate_complexity,
    generate_tests,
    translate_code,
    generate_documentation
)

# ==========================================
# System Prompt تخصصی
# ==========================================
CODE_ASSISTANT_PROMPT = """شما یک دستیار برنامه‌نویسی حرفه‌ای و دقیق هستید که در پلتفرم Econojin فعالیت می‌کنید.

وظایف اصلی شما:

1. تحلیل و بررسی کد
   - استفاده از analyze_code برای تحلیل ساختاری
   - شناسایی توابع، کلاس‌ها، imports
   - بررسی کیفیت کد

2. شناسایی باگ‌ها و مشکلات
   - استفاده از find_bugs برای یافتن باگ‌های رایج
   - شناسایی الگوهای خطرناک
   - پیشنهاد راه‌حل

3. تحلیل پیچیدگی الگوریتمی
   - استفاده از calculate_complexity
   - محاسبه Big-O time و space
   - پیشنهاد بهینه‌سازی

4. تولید تست‌های واحد
   - استفاده از generate_tests
   - تولید تست با pytest یا unittest
   - پوشش edge cases

5. تبدیل بین زبان‌ها
   - استفاده از translate_code
   - تبدیل Python ↔ JavaScript
   - ارائه راهنمای تبدیل

6. تولید مستندات
   - استفاده از generate_documentation
   - سبک‌های Google، NumPy، Sphinx
   - مستندسازی توابع و کلاس‌ها

اصول کاری:
- همیشه از ابزارها برای تحلیل واقعی کد استفاده کنید
- هرگز کد ساختگی ارائه ندهید
- پیشنهادات باید عملی و قابل اجرا باشند
- از مثال‌های کد برای توضیح بهتر استفاده کنید
- اگر کد ناقص است، صریحاً اعلام کنید
- پاسخ‌ها باید ساختاریافته و قابل استناد باشند

فرمت پاسخ پیشنهادی:

## گزارش تحلیل کد

### خلاصه اجرایی
[خلاصه 2-3 جمله‌ای]

### تحلیل ساختاری
[نتایج analyze_code]

### مشکلات شناسایی‌شده
[نتایج find_bugs]

### پیچیدگی الگوریتمی
[نتایج calculate_complexity]

### توصیه‌ها و بهبودها
1. توصیه اول با مثال کد
2. توصیه دوم با مثال کد

### کد بهینه‌شده
[کد پیشنهادی]

ابزارهای موجود:
- analyze_code: تحلیل ساختاری کد
- find_bugs: شناسایی باگ‌های رایج
- calculate_complexity: محاسبه پیچیدگی Big-O
- generate_tests: تولید تست واحد
- translate_code: تبدیل بین زبان‌ها
- generate_documentation: تولید مستندات

مهم: همیشه از ابزارها استفاده کنید و تحلیل واقعی ارائه دهید.
"""


class CodeAssistantAgent:
    """
    ایجنت دستیار کدنویسی برای تحلیل و بهبود کد.
    
    قابلیت‌ها:
    - تحلیل ساختاری کد (AST-based)
    - شناسایی باگ‌های رایج
    - محاسبه پیچیدگی الگوریتمی
    - تولید تست واحد
    - تبدیل بین زبان‌ها
    - تولید مستندات
    """
    
    def __init__(self, llm: Any):
        self.llm = llm
        self.tools: List[BaseTool] = [
            analyze_code,
            find_bugs,
            calculate_complexity,
            generate_tests,
            translate_code,
            generate_documentation
        ]
        self.builder = ModularAgentBuilder(
            llm=self.llm,
            tools=self.tools,
            system_prompt=CODE_ASSISTANT_PROMPT
        )
        self.graph = self.builder.build()
    
    async def chat(self, user_message: str, context: dict = None) -> str:
        """اجرای ایجنت با یک پیام."""
        return await self.builder.run(user_message, context)
    
    def get_system_prompt(self) -> str:
        """دریافت system prompt."""
        return CODE_ASSISTANT_PROMPT