#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Homepage - Corrected Version
================================
این اسکریپت صفحه اصلی را با سینتکس صحیح می‌نویسد.
r"""

import shutil
from datetime import datetime
from pathlib import Path

FRONTEND_DIR = Path(r"D:\econojin.com\frontend")
BACKUP_DIR = FRONTEND_DIR.parent / ".homepage_fix_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")


def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def print_success(msg):
    print(f"✓ {msg}")


def print_error(msg):
    print(f"✗ {msg}")


def print_info(msg):
    print(f"ℹ {msg}")


def backup_file(path):
    if path.exists():
        rel = path.relative_to(FRONTEND_DIR.parent)
        backup_path = BACKUP_DIR / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)
        print_info(f"Backup: {backup_path.relative_to(FRONTEND_DIR.parent)}")


def fix_homepage():
    """ایجاد صفحه اصلی با سینتکس صحیح"""
    print_header("🏠 Fix Homepage (app/[locale]/page.tsx)")

    page_path = FRONTEND_DIR / "app" / "[locale]" / "page.tsx"

    if page_path.exists():
        backup_file(page_path)

    # ✅ نکته کلیدی: استفاده از رشته معمولی """...""" نه f"""..."""
    # زیرا JSX شامل {} است که با f-string تداخل دارد

    content = """'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { 
  Calculator, Globe, Award, TreePine, ArrowRight, 
  Shield, Zap, Leaf, Satellite, Cpu, CheckCircle, 
  Star, TrendingUp, Users, Sparkles, BookOpen,
  MessageSquare, FlaskConical, Bot, Video, Wallet
} from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function HomePage() {
  const params = useParams();
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);
  const [searchQuery, setSearchQuery] = useState('');

  const features = [
    { 
      icon: BookOpen, 
      title: dict?.library?.title || 'کتابخانه دیجیتال', 
      desc: 'کتاب، مقاله، پایان‌نامه', 
      href: `/${locale}/library`,
      color: 'green'
    },
    { 
      icon: MessageSquare, 
      title: dict?.halls?.title || 'تالارهای گفتگو', 
      desc: 'بحث و تبادل نظر', 
      href: `/${locale}/halls`,
      color: 'blue'
    },
    { 
      icon: FlaskConical, 
      title: dict?.desk?.title || 'میز تحقیق', 
      desc: 'همکاری تحقیقاتی', 
      href: `/${locale}/desk`,
      color: 'purple'
    },
    { 
      icon: Bot, 
      title: dict?.advisors?.title || 'مشاوران AI', 
      desc: 'مشاوره تخصصی', 
      href: `/${locale}/advisors`,
      color: 'pink'
    },
    { 
      icon: Video, 
      title: dict?.webinars?.title || 'وبینارها', 
      desc: 'کلاس‌های آنلاین', 
      href: `/${locale}/webinars`,
      color: 'orange'
    },
    { 
      icon: Wallet, 
      title: dict?.wallet?.title || 'کیف پول Eco', 
      desc: 'مدیریت توکن‌ها', 
      href: `/${locale}/wallet`,
      color: 'yellow'
    },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 via-white to-blue-50">
      {/* Hero Section */}
      <section className="pt-24 pb-16 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 px-4 py-2 rounded-full mb-6">
            <Shield className="w-4 h-4" />
            <span className="text-sm font-medium">CVE-2025-66478 Patched • Next.js 15.0.5</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 bg-clip-text text-transparent">
            {dict?.common?.appName || (isRTL ? 'اکونوژین' : 'Econojin')}
          </h1>

          <p className="text-2xl text-gray-700 dark:text-gray-200 mb-4">
            {dict?.common?.tagline || (isRTL ? 'پلتفرم علمی کربن' : 'Scientific Carbon Platform')}
          </p>

          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8 max-w-3xl mx-auto">
            {isRTL
              ? 'ترکیب مدل‌های علمی RothC و AquaCrop، تصاویر ماهواره‌ای Sentinel-2 و بلاکچین Polygon برای 
                  تبدیل تأثیر زیست‌محیطی شما به دارایی‌های دیجیتال قابل تأیید.'               : 'Combining RothC & AquaCrop scientific models,
                  Sentinel-2 satellite imagery,
                  and Polygon blockchain to turn your environmental impact into verifiable digital assets.'}          </p>

          {/* Search Bar */}
          <div className="relative max-w-2xl mx-auto mb-8">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={isRTL ? 'جستجو در منابع...' : 'Search resources...'}
              className="w-full px-6 py-4 text-lg rounded-xl border-2 border-gray-200 dark:border-gray-700 focus:border-green-500 focus:outline-none bg-white dark:bg-gray-800"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href={`/${locale}/calculate`}
              className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-green-600 
                  to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white px-8 py-4 rounded-xl 
                  text-lg font-semibold transition shadow-xl hover:shadow-2xl"             >
              <Calculator className="w-5 h-5" />
              {dict?.common?.calculator || (isRTL ? 'محاسبه کربن' : 'Calculate Carbon')}
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href={`/${locale}/dashboard`}
              className="inline-flex items-center justify-center gap-2 bg-white dark:bg-gray-800 
                  hover:bg-gray-50 dark:hover:bg-gray-700 text-gray-900 dark:text-white px-8 py-4 rounded-xl 
                  text-lg font-semibold border-2 border-gray-200 dark:border-gray-700 transition"             >
              {dict?.common?.dashboard || (isRTL ? 'داشبورد' : 'Dashboard')}
            </Link>
          </div>

          {/* Trust Badges */}
          <div className="flex flex-wrap justify-center gap-4 mt-8 text-sm text-gray-500">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>IPCC 2019 Compliant</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>ESA Sentinel-2</span>
            </div>
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600" />
              <span>Polygon Blockchain</span>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Bar */}
      <section className="py-12 px-4 bg-white dark:bg-gray-800">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: TreePine, value: '1M+', label: isRTL ? 'درخت' : 'Trees', color: 'green' },
            { icon: Leaf, value: '203t', label: 'CO₂', color: 'emerald' },
            { icon: Award, value: '20K+', label: 'SEED', color: 'yellow' },
            { icon: Globe, value: '20', label: isRTL ? 'زبان' : 'Languages', color: 'blue' },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="text-center p-6 rounded-2xl bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
                <Icon className={`w-10 h-10 mx-auto mb-3 text-${stat.color}-500`} />
                <div className="text-3xl font-bold mb-1">{stat.value}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Features Grid */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">
              {isRTL ? 'ویژگی‌های اصلی' : 'Core Features'}
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              {isRTL ? 'همه ابزارهایی که برای تحقیق علمی نیاز دارید' : 'All the tools you need for scientific 
                  research'}             </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <Link
                  key={i}
                  href={feature.href}
                  className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-md hover:shadow-xl transition group"
                >
                  <div className={`w-14 h-14 rounded-xl bg-${feature.color}-100 dark:bg-${feature.color}-900/30 flex items-center justify-center mb-4 group-hover:scale-110 transition`}>
                    <Icon className={`w-7 h-7 text-${feature.color}-600`} />
                  </div>
                  <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                  <p className="text-gray-600 dark:text-gray-400">{feature.desc}</p>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 px-4 bg-gradient-to-r from-green-600 to-emerald-700 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <Sparkles className="w-16 h-16 mx-auto mb-6" />
          <h2 className="text-4xl font-bold mb-4">
            {isRTL ? 'آماده شروع هستید؟' : 'Ready to Get Started?'}
          </h2>
          <p className="text-xl text-green-100 mb-8">
            {isRTL 
              ? 'به جامعه علمی جهانی بپیوندید و تأثیر خود را اندازه‌گیری کنید' 
              : 'Join the global scientific community and measure your impact'}
          </p>
          <Link
            href={`/${locale}/register`}
            className="inline-flex items-center gap-2 bg-white text-green-700 px-8 py-4 rounded-xl font-bold hover:bg-green-50 transition"
          >
            {isRTL ? 'ثبت‌نام رایگان' : 'Sign Up Free'}
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
"""

    # ✅ نکته: استفاده از write_text با رشته معمولی، نه f-string
    page_path.write_text(content, encoding="utf-8")

    print_success(f"Created/Fixed: {page_path.relative_to(FRONTEND_DIR)}")
    print_info("✅ 'use client' در خط اول")
    print_info("✅ JSX با رشته معمولی نوشته شده (نه f-string)")
    print_info("✅ useParams بدون React.use() - مستقیم استفاده شده")
    return True


def clean_cache():
    """پاکسازی cache"""
    print_header("🧹 Clean Cache")

    dirs = [
        FRONTEND_DIR / ".next",
        FRONTEND_DIR / "node_modules" / ".cache",
    ]

    for d in dirs:
        if d.exists():
            shutil.rmtree(d, ignore_errors=True)
            print_success(f"Cleaned: {d.relative_to(FRONTEND_DIR)}")

    return True


def main():
    print_header("🛠️ FIX HOMEPAGE - Corrected Syntax")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    fixes = [
        ("Homepage (page.tsx)", fix_homepage),
        ("Clean Cache", clean_cache),
    ]

    results = []
    for name, func in fixes:
        try:
            print(f"\n▶ {name}")
            success = func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Failed: {name}")
            print_error(f"Error: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Summary
    print_header("📊 SUMMARY")

    success_count = sum(1 for _, s in results if s)
    total = len(results)

    for name, success in results:
        if success:
            print_success(name)
        else:
            print_error(name)

    print(f"\nنتیجه: {success_count}/{total} موفق")

    if success_count == total:
        print_success("✅ تمام اصلاحات انجام شد!")
        print_info("\n📋 مراحل بعدی:")
        print("  1. Frontend را متوقف کنید (Ctrl+C)")
        print(f"  2. cd {FRONTEND_DIR}")
        print("  3. npm run dev")
        print("  4. مرورگر: http://localhost:3000/fa")
        print(f"\n💾 Backup: {BACKUP_DIR}")
    else:
        print_warning(f"{total - success_count} مورد نیاز به بررسی دارد")

    return 0 if success_count == total else 1


if __name__ == "__main__":
    try:
        import sys

        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\nمتوقف شد")
        import sys

        sys.exit(1)
    except Exception as e:
        print_error(f"خطا: {e}")
        import traceback

        traceback.print_exc()
        import sys

        sys.exit(1)
