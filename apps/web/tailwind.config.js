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
        // Honey accent — complementary warm tone for highlights
        honey: {
          50: "#fffbeb",
          100: "#fef3c7",
          200: "#fde68a",
          300: "#fcd34d",
          400: "#fbbf24",
          500: "#f59e0b",
          600: "#d97706",
          700: "#b45309",
          800: "#92400e",
          900: "#78350f",
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
        glow: "0 0 40px -10px rgb(16 185 129 / 0.35)",
        "glow-lg": "0 0 60px -15px rgb(16 185 129 / 0.4)",
        // Premium design-system shadows
        "glow-emerald": "0 0 40px -8px rgb(16 185 129 / 0.45)",
        "glow-teal": "0 0 40px -8px rgb(20 184 166 / 0.45)",
        glass: "0 8px 32px -8px rgb(16 185 129 / 0.15)",
        "glass-lg": "0 20px 60px -15px rgb(16 185 129 / 0.25)",
        "inner-glow": "inset 0 1px 0 0 rgb(255 255 255 / 0.15)",
      },
      backgroundImage: {
        "gradient-emerald": "linear-gradient(135deg, #10b981 0%, #059669 50%, #047857 100%)",
        "gradient-aurora":  "linear-gradient(135deg, #10b981 0%, #14b8a6 35%, #06b6d4 70%, #3b82f6 100%)",
        "gradient-honey":   "linear-gradient(135deg, #f59e0b 0%, #d97706 100%)",
        "gradient-sunset":  "linear-gradient(135deg, #f97316 0%, #ec4899 100%)",
      },
      animation: {
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 2.5s linear infinite",
        // Premium design-system animations
        aurora: "aurora 18s ease-in-out infinite",
        "mesh-float": "mesh-float 12s ease-in-out infinite",
        "shimmer-emerald": "shimmer-emerald 3s linear infinite",
        "glow-pulse": "glow-pulse 3s ease-in-out infinite",
        "gradient-pan": "gradient-pan 6s ease infinite",
        "float-slow": "float 10s ease-in-out infinite",
        "spin-slow": "spin-slow 18s linear infinite",
      },
      keyframes: {
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" },
        },
        shimmer: {
          "0%": { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        aurora: {
          "0%, 100%": {
            transform: "translate(0, 0) rotate(0deg) scale(1)",
            opacity: "0.7",
          },
          "33%": {
            transform: "translate(3%, -3%) rotate(120deg) scale(1.08)",
            opacity: "0.9",
          },
          "66%": {
            transform: "translate(-3%, 3%) rotate(240deg) scale(0.96)",
            opacity: "0.8",
          },
        },
        "mesh-float": {
          "0%, 100%": { transform: "translate(0, 0) scale(1)" },
          "50%":      { transform: "translate(-2%, -2%) scale(1.05)" },
        },
        "shimmer-emerald": {
          "0%":   { backgroundPosition: "-200% center" },
          "100%": { backgroundPosition: "200% center" },
        },
        "glow-pulse": {
          "0%, 100%": { boxShadow: "0 0 20px -4px rgb(16 185 129 / 0.35)" },
          "50%":      { boxShadow: "0 0 35px -2px rgb(16 185 129 / 0.6)" },
        },
        "gradient-pan": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%":      { backgroundPosition: "100% 50%" },
        },
        "spin-slow": {
          to: { transform: "rotate(360deg)" },
        },
      },
    },
  },
  plugins: [],
};
