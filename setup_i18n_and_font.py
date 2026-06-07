#!/usr/bin/env python3
"""Setup Vazirmatn Font and next-intl for Internationalization"""
import subprocess
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "apps" / "web" / "src"

def run_command(cmd: list, cwd: Path):
    print(f"  Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ⚠️ Warning: {result.stderr.strip()}")
    else:
        print(f"  ✅ Success")

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  + {path.relative_to(ROOT)}")

def main():
    print("=" * 70)
    print("🌍 Setting up Vazirmatn Font & Multi-language (i18n) System")
    print("=" * 70)

    # =========================================================================
    # 1. Install next-intl
    # =========================================================================
    print("\n[1/6] Installing next-intl package...")
    run_command(["pnpm", "add", "next-intl"], WEB_DIR.parent)

    # =========================================================================
    # 2. Create i18n Configuration
    # =========================================================================
    print("\n[2/6] Creating i18n configuration files...")
    
    # i18n.ts
    i18n_content = '''import {notFound} from 'next/navigation';
import {getRequestConfig} from 'next-intl/server';

export const locales = ['fa', 'en', 'ar'];
export const defaultLocale = 'fa';

export default getRequestConfig(async ({locale}) => {
  if (!locales.includes(locale as any)) notFound();

  return {
    messages: (await import(`../messages/${locale}.json`)).default
  };
});
'''
    write_file(WEB_DIR / "i18n.ts", i18n_content)

    # middleware.ts
    middleware_content = '''import createMiddleware from 'next-intl/middleware';
import {locales, defaultLocale} from './i18n';

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'as-needed' // Only prefix if it's not the default locale
});

export const config = {
  matcher: ['/', '/(fa|en|ar)/:path*', '/((?!_next|_vercel|.*\\..*).*)']
};
'''
    write_file(WEB_DIR.parent / "middleware.ts", middleware_content)

    # =========================================================================
    # 3. Create Translation Messages
    # =========================================================================
    print("\n[3/6] Creating translation message files...")
    
    messages_fa = {
        "metadata": {
            "title": "اکو نوژین | پلتفرم جامع احیای زمین و اکو کوین",
            "description": "پلتفرم علمی-فناورانه احیای مناظر خشک، ماینینگ سبز و ارز دیجیتال اکولوژیک"
        },
        "nav": {
            "home": "خانه",
            "modules": "ماژول‌ها",
            "ecocoin": "اکو کوین",
            "ecomining": "اکو ماینینگ",
            "academy": "آکادمی",
            "blog": "وبلاگ",
            "about": "درباره ما",
            "contact": "تماس",
            "wallet": "کیف پول",
            "login": "ورود"
        },
        "hero": {
            "badge": "پلتفرم جامع احیای زمین",
            "title_1": "ساکن زمین هستیم،",
            "title_2": "احیاگر اکوسیستم",
            "desc": "اولین پلتفرم جامع علمی-فناورانه برای احیای مناظر خشک و نیمه‌خشک با سیستم ارز دیجیتال اکولوژیک و ماینینگ سبز",
            "btn_primary": "شروع با اکو کوین",
            "btn_secondary": "اکو ماینینگ"
        },
        "footer": {
            "rights": "© {year} اکو نوژین. تمامی حقوق محفوظ است.",
            "made_with": "ساخته شده با ❤️ برای زمین"
        }
    }

    messages_en = {
        "metadata": {
            "title": "Econojin | Comprehensive Land Restoration & EcoCoin Platform",
            "description": "Scientific-technological platform for dryland restoration, green mining, and ecological cryptocurrency."
        },
        "nav": {
            "home": "Home",
            "modules": "Modules",
            "ecocoin": "EcoCoin",
            "ecomining": "EcoMining",
            "academy": "Academy",
            "blog": "Blog",
            "about": "About Us",
            "contact": "Contact",
            "wallet": "Wallet",
            "login": "Login"
        },
        "hero": {
            "badge": "Comprehensive Land Restoration Platform",
            "title_1": "We are Earth's inhabitants,",
            "title_2": "Ecosystem Restorers",
            "desc": "The first comprehensive scientific-technological platform for dryland restoration with ecological cryptocurrency and green mining.",
            "btn_primary": "Start with EcoCoin",
            "btn_secondary": "EcoMining"
        },
        "footer": {
            "rights": "© {year} Econojin. All rights reserved.",
            "made_with": "Made with ❤️ for the Earth"
        }
    }

    messages_ar = {
        "metadata": {
            "title": "إكونوجين | منصة شاملة لاستعادة الأراضي وعملة إيكو كوين",
            "description": "منصة علمية وتكنولوجية شاملة لاستعادة الأراضي الجافة، التعدين الأخضر، والعملات المشفرة البيئية."
        },
        "nav": {
            "home": "الرئيسية",
            "modules": "الوحدات",
            "ecocoin": "إيكو كوين",
            "ecomining": "التعدين البيئي",
            "academy": "الأكاديمية",
            "blog": "المدونة",
            "about": "من نحن",
            "contact": "اتصل بنا",
            "wallet": "المحفظة",
            "login": "تسجيل الدخول"
        },
        "hero": {
            "badge": "منصة شاملة لاستعادة الأراضي",
            "title_1": "نحن سكان الأرض،",
            "title_2": "مستعيدو النظام البيئي",
            "desc": "أول منصة علمية وتكنولوجية شاملة لاستعادة الأراضي الجافة وشبه الجافة مع نظام العملة المشفرة البيئية والتعدين الأخضر.",
            "btn_primary": "ابدأ مع إيكو كوين",
            "btn_secondary": "التعدين البيئي"
        },
        "footer": {
            "rights": "© {year} إكونوجين. جميع الحقوق محفوظة.",
            "made_with": "صنع بـ ❤️ من أجل الأرض"
        }
    }

    import json
    write_file(WEB_DIR / "messages" / "fa.json", json.dumps(messages_fa, indent=2, ensure_ascii=False))
    write_file(WEB_DIR / "messages" / "en.json", json.dumps(messages_en, indent=2, ensure_ascii=False))
    write_file(WEB_DIR / "messages" / "ar.json", json.dumps(messages_ar, indent=2, ensure_ascii=False))

    # =========================================================================
    # 4. Update Root Layout with Fonts and i18n Provider
    # =========================================================================
    print("\n[4/6] Updating Root Layout with Vazirmatn, Inter, and NextIntlProvider...")
    
    layout_content = '''import type { Metadata } from "next";
import { Vazirmatn, Inter } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, getLocale } from "next-intl/server";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

// 1. Vazirmatn for Persian/Arabic (RTL)
const vazirmatn = Vazirmatn({ 
  subsets: ["arabic"],
  variable: "--font-vazir",
  display: "swap",
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"]
});

// 2. Inter for English/Latin (LTR)
const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap"
});

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  const messages = await getMessages();
  
  return {
    title: (messages as any).metadata.title,
    description: (messages as any).metadata.description,
  };
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  const messages = await getMessages();
  
  // Determine direction based on locale
  const dir = locale === "en" ? "ltr" : "rtl";
  const fontClass = locale === "en" ? inter.variable : vazirmatn.variable;

  return (
    <html lang={locale} dir={dir} suppressHydrationWarning>
      <body className={`${fontClass} font-sans antialiased bg-slate-950 text-white min-h-screen flex flex-col`}>
        <NextIntlClientProvider messages={messages}>
          <Navbar />
          <main className="flex-1 pt-20">
            {children}
          </main>
          <Footer />
        </NextIntlClientProvider>
      </body>
    </html>
  );
}
'''
    write_file(WEB_DIR / "app" / "layout.tsx", layout_content)

    # =========================================================================
    # 5. Update Tailwind Config for Font Variables
    # =========================================================================
    print("\n[5/6] Updating Tailwind Config for Font Variables...")
    tailwind_path = WEB_DIR.parent / "tailwind.config.ts"
    if tailwind_path.exists():
        tw_content = tailwind_path.read_text(encoding="utf-8")
        if "fontFamily" not in tw_content:
            # Inject fontFamily into theme
            tw_content = tw_content.replace(
                "theme: {",
                """theme: {
      fontFamily: {
        sans: ['var(--font-vazir)', 'var(--font-inter)', 'system-ui', 'sans-serif'],
        vazir: ['var(--font-vazir)', 'sans-serif'],
        inter: ['var(--font-inter)', 'sans-serif'],
      },"""
            )
            tailwind_path.write_text(tw_content, encoding="utf-8")
            print("  ✅ Tailwind config updated with font variables")

    # =========================================================================
    # 6. Create a sample localized page to demonstrate usage
    # =========================================================================
    print("\n[6/6] Creating sample localized homepage structure...")
    
    # We'll create a [locale] folder structure for the main app
    locale_app_dir = WEB_DIR / "app" / "[locale]"
    locale_app_dir.mkdir(parents=True, exist_ok=True)
    
    # Move existing page.tsx to [locale] if it exists, or create a new one
    # For safety, we'll create a new localized page.tsx
    sample_page_content = '''"use client";

import { useTranslations } from "next-intl";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Leaf, Coins, Pickaxe } from "lucide-react";

export default function LocalizedHomePage() {
  const t = useTranslations("hero");
  const tNav = useTranslations("nav");

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/30 via-slate-950 to-blue-900/30" />
      
      <div className="relative container mx-auto px-6 text-center z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-bold mb-6">
            <Leaf className="h-3 w-3" />
            {t("badge")}
          </div>

          <h1 className="text-5xl md:text-7xl font-black leading-tight mb-6">
            {t("title_1")}
            <br />
            <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-blue-400 bg-clip-text text-transparent">
              {t("title_2")}
            </span>
          </h1>

          <p className="text-lg text-slate-300 leading-relaxed mb-8 max-w-2xl mx-auto">
            {t("desc")}
          </p>

          <div className="flex flex-wrap justify-center gap-4">
            <Link
              href="/ecocoin"
              className="group px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/30"
            >
              <Coins className="h-5 w-5" />
              {t("btn_primary")}
              <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link
              href="/ecomining"
              className="px-6 py-3 bg-slate-800/50 backdrop-blur border border-slate-700 hover:bg-slate-800 rounded-xl font-bold flex items-center gap-2 transition-all"
            >
              <Pickaxe className="h-5 w-5 text-purple-400" />
              {t("btn_secondary")}
            </Link>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
'''
    write_file(locale_app_dir / "page.tsx", sample_page_content)

    # =========================================================================
    # Clean cache
    # =========================================================================
    print("\n[7/7] Cleaning Next.js cache...")
    next_dir = WEB_DIR.parent / ".next"
    if next_dir.exists():
        try:
            shutil.rmtree(next_dir)
            print("  ✅ .next cache removed")
        except Exception as e:
            print(f"  ⚠️ {e}")

    print("\n" + "=" * 70)
    print("✅ Vazirmatn Font & Multi-language System Setup Complete!")
    print("=" * 70)
    print("\n🌍 What was done:")
    print("  1. Installed 'next-intl' package.")
    print("  2. Configured Vazirmatn (for FA/AR) and Inter (for EN) via next/font.")
    print("  3. Set up dynamic RTL/LTR direction based on locale.")
    print("  4. Created translation files: messages/fa.json, en.json, ar.json.")
    print("  5. Added middleware for automatic locale detection and routing.")
    print("  6. Updated Tailwind config to use CSS font variables.")
    print("\n🚀 Next steps:")
    print("  1. Restart frontend:")
    print("     cd apps\\web")
    print("     pnpm run dev -- -p 3001")
    print("")
    print("  2. Test the locales:")
    print("     • Persian (Default): http://localhost:3001")
    print("     • English:           http://localhost:3001/en")
    print("     • Arabic:            http://localhost:3001/ar")
    print("")
    print("  3. To translate existing pages, use the 'useTranslations' hook:")
    print("     const t = useTranslations('namespace');")
    print("     <h1>{t('key')}</h1>")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())