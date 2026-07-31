/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "../../packages/ui/src/**/*.{ts,tsx}",
  ],
  darkMode: ["class"],
  theme: {
    extend: {
      colors: {
        eco: {
          50: '#f0fdf4', 100: '#dcfce7', 200: '#bbf7d0', 300: '#86efac',
          400: '#4ade80', 500: '#22c55e', 600: '#16a34a', 700: '#15803d',
          800: '#166534', 900: '#14532d', 950: '#052e16',
        },
        // Dynamic theme colors that can be customized
        primary: 'var(--color-primary, #15803d)',
        secondary: 'var(--color-secondary, #bbf7d0)',
        accent: 'var(--color-accent, #22c55e)',
        background: 'var(--color-background, #ffffff)',
        surface: 'var(--color-surface, #f8fafc)',
        text: 'var(--color-text, #1e293b)',
        textSecondary: 'var(--color-textSecondary, #64748b)',
      },
      fontFamily: {
        sans: ['Vazirmatn', 'system-ui', 'sans-serif'],
        display: ['Vazirmatn', 'system-ui', 'sans-serif'],
      },
      // Add RTL specific spacing utilities
      spacing: {
        'sidebar-width': '16rem', // Width of the sidebar
      },
    },
  },
  plugins: [
    // Add RTL support using built-in functionality
    function({ addVariant }) {
      addVariant('rtl', '.rtl &');
      addVariant('ltr', '.ltr &');
    }
  ],
}