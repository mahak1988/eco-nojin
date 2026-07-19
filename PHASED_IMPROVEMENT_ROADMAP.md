# نقشه‌راه ارتقاء چندفازی پروژه Econojin

---

## فاز ۰: رفع امور بحرانی امنیتی (۲۴ ساعت)

### فاز ۰.۱: حذف کلید دیکدود از کد
- **فایل مورد تغییر**: `apps/users/service.py`
- **وضعیت**: ✅ انجام شد - از `apps/shared_core/security.py` استفاده می‌شود
- **دستور**: `grep -r "SECRET_KEY.*=.*your-secret" apps/`

### فاز ۰.۲: یکپارسازی توابع امنیتی
- **فایل‌های تأثیر**: `apps/users/service.py`، `apps/shared_core/security.py`
- **کار انجام‌شده**: توابع `verify_password`، `get_password_hash`، `create_access_token` از shared_core فراخوانی می‌شوند

### فاز ۰.۳: افزودن Rate Limiting
- **فایل جدید**: `apps/shared_core/middleware/rate_limit.py`
- **وضعیت**: ✅ ایجاد شد
- **ویژگی‌ها**: 
  - ۵ تلاش ناموفق در ۶۰ ثانیه
  - فقط برای endpointهای auth فعال
  - ورژن production-friendly (Redis-ready)

---

## فاز ۱: بهبود معماری و کیفیت کد (۲ هفته)

### فاز ۱.۱: ایجاد auth/config.py
```python
# برنامه‌ریزی شد - نیاز به پیاده‌سازی
# apps/users/config.py
# تنظیمات JWT ماژولار
```

### فاز ۱.۲: ایجاد auth/exceptions.py
```python
# برنامه‌ریزی شد - نیاز به پیاده‌سازی
# کلاس‌های خطای استاندارد
# InvalidCredentials, TokenExpired, AccountLocked
```

### فاز ۱.۳: رفع God Files شناسایی‌شده
| فایل | خطوط | وضعیت |
|------|-----|------|
| `apps/web/generate_languages.py` | 1071 | ⚠️ نیاز به refactor |
| `apps/web/generate_batch2.py` | 548 | ⚠️ نیاز به refactor |

---

## فاز ۲: بهبود زیرساخت و CI/CD (۱ ماه)

### فاز ۲.۱: Migrationهای Alembic
```python
# alembic/versions/20240501_create_users_table.py
# برنامه‌ریزی شد - نیاز به ایجاد migrationهای جداول دیتابس
```

### فاز ۲.۲: بهبود Dockerfile
```dockerfile
# multi-stage build
# سحکت کرده شد - نیاز به پیاده‌سازی
FROM python:3.12-slim AS builder
# ...
USER 1000  # غیرفعال کردن root
```

### فاز ۲.۳: افزودن pre-commit hooks
```yaml
# .github/workflows/07-pre-commit.yml
# برنامه‌ریزی شد
- ruff check --fix
- ruff format
- bandit -r apps/
```

---

## فاز ۳: تست و کیفیت نهایی (۲ ماه)

### فاز ۳.۱: افزایش پوشش تست
- **هدف**: ۷۰٪ → ۹۰٪
- **راه‌حل**: تست‌های integration برای auth endpoints

### فاز ۳.۲: Audit Logging
```python
# apps/shared_core/middleware/audit_log.py
# برنامه‌ریزی شد
# Log تمام درخواست‌های auth
```

### فاز ۳.۳: Security Headers بهبود
- CSP
- HSTS  
- X-Frame-Options

---

## جدول زمان‌بندی پیشنهادی

| فاز | فعالیت | زمان تخمین | اولویت |
|-----|---------|------------|--------|
| ۰ | رفع امنیتی | ۲۴ ساعت | 🔴 بحرانی |
| ۱ | refactor کد | ۲ هفته | 🔴 بحرانی |
| ۲ | CI/CD + Docker | ۱ ماه | 🟠 متوسط |
| ۳ | تست + Audit | ۲ ماه | 🟠 متوسط |

---

## CLI Commands برای پیگیری

```bash
# بررسی God Files
python scripts/check_god_files.py

# بررسی امنیت
bandit -r apps/ -ll --skip B101
pip-audit -r requirements.txt

# تست
pytest apps/ -v --cov=apps