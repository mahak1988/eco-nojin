# آماده‌سازی فاز ۲ — پنل ادمین

**تاریخ:** ۱۴۰۵-۰۵-۱۵  
**پیش‌نیاز:** فاز ۱ + backlog پنج‌گانه خارج از فاز ۱ تکمیل شد.

---

## ✅ تکمیل‌شده (خارج از فاز ۱)

| # | مورد | پیاده‌سازی |
|---|------|------------|
| 1 | Auth cookie-first + Login + AuthGuard | `AuthContext`, `LoginPage`, `AuthGuard`, دکمه خروج در Layout |
| 2 | فارسی‌سازی UI | Users, AuditLogs, Reports, Dashboard, Monitoring, Sidebar, Layout |
| 3 | همگام Route/Sidebar | لینک‌های Dashboard فقط به مسیرهای موجود؛ NotFound فارسی |
| 4 | UX | Toast به‌جای alert؛ loading/error یکسان؛ تأیید حذف |
| 5 | آماده‌سازی فاز ۲ | این سند + نقاط اتصال بک‌اند مشخص شد |

---

## 🚀 فاز ۲ — پیشنهاد محدوده

### ۲.۱ اتصال واقعی ماژول‌های کشاورزی در ادمین
- FarmsPage / WeatherPage / RisksPage / SatellitePage / SimulationPage → APIهای `apps/farms`, `weather`, `risks`, `satellite`, `simulation`
- حذف داده mock در صفحات ادمین

### ۲.۲ حذف mock از router ادمین
- `advanced-settings`, `content versions`, `intelligent-analytics`, `auto-recommendations` فعلاً mock هستند
- جایگزینی با سرویس واقعی یا علامت‌گذاری feature-flag

### ۲.۳ RBAC دقیق‌تر در FE
- مخفی کردن منوها بر اساس permission
- نمایش پیام «دسترسی ندارید» به‌جای 403 خام

### ۲.۴ حسابداری ادمین
- اتصال Accounts / Journal / Invoices / Payments به `apps/api` accounting routes

### ۲.۵ سخت‌سازی cookie-only
- حذف کامل localStorage token پس از تأیید بک‌اند
- SameSite + Secure در production

---

## معیار شروع فاز ۲

- [x] Login + Guard فعال
- [x] Dashboard / Monitoring / Users به API واقعی متصل
- [x] UI اصلی فارسی
- [x] مسیرهای شکسته حذف شده
- [ ] (اختیاری) تست دستی با superuser روی محیط local

**آماده شروع فاز ۲.**
