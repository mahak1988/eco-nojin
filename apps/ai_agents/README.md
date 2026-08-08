# ai_agents | AI Agents Module for Econojin

> **Note:** This module provides **6 specialized AI agents** for the Econojin platform.
> Each agent has unique capabilities and supports multiple LLM providers (Groq, xAI, Gemini, OpenRouter, Ollama).

## Responsibilities

This module has three main responsibilities:

1. **6 Specialized Agents** (`agents/`)
   - **Financial** — Financial data analysis, Monte Carlo simulation, portfolio optimization
   - **Support** — Answering questions and user guidance
   - **Admin** — Reporting, KPI analysis, task prioritization
   - **Research** — Web search, article summarization, research report generation
   - **Data Analyst** — Statistics, correlation, hypothesis testing, ML
   - **Code Assistant** — AST code analysis, bug detection, test generation

2. **Chat Streaming** (`router.py`)
   - SSE streaming support for real-time responses
   - Non-streaming support for simple requests

3. **Conversation Management** (`service.py`, `repository.py`)
   - Create and maintain conversations
   - Store and retrieve message history

## ساختار

```
ai_agents/
├── __init__.py                # Module init
├── router.py                  # ★ روتر ایجنت‌ها (HTTP endpoints)
├── schemas.py                 # Pydantic validation models
├── service.py                 # Business logic (AI processing)
├── repository.py              # Database access (Conversations/Messages)
├── models.py                  # ORM models
├── dependencies.py            # FastAPI dependencies
├── agents/                    # ★ پیاده‌سازی ایجنت‌ها
│   ├── admin.py               #   ایجنت ادمین
│   ├── agronomy.py            #   ایجنت کشاورزی
│   ├── climate.py             #   ایجنت اقلیم
│   ├── code_assistant.py      #   ایجنت کدنویسی
│   ├── data_analyst.py        #   ایجنت تحلیل داده
│   ├── financial.py           #   ایجنت مالی
│   ├── research.py            #   ایجنت تحقیق
│   └── support.py             #   ایجنت پشتیبانی
├── tools/                     # ابزارهای ایجنت‌ها
└── tests/                     # Pytest tests
    ├── test_admin_agent.py
    ├── test_ai_agents.py
    ├── test_code_assistant_agent.py
    ├── test_data_analyst_agent.py
    └── test_research_agent.py
```

## ۶ ایجنت تخصصی

### ۱. 🤖 تحلیلگر مالی (Financial Agent)

| ویژگی | توضیح |
|-------|--------|
| **نوع** | `financial` |
| **قابلیت‌ها** | اجرای SQL, تحلیل روندها, محاسبات آماری (Numba JIT), شبیه‌سازی مونت کارلو, بهینه‌سازی پورتفوی |
| **موارد استفاده** | تحلیل صورت‌های مالی, پیش‌بینی بازار, مدیریت ریسک |

### ۲. 💁 پشتیبانی (Support Agent)

| ویژگی | توضیح |
|-------|--------|
| **نوع** | `support` |
| **قابلیت‌ها** | پاسخ به سوالات عمومی, راهنمایی پلتفرم, حل مشکلات فنی |
| **موارد استفاده** | چت پشتیبانی, FAQ هوشمند, راهنمای کاربری |

### ۳. 👨‍💼 کمک ادمین (Admin Agent)

| ویژگی | توضیح |
|-------|--------|
| **نوع** | `admin` |
| **قابلیت‌ها** | گزارش‌گیری, تحلیل KPI, اولویت‌بندی, تصمیم‌گیری استراتژیک |
| **موارد استفاده** | داشبورد مدیریت, گزارش‌های عملکرد, تحلیل پروژه |

### ۴. 🔬 محقق (Research Agent)

| ویژگی | توضیح |
|-------|--------|
| **نوع** | `research` |
| **قابلیت‌ها** | جستجوی وب, خلاصه‌سازی متون, استخراج نکات کلیدی, تولید گزارش |
| **موارد استفاده** | تحقیق بازار, مرور مقالات, تحلیل رقبا |

### ۵. 📊 تحلیلگر داده (Data Analyst Agent)

| ویژگی | توضیح |
|-------|--------|
| **نوع** | `data_analyst` |
| **قابلیت‌ها** | آمار سریع (Numba JIT), همبستگی, آزمون فرضیه (t-test, ANOVA), معادلات دیفرانسیل (SciPy), عملیات ماتریسی, ML, تولید نمودار |
| **موارد استفاده** | تحلیل داده‌های کشاورزی, پیش‌بینی روندها, مدل‌سازی آماری |

### ۶. 💻 دستیار کدنویسی (Code Assistant Agent)

| ویژگی | توضیح |
|-------|--------|
| **نوع** | `code_assistant` |
| **قابلیت‌ها** | تحلیل AST, شناسایی باگ, محاسبه پیچیدگی, تولید تست, تبدیل زبان, تولید مستندات |
| **موارد استفاده** | بازبینی کد, رفع باگ, مستندسازی, یادگیری برنامه‌نویسی |

## Endpointهای API

### Chat

| Method | Path | توضیح |
|--------|------|--------|
| POST | `/api/v1/ai-agents/chat` | ارسال پیام به ایجنت و دریافت پاسخ (non-streaming) |
| POST | `/api/v1/ai-agents/chat/stream` | ارسال پیام و دریافت پاسخ به صورت streaming (SSE) |

**Chat Request:**
```json
{
    "message": "تحلیل مالی شرکت من را انجام بده",
    "agent_type": "financial",
    "conversation_id": null
}
```

**Chat Response (Non-Streaming):**
```json
{
    "conversation_id": 123,
    "assistant_message": "بر اساس تحلیل انجام شده...",
    "messages": [
        {"role": "user", "content": "..."},
        {"role": "assistant", "content": "..."}
    ],
    "used_fallback": false
}
```

**Streaming Response (SSE):**
```
data: {"conversation_id": 123}
data: {"content": "بر اساس "}
data: {"content": "تحلیل انجام شده..."}
data: {"done": true, "used_fallback": false}
```

### مکالمات

| Method | Path | توضیح |
|--------|------|--------|
| GET | `/api/v1/ai-agents/conversations` | لیست مکالمات کاربر |
| GET | `/api/v1/ai-agents/conversations/{id}` | جزئیات مکالمه با پیام‌ها |
| POST | `/api/v1/ai-agents/conversations` | ایجاد مکالمه جدید |

### اطلاعات ایجنت‌ها و LLM

| Method | Path | توضیح |
|--------|------|--------|
| GET | `/api/v1/ai-agents/types` | لیست انواع ایجنت‌های موجود با قابلیت‌ها |
| GET | `/api/v1/ai-agents/llm/providers` | لیست ارائه‌دهندگان LLM |
| GET | `/api/v1/ai-agents/llm/current` | اطلاعات LLM فعلی |

**Agent Types Response:**
```json
{
    "agents": [
        {
            "type": "financial",
            "name": "تحلیلگر مالی",
            "description": "تحلیل داده‌های مالی و ارائه گزارش‌های استراتژیک",
            "capabilities": ["اجرای SQL", "تحلیل روندها", "شبیه‌سازی مونت کارلو"]
        }
    ]
}
```

## LLM Factory

ایجنت‌ها از `LLMFactory` در `apps/shared_ai/ai/llm_factory.py` برای اتصال به LLM استفاده می‌کنند:

| Provider | مدل پیش‌فرض | API Key مورد نیاز |
|----------|-------------|-------------------|
| **Groq** 🚀 | `llama-3.3-70b-versatile` | `GROQ_API_KEY` |
| **xAI/Grok** 🤖 | `grok-2` | `XAI_API_KEY` |
| **Gemini** 🧠 | `gemini-2.5-flash` | `GOOGLE_API_KEY` |
| **OpenRouter** 🌐 | `meta-llama/llama-4-maverick:free` | `OPENROUTER_API_KEY` |
| **Ollama** 💻 | `llama3.1:8b` | — (محلی) |
| **Fake** 🧪 | `fake` | — (تست) |

### پشتیبان خودکار (Fallback)
اگر provider اصلی در دسترس نباشد، سیستم به طور خودکار به **Fake LLM** برگشت می‌خورد:
```python
LLMFactory.create(provider="groq")  # اگر GROQ_API_KEY نباشد → Fake LLM
```

## مشخصات فنی

### مزایای Streaming
- ✅ پاسخ‌های real-time مانند ChatGPT
- ✅ کاهش تأخیر درک شده توسط کاربر
- ✅ پشتیبانی از nginx با هدر `X-Accel-Buffering: no`
- ✅ قابلیت نمایش تدریجی پاسخ

### مزایای Non-Streaming
- ✅ سادگی در پیاده‌سازی سمت کلاینت
- ✅ مناسب برای درخواست‌های کوتاه
- ✅ سازگاری با REST APIهای سنتی

## توسعه و تست

```bash
# از ریشه‌ی پروژه
cd d:\econojin.com

# اجرای تست‌های ایجنت‌ها
pytest apps/ai_agents/tests/ -v

# تست یک ایجنت خاص
pytest apps/ai_agents/tests/test_financial_agent.py -v
pytest apps/ai_agents/tests/test_code_assistant_agent.py -v

# اجرای سرور توسعه
python apps/main.py
```

## مثال‌های کاربردی

### Chat با Streaming (JavaScript)
```javascript
const eventSource = new EventSource('/api/v1/ai-agents/chat/stream');

// ارسال پیام
fetch('/api/v1/ai-agents/chat/stream', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer TOKEN'
    },
    body: JSON.stringify({
        message: 'تحلیل مالی شرکت من را انجام بده',
        agent_type: 'financial'
    })
});

// دریافت پاسخ streaming
eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    if (data.content) {
        console.log('Received chunk:', data.content);
    }
    if (data.done) {
        eventSource.close();
    }
};
```

### Chat با Python
```python
import httpx
import json

response = httpx.post(
    "http://localhost:8000/api/v1/ai-agents/chat",
    json={"message": "روندهای بازار را تحلیل کن", "agent_type": "financial"},
    headers={"Authorization": f"Bearer {token}"},
)

result = response.json()
print(f"پاسخ: {result['assistant_message']}")
print(f"مکالمه: {result['conversation_id']}")
```

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

## تغییرات مهم

- **فاز ۲:** افزودن ۶ ایجنت تخصصی با قابلیت‌های منحصربه‌فرد
- **فاز ۲:** پشتیبانی از Streaming (SSE) برای پاسخ‌های real-time
- **فاز ۲:** یکپارچه‌سازی با LLM Factory برای پشتیبانی از ۵+ provider
- **فاز ۲:** سیستم Fallback خودکار به Fake LLM در صورت عدم دسترسی به provider
- **فاز ۲:** مدیریت مکالمات (ایجاد، ذخیره، بازیابی تاریخچه)
