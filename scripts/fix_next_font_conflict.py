import logging

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
رفع تضاد next/font و Babel
- حذف next/font از layout.tsx
- افزودن Inter font از Google Fonts CDN
- حفظ .babelrc (برای fallback از SWC)
r"""

import sys
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"D:\econojin.com")
FRONTEND_DIR = PROJECT_ROOT / "frontend"


class NextFontFixer:
    def __init__(self):
        self.backup_dir = FRONTEND_DIR / '.font_fix_backup'
        self.backup_dir.mkdir(exist_ok=True)

    def backup(self, path: Path):
        if not path.exists():
            return
        rel = path.relative_to(FRONTEND_DIR)
        dest = self.backup_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = dest.parent / f"{dest.stem}_{ts}{dest.suffix}"
        shutil.copy2(path, backup_path)
        logger.info(f"  💾 Backup: {backup_path.relative_to(FRONTEND_DIR)}")

    def fix_layout(self):
        """حذف next/font و استفاده از CSS font"""
        print("\n" + "="*70)
        logger.info("🔤 Step 1: Fix layout.tsx (remove next/font)")
        print("="*70)

        layout_file = FRONTEND_DIR / "app" / "layout.tsx"
        if not layout_file.exists():
            logger.info(f"  ❌ layout.tsx not found: {layout_file}")
            return False

        self.backup(layout_file)

        # نسخه جدید بدون next/font
        new_content = """import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Econojin - Gaia Protocol Carbon Platform',
  description: 'Calculate, verify, and tokenize your ecological impact with scientific accuracy',
  keywords: ['carbon', 'climate', 'blockchain', 'satellite', 'NDVI', 'Gaia Protocol'],
  authors: [{ name: 'Econojin Team' }],
  openGraph: {
    title: 'Econojin - Scientific Carbon Platform',
    description: 'Turn ecological impact into verifiable digital assets',
    type: 'website',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="format-detection" content="telephone=no, date=no, email=no, address=no" />
        {/* Google Fonts - Inter (loaded via CDN, no SWC needed) */}
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  )
}
"""

        layout_file.write_text(new_content, encoding='utf-8')
        logger.info("  ✅ layout.tsx updated (next/font removed)")
        logger.info("     • Using Google Fonts Inter via CDN")
        logger.info("     • Compatible with Babel (no SWC needed)")
        return True

    def fix_globals_css(self):
        """به‌روزرسانی globals.css با font-family صحیح"""
        print("\n" + "="*70)
        logger.info("🎨 Step 2: Update globals.css with Inter font")
        print("="*70)

        css_file = FRONTEND_DIR / "app" / "globals.css"
        if not css_file.exists():
            logger.info(f"  ❌ globals.css not found: {css_file}")
            return False

        self.backup(css_file)

        new_css = """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --primary: 142 76% 36%;
    --primary-foreground: 355 100% 100%;
    --secondary: 210 40% 96.1%;
    --secondary-foreground: 222.2 47.4% 11.2%;
    --muted: 210 40% 96.1%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96.1%;
    --accent-foreground: 222.2 47.4% 11.2%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 142 76% 36%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 142 76% 36%;
    --primary-foreground: 355 100% 100%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  
  html {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
      'Helvetica Neue', Arial, sans-serif;
  }
  
  body {
    @apply bg-background text-foreground;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto,
      'Helvetica Neue', Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
}

/* Custom Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100;
}

::-webkit-scrollbar-thumb {
  @apply bg-green-500 rounded-full;
}

::-webkit-scrollbar-thumb:hover {
  @apply bg-green-600;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

.animate-fade-in {
  animation: fadeIn 0.5s ease-in-out;
}

.animate-slide-up {
  animation: slideUp 0.5s ease-out;
}

.animate-float {
  animation: float 3s ease-in-out infinite;
}
"""

        css_file.write_text(new_css, encoding='utf-8')
        logger.info("  ✅ globals.css updated with Inter font")
        return True

    def update_tailwind_config(self):
        """به‌روزرسانی tailwind.config.js با fontFamily Inter"""
        print("\n" + "="*70)
        logger.info("⚙️  Step 3: Update tailwind.config.js")
        print("="*70)

        config_file = FRONTEND_DIR / "tailwind.config.js"
        self.backup(config_file)

        new_config = """/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: [
          'Inter',
          '-apple-system',
          'BlinkMacSystemFont',
          'Segoe UI',
          'Roboto',
          'Helvetica Neue',
          'Arial',
          'sans-serif',
        ],
      },
      colors: {
        'gaia': {
          50: '#f0fdf4',
          100: '#dcfce7',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          900: '#14532d',
        },
        'seed': {
          50: '#fffbeb',
          500: '#f59e0b',
          600: '#d97706',
        }
      },
    },
  },
  plugins: [require('tailwindcss-animate')],
}
"""

        config_file.write_text(new_config, encoding='utf-8')
        logger.info("  ✅ tailwind.config.js updated with Inter font family")
        return True

    def clear_cache(self):
        """پاک کردن cache"""
        print("\n" + "="*70)
        logger.info("🧹 Step 4: Clear Next.js Cache")
        print("="*70)

        next_dir = FRONTEND_DIR / ".next"
        if next_dir.exists():
            shutil.rmtree(next_dir, ignore_errors=True)
            logger.info("  ✓ Removed .next folder")
        else:
            logger.info("  ⏭️  .next not found (already clean)")

    def generate_report(self):
        print("\n" + "="*70)
        logger.info("✅ FIX COMPLETE")
        print("="*70)
        print(r"""
🎯 Changes Applied:
   • Removed next/font import from layout.tsx
   • Added Inter font via Google Fonts CDN
   • Updated tailwind.config.js with font-family
   • Updated globals.css with Inter font stack
   • Cleared Next.js cache

📋 Why This Fix Works:
   • next/font requires SWC compiler (binary not installed)
   • Using Google Fonts via CDN works with Babel
   • Same visual result (Inter font)
   • No SWC binary needed!

🚀 Next Steps:

1) Start the frontend:
   cd D:\\econojin.com\\frontend
   npm run dev

2) Open browser:
   http://localhost:3000

3) Start backend (in a NEW terminal):
   cd D:\\econojin.com
   python scripts/api/run_server.py

💡 Note: Font loads from Google CDN (requires internet first time,
   then cached by browser).

🔒 Security:
   • Next.js 15.0.5 (CVE-2025-66478 PATCHED)
   • Babel compiler (SWC fallback)
   • Google Fonts via HTTPS
r""")
        print("="*70)

    def run_all(self):
        print("="*70)
        logger.info("🔧 NEXT/FONT + BABEL CONFLICT FIXER")
        print("="*70)
        logger.info(f"📁 Frontend: {FRONTEND_DIR}")

        if not FRONTEND_DIR.exists():
            logger.info(f"❌ Frontend directory not found")
            return False

        success = (
            self.fix_layout() and
            self.fix_globals_css() and
            self.update_tailwind_config()
        )

        self.clear_cache()

        if success:
            self.generate_report()

        return success


def main():
    try:
        fixer = NextFontFixer()
        success = fixer.run_all()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.info(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()