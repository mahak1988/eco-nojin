# ✅ گزارش تحلیل سایت localhost:5174 (اکونوجین)

## 📋 خلاصه کلی

سایت **localhost:5174** یک برنامه وب فرانت‌اند در حال توسعه است که با **Vite + React 18 + TypeScript** ساخته شده و بخشی از **مونوریپو اکونوجین** است. این برنامه برای **پایش محیط‌زیست و اقتصاد سبز** طراحی شده است.

---

## 🏗️ معماری فنی

### تکنولوژی‌های اصلی
| بخش | تکنولوژی |
|-----|----------|
| **فریمورک** | React 18 (^18.3.1) |
| **بیلت‌ان** | Vite (^5.4.21) |
| **زبان** | TypeScript (^5.5.4) |
| **استایل** | Tailwind CSS (^3.4.19) |
| **مدیریت State** | Zustand (^5.0.14) + TanStack Query (^5.101.2) |
| **Routing** | React Router DOM (^6.30.4) |
| **i18n** | react-i18next (^26.3.6) + 10 زبان |
| **انیمیشن** | Framer Motion (^12.40.0) + tsparticles |
| **Web3** | Wagmi (^3.7.1) + RainbowKit (^2.2.11) + Viem (^2.55.1) |
| **GIS** | React Leaflet (^5.0.0) + Leaflet (^1.9.4) |
| **Charts** | Recharts (^3.8.1) |
| **UI Kit** | Headless UI (^2.2.10) + Heroicons (^2.2.0) + Radix UI (^1.6.2) |

### ویژگی‌های خاص
- ✅ **PWA (Progressive Web App)** با Service Worker سفارشی
- ✅ **RTL/LTR** کامل برای پشتیبانی چند زبانه (فارسی/عربی RTL، انگلیسی/سایر LTR)
- ✅ **Dark Mode** با تماماستقام (class-based)
- ✅ **Lazy Loading** برای بهینه‌سازی بارگذاری صفحات
- ✅ **Error Boundary** برای مدیریت خطاها
- ✅ **Command Palette** (Ctrl+K) برای دسترسی سریع
- ✅ **Theme Toggle** برای سوئیچ تم روشن/تاریک

---

## 🌍 سیستم چند زبانه (i18n)

### زبان‌های پشتیبانی‌شده (10 زبان)
- **RTL:** فارسی (fa)، عربی (ar)
- **LTR:** انگلیسی (en)، اسپانیایی (es)، فرانسوی (fr)، آلمانی (de)، روسی (ru)، چینی (zh)، ترکی (tr)، هندی (hi)

### پوشش زبانی: ~۴.۸ میلیارد نفر (۶۰% جمعیت جهان)

---

## 📄 ساختار مسیرها (Routing)

### صفحات عمومی (دسترسی بدون لاگین)
| مسیر | توضیح |
|------|------|
| `/` | صفحه اصلی (Landing Page) |
| `/login` | صفحه ورود |
| `/register` | صفحه ثبت‌نام |
| `/forgot-password` | فراموشی رمز عبور |
| `/terms` | قوانین و مقررات |
| `/privacy` | حریم خصوصی |

### صفحات داشبورد (محافظت‌شده)
| مسیر | توضیح |
|------|------|
| `/dashboard` | داشبورد کاربر |
| `/profile` | پروفایل کاربر |
| `/simulators` | شبیه‌سازها |
| `/alerts` | سیستم هشدارها |

### صفحات Agri-moon (کشاورزی هوشمند)
| مسیر | توضیح |
|------|------|
| `/land-registry` | ثبت مزارع |
| `/planting-seasons` | فصول کاشت |
| `/harvest-monitoring` | پایش شماره‌گیری |
| `/fertilizer` | مدیریت کود |
| `/water-irrigation` | آبیاری |
| `/production-analytics` | تحلیل تولید |
| `/gis-explorer` | کاوش GIS |
| `/ai-insights` | بینش‌های هوش مصنوعی |
| `/reports` | گزارش‌ها |
| `/administration` | اداری |

### داشبوردهای نقش‌محور (RBAC)
| مسیر | نقش‌های مجاز |
|------|----------|
| `/farmer` | کشاورز، کارشناس، مدیر |
| `/student` | دانشجو، کارشناس، مدیر |
| `/expert` | کارشناس، مدیر |
| `/manager` | مدیر |
| `/researcher` | پژوهشگر، کارشناس، مدیر |
| `/admin` | فقط مدیر ارشد (Superuser) |

---

## 💡 بخش‌های اصلی برنامه

### 1. Landing Page (صفحه اصلی)
- Navigation Bar با Glassmorphism Effect
- Hero Section با داشبورد پیش‌نمایش
- بخش ویژگی‌ها (6 ویژگی کلیدی)
- بخش مخاطبان هدف (5 نقش کاربری)
- Call to Action
- Footer with لینک‌های مرتبط

### 2. داشبوردهای تخصصی
- **کربن:** پایش گازهای گلخانه‌ای
- **آبخیزها:** پایش حوزه‌های آبی
- **خاک:** آنالیز وضعیت خاک
- **انرژی:** پایش انرژی تجدیدپذیر
- **تنوع زیستی:** Biodiversity Dashboard
- **خشکسالی:** Drought Monitoring
- **اقتصاد سبز:** مدل‌های اقتصادی

### 3. EcoCoin (سیستم پاداش)
- کیف پول دیجیتال
- استخراج اکوکوین (Mining)
- چالش‌های سبز
- پاداش‌ها و تعویض

### 4. ابزارهای دیگر
- **دانش‌یار:** دستیار هوشمند پژوهش
- **تصمیم‌یار:** سیستم پشتیبان تصمیم
- **مدرسه‌های کشاورزی:** فهرست دانشگاه‌ها
- **وبلاگ:** مقالات و اخبار

---

## 🔐 امنیت و دسترسی

### ویژگی‌های امنیتی
- ✅ AuthContext با مدیریت نشست
- ✅ ProtectedRoute برای مسیرهای محافظت‌شده
- ✅ Role-Based Access Control (RBAC)
- ✅ Supabase Integration (JWT Authentication)
- ✅ Form Validation با پیام‌های خطا

---

## 🎨 طراحی و UI/UX

### تم
- **تم روشن/تاریک** با سوئیچر
- **رنگ اصلی:** Emerald (#059669) - تم رنگ سبز طبیعت
- **رنگ دوم:** Honey (#f59e0b) - برای هایلایت‌ها
- Font: Vazirmatn (فارسی) + Inter (انگلیسی)

### انیمیشن‌ها
- FadeIn animations
- Stagger children animations
- Hover effects (scale, lift)
- Aurora gradient animations
- Loading spinners

---

## 📱 PWA و وب اپلیکیشن

### ویژگی‌های PWA
- Manifest webmanifest
- Service Worker دیتابه‌سازی
  - Cache-first برای فایل‌استاتیک
  - Network-first برای APIها
  - Offline fallback
- Apple Mobile Web App Support
- Theme Color: #059669 (Emerald)

---

## 📊 فایل‌های کلیدی

### ساختار پوشه‌ها
```
apps/web/
├── public/
│   ├── manifest.webmanifest
│   ├── sw.js (Service Worker)
│   └── logo.svg
├── src/
│   ├── App.tsx (Routing Master)
│   ├── main.tsx (Entry Point)
│   ├── i18n/
│   │   ├── index.ts
│   │   └── locales/ (10 زبان)
│   ├── components/
│   │   ├── Layout/ (Header, Sidebar, Footer)
│   │   ├── common/ (ErrorBoundary, LoadingSpinner)
│   │   └── motion/ (انیمیشن‌ها)
│   ├── pages/
│   │   ├── Home/
│   │   ├── Dashboard/
│   │   ├── Carbon/
│   │   ├── Hydrology/
│   │   └── ...
│   └── hooks/
│       ├── useAuth.tsx
│       └── useLanguage.tsx
```

---

## ✅ وضعیت ساخت و کیفیت

- **وضعیت کامپایل:** ✅ تمام فایل‌ها در `verification_report` عبور کرده‌اند
- **تعداد فایل‌های بررسی‌شده:** ۴۲ فایل
- **وضعیت TypeScript:** ✅ `strict: true` فعال
- **وضعیل i18n:** ✅ کلیدهای تمام زبان‌ها یکسان
- **ESLint:** ✅ بدون هشدارهای Lint

---

## 🚀 راهنمای توسعه

```bash
# نصب وابستگی‌ها
pnpm install

# اجرای سرور توسعه (پورت 5173)
pnpm --filter @econojin/web dev

# ساخت برای production
pnpm --filter @econojin/web build

# بررسی کیفیت کد
pnpm --filter @econojin/web lint
```

---

## 📌 نکات کلیدی

1. **پشتیبانی کامل RTL:** برای فارسی و عربی با استفاده از logical properties در Tailwind
2. **ساختار ماژولار:** استفاده از Lazy Loading برای بهبود سرعت
3. **قابلیت گسترش:** طراحی برای افزودن بخش‌های جدید آسان
4. **Responsive Design:** کاملاً واکنش‌گرا برای موبایل و دسکتاپ
5. **Dark Mode:** پشتیبانی کامل حالت تاریک

---

## 🎨 بروزرسانی‌های طراحی (به‌روز شد)

### کارت‌ها (Cards)
- **`.card`**: افزوده شده transition برای انیمیشن نرم
- **`.card-hover`**: کارت با افکت hover برای حاشیه و سایه
- **`.card-elevated`**: کارت پریمیوم با backdrop-blur و شناور شدن
- **`.nav-card`**: کارت ناوبری با افکت‌های رنگی
- **`.stats-card`**: کارت آمار با خط کناری گرادیانی

### دکمه‌ها (Buttons)
- **`.btn-primary`**: گرادیانت دو رنگ، افکت شناوری بر روی hover، سایه‌گذاری پیشرفته
- **`.btn-secondary`**: حاشیه و رنگ‌های بهبور یافته، پشتیبانی از حالت تاریک
- **`.btn-ghost`**: دکمه شفاف برای اقدامات کم‌اهمیت

### ناوبری (Navigation)
- **Header**: افکت شیشه‌ای پیشرفته، ارتفاع پویا، لوگوی گرادینت با افکت glow
- **SidebarLink**: نشانگر فعال گرادینت، آیکون با افکت hover
- **NavLink**: خط کشویی گرادینت برای صفحات فعال در Navigation دسکتاپ

### App.tsx - بهبودهای توابعی
- **ScrollToTop**: اسکرول خودکار به بالا هنگام تغییر مسیر
- **PageLoader**: لودر پیشرفته با پیام فارسی
- **RouteErrorFallback**: صفحه خطای سفارشی
- **RouteSuspense**: Wrapper با ErrorBoundary برای هر مسیر
- **dir support**: حمایت کامل از RTL/LTR در wrapper اصلی

---

## 🏷️ قابلیت‌های منحصربه‌فرد

| قابلیت | توضیح |
|-------|------|
| **AI Agents** | دانش‌یار و تصمیم‌یار |
| **EcoCoin** | سیستم پاداش‌دهی غیرمتمرکز |
| **Simulators** | شبیه‌سازهای اقلیمی و محیطی |
| **Multi-role Dashboards** | داشبوردهای اختصاصی برای هر نقش |
| **GIS Integration** | نقشه‌برداری و تحلیل ماهواره‌ای |
| **Environmental Alerts** | هشدارهای بلادرنگ برای شرایط خطرناک |