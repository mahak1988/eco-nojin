# فاز ۱ — تثبیت امنیت و Hardening (پیاده‌سازی)

**شاخه:** `fix/tech-debt-phase1`  
**تاریخ:** ۱۴۰۵/۰۵/۱۵  

## تحویل‌پذیرها (مطابق IMPROVEMENT_REPORT)

| # | مورد | وضعیت | فایل‌ها |
|---|------|--------|---------|
| 1 | عدم وجود hardcoded secret | ✅ تأیید | فقط در `config.py` / `.env*` |
| 2 | ثبت RateLimit + Audit + SpiderGuard شرطی | ✅ | `apps/shared_core/security_init.py` |
| 3 | اسکریپت gen_jwt_keys + مستند | ✅ از قبل موجود | `scripts/gen_jwt_keys.sh` |
| 4 | REQUIRE_AUTH_FOR_WRITES در docker/staging | ✅ | `.env.docker` |
| 5 | model_registry کامل (پیش‌نیاز Alembic) | ✅ | `apps/shared_core/database/model_registry.py` |

## تغییرات کلیدی

### 1. `model_registry.py`
- لیست ماژول‌ها از ~۱۳ مورد به ۳۰+ مورد گسترش یافت:
  - users, rbac, shared_core
  - farms, crops, planting, inventory, monitoring, economics
  - simulation (models, models_runs, models_swat, runs, scenario)
  - ai_agents, shared_ai (+rag), shared_knowledge, shared_sim
  - api.models.* (education, accounting, community, games, ecocoin, library, agriculture_school, api)

### 2. `security_init.py`
- `RateLimitMiddleware` اضافه شد (اگر `ENABLE_RATE_LIMIT=true`)
- `AuditLogMiddleware` اضافه شد (اگر `ENABLE_AUDIT_LOG=true`)
- `SpiderGuardMiddleware` فقط وقتی `ENABLE_SPIDERGUARD=true` یا `ENVIRONMENT=production`

### 3. تنظیمات
- `.env.example` و `.env.docker` به‌روز با کامنت‌های production و toggleهای امنیتی
- `PHASE0_TODO.md` همگام‌سازی شد (T-03, T-04, T-05 و بخشی از T-01)

## معیار پذیرش (محلی)
- `git grep -n SECRET_KEY apps/` → فقط settings/config
- با `ENABLE_RATE_LIMIT=true`، بیش از ۱۰ تلاش ناموفق login → 429
- write بدون token وقتی `REQUIRE_AUTH_FOR_WRITES=true` → 401

## کارهای باقی‌مانده (فاز ۲+)
- migration یکپارچه Alembic برای مدل‌های جدید
- جایگزینی کامل `create_all` در production
- bandit / pip-audit در CI (اگر هنوز نیست)
- فعال‌سازی RS256 در production با کلیدهای واقعی

---
*این سند بخشی از برنامه ۱۰ فازی IMPROVEMENT_REPORT است.*
