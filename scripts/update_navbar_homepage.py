#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Update Navbar & Homepage - Fixed Version (No f-string issues)
==============================================================
r"""

import shutil
from datetime import datetime
from pathlib import Path

FRONTEND_DIR = Path(r"D:\econojin.com\frontend")
BACKUP_DIR = FRONTEND_DIR.parent / ".navbar_fix_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")


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


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print_success(f"Created: {path.relative_to(FRONTEND_DIR)}")


# ============================================================================
# FIX: Update Navbar - با رشته معمولی، نه f-string
# ============================================================================


def update_navbar():
    print_header("🧭 Update Navbar Component")

    navbar_path = FRONTEND_DIR / "components" / "Navbar.tsx"

    if navbar_path.exists():
        backup_file(navbar_path)

    # ✅ نکته کلیدی: استفاده از """...""" معمولی، نه f"""..."""
    # برای متغیرهای پایتون از .replace() استفاده می‌کنیم
    content = """'use client';

import { useState } from 'react';
import { useParams, usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Menu, X, Leaf, Droplets, FlaskConical, Sprout, 
  BarChart3, BookOpen, MessageSquare, Users, Bot, 
  Video, Wallet, Settings, User, LogOut, ChevronDown,
  Mountain, CloudRain, Wind, Sun, TreePine, Zap
} from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';
import { useAuth } from './providers/AuthProvider';

const ECONOJIN_MODULES = [
  { id: 'dashboard', name: { fa: 'داشبورد', en: 'Dashboard' }, path: '/dashboard', icon: BarChart3, color: 'green' },
  { id: 'hydrology', name: { fa: 'هیدرولوژی', en: 'Hydrology' }, path: '/hydrology', icon: Droplets, color: 'blue' },
  { id: 'soil-water',
      name: { fa: 'آب در خاک',
      en: 'Soil Water' },
      path: '/soil-water',
      icon: CloudRain,
      color: 'cyan' },
        { id: 'crop', name: { fa: 'رشد محصول', en: 'Crop Growth' }, path: '/crop', icon: Sprout, color: 'emerald' },
  { id: 'carbon', name: { fa: 'کربن خاک', en: 'Soil Carbon' }, path: '/carbon', icon: Leaf, color: 'lime' },
  { id: 'erosion', name: { fa: 'فرسایش', en: 'Erosion' }, path: '/erosion', icon: Mountain, color: 'orange' },
  { id: 'library', name: { fa: 'کتابخانه', en: 'Library' }, path: '/library', icon: BookOpen, color: 'purple' },
];

const USER_MODULES = [
  { id: 'halls', name: { fa: 'تالارها', en: 'Halls' }, path: '/halls', icon: MessageSquare },
  { id: 'advisors', name: { fa: 'مشاوران', en: 'Advisors' }, path: '/advisors', icon: Bot },
  { id: 'webinars', name: { fa: 'وبینارها', en: 'Webinars' }, path: '/webinars', icon: Video },
  { id: 'wallet', name: { fa: 'کیف پول', en: 'Wallet' }, path: '/wallet', icon: Wallet },
];

export default function Navbar({ locale }: { locale: Locale }) {
  const [isOpen, setIsOpen] = useState(false);
  const [showModules, setShowModules] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const pathname = usePathname();
  const router = useRouter();
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);
  const { user, logout } = useAuth();

  const isActive = (path: string) => pathname?.startsWith(path);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo */}
          <Link href={`/${locale}`} className="flex items-center gap-2">
            <Leaf className="w-8 h-8 text-green-600" />
            <span className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              Econojin
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            <div className="relative">
              <button
                onClick={() => setShowModules(!showModules)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                  isActive('/dashboard') || isActive('/hydrology') || isActive('/crop')
                    ? 'bg-green-100 text-green-700'
                    : 'hover:bg-gray-100'
                }`}
              >
                <FlaskConical className="w-4 h-4" />
                <span className="text-sm font-medium">{dict?.common?.modules || 'ماژول‌ها'}</span>
                <ChevronDown className={`w-4 h-4 transition ${showModules ? 'rotate-180' : ''}`} />
              </button>
              
              {showModules && (
                <div className="absolute right-0 top-full mt-2 w-72 bg-white rounded-xl shadow-xl border overflow-hidden">
                  <div className="p-3 grid grid-cols-2 gap-2">
                    {ECONOJIN_MODULES.map((module) => {
                      const Icon = module.icon;
                      return (
                        <Link
                          key={module.id}
                          href={`/${locale}${module.path}`}
                          onClick={() => setShowModules(false)}
                          className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50"
                        >
                          <div className={`w-10 h-10 rounded-lg bg-${module.color}-100 flex items-center justify-center`}>
                            <Icon className={`w-5 h-5 text-${module.color}-600`} />
                          </div>
                          <div className="text-right">
                            <div className="font-medium text-sm">{module.name[isRTL ? 'fa' : 'en']}</div>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {USER_MODULES.map((module) => {
              const Icon = module.icon;
              return (
                <Link
                  key={module.id}
                  href={`/${locale}${module.path}`}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                    isActive(module.path) ? 'bg-green-100' : 'hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{module.name[isRTL ? 'fa' : 'en']}</span>
                </Link>
              );
            })}
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-2">
            <select
              value={locale}
              onChange={(e) => router.push(`/${e.target.value}${pathname?.replace(`/${locale}`, '') || ''}`)}
              className="px-3 py-2 text-sm border rounded-lg bg-white"
            >
              <option value="fa">فارسی</option>
              <option value="en">English</option>
              <option value="ar">العربية</option>
            </select>

            {user ? (
              <button onClick={logout} className="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg">
                خروج
              </button>
            ) : (
              <div className="flex items-center gap-2">
                <Link href={`/${locale}/login`} className="px-4 py-2 text-sm hover:bg-gray-100 rounded-lg">ورود</Link>
                <Link href={`/${locale}/register`} className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg">ثبت‌نام</Link>
              </div>
            )}

            <button onClick={() => setIsOpen(!isOpen)} className="md:hidden p-2">
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 border-t">
            <div className="space-y-2">
              {ECONOJIN_MODULES.map((module) => (
                <Link
                  key={module.id}
                  href={`/${locale}${module.path}`}
                  onClick={() => setIsOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100"
                >
                  <module.icon className="w-5 h-5" />
                  <span>{module.name[isRTL ? 'fa' : 'en']}</span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
"""

    write_file(navbar_path, content)
    return True


# ============================================================================
# FIX: Update Homepage - با رشته معمولی
# ============================================================================


def update_homepage():
    print_header("🏠 Update Homepage")

    page_path = FRONTEND_DIR / "app" / "[locale]" / "page.tsx"

    if page_path.exists():
        backup_file(page_path)

    # ✅ رشته معمولی، نه f-string
    content = """'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { 
  Calculator, Globe, Award, TreePine, ArrowRight, 
  Shield, Zap, Leaf, Satellite, Cpu, CheckCircle, 
  Star, TrendingUp, Users, Sparkles, BookOpen,
  MessageSquare, FlaskConical, Bot, Video, Wallet,
  Droplets, CloudRain, Sprout, Mountain, BarChart3
} from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const SCIENTIFIC_MODULES = [
  { id: 'hydrology',
      icon: Droplets,
      title: { fa: 'هیدرولوژی',
      en: 'Hydrology' },
      desc: { fa: 'شبیه‌سازی رواناب',
      en: 'Runoff simulation' },
      href: '/hydrology',
      color: 'blue' },
        { id: 'soil-water',
      icon: CloudRain,
      title: { fa: 'آب در خاک',
      en: 'Soil Water' },
      desc: { fa: 'مدل‌سازی رطوبت',
      en: 'Moisture modeling' },
      href: '/soil-water',
      color: 'cyan' },
        { id: 'crop',
      icon: Sprout,
      title: { fa: 'رشد محصول',
      en: 'Crop Growth' },
      desc: { fa: 'شبیه‌سازی عملکرد',
      en: 'Yield simulation' },
      href: '/crop',
      color: 'emerald' },
        { id: 'carbon',
      icon: Leaf,
      title: { fa: 'کربن خاک',
      en: 'Soil Carbon' },
      desc: { fa: 'ترسیب کربن',
      en: 'Carbon sequestration' },
      href: '/carbon',
      color: 'lime' },
        { id: 'erosion',
      icon: Mountain,
      title: { fa: 'فرسایش',
      en: 'Erosion' },
      desc: { fa: 'برآورد فرسایش',
      en: 'Erosion estimation' },
      href: '/erosion',
      color: 'orange' },
        { id: 'dashboard',
      icon: BarChart3,
      title: { fa: 'داشبورد',
      en: 'Dashboard' },
      desc: { fa: 'نظارت لحظه‌ای',
      en: 'Real-time monitoring' },
      href: '/dashboard',
      color: 'purple' },
      ];

export default function HomePage() {
  const params = useParams();
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 via-white to-blue-50">
      
      {/* Hero */}
      <section className="pt-28 pb-16 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-green-100 px-4 py-2 rounded-full mb-6">
            <Shield className="w-4 h-4" />
            <span className="text-sm">CVE-2025-66478 Patched • Next.js 15.0.5</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
            {dict?.common?.appName || (isRTL ? 'اکونوژین' : 'Econojin')}
          </h1>

          <p className="text-2xl text-gray-700 mb-4">
            {dict?.common?.tagline || (isRTL ? 'پلتفرم علمی کربن' : 'Scientific Carbon Platform')}
          </p>

          <div className="relative max-w-2xl mx-auto mb-8">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={isRTL ? 'جستجو...' : 'Search...'}
              className="w-full px-6 py-4 text-lg rounded-xl border-2 focus:border-green-500 focus:outline-none bg-white"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href={`/${locale}/calculate`} className="inline-flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-4 rounded-xl font-semibold">
              <Calculator className="w-5 h-5" />
              {dict?.common?.calculator || (isRTL ? 'محاسبه' : 'Calculate')}
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href={`/${locale}/dashboard`} className="inline-flex items-center gap-2 bg-white px-8 py-4 rounded-xl font-semibold border-2">
              {dict?.common?.dashboard || (isRTL ? 'داشبورد' : 'Dashboard')}
            </Link>
          </div>

          <div className="flex flex-wrap justify-center gap-4 mt-8 text-sm text-gray-500">
            <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> IPCC Compliant</div>
            <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Sentinel-2</div>
            <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Polygon</div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 px-4 bg-white">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: TreePine, value: '1M+', label: isRTL ? 'درخت' : 'Trees' },
            { icon: Leaf, value: '203t', label: 'CO₂' },
            { icon: Award, value: '20K+', label: 'SEED' },
            { icon: Globe, value: '20', label: isRTL ? 'زبان' : 'Languages' },
          ].map((stat, i) => (
            <div key={i} className="text-center p-6 rounded-2xl bg-gray-50">
              <stat.icon className="w-10 h-10 mx-auto mb-3 text-green-500" />
              <div className="text-3xl font-bold">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Modules */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">{isRTL ? 'ماژول‌های علمی' : 'Scientific Modules'}</h2>
            <p className="text-gray-600">{isRTL ? 'همه متن‌باز و رایگان' : 'All open-source and free'}</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {SCIENTIFIC_MODULES.map((module, i) => {
              const Icon = module.icon;
              return (
                <Link key={module.id} href={`/${locale}${module.href}`} className="group bg-white rounded-2xl p-6 shadow hover:shadow-xl transition">
                  <div className={`w-14 h-14 rounded-xl bg-${module.color}-100 flex items-center justify-center mb-4`}>
                    <Icon className={`w-7 h-7 text-${module.color}-600`} />
                  </div>
                  <h3 className="text-xl font-bold mb-2">{module.title[isRTL ? 'fa' : 'en']}</h3>
                  <p className="text-gray-600 text-sm">{module.desc[isRTL ? 'fa' : 'en']}</p>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 bg-gradient-to-r from-green-600 to-emerald-700 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <Sparkles className="w-16 h-16 mx-auto mb-6" />
          <h2 className="text-4xl font-bold mb-4">{isRTL ? 'شروع کنید' : 'Get Started'}</h2>
          <Link href={`/${locale}/register`} className="inline-flex items-center gap-2 bg-white text-green-700 px-8 py-4 rounded-xl font-bold">
            {isRTL ? 'ثبت‌نام رایگان' : 'Sign Up Free'}
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
"""

    write_file(page_path, content)
    return True


# ============================================================================
# FIX: Create simple module pages
# ============================================================================


def create_module_pages():
    print_header("📄 Create Module Pages")

    modules = [
        "hydrology",
        "soil-water",
        "crop",
        "carbon",
        "erosion",
        "halls",
        "advisors",
        "webinars",
        "wallet",
    ]

    for module in modules:
        page_path = FRONTEND_DIR / "app" / "[locale]" / module / "page.tsx"

        if page_path.exists():
            print_info(f"Exists: {module}")
            continue

        # ✅ رشته معمولی + .replace() برای متغیرها
        content = """'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function Page() {
  const params = useParams();
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);
  
  const moduleNames: Record<string, {fa: string, en: string}> = {
    'hydrology': { fa: 'هیدرولوژی', en: 'Hydrology' },
    'soil-water': { fa: 'آب در خاک', en: 'Soil Water' },
    'crop': { fa: 'رشد محصول', en: 'Crop Growth' },
    'carbon': { fa: 'کربن خاک', en: 'Soil Carbon' },
    'erosion': { fa: 'فرسایش', en: 'Erosion' },
    'halls': { fa: 'تالارها', en: 'Halls' },
    'advisors': { fa: 'مشاوران', en: 'Advisors' },
    'webinars': { fa: 'وبینارها', en: 'Webinars' },
    'wallet': { fa: 'کیف پول', en: 'Wallet' },
  };
  
  const moduleName = moduleNames['MODULE_NAME'] || { fa: 'در حال توسعه', en: 'Under Development' };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white pt-24">
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-green-400 to-emerald-600 mb-6">
          <Loader2 className="w-10 h-10 text-white animate-spin" />
        </div>
        
        <h1 className="text-4xl font-bold mb-4">{moduleName[isRTL ? 'fa' : 'en']}</h1>
        <p className="text-lg text-gray-600 mb-8">
          {isRTL ? 'این ماژول در حال توسعه است.' : 'This module is under development.'}
        </p>
        
        <Link href={`/${locale}`} className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-xl">
          <ArrowLeft className="w-4 h-4" />
          {isRTL ? 'بازگشت به خانه' : 'Back to Home'}
        </Link>
      </div>
    </div>
  );
}
r"""
        # جایگزینی MODULE_NAME با نام ماژول فعلی
        content = content.replace("'MODULE_NAME'", f"'{module}'")

        page_path.parent.mkdir(parents=True, exist_ok=True)
        with open(page_path, "w", encoding="utf-8") as f:
            f.write(content)

        print_success(f"Created: app/[locale]/{module}/page.tsx")

    return True


# ============================================================================
# MAIN
# ============================================================================


def main():
    print_header("🔄 UPDATE NAVBAR & HOMEPAGE - FIXED")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    fixes = [
        ("Update Navbar", update_navbar),
        ("Update Homepage", update_homepage),
        ("Create Module Pages", create_module_pages),
    ]

    results = []
    for name, func in fixes:
        try:
            print(f"\n▶ {name}")
            success = func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Failed: {name} - {e}")
            results.append((name, False))

    print_header("📊 SUMMARY")

    for name, success in results:
        print(f"{'✓' if success else '✗'} {name}")

    if all(s for _, s in results):
        print_success("✅ بروزرسانی کامل شد!")
        print_info(f"\n💾 Backup: {BACKUP_DIR}")
        print_info("\n📋 اجرا کنید:")
        print(f"  cd {FRONTEND_DIR}")
        print("  npm run dev")
    else:
        print_error("برخی موارد نیاز به بررسی دارند")

    return 0


if __name__ == "__main__":
    import sys

    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⚠️  Interrupted")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
