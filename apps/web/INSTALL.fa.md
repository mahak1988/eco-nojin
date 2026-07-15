# وابستگی‌های مورد نیاز — نصب قبل از build

## ۱) وابستگی‌های اصلی

```powershell
cd D:\econojin.com\apps\web

# React + Router
pnpm add react react-dom react-router-dom

# i18n (بین‌المللی‌سازی)
pnpm add i18next react-i18next i18next-browser-languagedetector

# Dev dependencies
pnpm add -D typescript @types/react @types/react-dom @types/node
pnpm add -D vite @vitejs/plugin-react
pnpm add -D tailwindcss@^3.4 postcss autoprefixer
```

> ⚠️ حتماً Tailwind نسخه ۳.۴ یا بالاتر نصب شود — نسخه‌های قدیمی از
> logical properties (ms/me/ps/pe) پشتیبانی نمی‌کنند و تغییر جهت RTL/LTR
> کار نخواهد کرد.

## ۲) تنظیمات محیط

```powershell
# ساخت فایل env از روی مثال
copy .env.example .env.local

# سپس VITE_API_BASE_URL را به آدرس واقعی backend تغییر دهید
```

## ۳) فونت‌ها

در `index.html` این خطوط را به `<head>` اضافه کنید:

```html
<!-- Vazirmatn (فارسی) -->
<link rel="stylesheet"
      href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" />

<!-- Inter (English) -->
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet"
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" />
```

و در تگ `<html>`:
```html
<html lang="fa" dir="rtl">
```

## ۴) Build

```powershell
pnpm run build
```
