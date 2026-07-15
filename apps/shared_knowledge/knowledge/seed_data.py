from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import logging

from apps.shared_knowledge.knowledge.models import (
    KnowledgeArticle,
    BusinessRule,
    ResponseTemplate
)

logger = logging.getLogger(__name__)


# ==========================================
# دانش‌نامه ایجنت مالی
# ==========================================
FINANCIAL_KNOWLEDGE = [
    {
        "agent_type": "financial",
        "category": "اصول تحلیل",
        "title": "نسبت‌های مالی کلیدی",
        "content": """
نسبت‌های مالی مهم برای تحلیل:

1. نسبت نقدینگی (Liquidity Ratio):
   - نسبت جاری = دارایی‌های جاری / بدهی‌های جاری
   - نسبت سریع = (دارایی‌های جاری - موجودی کالا) / بدهی‌های جاری
   
2. نسبت اهرمی (Leverage Ratio):
   - نسبت بدهی = کل بدهی‌ها / کل دارایی‌ها
   - پوشش بهره = EBIT / هزینه بهره
   
3. نسبت سودآوری (Profitability Ratio):
   - حاشیه سود خالص = سود خالص / درآمد
   - ROE = سود خالص / حقوق صاحبان سهام
   - ROA = سود خالص / کل دارایی‌ها
   
4. نسبت کارایی (Efficiency Ratio):
   - گردش موجودی کالا = بهای تمام شده کالای فروش رفته / میانگین موجودی
   - دوره وصول مطالبات = (میانگین حساب‌های دریافتنی / فروش اعتباری) × 365
""",
        "keywords": "نسبت مالی, نقدینگی, اهرمی, سودآوری, کارایی, ROE, ROA",
        "priority": 10
    },
    {
        "agent_type": "financial",
        "category": "تحلیل تکنیکال",
        "title": "اندیکاتورهای تکنیکال پرکاربرد",
        "content": """
اندیکاتورهای مهم تحلیل تکنیکال:

1. میانگین متحرک (Moving Average):
   - SMA: میانگین ساده
   - EMA: میانگین نمایی (واکنش سریع‌تر)
   
2. RSI (Relative Strength Index):
   - بالای 70: اشباع خرید
   - زیر 30: اشباع فروش
   
3. MACD:
   - تقاطع خط سیگنال: سیگنال خرید/فروش
   - واگرایی: تغییر روند
   
4. Bollinger Bands:
   - باند بالا و پایین: نوسانات
   - فشردگی: احتمال حرکت بزرگ
""",
        "keywords": "تکنیکال, RSI, MACD, میانگین متحرک, Bollinger",
        "priority": 9
    },
    {
        "agent_type": "financial",
        "category": "مدیریت ریسک",
        "title": "اصول مدیریت ریسک",
        "content": """
اصول مدیریت ریسک در سرمایه‌گذاری:

1. تنوع‌بخشی (Diversification):
   - عدم تمرکز در یک دارایی
   - توزیع بین صنایع مختلف
   
2. حد ضرر (Stop Loss):
   - تعیین حد ضرر قبل از ورود
   - معمولاً 2-5% از قیمت ورود
   
3. اندازه پوزیشن:
   - حداکثر 2% سرمایه در هر معامله
   - ریسک به ریوارد حداقل 1:2
   
4. همبستگی (Correlation):
   - دارایی‌های با همبستگی منفی
   - کاهش ریسک کلی پورتفوی
""",
        "keywords": "ریسک, تنوع, حد ضرر, پوزیشن, همبستگی",
        "priority": 8
    }
]

# ==========================================
# دانش‌نامه ایجنت پشتیبانی
# ==========================================
SUPPORT_KNOWLEDGE = [
    {
        "agent_type": "support",
        "category": "FAQ",
        "title": "سوالات متداول - احراز هویت",
        "content": """
سوالات متداول درباره احراز هویت:

1. فراموشی رمز عبور:
   - کلیک روی "فراموشی رمز"
   - وارد کردن ایمیل
   - بررسی ایمیل و کلیک روی لینک
   - تنظیم رمز جدید
   
2. تغییر ایمیل:
   - ورود به تنظیمات پروفایل
   - کلیک روی "ویرایش ایمیل"
   - تایید ایمیل جدید
   
3. فعال‌سازی دو مرحله‌ای:
   - تنظیمات > امنیت
   - فعال‌سازی 2FA
   - اسکن QR با Google Authenticator
""",
        "keywords": "احراز هویت, رمز عبور, ایمیل, 2FA, امنیت",
        "priority": 10
    },
    {
        "agent_type": "support",
        "category": "راهنما",
        "title": "راهنمای استفاده از ایجنت‌ها",
        "content": """
راهنمای استفاده از ایجنت‌های Econojin:

1. انتخاب ایجنت مناسب:
   - تحلیلگر مالی: برای سوالات مالی و سرمایه‌گذاری
   - پشتیبانی: برای مشکلات فنی و راهنمایی
   - کمک ادمین: برای مدیریت پروژه
   - محقق: برای تحقیق و جمع‌آوری اطلاعات
   - تحلیلگر داده: برای تحلیل آماری
   - دستیار کدنویسی: برای کمک در برنامه‌نویسی
   
2. نحوه تعامل:
   - سوال واضح و مشخص بپرسید
   - در صورت نیاز، داده‌ها را ارائه دهید
   - از ایجنت بخواهید توضیح دهد
   
3. نکات مهم:
   - ایجنت‌ها برای کمک هستند، نه جایگزین تصمیم‌گیری
   - همیشه نتایج را بررسی کنید
   - در موارد حساس، با متخصص مشورت کنید
""",
        "keywords": "ایجنت, راهنما, استفاده, تعامل",
        "priority": 9
    }
]

# ==========================================
# دانش‌نامه ایجنت ادمین
# ==========================================
ADMIN_KNOWLEDGE = [
    {
        "agent_type": "admin",
        "category": "مدیریت پروژه",
        "title": "متدولوژی‌های مدیریت پروژه",
        "content": """
متدولوژی‌های مدیریت پروژه:

1. Agile:
   - Scrum: Sprintهای 2-4 هفته‌ای
   - Kanban: جریان کار مداوم
   - مناسب برای پروژه‌های با نیازهای متغیر
   
2. Waterfall:
   - مراحل خطی و متوالی
   - مناسب برای پروژه‌های با نیازهای ثابت
   
3. Hybrid:
   - ترکیب Agile و Waterfall
   - انعطاف‌پذیری با ساختار
   
4. KPIهای مهم:
   - Velocity: سرعت تیم
   - Burndown: پیشرفت کار
   - Cycle Time: زمان تکمیل تسک
   - Lead Time: زمان از درخواست تا تحویل
""",
        "keywords": "مدیریت پروژه, Agile, Scrum, Kanban, KPI",
        "priority": 10
    },
    {
        "agent_type": "admin",
        "category": "تصمیم‌گیری",
        "title": "چهارچوب‌های تصمیم‌گیری",
        "content": """
چهارچوب‌های تصمیم‌گیری:

1. SWOT Analysis:
   - Strengths: نقاط قوت
   - Weaknesses: نقاط ضعف
   - Opportunities: فرصت‌ها
   - Threats: تهدیدها
   
2. Decision Matrix:
   - لیست گزینه‌ها
   - معیارهای تصمیم‌گیری
   - وزن‌دهی به معیارها
   - امتیازدهی و انتخاب
   
3. Cost-Benefit Analysis:
   - محاسبه هزینه‌ها
   - محاسبه منافع
   - مقایسه و تصمیم‌گیری
   
4. Risk Assessment:
   - شناسایی ریسک‌ها
   - ارزیابی احتمال و تاثیر
   - برنامه‌ریزی پاسخ
""",
        "keywords": "تصمیم‌گیری, SWOT, Matrix, ریسک",
        "priority": 9
    }
]

# ==========================================
# دانش‌نامه ایجنت محقق
# ==========================================
RESEARCH_KNOWLEDGE = [
    {
        "agent_type": "research",
        "category": "متدولوژی",
        "title": "روش‌های تحقیق علمی",
        "content": """
روش‌های تحقیق علمی:

1. تحقیق کمی (Quantitative):
   - داده‌های عددی
   - تحلیل آماری
   - آزمون فرضیه‌ها
   
2. تحقیق کیفی (Qualitative):
   - مصاحبه
   - مشاهده
   - تحلیل محتوا
   
3. تحقیق ترکیبی (Mixed Methods):
   - ترکیب کمی و کیفی
   - اعتبار بالاتر
   
4. مراحل تحقیق:
   - تعریف مسئله
   - مرور ادبیات
   - طراحی روش
   - جمع‌آوری داده
   - تحلیل
   - نتیجه‌گیری
""",
        "keywords": "تحقیق, متدولوژی, کمی, کیفی",
        "priority": 10
    }
]

# ==========================================
# دانش‌نامه ایجنت تحلیلگر داده
# ==========================================
DATA_ANALYST_KNOWLEDGE = [
    {
        "agent_type": "data_analyst",
        "category": "آمار",
        "title": "مفاهیم آماری پایه",
        "content": """
مفاهیم آماری پایه:

1. آمار توصیفی:
   - میانگین (Mean): مجموع / تعداد
   - میانه (Median): مقدار وسطی
   - مد (Mode): پرتکرارترین مقدار
   - انحراف معیار (Std): پراکندگی داده‌ها
   
2. آمار استنباطی:
   - آزمون t: مقایسه دو گروه
   - ANOVA: مقایسه چند گروه
   - Chi-square: آزمون استقلال
   - Regression: پیش‌بینی
   
3. مفاهیم مهم:
   - p-value: احتمال مشاهده نتایج تصادفی
   - Confidence Interval: بازه اطمینان
   - Power: توان آزمون
   - Effect Size: اندازه اثر
""",
        "keywords": "آمار, میانگین, میانه, انحراف معیار, p-value",
        "priority": 10
    },
    {
        "agent_type": "data_analyst",
        "category": "visualization",
        "title": "اصول مصورسازی داده",
        "content": """
اصول مصورسازی داده:

1. انتخاب نمودار مناسب:
   - Line: روند زمانی
   - Bar: مقایسه دسته‌ها
   - Scatter: رابطه دو متغیر
   - Histogram: توزیع داده
   - Pie: نسبت اجزا
   
2. اصول طراحی:
   - سادگی و وضوح
   - برچسب‌گذاری مناسب
   - انتخاب رنگ مناسب
   - عدم اغراق در مقیاس
   
3. ابزارها:
   - Matplotlib: پایه‌ای
   - Seaborn: آماری
   - Plotly: تعاملی
""",
        "keywords": "visualization, نمودار, مصورسازی, Matplotlib",
        "priority": 9
    }
]

# ==========================================
# دانش‌نامه ایجنت دستیار کدنویسی
# ==========================================
CODE_ASSISTANT_KNOWLEDGE = [
    {
        "agent_type": "code_assistant",
        "category": "Best Practices",
        "title": "اصول کدنویسی تمیز",
        "content": """
اصول کدنویسی تمیز (Clean Code):

1. نام‌گذاری:
   - نام‌های معنادار و توصیفی
   - avoid abbreviations
   - functions: verbs
   - variables: nouns
   
2. توابع:
   - کوچک و متمرکز (SRP)
   - حداکثر 20 خط
   - حداکثر 3-4 پارامتر
   - بدون عوارض جانبی
   
3. کلاس‌ها:
   - مسئولیت واحد
   - cohesion بالا
   - coupling پایین
   
4. خطاها:
   - استفاده از exceptions
   - پیام‌های خطای واضح
   - logging مناسب
""",
        "keywords": "Clean Code, نام‌گذاری, توابع, کلاس‌ها",
        "priority": 10
    },
    {
        "agent_type": "code_assistant",
        "category": "الگوهای طراحی",
        "title": "الگوهای طراحی رایج",
        "content": """
الگوهای طراحی رایج:

1. Creational Patterns:
   - Singleton: یک نمونه
   - Factory: ساخت اشیاء
   - Builder: ساخت گام‌به‌گام
   
2. Structural Patterns:
   - Adapter: تطبیق interface
   - Decorator: افزودن قابلیت
   - Facade: interface ساده
   
3. Behavioral Patterns:
   - Observer: اطلاع‌رسانی تغییرات
   - Strategy: الگوریتم‌های قابل تعویض
   - Command: encapsulate درخواست
   
4. اصول SOLID:
   - S: Single Responsibility
   - O: Open/Closed
   - L: Liskov Substitution
   - I: Interface Segregation
   - D: Dependency Inversion
""",
        "keywords": "Design Patterns, Singleton, Factory, SOLID",
        "priority": 9
    }
]

# ==========================================
# قوانین کسب‌وکار
# ==========================================
BUSINESS_RULES = [
    {
        "agent_type": "financial",
        "rule_name": "هشدار ریسک بالا",
        "condition": '{"keywords": ["ریسک بالا", "سرمایه‌گذاری پرخطر"]}',
        "action": "همیشه هشدار ریسک و توصیه مشورت با متخصص را ارائه دهید",
        "priority": 10
    },
    {
        "agent_type": "support",
        "rule_name": "ارجاع به پشتیبانی انسانی",
        "condition": '{"keywords": ["شکایت", "نارضایتی", "مشکل حل نشد"]}',
        "action": "در صورت نارضایتی کاربر، ارجاع به پشتیبانی انسانی را پیشنهاد دهید",
        "priority": 10
    },
    {
        "agent_type": "admin",
        "rule_name": "اولویت‌بندی تسک‌ها",
        "condition": '{"context": "task_management"}',
        "action": "تسک‌ها را بر اساس Urgency × Importance اولویت‌بندی کنید",
        "priority": 9
    },
    {
        "agent_type": "code_assistant",
        "rule_name": "امنیت کد",
        "condition": '{"keywords": ["password", "secret", "api_key"]}',
        "action": "همیشه توصیه به استفاده از environment variables و عدم hardcode کردن secrets را بدهید",
        "priority": 10
    }
]

# ==========================================
# قالب‌های پاسخ
# ==========================================
RESPONSE_TEMPLATES = [
    {
        "agent_type": "financial",
        "intent": "greeting",
        "template": """
سلام! من ایجنت تحلیلگر مالی Econojin هستم.

می‌توانم در موارد زیر به شما کمک کنم:
- تحلیل صورت‌های مالی
- محاسبه نسبت‌های مالی
- تحلیل تکنیکال و فاندامنتال
- مدیریت ریسک و پورتفوی

لطفاً سوال یا درخواست خود را مطرح کنید.
"""
    },
    {
        "agent_type": "financial",
        "intent": "error_no_data",
        "template": """
متأسفانه داده‌های کافی برای تحلیل در دسترس نیست.

لطفاً اطلاعات زیر را ارائه دهید:
- {required_data}

پس از دریافت داده‌ها، تحلیل کامل را ارائه خواهم داد.
"""
    },
    {
        "agent_type": "support",
        "intent": "greeting",
        "template": """
سلام! من ایجنت پشتیبانی Econojin هستم.

چگونه می‌توانم به شما کمک کنم؟
- راهنمایی در استفاده از پلتفرم
- حل مشکلات فنی
- پاسخ به سوالات عمومی

لطفاً مشکل یا سوال خود را شرح دهید.
"""
    },
    {
        "agent_type": "admin",
        "intent": "greeting",
        "template": """
سلام! من دستیار مدیریت پروژه شما هستم.

می‌توانم در موارد زیر کمک کنم:
- گزارش‌گیری از وضعیت پروژه
- اولویت‌بندی تسک‌ها
- تحلیل KPIها
- پشتیبانی تصمیم‌گیری

لطفاً درخواست خود را مطرح کنید.
"""
    },
    {
        "agent_type": "research",
        "intent": "greeting",
        "template": """
سلام! من ایجنت محقق Econojin هستم.

می‌توانم در موارد زیر کمک کنم:
- جستجو در وب و یافتن منابع
- خلاصه‌سازی مقالات
- استخراج نکات کلیدی
- تولید گزارش‌های تحقیقاتی

لطفاً موضوع تحقیق خود را مشخص کنید.
"""
    },
    {
        "agent_type": "data_analyst",
        "intent": "greeting",
        "template": """
سلام! من ایجنت تحلیلگر داده Econojin هستم.

می‌توانم در موارد زیر کمک کنم:
- تحلیل آماری داده‌ها
- تولید نمودار و visualization
- آزمون فرضیه‌ها
- شناسایی روندها

لطفاً داده‌ها یا سوال خود را ارائه دهید.
"""
    },
    {
        "agent_type": "code_assistant",
        "intent": "greeting",
        "template": """
سلام! من دستیار کدنویسی Econojin هستم.

می‌توانم در موارد زیر کمک کنم:
- تحلیل و بررسی کد
- شناسایی باگ‌ها
- محاسبه پیچیدگی الگوریتمی
- تولید تست واحد
- تبدیل بین زبان‌ها
- تولید مستندات

لطفاً کد یا درخواست خود را ارائه دهید.
"""
    },
    {
        "agent_type": "all",
        "intent": "fallback",
        "template": """
متأسفانه در حال حاضر نمی‌توانم پاسخ دقیقی ارائه دهم.

دلایل احتمالی:
- اطلاعات کافی در دانش‌نامه موجود نیست
- سوال نیاز به تحلیل پیچیده‌تری دارد
- سیستم در حالت offline است

پیشنهادات:
1. سوال خود را ساده‌تر مطرح کنید
2. اطلاعات بیشتری ارائه دهید
3. با پشتیبانی انسانی تماس بگیرید

با عرض پوزش برای inconvenience.
"""
    }
]


async def seed_knowledge_base(session: AsyncSession):
    """بارگذاری داده‌های اولیه به دانش‌نامه."""
    logger.info("🌱 Seeding knowledge base...")
    
    # بررسی وجود داده‌ها
    result = await session.execute(select(KnowledgeArticle).limit(1))
    if result.scalars().first():
        logger.info("✅ Knowledge base already seeded")
        return
    
    # بارگذاری مقالات
    all_articles = (
        FINANCIAL_KNOWLEDGE +
        SUPPORT_KNOWLEDGE +
        ADMIN_KNOWLEDGE +
        RESEARCH_KNOWLEDGE +
        DATA_ANALYST_KNOWLEDGE +
        CODE_ASSISTANT_KNOWLEDGE
    )
    
    for article_data in all_articles:
        article = KnowledgeArticle(**article_data)
        session.add(article)
    
    logger.info(f"✅ Added {len(all_articles)} knowledge articles")
    
    # بارگذاری قوانین
    for rule_data in BUSINESS_RULES:
        rule = BusinessRule(**rule_data)
        session.add(rule)
    
    logger.info(f"✅ Added {len(BUSINESS_RULES)} business rules")
    
    # بارگذاری قالب‌ها
    for template_data in RESPONSE_TEMPLATES:
        template = ResponseTemplate(**template_data)
        session.add(template)
    
    logger.info(f"✅ Added {len(RESPONSE_TEMPLATES)} response templates")
    
    await session.commit()
    logger.info("✅ Knowledge base seeded successfully")