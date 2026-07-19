# 📈 برنامه بهبودهای بعدی (Week 13+)

**هدف:** رفع نقطه ضعف‌ها و ارتقای کیفیت

---

## 🎯 کارهای باقی‌مانده

### ۱. به‌روزرسانی Docker Images

**مشکل فعلی:**
- Dockerfile.api از Python 3.12 استفاده می‌کند (خوب است)
- Frontend از Node 20 استفاده می‌کند (خوب است)
- اما Multi-stage build ناقص است

**راه‌حل:**
```dockerfile
# ساختار پیشنهادی (از docker/Dockerfile.api)
# Stage 1: Builder
FROM python:3.12-slim AS builder
# Stage 2: Production  
FROM python:3.12-slim AS production
# Stage 3: Frontend
FROM node:20-alpine AS frontend-builder
```

### ۲. افزایش Test Coverage (۷۰% → ۹۰%)

**شاخص‌های فعلی:**
- Backend: ۷۰% درختاند
- Frontend: ۴۰% درختاند

**برنامه:**
| ماژول | هدف | کار |
|-------|-----|-----|
| API Routes | ۱۰۰% | تست endpointهای REST |
| Services | ۱۰۰% | تست لایه کسب و کار |
| Repositories | ۱۰۰% | تست لایه دسترسی داده |
| Simulation | ۸۰% | تست مدل‌های AquaCrop و SWAT+ |
| Frontend | ۷۰% | تست hooks و components |

### ۳. مستندسازی API با Swagger

**FastAPI از Swagger UI بومی پشتیبانی می‌کند.**

راه‌اندازی:
- `/docs` - Swagger UI خودکار
- `/openapi.json` - اسکما OpenAPI
- اضافه کردن description به endpointها

### ۴. گسترش CI/CD

**فعلی:**
- تست ساده بک‌اند
- بیلد ساده فرانت‌اند
- داکر push

**پیشنهاد:**
```yaml
# .github/workflows/بهبود.yml
jobs:
  test-backend:
    strategy:
      matrix:
        python-version: [3.11, 3.12]
    steps:
      - run: pytest --cov=apps --cov-report=xml
      - uses: codecov/codecov-action@v3
      
  test-frontend:
    steps:
      - run: pnpm test --coverage
      
  security-audit:
    steps:
      - run: pip-audit
      - run: pnpm audit
      
  deploy-preview:
    # برای PRهای Vercel
    
  deploy-production:
    # برای push به main
    needs: [test-backend, test-frontend, security-audit]
```

---

## 📋 برنامه زمان‌بندی

| هفته | کار |
|------|-----|
| هفته ۱۳ | Docker multi-stage + Security scan |
| هفته ۱۴ | Test coverage افزایش |
| هفته ۱۵ | API docs + CI/CD گسترش |
| هفته ۱۶ | Production hardening |

---

## ✅ چک‌لیست پیاده‌سازی

- [x] به‌روزرسانی docker/Dockerfile.api (multi-stage)
- [x] افزودن docker/Dockerfile.frontend (multi-stage)
- [x] نوشتن تست‌های pytest برای education, community, games
- [x] تست‌های simulation framework
- [x] گسترش GitHub Actions با coverage و security
- [x] تنظیم codecov action در CI/CD

---

## 📝 تکمیل‌شده (Week 13)

| فایل | توضیح |
|-----|-------|
| `docker/Dockerfile.api` | Multi-stage build با builder و production |
| `docker/Dockerfile.frontend` | Multi-stage build با nginx |
| `infra/nginx/default.conf` | پیکربندی nginx برای SPA |
| `docker-compose.apps.yml` | سرویس frontend production |
| `apps/api/tests/test_education.py` | تست‌های CRUD |
| `apps/api/tests/test_community.py` | تست‌های CRUD |
| `apps/api/tests/test_games.py` | تست‌های CRUD |
| `apps/api/tests/test_simulation.py` | تست‌های framework |
| `.github/workflows/econojin-apps-ci.yml` | CI/CD گسترش‌یافته |
| `ruff.toml` | پیکربِرهی Linting |
| `.pre-commit-config.yaml` | به‌روزرسانی با ruff |

---

## 🤖 برنامه توسعه ایجنت‌ها و اتوماسیون (Week 15)

### ۱. به‌روزرسانی Dependencies Pattern

**از الگوی فعلی:**
```python
async def get_user(user_id: int = Depends(get_user_dep)):
    ...
```

**به الگوی Best Practices:**
```python
from typing import Annotated
UserDep = Annotated[User, Depends(get_user_dep)]
```

### ۲. گسترش ایجنت‌ها

| ایجنت | هدف | وضعیت |
|-------|-----|-------|
| FinancialAgent | مشاور مالی | ✅ FinancialAnalystAgent پیاده‌سازی شده |
| SupportAgent | پشتیبانی فنی | ✅ SupportAgent پیاده‌سازی شده |
| AgronomyAgent | مشاور کشاورزی | ✅ پیاده‌سازی شده (Week 16) |
| ClimateAgent | تحلیل آب و هوا | ✅ پیاده‌سازی شده (Week 16) |

**ایجنت‌های فعلی:**
- FinancialAnalystAgent
- SupportAgent
- AdminAssistantAgent
- ResearchAgent
- DataAnalystAgent
- CodeAssistantAgent
- AgronomyAgent (جدید)
- ClimateAgent (جدید)

### ۳. Tool Calling Automation

```python
# apps/ai_agents/tools/registry.py
class AgentToolRegistry:
    _tools: dict[str, Callable] = {}
    
    @classmethod
    def register(cls, name: str):
        def decorator(fn):
            cls._tools[name] = fn
            return fn
        return decorator
```

### ۴. Background Tasks / Celery

| کار | وضعیت |
|-----|-------|
| Celery integration | ✅ تکمیل (apps/shared_ai/celery_app.py) |
| Redis for queuing | ✅ تکمیل (در docker-compose.yml) |
| Task monitoring | ✅ تکمیل (Week 16) |

---

## 📝 تکمیل‌شده (Week 15)

| فایل | توضیح |
|-----|-------|
| `apps/shared_ai/celery_app.py` | Celery tasks برای شبیه‌سازی |
| `apps/ai_agents/tools/registry.py` | ابزارهای ایجنت‌ها |

---

## 📝 تکمیل‌شده (Week 16)

| فایل | توضیح |
|-----|-------|
| `apps/ai_agents/agents/agronomy.py` | AgronomyAgent - مشاور کشاورزی |
| `apps/ai_agents/agents/climate.py` | ClimateAgent - تحلیل گر آب و هوا |
| `apps/shared_ai/celery_app.py` | بهبودهای TaskMonitor با signal handlers |

### ۵. API Documentation

- `/docs` - FastAPI Swagger UI (خودکار)
- `/openapi.json` - اسکما (خودکار)
- اضافه کردن description به endpointها

### ۶. CI/CD گسترش

| افزودن | وضعیت |
|-------|-------|
| matrix testing (Python 3.11/3.12) | ✅ تکمیل |
| security audit (pip-audit) | ✅ تکمیل |
| codecov integration | ✅ تکمیل |
| vercel preview deploy | ✅ تکمیل |
| dependency override testing | ✅ تکمیل |

---

## ✅ تمامی کارها تکمیل شده

تمام ایتم‌های برنامه به‌روزرسانی تا هفته ۱۶ با موفقیت اجرا شد: