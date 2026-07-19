# 🌱 برنامه توسعه اکو نوژین

**تاریخ:** ۱۴۰۵/۰۴/۲۸  
**وضعیت فعلی:** FastAPI + Next.js + SQLite

---

## 📊 وضعیت کنونی پروژه

| بخش | تکمیل | نکات |
|-----|--------|------|
| **Backend Core** | ✅ | FastAPI، Auth JWT، OTP، Security |
| **Accounting System** | ✅ | Model → Schema → Repository → Service → Router |
| **Agriculture Schools** | ✅ | CRUD کامل + DB بکار رفت |
| **Education System** | ✅ | Course, Lesson, Enrollment CRUD + stats |
| **Library System** | ✅ | LibraryResource CRUD + file upload |
| **Community System** | ✅ | Posts, Comments, Likes با CRUD کامل |
| **Games System** | ✅ | Vocabulary + Quiz + Attempts |
| **Alembic Migrations** | ✅ | تنظیم شد، modelها ثبت شدند |
| **Database Tests** | ✅ | تست‌های CRUD اضافه شدند |
| **Simulation** | ✅ | ۲۸ شبیه‌ساز فعال، AquaCrop گسترش یافت |
| **AI Agents** | ⚠️ | LLM Factory آماده، عملیات در انتظار |
| **Tests Coverage** | ⚠️ | pytest پایه وجود دارد |

---

## 🎯 برنامه فازی پیشنهادی

### **فاز P0 — تکمیل ضروری برای Production (۲-۳ هفته)**

- [x] Accounting System - تکمیل شد
- [x] Agriculture Schools - تکمیل شد  
- [x] Alembic Migrations - تنظیم شد
- [x] Database Tests - اضافه شد
- [ ] OTP Tests با mock SMS
- [ ] REQUIRE_AUTH_FOR_WRITES=true در production

### **فاز P1 — پایداری API/UI (۳-۴ هفته)**

| ماژول | وضعیت | کار |
|-------|-------|-----|
| education | ✅ | Course, Lesson, Enrollment CRUD + stats |
| library | ✅ | LibraryResource CRUD + file upload |
| community | ✅ | Posts, Comments, Likes with CRUD |
| games | ✅ | Vocabulary + Quiz + Attempts |

### **فاز P2 — علمی و داده واقعی (۶-۸ هفته)**

- [x] FAO AquaCrop integration (crop database + water-yield calculations)
- [x] SWAT+ basin-scale modeling with nutrients
- [x] Sentinel-2 vegetation indices fetcher
- [x] ERA5-Land climate data fetcher
- [x] CHIRPS precipitation fetcher
- [x] PostGIS integration

### **فاز P3 — استقرار نهایی (۲-۳ هفته)**

- [x] Solidity contracts (EcoCoin + VerificationOracle)
- [x] Vercel + Render + Neon deployment (CI/CD + vercel.json)

---

## 🔧 الگوی یکسان برای تمام ماژول‌ها

### الگوی پیاده‌سازی (Model → Schema → Repository → Service → Router)

```
apps/api/
├── models/
│   └── {module}.py          # SQLAlchemy models
├── schemas/
│   └── {module}.py          # Pydantic schemas
├── repositories/
│   └── {module}.py          # Data access layer
├── services/
│   └── {module}.py          # Business logic
└── routes/
    └── {module}.py          # FastAPI endpoints
```

---

## 📅 برنامه هفتگی پیشنهادی

| هفته | کار |
|------|-----|
| هفته ۱ | ✅ Accounting + Agriculture Schools |
| هفته ۲ | ✅ Alembic + Database Tests |
| هفته ۳ | ✅ Education + Library CRUD |
| هفته ۴ | ✅ Community + Games CRUD |
| هفته ۵-۶ | ✅ AquaCrop integration |
| هفته ۷-۸ | ✅ SWAT+ + Sentinel fetchers |
| هفته ۹ | ✅ Solidity contracts |
| هفته ۱۰ | ✅ Deploy Vercel/Render/Neon |
| هفته ۱۱ | ✅ Monitoring + Sentry |
| هفته ۱۲ | ✅ PWA support |

---

## 📝 فایل‌های ایجاد شده

### Accounting System (apps/api/)
| فایل | توضیح |
|-----|-------|
| `models/accounting.py` | 8 مدل (حساب، ژورنل، فاکتور، پرداخت، بودجه، مالیات، دارایی) |
| `schemas/accounting.py` | اسکماهای Pydantic با اعتبارسنجی |
| `repositories/accounting.py` | لایه دسترسی داده |
| `services/accounting.py` | لایه کسب و کار |
| `routes/accounting.py` | ۱۴ endpoint RESTful |

### Agriculture Schools (apps/api/)
| فایل | توضیح |
|-----|-------|
| `models/agriculture_school.py` | مدل مدارس کشاورزی |
| `schemas/agriculture_school.py` | اسکماهای Pydantic |
| `repositories/agriculture_school.py` | لایه دسترسی داده |
| `services/agriculture_school.py` | لایه کسب و کار |
| `routes/agriculture_schools.py` | ۵ endpoint CRUD + stats |

### Frontend (apps/web/src/pages/Accounting/)
- `Accounting.tsx` متصل به API واقعی

### Packages (packages/api-client/src/modules/)
- `accounting.api.ts` - کلاینت TypeScript

### Tests (apps/api/tests/)
- `test_accounting.py` - تست‌های enumeration
- `test_database.py` - تست‌های CRUD دیتابیس

### Education System (apps/api/)
| فایل | توضیح |
|-----|-------|
| `models/education.py` | Course, Lesson, Enrollment مدل‌ها |
| `schemas/education.py` | اسکماهای Pydantic با Category/Level Enum |
| `repositories/education.py` | لایه دسترسی داده با ۱۵ متد |
| `services/education.py` | لایه کسب و کار |
| `routes/education.py` | ۱۵ endpoint RESTful |

### Library System (apps/api/)
| فایل | توضیح |
|-----|-------|
| `models/library.py` | LibraryResource مدل |
| `schemas/library.py` | اسکماهای Pydantic + FileUploadResponse |
| `repositories/library.py` | لایه دسترسی داده |
| `services/library.py` | لایه کسب و کار |
| `routes/library.py` | ۸ endpoint شامل file upload |

### Community System (apps/api/)
| فایل | توضیح |
|-----|-------|
| `models/community.py` | Post, Comment, Like مدل‌ها |
| `schemas/community.py` | اسکماهای Pydantic + stats |
| `repositories/community.py` | لایه دسترسی داده |
| `services/community.py` | لایه کسب و کار |
| `routes/community.py` | ۱۰ endpoint RESTful |

### Games System (apps/api/)
| فایل | توضیح |
|-----|-------|
| `models/games.py` | VocabularyWord, Quiz, QuizQuestion, QuizAttempt مدل‌ها |
| `schemas/games.py` | اسکماهای Pydantic با Enum |
| `repositories/games.py` | لایه دسترسی داده |
| `services/games.py` | لایه کسب و کار |
| `routes/games.py` | ۱۴ endpoint RESTful |


### Smart Contracts (contracts/)
| فایل | توضیح |
|-----|-------|
| `EcoCoin.sol` | Environmental token with staking (1B max supply) |
| `VerificationOracle.sol` | Ecological project verification system |
| `README.md` | Development and deployment instructions |

### Monitoring System (apps/shared_core/monitoring/)
| فایل | توضیح |
|-----|-------|
| `sentry.py` | Sentry integration for error tracking and performance monitoring |
| `__init__.py` | Module exports (init_sentry, capture_exception, capture_message) |

**ویژگی‌ها:**
- `init_sentry(app)` - مقداردهی اولیه سرویس با FastAPI، SQLAlchemy، و AsyncIO integrations
- `capture_exception(exc, context)` - گرفتن استثنا با زمینه اضافی
- `capture_message(message, level)` - گرفتن پیام در سطوح مختلف (info, warning, error)

### PWA Support (apps/web/)
| فایل | توضیح |
|-----|-------|
| `public/manifest.webmanifest` | PWA manifest with shortcuts and icons |
| `public/sw.js` | Service worker with cache strategies |
| `index.html` | PWA meta tags and service worker registration |
| `src/hooks/usePWA.ts` | React hooks for PWA state management |

**ویژگی‌ها:**
- نصب قابل‌دسترس (Before Install Prompt)
- کش افلاین برای محتوا
- شورتکات‌های نصب (Dashboard، Simulators، Satellites)
- پشتیبانی از iOS و Android

این برنامه می‌تواند به عنوان الگو برای توسعه‌دهندگان دیگر نیز استفاده شود.
