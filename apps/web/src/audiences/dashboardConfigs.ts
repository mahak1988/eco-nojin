import type { DashboardConfig } from "../components/eco/DashboardShell";
export const FARMER_CONFIG: DashboardConfig = { title: "داشبورد کشاورز",
  subtitle: "پایش مزرعه و پیش‌بینی محصول", icon: "🌾",
  stats: [
    { label: "رطوبت خاک", value: 67, suffix: "٪", icon: "💧", trend: { value: 3, up: true } },
    { label: "شاخص NDVI", value: 0.72, decimals: 2, icon: "🌿", trend: { value: 5, up: true } },
    { label: "دمای هوا", value: 28, suffix: "°C", icon: "🌡️" },
    { label: "پیش‌بینی محصول", value: 4.2, suffix: " تن", decimals: 1, icon: "📦", trend: { value: 8, up: true } } ],
  quickActions: [ { label: "نقشهٔ مزرعه", icon: "🗺️" }, { label: "برنامهٔ آبیاری", icon: "💧" },
    { label: "هشدار آفت", icon: "🐛" }, { label: "گزارش محصول", icon: "📊" } ] };
export const EXPERT_CONFIG: DashboardConfig = { title: "داشبورد کارشناس",
  subtitle: "تحلیل پیشرفته و مدل‌سازی", icon: "🔬",
  stats: [
    { label: "تحلیل‌های فعال", value: 12, icon: "📈", trend: { value: 2, up: true } },
    { label: "مدل‌های در حال اجرا", value: 3, icon: "🤖" },
    { label: "دادهٔ پردازش‌شده", value: 847, suffix: " GB", icon: "💾" },
    { label: "دقت مدل", value: 94.3, suffix: "٪", decimals: 1, icon: "🎯", trend: { value: 1.2, up: true } } ],
  quickActions: [ { label: "تحلیل طیفی", icon: "🌈" }, { label: "مدل‌سازی", icon: "🤖" },
    { label: "مقایسهٔ دوره‌ای", icon: "📊" }, { label: "خروجی گزارش", icon: "📄" } ] };
export const MANAGER_CONFIG: DashboardConfig = { title: "داشبورد مدیر",
  subtitle: "نمای کلان و تصمیم‌گیری", icon: "📋",
  stats: [
    { label: "پروژه‌های فعال", value: 8, icon: "📁", trend: { value: 1, up: true } },
    { label: "کاربران فعال", value: 234, icon: "👥", trend: { value: 12, up: true } },
    { label: "هشدارهای باز", value: 5, icon: "⚠️", trend: { value: 2, up: false } },
    { label: "بودجهٔ مصرفی", value: 73, suffix: "٪", icon: "💰" } ],
  quickActions: [ { label: "گزارش مدیریتی", icon: "📊" }, { label: "مدیریت کاربران", icon: "👥" },
    { label: "تنظیمات", icon: "⚙️" }, { label: "صدور مجوز", icon: "🔑" } ] };
export const RESEARCHER_CONFIG: DashboardConfig = { title: "داشبورد پژوهشگر",
  subtitle: "داده‌کاوی و انتشار یافته‌ها", icon: "🎓",
  stats: [
    { label: "مقالات در حال نگارش", value: 3, icon: "📝" },
    { label: "دیتاست‌های قابل دسترس", value: 47, icon: "🗃️", trend: { value: 5, up: true } },
    { label: "استنادها", value: 128, icon: "🔗", trend: { value: 9, up: true } },
    { label: "همکاران", value: 16, icon: "🤝" } ],
  quickActions: [ { label: "کاوش داده", icon: "🔍" }, { label: "آزمایشگاه", icon: "🧪" },
    { label: "کتابخانه", icon: "📚" }, { label: "انتشار", icon: "🚀" } ] };
export const STUDENT_CONFIG: DashboardConfig = { title: "داشبورد دانشجو",
  subtitle: "یادگیری و تمرین", icon: "📖",
  stats: [
    { label: "دوره‌های فعال", value: 4, icon: "🎓", trend: { value: 1, up: true } },
    { label: "تمرین‌های انجام‌شده", value: 23, icon: "✅" },
    { label: "امتیاز", value: 870, icon: "⭐", trend: { value: 45, up: true } },
    { label: "رتبه", value: 12, icon: "🏆", trend: { value: 3, up: true } } ],
  quickActions: [ { label: "دوره‌ها", icon: "📚" }, { label: "آزمون", icon: "📝" },
    { label: "بازی‌ها", icon: "🎮" }, { label: "گواهی‌ها", icon: "📜" } ] };
