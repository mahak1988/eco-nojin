# shared_ai | ماژول هوش مصنوعی اشتراکی Econojin

> **نکته:** این ماژول **لایه هوش مصنوعی اشتراکی** پلتفرم Econojin است.
> شامل LLM Factory (اتصال به ۶ provider مختلف)، Celery app برای پردازش ناهمزمان،
> و مدل‌های داده‌ای مشترک برای تمام ماژول‌های AI.

## مسئولیت‌ها

این ماژول سه وظیفه‌ی اصلی دارد:

1. **LLM Factory** (`ai/llm_factory.py`)
   - کارخانه‌ی چندگانه برای اتصال به ۶ provider مختلف LLM
   - پشتیبانی از Groq, xAI/Grok, Google Gemini, OpenRouter, Ollama, Fake
   - سیستم Fallback خودکار در صورت عدم دسترسی به provider
   - لیست کردن providerهای موجود و وضعیت آن‌ها

2. **پردازش ناهمزمان** (`celery_app.py`)
   - Celery app برای jobهای سنگین AI
   - پردازش پس‌زمینه درخواست‌های طولانی

3. **مدل‌های اشتراکی AI** (`models.py`, `schemas.py`, `service.py`)
   - مدل `SharedAi` برای ذخیره‌سازی داده‌های مشترک AI
   - CRUD کامل با صفحه‌بندی

## ساختار

```
shared_ai/
├── __init__.py                # Module init
├── router.py                  # ★ FastAPI router (HTTP endpoints)
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic
├── repository.py              # Database access (SQLAlchemy)
├── models.py                  # ★ ORM model SharedAi
├── dependencies.py            # FastAPI dependencies
├── celery_app.py              # ★ Celery app برای jobهای ناهمزمان
├── ai/                        # ★ هسته AI
│   └── llm_factory.py         #   ★ LLM Factory (6 provider)
└── tests/                     # Pytest tests
    ├── test_shared_ai.py
    └── ...
```

## LLM Factory (`ai/llm_factory.py`)

### Providerهای پشتیبانی‌شده

| Provider | کلاس | مدل پیش‌فرض | API Key | سرعت | هزینه |
|----------|------|-------------|---------|------|-------|
| **Groq** 🚀 | `ChatGroq` | `llama-3.3-70b-versatile` | `GROQ_API_KEY` | ⚡ فوق‌سریع | رایگان |
| **xAI/Grok** 🤖 | `ChatOpenAI` | `grok-2` | `XAI_API_KEY` | 🚀 سریع | پولی |
| **Gemini** 🧠 | `ChatGoogleGenerativeAI` | `gemini-2.5-flash` | `GOOGLE_API_KEY` | 🚀 سریع | رایگان (محدود) |
| **OpenRouter** 🌐 | `ChatOpenAI` | `meta-llama/llama-4-maverick:free` | `OPENROUTER_API_KEY` | ⚡ فوق‌سریع | رایگان + پولی |
| **Ollama** 💻 | `ChatOllama` | `llama3.1:8b` | — (محلی) | 🐢 متوسط | رایگان |
| **Fake** 🧪 | `FakeMessagesListChatModel` | `fake` | — | ⚡ آنی | رایگان |

### نحوه استفاده

```python
from apps.shared_ai.ai.llm_factory import LLMFactory

# ایجاد با provider پیش‌فرض (از .env)
llm = LLMFactory.create()

# ایجاد با provider مشخص
llm = LLMFactory.create(provider="groq")
llm = LLMFactory.create(provider="gemini", model="gemini-2.5-flash")

# ایجاد با تنظیمات سفارشی
llm = LLMFactory.create(
    provider="openrouter",
    model="meta-llama/llama-4-maverick:free",
    temperature=0.3
)
```

### Fallback خودکار

اگر provider اصلی در دسترس نباشد (API Key معتبر وجود نداشته باشد)،
سیستم به طور خودکار به **Fake LLM** برگشت می‌خورد:

```python
# اگر GROQ_API_KEY در .env تنظیم نشده باشد:
llm = LLMFactory.create(provider="groq")
# ⚠️ Fallback به Fake LLM با پیام خطا در لاگ
```

### لیست providerها

```python
from apps.shared_ai.ai.llm_factory import LLMFactory

providers = LLMFactory.list_providers()
# خروجی:
# {
#   "groq": {"name": "Groq", "status": "available", ...},
#   "xai": {"name": "xAI (Grok)", "status": "not_configured", ...},
#   ...
# }
```

## Celery App (`celery_app.py`)

برای پردازش ناهمزمان jobهای سنگین AI:

```python
from apps.shared_ai.celery_app import celery_app

@celery_app.task
def process_heavy_ai_task(data):
    # پردازش سنگین در پس‌زمینه
    result = llm.invoke(data)
    return result
```

## مدل داده (`models.py`)

```python
class SharedAi(Base):
    """مدل اشتراکی AI."""
    
    __tablename__ = "shared_ai"
    
    id: int                    # شناسه یکتا
    name: str                  # نام (index)
    description: str | None    # توضیحات
    is_active: bool            # وضعیت فعال (پیش‌فرض: True)
    created_at: datetime       # تاریخ ایجاد
    updated_at: datetime       # تاریخ بروزرسانی
```

## Endpointهای API

| Method | Path | توضیح |
|--------|------|--------|
| GET | `/shared_ai` | لیست با صفحه‌بندی |
| GET | `/shared_ai/{id}` | دریافت بر اساس ID |
| POST | `/shared_ai` | ایجاد جدید |
| PATCH | `/shared_ai/{id}` | بروزرسانی |
| DELETE | `/shared_ai/{id}` | حذف |

## متغیرهای محیطی (`.env`)

```ini
# LLM Provider
LLM_PROVIDER=groq                   # groq | xai | gemini | openrouter | ollama | fake
LLM_MODEL=                          # خالی = مدل پیش‌فرض Provider

# API Keys
GROQ_API_KEY=gsk_...                # https://console.groq.com
XAI_API_KEY=xai-...                 # https://console.x.ai
GOOGLE_API_KEY=AIza...              # https://aistudio.google.com
OPENROUTER_API_KEY=sk-or-...        # https://openrouter.ai
OLLAMA_BASE_URL=http://localhost:11434  # برای Ollama محلی
```

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌ها
pytest apps/shared_ai/tests/ -v

# اجرای سرور توسعه
python apps/main.py
```

## تغییرات مهم

- **فاز ۲:** بازنویسی کامل LLM Factory با پشتیبانی از ۶ provider
- **فاز ۲:** افزودن Celery app برای پردازش ناهمزمان
- **فاز ۲:** سیستم Fallback خودکار به Fake LLM
