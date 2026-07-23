/**
 * Tailwind CSS configuration — econojin.com / apps/web
 *
 * i18n: از logical properties استفاده کنید (ms-/me-/ps-/pe-/start-/end-)
 * dir="rtl|ltr" روی <html> این‌ها را خودکار معکوس می‌کند.
 *
 * @type {import('tailwindcss').Config}
 */
export default {
  content: [
    "./index.html",
    "./src/**/*.{ts,tsx,js,jsx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // ── برند (بدون تغییر) ──
        brand: {
          50:  "#ecfdf5", 100: "#d1fae5", 200: "#a7f3d0",
          300: "#6ee7b7", 400: "#34d399", 500: "#10b981",
          600: "#059669", 700: "#047857", 800: "#065f46",
          900: "#064e3b",
        },
        // ── توکن‌های معنایی (جدید) ──
        success: { DEFAULT: "#10b981", dark: "#059669" },
        warning: { DEFAULT: "#f59e0b", dark: "#d97706" },
        danger:  { DEFAULT: "#ef4444", dark: "#dc2626" },
        info:    { DEFAULT: "#3b82f6", dark: "#2563eb" },
      },
      fontFamily: {
        fa: ['"Vazirmatn"', '"IRANSans"', "system-ui", "sans-serif"],
        en: ['"Inter"', "system-ui", "sans-serif"],
      },
      borderWidth: { 3: "3px" },
      boxShadow: {
        card:      "0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)",
        glow:      "0 0 40px -10px rgb(16 185 129 / 0.35)",
        "glow-lg": "0 0 60px -15px rgb(16 185 129 / 0.4)",
      },
      animation: {
        float:   "float 6s ease-in-out infinite",
        shimmer: "shimmer 2.5s linear infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%":      { transform: "translateY(-8px)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
      },
    },
  },
  plugins: [],
};