/**
 * Tailwind CSS configuration — econojin.com / apps/web
 *
 * IMPORTANT (i18n): This config uses Tailwind v3.3+ LOGICAL PROPERTIES so the
 * same class works in both RTL (Persian) and LTR (English) without changes.
 * Examples:
 *   ms-2 / me-2   (margin-inline-start / end)   — instead of ml-2 / mr-2
 *   ps-2 / pe-2   (padding-inline-start / end)  — instead of pl-2 / pr-2
 *   start-0 / end-0                             — instead of left-0 / right-0
 *   text-start / text-end                       — instead of text-left / text-right
 *   border-s / border-e                         — instead of border-l / border-r
 *   rounded-s-lg / rounded-e-lg                 — instead of rounded-l-lg / rounded-r-lg
 *
 * The `dir="rtl|ltr"` attribute on <html> (set by useLanguage hook) flips
 * these automatically — no extra CSS needed.
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
        brand: {
          50: "#ecfdf5",
          100: "#d1fae5",
          200: "#a7f3d0",
          300: "#6ee7b7",
          400: "#34d399",
          500: "#10b981",
          600: "#059669",
          700: "#047857",
          800: "#065f46",
          900: "#064e3b",
        },
      },
      fontFamily: {
        fa: ['"Vazirmatn"', '"IRANSans"', "system-ui", "sans-serif"],
        en: ['"Inter"', "system-ui", "sans-serif"],
      },
      borderWidth: {
        3: "3px",
      },
      boxShadow: {
        card: "0 1px 3px 0 rgb(0 0 0 / 0.06), 0 1px 2px -1px rgb(0 0 0 / 0.06)",
      },
    },
  },
  plugins: [],
};
