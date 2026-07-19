# کامپوننت‌های فرانت‌اند زیبا 🌟

این پوشه شامل کامپوننت‌های استخراج‌شده از گیت‌هاب برای پروژه EcoNojin است.

## 📦 کامپوننت‌های ساخته‌شده

### DashboardGrid.tsx
داشبورد زیبا با کارت‌های آماری - از الهام `salvia-kit/dashboard` و `bulletproof-react`

### EcoSidebar.tsx
منوی کناری زیبا - از الهام `agri-moon/Sidebar` (Vite + React + Tailwind)

### EcoDashboardMap.tsx
نقشه GIS کشاورزی - از الهام `agri-moon/DashboardMap` (react-leaflet)

## 🔗 منابع گیت‌هاب استخراج‌شده

| مخزن | کامپوننت | توضیح |
|-------|---------|--------|
| [salvia-kit/salvia-kit](https://github.com/salvia-kit/salvia-kit) | DashboardCard | چهار کارت آمار با ترند |
| [agri-moon](https://github.com/aminju14/agri-moon) | Sidebar | منوی کناری با قابلیت جمع‌شدن |
| [agri-moon](https://github.com/aminju14/agri-moon) | DashboardMap | نقشه GIS با react-leaflet |
| [alan2207/bulletproof-react](https://github.com/alan2207/bulletproof-react) | Button | دکمه با انیمیشن و Variant |

## 🚀 نحوه استفاده

```tsx
import { EcoDashboard } from "@/components/common/DashboardGrid"
import EcoSidebar from "@/components/common/EcoSidebar"
import EcoDashboardMap from "@/components/charts/EcoDashboardMap"

function DashboardPage() {
  return (
    <div className="flex h-screen">
      <EcoSidebar />
      <main className="flex-1 p-6 overflow-auto">
        <EcoDashboard />
        <EcoDashboardMap />
      </main>
    </div>
  )
}