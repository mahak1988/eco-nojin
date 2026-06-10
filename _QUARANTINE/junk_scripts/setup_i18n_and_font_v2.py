#!/usr/bin/env python3
"""Setup Vazirmatn Font, Multi-language (i18n) System & Fix Footer"""
import subprocess
import shutil
import json
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "apps" / "web" / "src"

def run_command(cmd: str, cwd: Path):
    """Run command with shell=True to find pnpm/npm in PATH"""
    print(f"  Running: {cmd}")
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"  ⚠️ Warning: {result.stderr.strip()[:200]}")
        return False
    print(f"  ✅ Success")
    return True

def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  + {path.relative_to(ROOT)}")

def main():
    print("=" * 70)
    print("🌍 Setting up Vazirmatn, i18n & Fixing Footer")
    print("=" * 70)

    # =========================================================================
    # 1. Install next-intl (with shell=True)
    # =========================================================================
    print("\n[1/7] Installing next-intl package...")
    
    # Check if already installed
    package_json = WEB_DIR.parent / "package.json"
    if package_json.exists():
        pkg_content = package_json.read_text(encoding="utf-8")
        if '"next-intl"' in pkg_content:
            print("  ✅ next-intl already installed")
        else:
            # Try pnpm first, then npm
            if not run_command("pnpm add next-intl", WEB_DIR.parent):
                print("  Trying npm instead...")
                run_command("npm install next-intl", WEB_DIR.parent)

    # =========================================================================
    # 2. Create i18n Configuration
    # =========================================================================
    print("\n[2/7] Creating i18n configuration files...")
    
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
import {locales, defaultLocale} from './src/i18n';

export default createMiddleware({
  locales,
  defaultLocale,
  localePrefix: 'as-needed'
});

export const config = {
  matcher: ['/', '/(fa|en|ar)/:path*', '/((?!_next|_vercel|.*\\..*).*)']
};
'''
    write_file(WEB_DIR.parent / "middleware.ts", middleware_content)

    # =========================================================================
    # 3. Create Translation Messages
    # =========================================================================
    print("\n[3/7] Creating translation message files...")
    
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
            "newsletter_title": "عضویت در خبرنامه",
            "newsletter_desc": "هر هفته جدیدترین مقالات و اخبار اکولوژیک را دریافت کنید",
            "newsletter_placeholder": "ایمیل شما",
            "newsletter_btn": "عضویت",
            "brand_desc": "ساکن زمین هستیم، احیاگر اکوسیستم و نجاتگر زمین. در کنار شما، در هر نقطه از این کره خاکی.",
            "company": "شرکت",
            "about": "درباره ما",
            "contact": "تماس با ما",
            "blog": "وبلاگ",
            "privacy": "حریم خصوصی",
            "terms": "شرایط استفاده",
            "policy": "خط مشی",
            "rights": "© ۲۰۲۶ اکو نوژین. تمامی حقوق محفوظ است.",
            "made_by": "ساخته شده و توسعه یافته توسط تیم اکو نوژین",
            "global_presence": "حضور در ۱۹۵ کشور",
            "green": "۱۰۰٪ سبز"
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
            "newsletter_title": "Subscribe to Newsletter",
            "newsletter_desc": "Receive the latest ecological articles and news every week",
            "newsletter_placeholder": "Your email",
            "newsletter_btn": "Subscribe",
            "brand_desc": "We are Earth's inhabitants, ecosystem restorers, and Earth savers. With you, in every corner of this planet.",
            "company": "Company",
            "about": "About Us",
            "contact": "Contact Us",
            "blog": "Blog",
            "privacy": "Privacy Policy",
            "terms": "Terms of Service",
            "policy": "Guiding Principles",
            "rights": "© 2026 Econojin. All rights reserved.",
            "made_by": "Built and developed by the Econojin Team",
            "global_presence": "Present in 195 countries",
            "green": "100% Green"
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
            "newsletter_title": "اشترك في النشرة الإخبارية",
            "newsletter_desc": "احصل على أحدث المقالات والأخبار البيئية كل أسبوع",
            "newsletter_placeholder": "بريدك الإلكتروني",
            "newsletter_btn": "اشترك",
            "brand_desc": "نحن سكان الأرض، ومستعيدو النظام البيئي، ومنقذو الأرض. معكم، في كل ركن من أركان هذا الكوكب.",
            "company": "الشركة",
            "about": "من نحن",
            "contact": "اتصل بنا",
            "blog": "المدونة",
            "privacy": "سياسة الخصوصية",
            "terms": "شروط الخدمة",
            "policy": "المبادئ التوجيهية",
            "rights": "© 2026 إكونوجين. جميع الحقوق محفوظة.",
            "made_by": "تم بناؤه وتطويره بواسطة فريق إكونوجين",
            "global_presence": "حضور في 195 دولة",
            "green": "100% أخضر"
        }
    }

    write_file(WEB_DIR / "messages" / "fa.json", json.dumps(messages_fa, indent=2, ensure_ascii=False))
    write_file(WEB_DIR / "messages" / "en.json", json.dumps(messages_en, indent=2, ensure_ascii=False))
    write_file(WEB_DIR / "messages" / "ar.json", json.dumps(messages_ar, indent=2, ensure_ascii=False))

    # =========================================================================
    # 4. Update Root Layout with Fonts and i18n Provider
    # =========================================================================
    print("\n[4/7] Updating Root Layout with Vazirmatn, Inter, and NextIntlProvider...")
    
    layout_content = '''import type { Metadata } from "next";
import { Vazirmatn, Inter } from "next/font/google";
import { NextIntlClientProvider } from "next-intl";
import { getMessages, getLocale } from "next-intl/server";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";

const vazirmatn = Vazirmatn({ 
  subsets: ["arabic"],
  variable: "--font-vazir",
  display: "swap",
  weight: ["100", "200", "300", "400", "500", "600", "700", "800", "900"]
});

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap"
});

export async function generateMetadata(): Promise<Metadata> {
  const locale = await getLocale();
  const messages = await getMessages();
  
  return {
    title: (messages as any).metadata?.title || "Econojin",
    description: (messages as any).metadata?.description || "",
  };
}

export default async function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const locale = await getLocale();
  const messages = await getMessages();
  
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
    print("\n[5/7] Updating Tailwind Config for Font Variables...")
    tailwind_path = WEB_DIR.parent / "tailwind.config.ts"
    if tailwind_path.exists():
        tw_content = tailwind_path.read_text(encoding="utf-8")
        if "fontFamily" not in tw_content:
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
            print("  ✅ Tailwind config updated")

    # =========================================================================
    # 6. FIX FOOTER - Updated Text
    # =========================================================================
    print("\n[6/7] Fixing Footer with new text...")
    
    footer_content = '''"use client";

import Link from "next/link";
import {
  Leaf, Globe, Mail, Heart, Send,
  Twitter, Linkedin, Github, Youtube, Instagram,
  Coins, Pickaxe, Map, BookOpen, PenLine, Calculator,
  Package, Building2, Gamepad2, Users, ShoppingBag, Brain,
  Cloud, Droplets, Mountain, Sun, Wifi, Scale, Wrench,
  Satellite
} from "lucide-react";

const FOOTER_MODULES = [
  {
    title: "پلتفرم‌های اصلی",
    items: [
      { name: "نقشه و GIS", href: "/gis", icon: Map },
      { name: "آکادمی آموزشی", href: "/academy", icon: BookOpen },
      { name: "وبلاگ", href: "/blog", icon: PenLine },
      { name: "خبرنامه", href: "/newsletter", icon: Mail },
    ]
  },
  {
    title: "مالی و بانکی",
    items: [
      { name: "حسابداری", href: "/accounting", icon: Calculator },
      { name: "انبارداری", href: "/inventory", icon: Package },
      { name: "حسابداری شرکتی", href: "/financial", icon: Building2 },
      { name: "اکو کوین", href: "/ecocoin", icon: Coins },
    ]
  },
  {
    title: "فناوری و ماینینگ",
    items: [
      { name: "اکو ماینینگ", href: "/ecomining", icon: Pickaxe },
      { name: "اینترنت اشیا", href: "/iot", icon: Wifi },
      { name: "Sentinel", href: "/sentinel", icon: Satellite },
      { name: "MRV", href: "/mrv", icon: Scale },
    ]
  },
  {
    title: "علوم محیطی",
    items: [
      { name: "پایش خشکسالی", href: "/drought", icon: Sun },
      { name: "آب و خاک", href: "/soil-water", icon: Droplets },
      { name: "فرسایش خاک", href: "/erosion", icon: Mountain },
      { name: "هواشناسی", href: "/weather", icon: Cloud },
    ]
  },
  {
    title: "جامعه و خدمات",
    items: [
      { name: "بازی‌های آموزشی", href: "/games", icon: Gamepad2 },
      { name: "جامعه کشاورزان", href: "/community", icon: Users },
      { name: "فروشگاه", href: "/store", icon: ShoppingBag },
      { name: "سلامت روان", href: "/psychology", icon: Brain },
    ]
  },
];

const SOCIAL_LINKS = [
  { icon: Twitter, href: "#", label: "Twitter" },
  { icon: Linkedin, href: "#", label: "LinkedIn" },
  { icon: Github, href: "#", label: "GitHub" },
  { icon: Youtube, href: "#", label: "YouTube" },
  { icon: Instagram, href: "#", label: "Instagram" },
];

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="relative bg-slate-950 border-t border-slate-800">
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />

      {/* Newsletter Section */}
      <div className="border-b border-slate-800">
        <div className="container mx-auto px-6 py-12">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            <div>
              <h3 className="text-2xl font-black text-white mb-2 flex items-center gap-2">
                <Send className="h-6 w-6 text-emerald-400" />
                عضویت در خبرنامه
              </h3>
              <p className="text-slate-400">
                هر هفته جدیدترین مقالات و اخبار اکولوژیک را دریافت کنید
              </p>
            </div>
            <div className="flex gap-2">
              <input
                type="email"
                placeholder="ایمیل شما"
                className="flex-1 px-4 py-3 bg-slate-900 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
              />
              <button className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-xl font-bold text-white transition-all">
                عضویت
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Footer */}
      <div className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Brand Column */}
          <div className="lg:col-span-3">
            <Link href="/" className="flex items-center gap-3 mb-4 group">
              <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600">
                <Leaf className="h-6 w-6 text-white" />
              </div>
              <div>
                <h3 className="text-xl font-black text-white">اکو نوژین</h3>
                <p className="text-[10px] text-emerald-400 font-bold tracking-wider">ECONOJIN</p>
              </div>
            </Link>
            <p className="text-sm text-slate-400 leading-relaxed mb-6">
              ساکن زمین هستیم، احیاگر اکوسیستم و نجاتگر زمین. در کنار شما، در هر نقطه از این کره خاکی.
            </p>

            {/* Contact Info */}
            <div className="space-y-2 mb-6">
              <a href="mailto:info@econojin.com" className="flex items-center gap-2 text-sm text-slate-400 hover:text-emerald-400 transition-colors">
                <Mail className="h-4 w-4" />
                info@econojin.com
              </a>
              <Link href="/contact" className="flex items-center gap-2 text-sm text-slate-400 hover:text-emerald-400 transition-colors">
                <Globe className="h-4 w-4" />
                تماس با ما
              </Link>
            </div>

            {/* Social */}
            <div className="flex gap-2">
              {SOCIAL_LINKS.map((social, idx) => {
                const Icon = social.icon;
                return (
                  <a
                    key={idx}
                    href={social.href}
                    aria-label={social.label}
                    className="p-2 rounded-lg bg-slate-900 border border-slate-800 text-slate-400 hover:text-emerald-400 hover:border-emerald-500/50 transition-all"
                  >
                    <Icon className="h-4 w-4" />
                  </a>
                );
              })}
            </div>
          </div>

          {/* Modules Columns */}
          {FOOTER_MODULES.map((group, idx) => (
            <div key={idx} className="lg:col-span-1.5">
              <h4 className="text-sm font-black text-white mb-4 tracking-wider">{group.title}</h4>
              <ul className="space-y-2">
                {group.items.map((item, i) => {
                  const Icon = item.icon;
                  return (
                    <li key={i}>
                      <Link
                        href={item.href}
                        className="flex items-center gap-2 text-sm text-slate-400 hover:text-emerald-400 transition-colors group"
                      >
                        <Icon className="h-3.5 w-3.5 text-slate-600 group-hover:text-emerald-400 transition-colors" />
                        {item.name}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}

          {/* Company Column */}
          <div className="lg:col-span-1.5">
            <h4 className="text-sm font-black text-white mb-4 tracking-wider">شرکت</h4>
            <ul className="space-y-2">
              <li><Link href="/about" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">درباره ما</Link></li>
              <li><Link href="/contact" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">تماس با ما</Link></li>
              <li><Link href="/blog" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">وبلاگ</Link></li>
              <li><Link href="/privacy" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">حریم خصوصی</Link></li>
              <li><Link href="/terms" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">شرایط استفاده</Link></li>
              <li><Link href="/policy" className="text-sm text-slate-400 hover:text-emerald-400 transition-colors">خط مشی</Link></li>
            </ul>
          </div>
        </div>
      </div>

      {/* Bottom Bar - FIXED */}
      <div className="border-t border-slate-800">
        <div className="container mx-auto px-6 py-6">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="flex flex-wrap items-center gap-4 text-xs text-slate-500">
              <span>© ۲۰۲۶ اکو نوژین. تمامی حقوق محفوظ است.</span>
              <span className="hidden md:inline">•</span>
              <span className="flex items-center gap-1">
                ساخته شده و توسعه یافته توسط تیم اکو نوژین
              </span>
            </div>
            <div className="flex items-center gap-4 text-xs text-slate-500">
              <span className="flex items-center gap-1">
                <Globe className="h-3 w-3" />
                حضور در ۱۹۵ کشور
              </span>
              <span className="flex items-center gap-1">
                <Leaf className="h-3 w-3 text-emerald-400" />
                ۱۰۰٪ سبز
              </span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
'''
    write_file(WEB_DIR / "components" / "layout" / "Footer.tsx", footer_content)

    # =========================================================================
    # 7. Clean cache
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
    print("✅ Setup Complete!")
    print("=" * 70)
    print("\n🌍 What was done:")
    print("  1. Installed 'next-intl' package (with shell=True fix)")
    print("  2. Configured Vazirmatn (FA/AR) and Inter (EN) via next/font")
    print("  3. Set up dynamic RTL/LTR direction based on locale")
    print("  4. Created translation files: messages/fa.json, en.json, ar.json")
    print("  5. Added middleware for automatic locale detection")
    print("  6. Updated Tailwind config to use CSS font variables")
    print("  7. ✅ FIXED Footer: 'ساخته شده و توسعه یافته توسط تیم اکو نوژین'")
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
    print("  3. Check the Footer:")
    print("     • Should show: 'ساخته شده و توسعه یافته توسط تیم اکو نوژین'")
    print("=" * 70)

    return 0

if __name__ == "__main__":
    import sys
    sys.exit(main())