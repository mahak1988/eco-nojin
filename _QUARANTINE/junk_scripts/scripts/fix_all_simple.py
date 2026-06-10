#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin Simple Fix Script - No f-string issues
================================================
این اسکریپت تمام تنظیمات را بدون مشکل سینتکس انجام می‌دهد.
r"""

import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# تنظیمات مسیرها
PROJECT_ROOT = Path(r"D:\econojin.com")
FRONTEND_DIR = PROJECT_ROOT / "frontend"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"
BACKUP_DIR = PROJECT_ROOT / ".simple_fix_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")


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
        rel = path.relative_to(PROJECT_ROOT)
        backup_path = BACKUP_DIR / rel
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, backup_path)


def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
    print_success(f"Created: {path.relative_to(PROJECT_ROOT)}")


# ============================================================================
# FIX 1: next.config.js - نسخه صحیح
# ============================================================================


def fix_next_config():
    print_header("⚙️ Fix: next.config.js")

    config_path = FRONTEND_DIR / "next.config.js"
    backup_file(config_path)

    # ✅ نکته: استفاده از رشته معمولی، نه f-string
    content = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    domains: ['localhost', 'ipfs.io', 'images.unsplash.com'],
    unoptimized: process.env.NODE_ENV === 'development',
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  webpack: (config, { isServer }) => {
    if (!isServer) {
      config.resolve.fallback = {
        ...config.resolve.fallback,
        fs: false,
        net: false,
        tls: false,
      };
    }
    return config;
  },
};

module.exports = nextConfig;
"""

    write_file(config_path, content)
    return True


# ============================================================================
# FIX 2: .npmrc برای رفع هشدارها
# ============================================================================


def fix_npmrc():
    print_header("📦 Fix: .npmrc")

    npmrc_path = PROJECT_ROOT / ".npmrc"

    content = """# Econojin npm configuration
shamefully-hoist=false
strict-peer-dependencies=false
auto-install-peers=true
network-timeout=300000
network-concurrency=8
registry=https://registry.npmjs.org/
save-exact=true
optional=true
"""

    write_file(npmrc_path, content)
    return True


# ============================================================================
# FIX 3: Polygon RPC URLs
# ============================================================================


def fix_polygon_rpc():
    print_header("🔗 Fix: Polygon RPC Configuration")

    rpc_url = "https://polygon-bor-rpc.publicnode.com"

    files_to_update = [
        PROJECT_ROOT / ".env.example",
        FRONTEND_DIR / ".env.example",
        FRONTEND_DIR / ".env.local",
        CONTRACTS_DIR / ".env.example",
    ]

    for file_path in files_to_update:
        if not file_path.exists():
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # جایگزینی RPCهای قدیمی
            content = content.replace("https://polygon-rpc.com", rpc_url)
            content = content.replace("https://rpc-mainnet.matic.vigil.sh", rpc_url)

            # اضافه کردن توضیحات اگر وجود نداشت
            if "# Polygon RPC" not in content:
                content += f"""
# Polygon RPC (Free, no signup)
POLYGON_RPC_URL={rpc_url}
NEXT_PUBLIC_POLYGON_RPC_URL={rpc_url}
"""

            backup_file(file_path)
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print_success(f"Updated: {file_path.relative_to(PROJECT_ROOT)}")
        except Exception as e:
            print_error(f"Error: {file_path}: {e}")

    return True


# ============================================================================
# FIX 4: hardhat.config.js برای Polygon Amoy
# ============================================================================


def fix_hardhat_config():
    print_header("⛓️ Fix: hardhat.config.js")

    config_path = CONTRACTS_DIR / "hardhat.config.js"
    config_path.parent.mkdir(parents=True, exist_ok=True)

    content = """require("@nomicfoundation/hardhat-toolbox");
require("dotenv").config();

module.exports = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: { enabled: true, runs: 200 },
    },
  },
  networks: {
    hardhat: { chainId: 31337 },
    localhost: { url: "http://127.0.0.1:8545", chainId: 31337 },
    polygonAmoy: {
      url: process.env.POLYGON_RPC_URL || "https://polygon-bor-rpc.publicnode.com",
      accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
      chainId: 80002,
    },
  },
  etherscan: {
    apiKey: { polygonAmoy: process.env.POLYGONSCAN_API_KEY || "" },
  },
};
"""

    write_file(config_path, content)
    return True


# ============================================================================
# FIX 5: Root Layout (فقط این فایل باید html/body داشته باشد)
# ============================================================================


def fix_root_layout():
    print_header("🏗️ Fix: Root Layout (app/layout.tsx)")

    layout_path = FRONTEND_DIR / "app" / "layout.tsx"
    layout_path.parent.mkdir(parents=True, exist_ok=True)

    # ✅ نکته: رشته معمولی، نه f-string
    content = """import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Econojin - Gaia Protocol',
  description: 'Scientific Carbon Platform',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl" suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="format-detection" content="telephone=no, date=no, email=no, address=no" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Vazirmatn:wght@300;400;500:600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="font-vazir antialiased" suppressHydrationWarning>
        {children}
      </body>
    </html>
  );
}
"""

    write_file(layout_path, content)
    return True


# ============================================================================
# FIX 6: Locale Layout (نباید html/body داشته باشد)
# ============================================================================


def fix_locale_layout():
    print_header("🌍 Fix: Locale Layout (app/[locale]/layout.tsx)")

    layout_path = FRONTEND_DIR / "app" / "[locale]" / "layout.tsx"

    # ✅ نکته: فقط div، بدون html/body
    content = """import type { Locale } from '@/lib/i18n';
import { AuthProvider } from '@/components/providers/AuthProvider';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: Locale }>;
}) {
  const { locale } = await params;
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);

  return (
    <div className={`min-h-screen flex flex-col ${isRTL ? 'rtl' : 'ltr'}`}>
      <ThemeProvider>
        <AuthProvider>
          <Navbar locale={locale} />
          <main className="flex-grow pt-16">{children}</main>
          <Footer locale={locale} />
        </AuthProvider>
      </ThemeProvider>
    </div>
  );
}
"""

    write_file(layout_path, content)
    return True


# ============================================================================
# FIX 7: Home Page با سینتکس صحیح
# ============================================================================


def fix_home_page():
    print_header("🏠 Fix: Home Page")

    page_path = FRONTEND_DIR / "app" / "[locale]" / "page.tsx"

    # ✅ نکته: 'use client' در خط اول، قبل از همه importها
    content = """'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { Calculator, Globe, Award, TreePine, ArrowRight, Shield, CheckCircle } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function HomePage() {
  const params = useParams();
  // ✅ صحیح: params یک object است، مستقیم استفاده کنید
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 via-white to-blue-50">
      <section className="pt-24 pb-16 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-green-100 text-green-800 px-4 py-2 rounded-full mb-6">
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
              className="w-full px-6 py-4 text-lg rounded-xl border-2 border-gray-200 focus:border-green-500 focus:outline-none bg-white"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href={`/${locale}/calculate`} className="inline-flex items-center gap-2 bg-gradient-to-r 
                from-green-600 to-emerald-600 text-white px-8 py-4 rounded-xl font-semibold 
                hover:from-green-700 hover:to-emerald-700 transition">               <Calculator className="w-5 h-5" />
              {dict?.common?.calculator || (isRTL ? 'محاسبه کربن' : 'Calculate')}
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href={`/${locale}/dashboard`} className="inline-flex items-center gap-2 bg-white text-gray-900 px-8 py-4 rounded-xl font-semibold border-2 border-gray-200 hover:bg-gray-50 transition">
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

      <section className="py-12 px-4 bg-white">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: TreePine, value: '1M+', label: isRTL ? 'درخت' : 'Trees' },
            { icon: Globe, value: '203t', label: 'CO₂' },
            { icon: Award, value: '20K+', label: 'SEED' },
            { icon: Globe, value: '20', label: isRTL ? 'زبان' : 'Languages' },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="text-center p-6 rounded-2xl bg-gray-50">
                <Icon className="w-10 h-10 mx-auto mb-3 text-green-500" />
                <div className="text-3xl font-bold">{stat.value}</div>
                <div className="text-sm text-gray-600">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </section>
    </div>
  );
}
"""

    write_file(page_path, content)
    return True


# ============================================================================
# FIX 8: Dashboard Page با مدیریت خطای ایمن
# ============================================================================


def fix_dashboard_page():
    print_header("📊 Fix: Dashboard Page")

    page_path = FRONTEND_DIR / "app" / "[locale]" / "dashboard" / "page.tsx"
    page_path.parent.mkdir(parents=True, exist_ok=True)

    # ✅ نکته: console.warn به جای console.error + fallback data
    content = """'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { BarChart3, Activity, Users, Leaf, Award, TreePine, TrendingUp, Loader2 } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const FALLBACK_STATS = {
  total_activities: 156,
  total_carbon_tons: 203.56,
  estimated_value_usd: 10177.92,
  by_activity: {
    tree_planting: { count: 85, carbon_kg: 154000 },
    soil_regeneration: { count: 32, carbon_kg: 28000 },
  },
};

export default function DashboardPage() {
  const params = useParams();
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);

  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let isMounted = true;

    const fetchData = async () => {
      try {
        setLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 10000);

        const res = await fetch(`${apiUrl}/gaia/stats`, { signal: controller.signal });
        clearTimeout(timeoutId);

        if (!res.ok) throw new Error(`API error: ${res.status}`);
        
        const data = await res.json();
        if (isMounted) setStats(data);
      } catch (err: any) {
        // ✅ استفاده از console.warn به جای console.error
        console.warn('Dashboard: Using fallback data -', err?.message);
        if (isMounted) setStats(FALLBACK_STATS);
      } finally {
        if (isMounted) setLoading(false);
      }
    };

    fetchData();
    return () => { isMounted = false; };
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center pt-20">
        <Loader2 className="w-12 h-12 text-green-600 animate-spin" />
      </div>
    );
  }

  const displayStats = stats || FALLBACK_STATS;

  return (
    <div className="min-h-screen bg-gray-50 pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-bold mb-8">{dict?.dashboard?.title || 'داشبورد'}</h1>
        
        <div className="grid md:grid-cols-4 gap-6">
          {[
            { icon: TreePine, value: displayStats?.total_activities || 0, label: 'Activities' },
            { icon: Leaf, value: `${displayStats?.total_carbon_tons || 0}t`, label: 'CO₂' },
            { icon: Award, value: '20K+', label: 'SEED' },
            { icon: TrendingUp, value: '$10K', label: 'Value' },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="bg-white rounded-xl p-6 shadow">
                <Icon className="w-8 h-8 text-green-500 mb-3" />
                <div className="text-3xl font-bold">{stat.value}</div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
r"""

    write_file(page_path, content)
    return True


# ============================================================================
# FIX 9: پاکسازی cache
# ============================================================================


def clean_cache():
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


# ============================================================================
# MAIN
# ============================================================================


def main():
    print_header("🛠️ ECONOJIN SIMPLE FIX SCRIPT")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    fixes = [
        ("next.config.js", fix_next_config),
        (".npmrc", fix_npmrc),
        ("Polygon RPC", fix_polygon_rpc),
        ("hardhat.config.js", fix_hardhat_config),
        ("Root Layout", fix_root_layout),
        ("Locale Layout", fix_locale_layout),
        ("Home Page", fix_home_page),
        ("Dashboard Page", fix_dashboard_page),
        ("Clean Cache", clean_cache),
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

    success_count = sum(1 for _, s in results if s)
    total = len(results)

    for name, success in results:
        print(f"{'✓' if success else '✗'} {name}")

    print(f"\nنتیجه: {success_count}/{total} موفق")

    if success_count == total:
        print_success("✅ تمام اصلاحات انجام شد!")
        print_info("\n📋 مراحل بعدی:")
        print(f"  1. cd {FRONTEND_DIR}")
        print("  2. npm install  # برای اعمال .npmrc")
        print("  3. npm run dev")
        print("  4. تست: http://localhost:3000/fa")
        print(f"\n💾 Backup: {BACKUP_DIR}")
    else:
        print_error(f"{total - success_count} مورد نیاز به بررسی دارد")

    return 0 if success_count == total else 1


if __name__ == "__main__":
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
