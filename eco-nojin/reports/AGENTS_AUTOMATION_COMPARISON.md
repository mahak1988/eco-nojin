# 🤖 مقایسه‌ای ایجنت‌ها و اتوماسیون

**تاریخ:** ۱۴۰۵/۰۴/۳۰  
**مقایسه با:** FastAPI Best Practices AGENTS.md

---

## 📊 خلاصه مقایسه

| ویژگی | اکو نوژین | FastAPI Best Practices | وضعیت |
|-------|-----------|-----------------------|-------|
| الگوی معماری | ✅ Model → Schema → Service → Router | ✅ Domain-based structure | ✅ هماهنگ |
| Async/await | ✅ استفاده در routes | ✅ الزامی | ✅ برقرار |
| Dependencies | ✅ FastAPI Depends | ✅ Annotated + Depends | ⚠️ بهبود نیاز دارد |
| Validation | ✅ Pydantic v2 | ✅ Field validators | ✅ برقرار |
| JWT Auth | ✅ PyJWT | ✅ PyJWT | ✅ برقرار |
| DB Async | ✅ AsyncSession | ✅ AsyncSession | ✅ برقرار |
| Testing | ⚠️ pytest اولیه | ✅ httpx + ASGITransport | ⚠️ گسترش نیاز دارد |
| CI/CD | ✅ GitHub Actions | ⚠️ متنوع | ⚠️ در حال توسعه |

---

## 🔧 ایجنت‌های اکو نوژین

### استانداردهای فعلی:
- Conversation / Message مدل‌ها
- Agent type: financial, support
- Tool calls پشتیبانی
- Metadata tracking (tokens, latency)

### مقایسه با Best Practices:

| الزام | اکو نوژین | Best Practices | پیشنهاد |
|------|-----------|---------------|---------|
| Dependencies | از `Depends` استفاده می‌کند | `Annotated[T, Depends(...)]` پیشنهاد می‌شود | به‌روزرسانی ضروری |
| Testing | pytest اولیه | `httpx.AsyncClient` + `ASGITransport` | جایگزینی پیشنهاد می‌شود |
| Linting | ruff وجود ندارد | ruff check --fix | اضافه کردن |

---

## 📈 برنامه اتوماسیون (Week 14)

### ۱. به‌روزرسانی Dependencies
```python
# از:
async def get_user(user_id: int = Depends(get_user_dep)):
    ...

# به:
from typing import Annotated
UserDep = Annotated[User, Depends(get_user_dep)]
```

### ۲. بهبود Testing
```python
# اضافه کردن به tests/conftest.py
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

### ۳. Linting Automation
```yaml
# .github/workflows/lint.yml
- run: pip install ruff
- run: ruff check --fix apps
- run: ruff format apps
```

### ۴. Pre-commit Hook
```yaml
# .pre-commit-config.yaml گسترش
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks:
      - id: ruff
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.11.0
    hooks:
      - id: mypy
```

---

## ✅ چک‌لیست پیاده‌سازی

- [ ] به‌روزرسانی dependencies به Annotated form
- [ ] جایگزینی test client با httpx + ASGITransport
- [ ] اضافه کردن ruff linting
- [ ] بهبود pytest fixtures
- [ ] اضافه کردن type hints کامل
- [ ] استفاده از pydantic-settings در domains

---

## 📝 نتیجه‌گیری

اکو نوژین در **۷۰%** موارد با Best Practices سازگار است.
نیاز به **۳ تغییر کلیدی** دارد:
1. Dependencies به‌روزرسانی شود
2. Testing framework گسترش یابد
3. Linting اضافه گردد