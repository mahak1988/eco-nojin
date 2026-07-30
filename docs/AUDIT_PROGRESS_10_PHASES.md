# ممیزی پیشرفت + بدهی فنی + برنامه ۱۰ فاز — Econojin

**تاریخ:** 2026-07-30  
**مخزن:** mahak1988/eco-nojin  
**محیط هدف توسعه:** Zero-Install (venv + SQLite + pnpm) — بدون Docker اجباری  
**کلیدهای بیرونی:** پس از فاز ۱۰ توسط مالک پروژه

---

## ۱. پیشرفت واقعی (آنچه اثبات شده)

### زیرساخت و امنیت
| مورد | شواهد |
|------|--------|
| API boot local | uvicorn + health `database: ok` |
| JWT متمرکز | `shared_core.security` + Settings |
| Auth register/login/me | 200 با Bearer (Invoke-RestMethod) |
| HttpOnly cookie path | در auth_router |
| Rate limit / audit / SpiderGuard | middleware موجود؛ prod فعال‌تر |
| Zero-Docker docs | `ZERO_INSTALL_LOCAL.md`, `run_local.ps1` |

### فاز کشاورزی (هسته)
| مورد | شواهد |
|------|--------|
| farms list | 200 + meta + داده نمونه |
| crops catalog | 200 + چند صفحه داده |
| modules | farms, crops, water, planting, inventory, weather, notifications, dashboard |

### پایش / علم / ماهواره
| مورد | شواهد |
|------|--------|
| routers loaded ~46 | health debug |
| science / satellite / monitoring در کد | apps/* |
| synthetic EO fallback | بدون کلید |
| scenario SyntaxError | رفع در commit اخیر |
| data satellite stub | رفع import |

### فرانت
| مورد | شواهد |
|------|--------|
| Vite + pnpm | localhost:5173 |
| صفحات زیاد | structure موجود |
| اتصال API | ناهمگون؛ برخی mock |

---

## ۲. نواقص و شکاف‌ها (صادقانه)

1. **Alembic multiple heads** — `upgrade head` روی SQLite خطا؛ اتکا به `create_all` در local  
2. **ai_agents** بدون `langchain_core` — router fail (اختیاری)  
3. **name_fa** در SQLite/console — mojibake encoding  
4. **کشت agronomy fields** روی بسیاری ردیف‌ها `null`  
5. **FE↔API** ناقص روی بخشی از صفحات  
6. **coverage %** اندازه‌گیری سراسری ثبت‌نشده در CI gate سخت  
7. **Docker/PostGIS** روی host کاربر در دسترس نیست (عمداً با SQLite جایگزین)  
8. **GEE live** بدون credential  
9. **RS256** پیش‌فرض نیست  
10. **nested path** `D:\econojin.com` vs `eco-nojin\.venv` — گیج‌کننده  
11. **اسناد متعدد PHASE_* با ادعاهای متناقض** — نیاز به این فایل به‌عنوان SSOT  
12. **فایل‌های ریشه شلوغ** (analyze scripts, empty stubs) — بدهی hygiene

---

## ۳. بدهی فنی اولویت‌دار

| ID | بدهی | شدت | فاز رفع |
|----|------|------|--------|
| TD-01 | Multiple Alembic heads / MODEL_MODULES import | بالا | 2 |
| TD-02 | Schema drift SQLite vs ORM (ستون‌های جدید) | بالا | 2 |
| TD-03 | Optional routers fail noisy (langchain, …) | متوسط | 3 |
| TD-04 | FE mock / incomplete API wiring | بالا | 4 |
| TD-05 | RBAC نه روی همه writeها وقتی flag روشن | بالا | 1/8 |
| TD-06 | HS256 default | متوسط | 1/10 |
| TD-07 | No measured cov gate | متوسط | 6 |
| TD-08 | Encoding فارسی در DB/console | پایین | 9 |
| TD-09 | Crop agronomy nulls | متوسط | 3 |
| TD-10 | Repo root clutter / nested eco-nojin | پایین | 7 |
| TD-11 | Secrets template ناقص (قبل از این commit) | متوسط | 0/done |
| TD-12 | Celery بدون Redis فقط sync | پذیرفته local | 5/10 |

---

## ۴. برنامه ۱۰ فاز (اجرایی — کلیدها در انتها)

| فاز | نام | هدف | کلید خارجی؟ |
|-----|-----|------|-------------|
| **1** | امنیت و Hardening | middleware، secret hygiene، write-auth flag docs | خیر |
| **2** | دیتابیس local-first | merge alembic heads، SQLite پایدار، seed | خیر |
| **3** | API یکپارچه | router health، pagination، science/monitoring smoke | خیر |
| **4** | FE اتصال واقعی | login، farms، crops، monitoring، science | خیر |
| **5** | علم/EO offline-complete | synthetic+Open-Meteo، Celery sync path | خیر (GEE بعداً) |
| **6** | تست و observability | pytest-cov، contract، Sentry optional empty | Sentry بعداً |
| **7** | CI و hygiene | Actions، ruff، repo cleanup | خیر |
| **8** | Admin + RBAC | users/roles UI + enforce writes | خیر |
| **9** | PWA + i18n fa/en | dict متمرکز، RTL | خیر |
| **10** | Deploy + **ثبت کلیدها** | Neon/Vercel یا VPS؛ سپس GEE/OWM/Sentry/RS256 | **بله — اینجا** |

پس از فاز ۱۰: پر کردن `.env` طبق `docs/ENV_KEYS_MAP.md` و تست live.

---

## ۵. فاز بعدی فوری = فاز ۱ (امنیت) روی Zero-Install

بدون کلید:

1. تأیید `.env` از template  
2. اطمینان عدم hardcode secret  
3. مستند/تست rate-limit در local در صورت نیاز  
4. آماده‌سازی مسیر `secrets/` خالی  

سپس فاز ۲: اصلاح Alembic heads.

---

## ۶. درصد تخمینی (غیررسمی — نه KPI تبلیغاتی)

| لایه | تخمین واقعی |
|------|-------------|
| Backend skeleton + science | ~55–65٪ |
| FE UI | ~50–60٪ |
| FE↔API live | ~35–45٪ |
| Prod-ready (keys, Postgres, RS256, cov gate) | ~15–25٪ |

**کل قابل استفاده local demo:** حدود نصف راه؛ production کامل بعد از فاز ۱۰ + کلیدها.
