#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin Final Fix Script - رفع تمام خطاها
==========================================
این اسکریپت تمام خطاهای باقی‌مانده را به صورت خودکار اصلاح می‌کند:

1. ✅ next.config.js - حذف گزینه‌های نامعتبر
2. ✅ 'use client' directive - اصلاح موقعیت در تمام صفحات
3. ✅ AuthProvider wrapper - اصلاح layout
4. ✅ Polygon RPC - جایگزینی با RPC معتبر
5. ✅ بررسی تمام صفحات برای مشکلات مشابه
r"""

import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# ============================================================================
# CONFIGURATION
# ============================================================================


class Colors:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    END = "\033[0m"


PROJECT_ROOT = Path(r"D:\econojin.com")
FRONTEND_DIR = PROJECT_ROOT / "frontend"
BACKEND_DIR = PROJECT_ROOT / "backend"
BACKUP_DIR = PROJECT_ROOT / ".final_fix_backup" / datetime.now().strftime("%Y%m%d_%H%M%S")


def print_header(title: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{title:^70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}\n")


def print_success(msg: str):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")


def print_warning(msg: str):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")


def print_error(msg: str):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")


def print_info(msg: str):
    print(f"{Colors.BLUE}ℹ {msg}{Colors.END}")


def backup_file(path: Path):
    """ایجاد backup از فایل"""
    if not path.exists():
        return
    rel = path.relative_to(PROJECT_ROOT)
    backup_path = BACKUP_DIR / rel
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(path, backup_path)


# ============================================================================
# FIX 1: NEXT.CONFIG.JS - نسخه صحیح برای Next.js 15
# ============================================================================


def fix_next_config():
    """اصلاح next.config.js - حذف گزینه‌های نامعتبر"""
    print_header("⚙️  Fix 1: next.config.js (Next.js 15 Compatible)")

    config_path = FRONTEND_DIR / "next.config.js"
    if not config_path.exists():
        print_error("next.config.js not found")
        return False

    backup_file(config_path)

    # نسخه صحیح - بدون i18n (چون از middleware استفاده می‌کنیم)
    # App Router در Next.js 15 از i18n config پشتیبانی نمی‌کند
    new_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  
  // Image optimization
  images: {
    domains: ['localhost', 'ipfs.io', 'images.unsplash.com'],
    unoptimized: process.env.NODE_ENV === 'development',
  },
  
  // توجه: i18n config برای Pages Router است
  // برای App Router از middleware.ts استفاده می‌کنیم
  
  // API rewrites to backend
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
    ];
  },
  
  // Webpack customization
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

    config_path.write_text(new_config, encoding="utf-8")
    print_success("next.config.js بازنویسی شد")
    print_info("حذف شد: swcMinify, i18n, experimental.serverActions")
    print_info("دلیل: i18n در App Router پشتیبانی نمی‌شود (از middleware استفاده می‌کنیم)")
    return True


# ============================================================================
# FIX 2: 'use client' DIRECTIVE - اصلاح در تمام فایل‌ها
# ============================================================================


def fix_use_client_directive():
    """اصلاح موقعیت 'use client' در تمام فایل‌های page.tsx"""
    print_header("📝 Fix 2: 'use client' Directive Position")

    # پیدا کردن تمام فایل‌های tsx
    patterns = [
        "app/**/page.tsx",
        "app/**/layout.tsx",
        "components/**/*.tsx",
    ]

    fixed_count = 0
    error_count = 0

    for pattern in patterns:
        for file_path in FRONTEND_DIR.glob(pattern):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                original = content

                # بررسی آیا فایل 'use client' دارد
                if "'use client'" not in content and '"use client"' not in content:
                    continue

                lines = content.split("\n")

                # پیدا کردن index خط 'use client'
                use_client_idx = None
                for i, line in enumerate(lines):
                    if "'use client'" in line or '"use client"' in line:
                        use_client_idx = i
                        break

                if use_client_idx is None or use_client_idx == 0:
                    continue  # درست است یا وجود ندارد

                # بررسی آیا قبل از 'use client' کد غیر از comment/whitespace وجود دارد
                has_code_before = False
                for i in range(use_client_idx):
                    line = lines[i].strip()
                    if line and not line.startswith("//") and not line.startswith("/*"):
                        has_code_before = True
                        break

                if not has_code_before:
                    continue

                # استخراج 'use client' line
                use_client_line = lines[use_client_idx]

                # حذف از موقعیت فعلی
                lines.pop(use_client_idx)

                # اضافه کردن به ابتدای فایل
                lines.insert(0, use_client_line)

                # نوشتن
                new_content = "\n".join(lines)
                if new_content != original:
                    backup_file(file_path)
                    file_path.write_text(new_content, encoding="utf-8")
                    rel_path = file_path.relative_to(FRONTEND_DIR)
                    print_success(f"Fixed: {rel_path}")
                    fixed_count += 1

            except Exception as e:
                print_error(f"Error in {file_path}: {e}")
                error_count += 1

    print_info(f"تعداد فایل‌های اصلاح شده: {fixed_count}")
    if error_count > 0:
        print_warning(f"تعداد خطاها: {error_count}")

    return fixed_count > 0 or error_count == 0


# ============================================================================
# FIX 3: LAYOUT.TSX - اضافه کردن AuthProvider
# ============================================================================


def fix_layout_with_auth_provider():
    """اصلاح layout.tsx با AuthProvider wrapper"""
    print_header("🔐 Fix 3: Layout with AuthProvider")

    layout_path = FRONTEND_DIR / "app" / "[locale]" / "layout.tsx"
    if not layout_path.exists():
        print_error("layout.tsx not found")
        return False

    backup_file(layout_path)

    # نسخه صحیح با AuthProvider
    new_layout = """import '../globals.css';
import type { Metadata } from 'next';
import { locales, type Locale, getDirection } from '@/lib/i18n';
import { AuthProvider } from '@/components/providers/AuthProvider';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'Econojin - Gaia Protocol Carbon Platform',
  description: 'Scientific Carbon Platform powered by Gaia Protocol',
  keywords: ['carbon', 'climate', 'blockchain', 'satellite', 'NDVI', 'Gaia Protocol'],
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default async function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: Promise<{ locale: Locale }>;
}) {
  const { locale } = await params;
  const direction = getDirection(locale);
  const isRTL = direction === 'rtl';

  return (
    <html lang={locale} dir={direction} suppressHydrationWarning>
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="format-detection" content="telephone=no, date=no, email=no, address=no" />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Vazirmatn:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet"
        />
      </head>
      <body
        className={`${isRTL ? 'font-vazir' : 'font-inter'} antialiased`}
        suppressHydrationWarning
      >
        <ThemeProvider>
          <AuthProvider>
            <div className="flex flex-col min-h-screen">
              <Navbar locale={locale} />
              <main className="flex-grow pt-16">{children}</main>
              <Footer locale={locale} />
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
"""

    layout_path.write_text(new_layout, encoding="utf-8")
    print_success("layout.tsx با AuthProvider بازنویسی شد")
    print_info("اضافه شد: suppressHydrationWarning برای html و body")
    print_info("اضافه شد: meta format-detection برای iOS")
    return True


# ============================================================================
# FIX 4: POLYGON RPC - جایگزینی با RPC معتبر
# ============================================================================


def fix_polygon_rpc():
    """جایگزینی polygon-rpc.com با RPC معتبر"""
    print_header("🔗 Fix 4: Polygon RPC Configuration")

    print_warning("polygon-rpc.com نیاز به sign-in دارد (از تاریخ 2026)")
    print_info("جایگزین‌های رایگان پیشنهادی:")
    print_info("  1. PublicNode: https://polygon-bor-rpc.publicnode.com (رایگان، بدون ثبت‌نام)")
    print_info("  2. Ankr: https://rpc.ankr.com/polygon (رایگان با محدودیت)")
    print_info("  3. Alchemy: https://www.alchemy.com/ (نیاز به ثبت‌نام)")

    # RPC پیشنهادی (رایگان و بدون ثبت‌نام)
    recommended_rpc = "https://polygon-bor-rpc.publicnode.com"
    fallback_rpc = "https://rpc.ankr.com/polygon"

    # فایل‌هایی که باید به‌روزرسانی شوند
    files_to_update = [
        FRONTEND_DIR / ".env.local",
        FRONTEND_DIR / ".env.example",
        BACKEND_DIR / ".env",
        BACKEND_DIR / ".env.example",
        PROJECT_ROOT / ".env",
        PROJECT_ROOT / ".env.example",
    ]

    updated_count = 0

    for file_path in files_to_update:
        if not file_path.exists():
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original = content

            # جایگزینی polygon-rpc.com
            content = re.sub(r"https?://polygon-rpc\.com", recommended_rpc, content)

            # جایگزینی سایر RPC های مشکل‌دار
            content = re.sub(r"https?://rpc-mainnet\.matic\.vigil\.sh", recommended_rpc, content)

            if content != original:
                backup_file(file_path)
                file_path.write_text(content, encoding="utf-8")
                rel_path = file_path.relative_to(PROJECT_ROOT)
                print_success(f"Updated: {rel_path}")
                updated_count += 1

        except Exception as e:
            print_error(f"Error updating {file_path}: {e}")

    # بررسی backend config
    backend_config = BACKEND_DIR / "api" / "config.py"
    if backend_config.exists():
        try:
            with open(backend_config, "r", encoding="utf-8") as f:
                content = f.read()

            original = content

            # جایگزینی RPC URL در backend
            content = re.sub(
                r'POLYGON_RPC_URL\s*=\s*os\.getenv\([^,]+,\s*["\']https?://polygon-rpc\.com["\']',
                f'POLYGON_RPC_URL = os.getenv("POLYGON_RPC_URL", "{recommended_rpc}")',
                content,
            )

            # اگر وجود نداشت، اضافه کردن
            if "POLYGON_RPC_URL" not in content:
                content += f'\n# Polygon RPC\nPOLYGON_RPC_URL = os.getenv("POLYGON_RPC_URL", "{recommended_rpc}")\n'

            if content != original:
                backup_file(backend_config)
                backend_config.write_text(content, encoding="utf-8")
                print_success("backend/api/config.py به‌روزرسانی شد")

        except Exception as e:
            print_error(f"Error updating backend config: {e}")

    print_success(f"تعداد فایل‌های به‌روزرسانی شده: {updated_count}")
    print_info(f"RPC جدید: {recommended_rpc}")
    return True


# ============================================================================
# FIX 5: بررسی و اصلاح تمام صفحات
# ============================================================================


def audit_all_pages():
    """بررسی تمام صفحات برای مشکلات مشابه"""
    print_header("🔍 Fix 5: Audit All Pages")

    patterns = [
        "app/**/page.tsx",
        "app/**/layout.tsx",
    ]

    issues_found = []

    for pattern in patterns:
        for file_path in FRONTEND_DIR.glob(pattern):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()

                rel_path = str(file_path.relative_to(FRONTEND_DIR))

                # بررسی مشکلات رایج

                # 1. useParams بدون 'use client'
                if (
                    "useParams" in content
                    and "'use client'" not in content
                    and '"use client"' not in content
                ):
                    issues_found.append((rel_path, "useParams needs 'use client' directive"))

                # 2. useState/useEffect بدون 'use client'
                if (
                    ("useState" in content or "useEffect" in content)
                    and "'use client'" not in content
                    and '"use client"' not in content
                ):
                    issues_found.append((rel_path, "useState/useEffect needs 'use client'"))

                # 3. استفاده از params بدون await (در Server Components)
                if (
                    "params" in content
                    and "await params" not in content
                    and "'use client'" not in content
                    and '"use client"' not in content
                    and "async function" in content
                ):
                    # بررسی اینکه آیا params destructured شده بدون await
                    if re.search(r"const\s+\{[^}]+\}\s*=\s*params(?!\s*;)", content):
                        issues_found.append(
                            (rel_path, "params should be awaited in Server Component")
                        )

                # 4. import React قبل از 'use client'
                lines = content.split("\n")
                use_client_idx = None
                react_import_idx = None

                for i, line in enumerate(lines):
                    if "'use client'" in line or '"use client"' in line:
                        use_client_idx = i
                    if "import React" in line or "import * as React" in line:
                        react_import_idx = i

                if use_client_idx is not None and react_import_idx is not None:
                    if react_import_idx < use_client_idx:
                        issues_found.append(
                            (rel_path, "'use client' must be before 'import React'")
                        )

            except Exception as e:
                print_error(f"Error auditing {file_path}: {e}")

    if issues_found:
        print_warning(f"تعداد مشکلات یافت شده: {len(issues_found)}")
        for path, issue in issues_found:
            print_info(f"  {path}: {issue}")
    else:
        print_success("هیچ مشکلی در صفحات یافت نشد")

    return len(issues_found) == 0


# ============================================================================
# FIX 6: تأیید AuthProvider وجود دارد
# ============================================================================


def verify_auth_provider():
    """بررسی وجود AuthProvider"""
    print_header("🔐 Fix 6: Verify AuthProvider")

    auth_provider_path = FRONTEND_DIR / "components" / "providers" / "AuthProvider.tsx"

    if not auth_provider_path.exists():
        print_warning("AuthProvider.tsx یافت نشد - ایجاد نسخه پایه")

        auth_provider_path.parent.mkdir(parents=True, exist_ok=True)

        content = """'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface User {
  id: string;
  email: string;
  name: string;
  wallet?: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, name: string) => Promise<void>;
  logout: () => void;
  connectWallet: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // بررسی session قبلی
    try {
      const saved = localStorage.getItem('user');
      if (saved) {
        setUser(JSON.parse(saved));
      }
    } catch (e) {
      localStorage.removeItem('user');
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const mockUser = {
      id: 'user_' + Date.now(),
      email,
      name: email.split('@')[0],
    };
    setUser(mockUser);
    localStorage.setItem('user', JSON.stringify(mockUser));
  };

  const register = async (email: string, password: string, name: string) => {
    const mockUser = {
      id: 'user_' + Date.now(),
      email,
      name,
    };
    setUser(mockUser);
    localStorage.setItem('user', JSON.stringify(mockUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const connectWallet = async () => {
    if (typeof window !== 'undefined' && (window as any).ethereum) {
      try {
        const accounts = await (window as any).ethereum.request({
          method: 'eth_requestAccounts',
        });
        if (user && accounts[0]) {
          const updated = { ...user, wallet: accounts[0] };
          setUser(updated);
          localStorage.setItem('user', JSON.stringify(updated));
        }
      } catch (err) {
        console.error('Wallet connection failed:', err);
      }
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, connectWallet }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return ctx;
}
"""

        auth_provider_path.write_text(content, encoding="utf-8")
        print_success("AuthProvider.tsx ایجاد شد")
        return True

    print_success("AuthProvider.tsx موجود است")
    return True


# ============================================================================
# FIX 7: پاکسازی Cache
# ============================================================================


def clean_caches():
    """پاکسازی تمام cache ها"""
    print_header("🧹 Fix 7: Clean Caches")

    dirs_to_clean = [
        FRONTEND_DIR / ".next",
        FRONTEND_DIR / "node_modules" / ".cache",
        BACKEND_DIR / "__pycache__",
    ]

    cleaned = 0

    for dir_path in dirs_to_clean:
        if dir_path.exists():
            try:
                shutil.rmtree(dir_path, ignore_errors=True)
                rel = dir_path.relative_to(PROJECT_ROOT)
                print_success(f"Cleaned: {rel}")
                cleaned += 1
            except Exception as e:
                print_error(f"Error cleaning {dir_path}: {e}")

    print_info(f"تعداد پوشه‌های پاک شده: {cleaned}")
    return True


# ============================================================================
# MAIN
# ============================================================================


def main():
    print_header("🛠️ ECONOJIN COMPREHENSIVE FIX")
    print_info(f"Project: {PROJECT_ROOT}")
    print_info(f"Backup: {BACKUP_DIR}")
    print_info(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    fixes = [
        ("next.config.js (Next.js 15 Compatible)", fix_next_config),
        ("'use client' Directive Position", fix_use_client_directive),
        ("Layout with AuthProvider", fix_layout_with_auth_provider),
        ("Polygon RPC Configuration", fix_polygon_rpc),
        ("Audit All Pages", audit_all_pages),
        ("Verify AuthProvider", verify_auth_provider),
        ("Clean Caches", clean_caches),
    ]

    results = []
    for name, fix_func in fixes:
        try:
            print(f"\n{Colors.BOLD}▶ Running: {name}{Colors.END}")
            success = fix_func()
            results.append((name, success))
        except Exception as e:
            print_error(f"Fix failed: {name}")
            print_error(f"Error: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Summary
    print_header("📊 SUMMARY")

    success_count = sum(1 for _, s in results if s)
    total_count = len(results)

    for name, success in results:
        if success:
            print_success(name)
        else:
            print_error(name)

    print(f"\n{Colors.BOLD}نتیجه: {success_count}/{total_count} موفق{Colors.END}")

    if success_count == total_count:
        print_success("تمام اصلاحات با موفقیت انجام شد! 🎉")
        print_info("\n📋 مراحل بعدی:")
        print("  1. Frontend را متوقف کنید (Ctrl+C)")
        print("  2. Backend را متوقف کنید (Ctrl+C)")
        print("  3. Frontend را دوباره اجرا کنید:")
        print(f"     cd {FRONTEND_DIR}")
        print("     npm run dev")
        print("  4. Backend را دوباره اجرا کنید (ترمینال جدید):")
        print(f"     cd {PROJECT_ROOT}")
        print("     python scripts/api/run_server.py")
        print("  5. مرورگر را باز کنید: http://localhost:3000")
        print(f"\n💾 Backup ها در: {BACKUP_DIR}")
    else:
        print_warning(f"{total_count - success_count} مورد نیاز به بررسی دارد")
        print_info(f"Backups در: {BACKUP_DIR}")

    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_warning("\nمتوقف شد")
        sys.exit(1)
    except Exception as e:
        print_error(f"خطای غیرمنتظره: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
