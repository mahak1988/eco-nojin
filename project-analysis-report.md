# 📊 گزارش تحلیل ساختار پروژه فرانت‌اند

**تاریخ تحلیل:** 2026-06-11T23:20:56.181797
**مسیر پروژه:** `.`

## 📈 آمار کلی

| دسته | تعداد |
|------|-------|
| کل فایل‌ها | 4 |
| کل خطوط کد | 134 |
| کامپوننت‌ها | 2 |
| هوک‌ها | 2 |
| سرویس‌ها | 0 |
| تایپ‌ها | 0 |
| utilities | 0 |
| استایل‌ها | 0 |
| پوشه‌ها | 3 |

## 🧩 کامپوننت‌ها

- `components\ChartsPanel.tsx`
- `components\LanguageProviderRoot.tsx`

## 🪝 هوک‌ها

- `hooks\useWebSocket.ts`
- `store\useAnalysisStore.ts`

## 💡 پیشنهادات بازسازی

### 🟠 HIGH: API
هیچ service layer یافت نشد. تمام درخواست‌های API را به یک لایه سرویس منتقل کنید.

### 🟡 MEDIUM: TYPES
هیچ type definition یافت نشد. TypeScript interfaces و types را در فایل‌های جداگانه تعریف کنید.

