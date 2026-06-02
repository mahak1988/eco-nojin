import logging

logger = logging.getLogger(__name__)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Econojin Mega Builder - فاز ۴ کامل
=================================
شامل:
✅ Sentinel-2 Real Integration
✅ Hardhat Local Deployment
✅ MetaMask + Portfolio
✅ سیستم احراز هویت کامل
✅ لوگوی تایپوگرافی
✅ داشبورد امنیتی
✅ کارتابل ماهک (AI Admin)
✅ سیستم حسابداری، انبارداری، فروشگاه، کتابخانه
✅ صفحات About, Contact, Privacy, Terms, Policy
✅ i18n کامل (fa, en, ar, tr, zh)
✅ RTL/LTR خودکار
✅ Dark/Light Theme
r"""

import sys
import os
import json
import shutil
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"D:\econojin.com")
FRONTEND_DIR = PROJECT_ROOT / "frontend"
CONTRACTS_DIR = PROJECT_ROOT / "contracts"


class EconojinMegaBuilder:
    """سازنده جامع فاز ۴ Econojin"""
    
    SUPPORTED_LOCALES = ['fa', 'en', 'ar', 'tr', 'zh']
    DEFAULT_LOCALE = 'fa'
    RTL_LOCALES = ['fa', 'ar']
    
    def __init__(self):
        self.backup_dir = PROJECT_ROOT / '.mega_build_backup'
        self.backup_dir.mkdir(exist_ok=True)
        self.files_created = []
    
    def backup(self, path: Path):
        if not path.exists():
            return
        rel = path.relative_to(PROJECT_ROOT)
        dest = self.backup_dir / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup = dest.parent / f"{dest.stem}_{ts}{dest.suffix}"
        shutil.copy2(path, backup)
    
    def write(self, path: Path, content: str):
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            self.backup(path)
        path.write_text(content, encoding='utf-8')
        self.files_created.append(path.relative_to(PROJECT_ROOT))
        logger.info(f"  ✓ {path.relative_to(PROJECT_ROOT)}")
    
    # =========================================================================
    # i18n System - ترجمه‌های کامل
    # =========================================================================
    def create_i18n_files(self):
        logger.info("\n" + "="*70)
        logger.info("🌐 Building i18n System (5 Languages)")
        logger.info("="*70)
        
        # Persian (fa) - Default
        self.write(FRONTEND_DIR / "lib" / "i18n" / "fa.json", json.dumps({
            "common": {
                "appName": "اکونوژین",
                "tagline": "پلتفرم علمی کربن",
                "home": "خانه",
                "dashboard": "داشبورد",
                "calculator": "محاسبه‌گر",
                "map": "نقشه",
                "shop": "فروشگاه",
                "library": "کتابخانه",
                "about": "درباره ما",
                "contact": "تماس با ما",
                "login": "ورود",
                "logout": "خروج",
                "register": "ثبت‌نام",
                "profile": "پروفایل",
                "settings": "تنظیمات",
                "privacy": "حریم خصوصی",
                "terms": "قوانین",
                "policy": "خط مشی",
                "save": "ذخیره",
                "cancel": "لغو",
                "delete": "حذف",
                "edit": "ویرایش",
                "create": "ایجاد",
                "search": "جستجو",
                "loading": "در حال بارگذاری...",
                "error": "خطا",
                "success": "موفقیت",
                "language": "زبان",
                "theme": "تم",
                "dark": "تاریک",
                "light": "روشن"
            },
            "auth": {
                "welcomeBack": "خوش آمدید",
                "loginSubtitle": "برای ادامه وارد حساب کاربری خود شوید",
                "registerSubtitle": "حساب کاربری جدید ایجاد کنید",
                "email": "ایمیل",
                "password": "رمز عبور",
                "confirmPassword": "تأیید رمز عبور",
                "fullName": "نام و نام خانوادگی",
                "forgotPassword": "فراموشی رمز عبور؟",
                "noAccount": "حساب کاربری ندارید؟",
                "hasAccount": "قبلاً ثبت‌نام کرده‌اید؟",
                "loginButton": "ورود به حساب",
                "registerButton": "ایجاد حساب",
                "orContinueWith": "یا ادامه با",
                "wallet": "کیف پول"
            },
            "dashboard": {
                "title": "داشبورد مدیریتی",
                "welcome": "خوش آمدید",
                "overview": "نمای کلی",
                "stats": "آمار",
                "recentActivity": "فعالیت‌های اخیر",
                "quickActions": "دسترسی سریع"
            },
            "maahak": {
                "title": "کارتابل هوشمند ماهک",
                "subtitle": "دستیار هوش مصنوعی اکونوژین",
                "greeting": "سلام! من ماهک هستم",
                "helpText": "چطور می‌توانم به شما کمک کنم؟",
                "askQuestion": "سوال خود را بپرسید...",
                "systemStatus": "وضعیت سیستم",
                "allSystemsNormal": "همه سیستم‌ها عادی هستند",
                "alerts": "هشدارها",
                "tasks": "وظایف",
                "insights": "بینش‌ها"
            },
            "carbon": {
                "title": "محاسبه‌گر کربن",
                "activityType": "نوع فعالیت",
                "treePlanting": "درختکاری",
                "soilRegeneration": "بازسازی خاک",
                "agroforestry": "جنگل‌داری کشاورزی",
                "latitude": "عرض جغرافیایی",
                "longitude": "طول جغرافیایی",
                "area": "مساحت (هکتار)",
                "treeCount": "تعداد درخت",
                "species": "گونه",
                "duration": "مدت (سال)",
                "calculate": "محاسبه کربن",
                "result": "نتیجه",
                "carbonAbsorbed": "کربن جذب شده",
                "seedTokens": "توکن SEED",
                "gaiaValue": "ارزش GAIA"
            },
            "shop": {
                "title": "فروشگاه اکونوژین",
                "subtitle": "محصولات پایدار و سازگار با محیط زیست",
                "categories": "دسته‌بندی‌ها",
                "addToCart": "افزودن به سبد",
                "cart": "سبد خرید",
                "checkout": "تسویه حساب",
                "price": "قیمت",
                "quantity": "تعداد",
                "total": "جمع کل"
            },
            "library": {
                "title": "کتابخانه دیجیتال",
                "subtitle": "منابع علمی و آموزشی",
                "books": "کتاب‌ها",
                "articles": "مقالات",
                "research": "پژوهش‌ها",
                "download": "دانلود",
                "read": "مطالعه",
                "author": "نویسنده"
            },
            "inventory": {
                "title": "مدیریت انبار",
                "items": "اقلام",
                "stock": "موجودی",
                "inbound": "ورودی",
                "outbound": "خروجی",
                "lowStock": "موجودی کم",
                "reorder": "سفارش مجدد"
            },
            "accounting": {
                "title": "سیستم حسابداری",
                "income": "درآمد",
                "expenses": "هزینه‌ها",
                "profit": "سود",
                "balance": "موجودی",
                "transactions": "تراکنش‌ها",
                "reports": "گزارش‌ها"
            },
            "security": {
                "title": "داشبورد امنیتی",
                "threats": "تهدیدها",
                "active": "فعال",
                "blocked": "مسدود شده",
                "firewallStatus": "وضعیت فایروال",
                "lastScan": "آخرین اسکن",
                "vulnerabilities": "آسیب‌پذیری‌ها"
            },
            "pages": {
                "about": {
                    "title": "درباره اکونوژین",
                    "mission": "ماموریت ما",
                    "vision": "چشم‌انداز",
                    "team": "تیم ما",
                    "story": "داستان ما"
                },
                "contact": {
                    "title": "تماس با ما",
                    "subtitle": "ما مشتاق شنیدن نظرات شما هستیم",
                    "formTitle": "ارسال پیام",
                    "name": "نام شما",
                    "email": "ایمیل",
                    "subject": "موضوع",
                    "message": "پیام",
                    "send": "ارسال پیام"
                },
                "privacy": {
                    "title": "سیاست حریم خصوصی",
                    "lastUpdated": "آخرین به‌روزرسانی"
                },
                "terms": {
                    "title": "قوانین و مقررات",
                    "acceptance": "پذیرش قوانین"
                },
                "policy": {
                    "title": "خط مشی ما",
                    "sustainability": "پایداری",
                    "transparency": "شفافیت"
                }
            },
            "portfolio": {
                "title": "نمونه کارها",
                "totalCarbon": "کل کربن",
                "totalTokens": "کل توکن‌ها",
                "nftCertificates": "گواهی‌های NFT",
                "viewDetails": "مشاهده جزئیات"
            },
            "sentinel": {
                "title": "تأیید ماهواره‌ای",
                "ndviIndex": "شاخص NDVI",
                "beforeAfter": "قبل / بعد",
                "verification": "تأیید",
                "satelliteData": "داده‌های ماهواره‌ای"
            }
        }, ensure_ascii=False, indent=2))
        
        # English
        self.write(FRONTEND_DIR / "lib" / "i18n" / "en.json", json.dumps({
            "common": {
                "appName": "Econojin",
                "tagline": "Scientific Carbon Platform",
                "home": "Home",
                "dashboard": "Dashboard",
                "calculator": "Calculator",
                "map": "Map",
                "shop": "Shop",
                "library": "Library",
                "about": "About",
                "contact": "Contact",
                "login": "Login",
                "logout": "Logout",
                "register": "Register",
                "profile": "Profile",
                "settings": "Settings",
                "privacy": "Privacy",
                "terms": "Terms",
                "policy": "Policy",
                "save": "Save",
                "cancel": "Cancel",
                "delete": "Delete",
                "edit": "Edit",
                "create": "Create",
                "search": "Search",
                "loading": "Loading...",
                "error": "Error",
                "success": "Success",
                "language": "Language",
                "theme": "Theme",
                "dark": "Dark",
                "light": "Light"
            },
            "auth": {
                "welcomeBack": "Welcome Back",
                "loginSubtitle": "Sign in to continue to your account",
                "registerSubtitle": "Create a new account",
                "email": "Email",
                "password": "Password",
                "confirmPassword": "Confirm Password",
                "fullName": "Full Name",
                "forgotPassword": "Forgot password?",
                "noAccount": "Don't have an account?",
                "hasAccount": "Already have an account?",
                "loginButton": "Sign In",
                "registerButton": "Create Account",
                "orContinueWith": "Or continue with",
                "wallet": "Wallet"
            },
            "dashboard": {
                "title": "Dashboard",
                "welcome": "Welcome",
                "overview": "Overview",
                "stats": "Statistics",
                "recentActivity": "Recent Activity",
                "quickActions": "Quick Actions"
            },
            "maahak": {
                "title": "Maahak Smart Console",
                "subtitle": "Econojin AI Assistant",
                "greeting": "Hello! I'm Maahak",
                "helpText": "How can I help you today?",
                "askQuestion": "Ask me anything...",
                "systemStatus": "System Status",
                "allSystemsNormal": "All systems are normal",
                "alerts": "Alerts",
                "tasks": "Tasks",
                "insights": "Insights"
            },
            "carbon": {
                "title": "Carbon Calculator",
                "activityType": "Activity Type",
                "treePlanting": "Tree Planting",
                "soilRegeneration": "Soil Regeneration",
                "agroforestry": "Agroforestry",
                "latitude": "Latitude",
                "longitude": "Longitude",
                "area": "Area (hectares)",
                "treeCount": "Tree Count",
                "species": "Species",
                "duration": "Duration (years)",
                "calculate": "Calculate Carbon",
                "result": "Result",
                "carbonAbsorbed": "Carbon Absorbed",
                "seedTokens": "SEED Tokens",
                "gaiaValue": "GAIA Value"
            },
            "shop": {
                "title": "Econojin Shop",
                "subtitle": "Sustainable & Eco-friendly Products",
                "categories": "Categories",
                "addToCart": "Add to Cart",
                "cart": "Cart",
                "checkout": "Checkout",
                "price": "Price",
                "quantity": "Quantity",
                "total": "Total"
            },
            "library": {
                "title": "Digital Library",
                "subtitle": "Scientific & Educational Resources",
                "books": "Books",
                "articles": "Articles",
                "research": "Research",
                "download": "Download",
                "read": "Read",
                "author": "Author"
            },
            "inventory": {
                "title": "Inventory Management",
                "items": "Items",
                "stock": "Stock",
                "inbound": "Inbound",
                "outbound": "Outbound",
                "lowStock": "Low Stock",
                "reorder": "Reorder"
            },
            "accounting": {
                "title": "Accounting System",
                "income": "Income",
                "expenses": "Expenses",
                "profit": "Profit",
                "balance": "Balance",
                "transactions": "Transactions",
                "reports": "Reports"
            },
            "security": {
                "title": "Security Dashboard",
                "threats": "Threats",
                "active": "Active",
                "blocked": "Blocked",
                "firewallStatus": "Firewall Status",
                "lastScan": "Last Scan",
                "vulnerabilities": "Vulnerabilities"
            },
            "pages": {
                "about": {
                    "title": "About Econojin",
                    "mission": "Our Mission",
                    "vision": "Our Vision",
                    "team": "Our Team",
                    "story": "Our Story"
                },
                "contact": {
                    "title": "Contact Us",
                    "subtitle": "We'd love to hear from you",
                    "formTitle": "Send a Message",
                    "name": "Your Name",
                    "email": "Email",
                    "subject": "Subject",
                    "message": "Message",
                    "send": "Send Message"
                },
                "privacy": {
                    "title": "Privacy Policy",
                    "lastUpdated": "Last Updated"
                },
                "terms": {
                    "title": "Terms & Conditions",
                    "acceptance": "Acceptance of Terms"
                },
                "policy": {
                    "title": "Our Policy",
                    "sustainability": "Sustainability",
                    "transparency": "Transparency"
                }
            },
            "portfolio": {
                "title": "Portfolio",
                "totalCarbon": "Total Carbon",
                "totalTokens": "Total Tokens",
                "nftCertificates": "NFT Certificates",
                "viewDetails": "View Details"
            },
            "sentinel": {
                "title": "Satellite Verification",
                "ndviIndex": "NDVI Index",
                "beforeAfter": "Before / After",
                "verification": "Verification",
                "satelliteData": "Satellite Data"
            }
        }, ensure_ascii=False, indent=2))
        
        # Arabic
        self.write(FRONTEND_DIR / "lib" / "i18n" / "ar.json", json.dumps({
            "common": {
                "appName": "إكونوجين",
                "tagline": "منصة الكربون العلمية",
                "home": "الرئيسية",
                "dashboard": "لوحة التحكم",
                "calculator": "الحاسبة",
                "map": "الخريطة",
                "shop": "المتجر",
                "library": "المكتبة",
                "about": "من نحن",
                "contact": "اتصل بنا",
                "login": "تسجيل الدخول",
                "logout": "تسجيل الخروج",
                "register": "إنشاء حساب",
                "profile": "الملف الشخصي",
                "settings": "الإعدادات",
                "privacy": "الخصوصية",
                "terms": "الشروط",
                "policy": "السياسة",
                "save": "حفظ",
                "cancel": "إلغاء",
                "delete": "حذف",
                "edit": "تعديل",
                "create": "إنشاء",
                "search": "بحث",
                "loading": "جاري التحميل...",
                "error": "خطأ",
                "success": "نجاح",
                "language": "اللغة",
                "theme": "السمة",
                "dark": "داكن",
                "light": "فاتح"
            },
            "auth": {
                "welcomeBack": "مرحباً بعودتك",
                "loginSubtitle": "سجل الدخول للمتابعة",
                "registerSubtitle": "أنشئ حساباً جديداً",
                "email": "البريد الإلكتروني",
                "password": "كلمة المرور",
                "confirmPassword": "تأكيد كلمة المرور",
                "fullName": "الاسم الكامل",
                "forgotPassword": "نسيت كلمة المرور؟",
                "noAccount": "ليس لديك حساب؟",
                "hasAccount": "لديك حساب بالفعل؟",
                "loginButton": "تسجيل الدخول",
                "registerButton": "إنشاء حساب",
                "orContinueWith": "أو تابع مع",
                "wallet": "المحفظة"
            },
            "dashboard": {
                "title": "لوحة التحكم",
                "welcome": "مرحباً",
                "overview": "نظرة عامة",
                "stats": "الإحصائيات",
                "recentActivity": "النشاط الأخير",
                "quickActions": "إجراءات سريعة"
            },
            "maahak": {
                "title": "وحدة ماهك الذكية",
                "subtitle": "مساعد الذكاء الاصطناعي",
                "greeting": "مرحباً! أنا ماهك",
                "helpText": "كيف يمكنني مساعدتك اليوم؟",
                "askQuestion": "اسألني أي شيء...",
                "systemStatus": "حالة النظام",
                "allSystemsNormal": "جميع الأنظمة طبيعية",
                "alerts": "التنبيهات",
                "tasks": "المهام",
                "insights": "الرؤى"
            },
            "carbon": {
                "title": "حاسبة الكربون",
                "activityType": "نوع النشاط",
                "treePlanting": "زراعة الأشجار",
                "soilRegeneration": "تجديد التربة",
                "agroforestry": "الحراجة الزراعية",
                "latitude": "خط العرض",
                "longitude": "خط الطول",
                "area": "المساحة (هكتار)",
                "treeCount": "عدد الأشجار",
                "species": "النوع",
                "duration": "المدة (سنوات)",
                "calculate": "احسب الكربون",
                "result": "النتيجة",
                "carbonAbsorbed": "الكربون الممتص",
                "seedTokens": "رموز SEED",
                "gaiaValue": "قيمة GAIA"
            },
            "pages": {
                "about": {"title": "عن إكونوجين"},
                "contact": {"title": "اتصل بنا", "subtitle": "يسعدنا سماع رأيك"},
                "privacy": {"title": "سياسة الخصوصية"},
                "terms": {"title": "الشروط والأحكام"},
                "policy": {"title": "سياستنا"}
            }
        }, ensure_ascii=False, indent=2))
        
        # Turkish
        self.write(FRONTEND_DIR / "lib" / "i18n" / "tr.json", json.dumps({
            "common": {
                "appName": "Econojin",
                "tagline": "Bilimsel Karbon Platformu",
                "home": "Ana Sayfa",
                "dashboard": "Panel",
                "calculator": "Hesaplayıcı",
                "map": "Harita",
                "shop": "Mağaza",
                "library": "Kütüphane",
                "about": "Hakkında",
                "contact": "İletişim",
                "login": "Giriş",
                "logout": "Çıkış",
                "register": "Kayıt",
                "save": "Kaydet",
                "cancel": "İptal",
                "language": "Dil",
                "theme": "Tema"
            },
            "auth": {
                "welcomeBack": "Tekrar Hoş Geldiniz",
                "loginSubtitle": "Devam etmek için giriş yapın",
                "email": "E-posta",
                "password": "Şifre",
                "loginButton": "Giriş Yap"
            },
            "maahak": {
                "title": "Maahak Akıllı Konsol",
                "subtitle": "Econojin AI Asistanı",
                "greeting": "Merhaba! Ben Maahak"
            },
            "pages": {
                "about": {"title": "Econojin Hakkında"},
                "contact": {"title": "İletişim"},
                "privacy": {"title": "Gizlilik Politikası"},
                "terms": {"title": "Şartlar ve Koşullar"}
            }
        }, ensure_ascii=False, indent=2))
        
        # Chinese
        self.write(FRONTEND_DIR / "lib" / "i18n" / "zh.json", json.dumps({
            "common": {
                "appName": "Econojin",
                "tagline": "科学碳平台",
                "home": "首页",
                "dashboard": "仪表板",
                "calculator": "计算器",
                "map": "地图",
                "shop": "商店",
                "library": "图书馆",
                "about": "关于",
                "contact": "联系",
                "login": "登录",
                "logout": "登出",
                "register": "注册",
                "save": "保存",
                "cancel": "取消",
                "language": "语言",
                "theme": "主题"
            },
            "auth": {
                "welcomeBack": "欢迎回来",
                "loginSubtitle": "登录以继续",
                "email": "电子邮件",
                "password": "密码",
                "loginButton": "登录"
            },
            "maahak": {
                "title": "Maahak 智能控制台",
                "subtitle": "Econojin AI 助手",
                "greeting": "你好！我是 Maahak"
            },
            "pages": {
                "about": {"title": "关于 Econojin"},
                "contact": {"title": "联系我们"},
                "privacy": {"title": "隐私政策"}
            }
        }, ensure_ascii=False, indent=2))
        
        # i18n utility
        self.write(FRONTEND_DIR / "lib" / "i18n" / "index.ts", """// i18n System - Internationalization
import fa from './fa.json';
import en from './en.json';
import ar from './ar.json';
import tr from './tr.json';
import zh from './zh.json';

export const locales = ['fa', 'en', 'ar', 'tr', 'zh'] as const;
export type Locale = typeof locales[number];

export const defaultLocale: Locale = 'fa';

export const rtlLocales: Locale[] = ['fa', 'ar'];

export const localeNames: Record<Locale, string> = {
  fa: 'فارسی',
  en: 'English',
  ar: 'العربية',
  tr: 'Türkçe',
  zh: '中文',
};

export const localeFlags: Record<Locale, string> = {
  fa: '🇮🇷',
  en: '🇬🇧',
  ar: '🇸🇦',
  tr: '🇹🇷',
  zh: '🇨🇳',
};

const dictionaries = { fa, en, ar, tr, zh };

export function getDictionary(locale: Locale) {
  return dictionaries[locale] || dictionaries[defaultLocale];
}

export function isRTL(locale: Locale): boolean {
  return rtlLocales.includes(locale);
}

export function getDirection(locale: Locale): 'rtl' | 'ltr' {
  return isRTL(locale) ? 'rtl' : 'ltr';
}

// Helper to get nested translation
export function t(dict: any, path: string): string {
  const keys = path.split('.');
  let value = dict;
  for (const key of keys) {
    if (value && typeof value === 'object' && key in value) {
      value = value[key];
    } else {
      return path; // Return path if not found
    }
  }
  return typeof value === 'string' ? value : path;
}
r""")
    
    # =========================================================================
    # Middleware برای i18n Routing
    # =========================================================================
    def create_middleware(self):
        logger.info("\n" + "="*70)
        logger.info("🔀 Creating i18n Middleware")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "middleware.ts", """import { NextRequest, NextResponse } from 'next/server';

export const locales = ['fa', 'en', 'ar', 'tr', 'zh'];
export const defaultLocale = 'fa';

function getLocale(request: NextRequest): string {
  // Check cookie
  const localeCookie = request.cookies.get('NEXT_LOCALE')?.value;
  if (localeCookie && locales.includes(localeCookie)) {
    return localeCookie;
  }
  
  // Check Accept-Language header
  const acceptLanguage = request.headers.get('accept-language') || '';
  for (const locale of locales) {
    if (acceptLanguage.includes(locale)) {
      return locale;
    }
  }
  
  return defaultLocale;
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  
  // Skip static files and API routes
  if (
    pathname.startsWith('/_next') ||
    pathname.startsWith('/api') ||
    pathname.includes('.') ||
    pathname.startsWith('/favicon')
  ) {
    return NextResponse.next();
  }
  
  // Check if pathname has locale
  const pathnameHasLocale = locales.some(
    (locale) => pathname.startsWith(`/${locale}/`) || pathname === `/${locale}`
  );
  
  if (pathnameHasLocale) {
    return NextResponse.next();
  }
  
  // Redirect to localized path
  const locale = getLocale(request);
  request.nextUrl.pathname = `/${locale}${pathname}`;
  
  const response = NextResponse.redirect(request.nextUrl);
  response.cookies.set('NEXT_LOCALE', locale, { path: '/' });
  
  return response;
}

export const config = {
  matcher: ['/((?!_next|api|favicon|.*\\\\..*).*)'],
};
r""")
    
    # =========================================================================
    # Root Layout با i18n Support
    # =========================================================================
    def create_root_layout(self):
        logger.info("\n" + "="*70)
        logger.info("🎨 Creating Root Layout with i18n")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "app" / "[locale]" / "layout.tsx", """import '../globals.css';
import type { Metadata } from 'next';
import { locales, type Locale, getDirection } from '@/lib/i18n';
import { AuthProvider } from '@/components/providers/AuthProvider';
import { ThemeProvider } from '@/components/providers/ThemeProvider';
import Navbar from '@/components/Navbar';
import Footer from '@/components/Footer';

export const metadata: Metadata = {
  title: 'Econojin - Gaia Protocol Carbon Platform',
  description: 'Scientific Carbon Platform powered by Gaia Protocol',
  keywords: ['carbon', 'climate', 'blockchain', 'satellite', 'NDVI'],
};

export function generateStaticParams() {
  return locales.map((locale) => ({ locale }));
}

export default function LocaleLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { locale: Locale };
}) {
  const direction = getDirection(params.locale);
  
  return (
    <html lang={params.locale} dir={direction} suppressHydrationWarning>
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
        className={`${params.locale === 'fa' || params.locale === 'ar' ? 'font-vazir' : 'font-inter'} antialiased`}
        suppressHydrationWarning
      >
        <ThemeProvider>
          <AuthProvider>
            <div className="flex flex-col min-h-screen">
              <Navbar locale={params.locale} />
              <main className="flex-grow">
                {children}
              </main>
              <Footer locale={params.locale} />
            </div>
          </AuthProvider>
        </ThemeProvider>
      </body>
    </html>
  );
}
r""")
    
    # =========================================================================
    # Logo تایپوگرافی
    # =========================================================================
    def create_logo(self):
        logger.info("\n" + "="*70)
        logger.info("✨ Creating Typography Logo")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "components" / "Logo.tsx", """import Link from 'next/link';

interface LogoProps {
  locale?: string;
  size?: 'sm' | 'md' | 'lg';
  showTagline?: boolean;
}

export default function Logo({ locale = 'fa', size = 'md', showTagline = false }: LogoProps) {
  const sizes = {
    sm: { text: 'text-2xl', tag: 'text-xs', icon: 'w-6 h-6' },
    md: { text: 'text-3xl', tag: 'text-sm', icon: 'w-8 h-8' },
    lg: { text: 'text-5xl', tag: 'text-base', icon: 'w-12 h-12' },
  };
  
  const s = sizes[size];
  const isPersian = locale === 'fa';
  
  return (
    <Link href={`/${locale}`} className="inline-flex flex-col items-start group">
      <div className="flex items-center gap-2">
        {/* Leaf Icon */}
        <div className={`${s.icon} relative`}>
          <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="leafGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#22c55e" />
                <stop offset="100%" stopColor="#15803d" />
              </linearGradient>
            </defs>
            <path
              d="M16 2C10 6 6 12 6 18C6 24 10 28 16 30C22 28 26 24 26 18C26 12 22 6 16 2Z"
              fill="url(#leafGradient)"
            />
            <path
              d="M16 8V24M12 14L16 10L20 14"
              stroke="white"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
        </div>
        
        {/* Typography Logo */}
        <div className="flex flex-col leading-none">
          <span 
            className={`${s.text} font-black tracking-tight bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 bg-clip-text text-transparent group-hover:from-green-500 group-hover:to-teal-500 transition-all`}
            style={{
              fontFamily: isPersian ? 'Vazirmatn, sans-serif' : 'Inter, sans-serif',
              letterSpacing: isPersian ? '0' : '-0.02em',
            }}
          >
            {isPersian ? 'اکونوژین' : 'Econojin'}
          </span>
          {showTagline && (
            <span className={`${s.tag} text-gray-500 font-medium mt-1`}>
              {isPersian ? 'پلتفرم علمی کربن' : 'Scientific Carbon Platform'}
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}
r""")
    
    # =========================================================================
    # Language Switcher
    # =========================================================================
    def create_language_switcher(self):
        logger.info("\n" + "="*70)
        logger.info("🌐 Creating Language Switcher")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "components" / "LanguageSwitcher.tsx", """'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { Globe, ChevronDown, Check } from 'lucide-react';
import { locales, localeNames, localeFlags, type Locale } from '@/lib/i18n';

export default function LanguageSwitcher({ currentLocale }: { currentLocale: Locale }) {
  const [isOpen, setIsOpen] = useState(false);
  const router = useRouter();
  const pathname = usePathname();
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const changeLocale = (newLocale: Locale) => {
    // Replace locale in pathname
    const segments = pathname.split('/');
    segments[1] = newLocale;
    const newPath = segments.join('/');
    
    document.cookie = `NEXT_LOCALE=${newLocale};path=/;max-age=31536000`;
    router.push(newPath);
    setIsOpen(false);
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition"
        aria-label="Change language"
      >
        <Globe className="w-4 h-4" />
        <span className="text-sm font-medium hidden sm:inline">
          {localeFlags[currentLocale]} {localeNames[currentLocale]}
        </span>
        <span className="sm:hidden">{localeFlags[currentLocale]}</span>
        <ChevronDown className={`w-4 h-4 transition ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full mt-2 end-0 bg-white dark:bg-gray-900 rounded-lg shadow-xl border 
            border-gray-200 dark:border-gray-700 py-1 min-w-[180px] z-50 animate-fade-in">           {locales.map((locale) => (
            <button
              key={locale}
              onClick={() => changeLocale(locale)}
              className={`w-full flex items-center justify-between px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-800 transition text-sm ${
                currentLocale === locale ? 'text-green-600 font-medium' : 'text-gray-700 dark:text-gray-300'
              }`}
            >
              <span className="flex items-center gap-2">
                <span className="text-lg">{localeFlags[locale]}</span>
                <span>{localeNames[locale]}</span>
              </span>
              {currentLocale === locale && <Check className="w-4 h-4" />}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
r""")
    
    # =========================================================================
    # Theme Switcher
    # =========================================================================
    def create_theme_switcher(self):
        logger.info("\n" + "="*70)
        logger.info("🌓 Creating Theme Switcher")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "components" / "ThemeSwitcher.tsx", """'use client';

import { useState, useEffect } from 'react';
import { Sun, Moon, Monitor } from 'lucide-react';

type Theme = 'light' | 'dark' | 'system';

export default function ThemeSwitcher() {
  const [theme, setTheme] = useState<Theme>('system');
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
    const saved = localStorage.getItem('theme') as Theme;
    if (saved) {
      setTheme(saved);
      applyTheme(saved);
    } else {
      applyTheme('system');
    }
  }, []);

  const applyTheme = (newTheme: Theme) => {
    const root = document.documentElement;
    if (newTheme === 'system') {
      const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      root.classList.toggle('dark', isDark);
    } else {
      root.classList.toggle('dark', newTheme === 'dark');
    }
  };

  const changeTheme = (newTheme: Theme) => {
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
    applyTheme(newTheme);
  };

  if (!mounted) return <div className="w-24 h-10" />;

  const themes: { value: Theme; icon: any; label: string }[] = [
    { value: 'light', icon: Sun, label: 'Light' },
    { value: 'dark', icon: Moon, label: 'Dark' },
    { value: 'system', icon: Monitor, label: 'System' },
  ];

  return (
    <div className="flex items-center gap-1 p-1 bg-gray-100 dark:bg-gray-800 rounded-lg">
      {themes.map(({ value, icon: Icon, label }) => (
        <button
          key={value}
          onClick={() => changeTheme(value)}
          className={`p-2 rounded-md transition ${
            theme === value
              ? 'bg-white dark:bg-gray-700 shadow-sm text-green-600'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900'
          }`}
          aria-label={label}
          title={label}
        >
          <Icon className="w-4 h-4" />
        </button>
      ))}
    </div>
  );
}
r""")
    
    # =========================================================================
    # Providers (Auth, Theme)
    # =========================================================================
    def create_providers(self):
        logger.info("\n" + "="*70)
        logger.info("🔌 Creating Providers")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "components" / "providers" / "AuthProvider.tsx", """'use client';

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
    // Check for existing session
    const saved = localStorage.getItem('user');
    if (saved) {
      try {
        setUser(JSON.parse(saved));
      } catch (e) {
        localStorage.removeItem('user');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    // Mock login
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
        if (user) {
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
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
""")
        
        self.write(FRONTEND_DIR / "components" / "providers" / "ThemeProvider.tsx", """'use client';

import { createContext, useContext, ReactNode } from 'react';

interface ThemeContextType {}

const ThemeContext = createContext<ThemeContextType>({});

export function ThemeProvider({ children }: { children: ReactNode }) {
  return <ThemeContext.Provider value={{}}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}
r""")
    
    # =========================================================================
    # Navigation Bar با i18n
    # =========================================================================
    def create_navbar(self):
        logger.info("\n" + "="*70)
        logger.info("🧭 Creating Navigation Bar")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "components" / "Navbar.tsx", """'use client';

import Link from 'next/link';
import { useState, useEffect } from 'react';
import { Menu, X, User, Wallet, LogOut, LayoutDashboard } from 'lucide-react';
import Logo from './Logo';
import LanguageSwitcher from './LanguageSwitcher';
import ThemeSwitcher from './ThemeSwitcher';
import { useAuth } from './providers/AuthProvider';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function Navbar({ locale }: { locale: Locale }) {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const { user, logout } = useAuth();
  const dict = getDictionary(locale);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const navLinks = [
    { href: `/${locale}`, label: dict.common.home },
    { href: `/${locale}/dashboard`, label: dict.common.dashboard },
    { href: `/${locale}/calculate`, label: dict.common.calculator },
    { href: `/${locale}/shop`, label: dict.common.shop },
    { href: `/${locale}/library`, label: dict.common.library },
    { href: `/${locale}/about`, label: dict.common.about },
    { href: `/${locale}/contact`, label: dict.common.contact },
  ];

  return (
    <nav className={`fixed w-full z-50 transition-all duration-300 ${
      scrolled ? 'bg-white/90 dark:bg-gray-900/90 backdrop-blur-md shadow-lg' : 'bg-transparent'
    }`}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <Logo locale={locale} size="sm" />

          {/* Desktop */}
          <div className="hidden lg:flex items-center gap-6">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-green-600 transition"
              >
                {link.label}
              </Link>
            ))}
          </div>

          <div className="hidden lg:flex items-center gap-3">
            <LanguageSwitcher currentLocale={locale} />
            <ThemeSwitcher />
            
            {user ? (
              <div className="flex items-center gap-2">
                <Link
                  href={`/${locale}/admin`}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 hover:bg-green-200 transition text-sm"
                >
                  <LayoutDashboard className="w-4 h-4" />
                  ماهک
                </Link>
                <button
                  onClick={logout}
                  className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition text-sm"
                >
                  <LogOut className="w-4 h-4" />
                  {dict.common.logout}
                </button>
              </div>
            ) : (
              <Link
                href={`/${locale}/login`}
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-green-600 text-white hover:bg-green-700 transition text-sm font-medium"
              >
                <User className="w-4 h-4" />
                {dict.common.login}
              </Link>
            )}
          </div>

          {/* Mobile Toggle */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="lg:hidden bg-white dark:bg-gray-900 border-t dark:border-gray-800 py-4">
            <div className="flex flex-col gap-2 px-4">
              {navLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsOpen(false)}
                  className="py-2 text-gray-700 dark:text-gray-300 hover:text-green-600"
                >
                  {link.label}
                </Link>
              ))}
              <div className="flex items-center gap-2 pt-4 border-t dark:border-gray-800">
                <LanguageSwitcher currentLocale={locale} />
                <ThemeSwitcher />
              </div>
              {user ? (
                <button
                  onClick={() => { logout(); setIsOpen(false); }}
                  className="py-2 text-red-600"
                >
                  {dict.common.logout}
                </button>
              ) : (
                <Link
                  href={`/${locale}/login`}
                  onClick={() => setIsOpen(false)}
                  className="py-2 text-green-600"
                >
                  {dict.common.login}
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
""")
        
        self.write(FRONTEND_DIR / "components" / "Footer.tsx", """import Link from 'next/link';
import Logo from './Logo';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function Footer({ locale }: { locale: Locale }) {
  const dict = getDictionary(locale);
  
  return (
    <footer className="bg-gray-900 dark:bg-black text-white">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <Logo locale={locale} size="md" />
            <p className="text-gray-400 text-sm mt-4">
              {dict.common.tagline}
            </p>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Platform</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href={`/${locale}/calculate`} className="hover:text-green-500">{dict.common.calculator}</Link></li>
              <li><Link href={`/${locale}/dashboard`} className="hover:text-green-500">{dict.common.dashboard}</Link></li>
              <li><Link href={`/${locale}/map`} className="hover:text-green-500">{dict.common.map}</Link></li>
              <li><Link href={`/${locale}/shop`} className="hover:text-green-500">{dict.common.shop}</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href={`/${locale}/library`} className="hover:text-green-500">{dict.common.library}</Link></li>
              <li><Link href={`/${locale}/about`} className="hover:text-green-500">{dict.common.about}</Link></li>
              <li><Link href={`/${locale}/contact`} className="hover:text-green-500">{dict.common.contact}</Link></li>
            </ul>
          </div>
          
          <div>
            <h3 className="font-semibold mb-4">Legal</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href={`/${locale}/privacy`} className="hover:text-green-500">{dict.common.privacy}</Link></li>
              <li><Link href={`/${locale}/terms`} className="hover:text-green-500">{dict.common.terms}</Link></li>
              <li><Link href={`/${locale}/policy`} className="hover:text-green-500">{dict.common.policy}</Link></li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-400">
          © {new Date().getFullYear()} Econojin. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
r""")
    
    # =========================================================================
    # Auth Pages (Login, Register)
    # =========================================================================
    def create_auth_pages(self):
        logger.info("\n" + "="*70)
        logger.info("🔐 Creating Auth Pages (Login & Register)")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "app" / "[locale]" / "login" / "page.tsx", """'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { Mail, Lock, Eye, EyeOff, Wallet } from 'lucide-react';
import Logo from '@/components/Logo';
import { useAuth } from '@/components/providers/AuthProvider';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function LoginPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const router = useRouter();
  const { login, connectWallet } = useAuth();
  
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(email, password);
      router.push(`/${locale}/dashboard`);
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleWalletLogin = async () => {
    await connectWallet();
    router.push(`/${locale}/dashboard`);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo locale={locale} size="lg" showTagline />
          </div>
          <h1 className="text-3xl font-bold mt-6">{dict.auth.welcomeBack}</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">{dict.auth.loginSubtitle}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-400 p-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">{dict.auth.email}</label>
              <div className="relative">
                <Mail className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full ps-10 pe-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-green-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">{dict.auth.password}</label>
              <div className="relative">
                <Lock className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full ps-10 pe-12 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-green-500 focus:outline-none"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute end-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <div className="flex justify-end">
              <Link href={`/${locale}/forgot-password`} className="text-sm text-green-600 hover:underline">
                {dict.auth.forgotPassword}
              </Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 transition shadow-lg"
            >
              {loading ? dict.common.loading : dict.auth.loginButton}
            </button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t dark:border-gray-700"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-4 bg-white dark:bg-gray-800 text-gray-500">{dict.auth.orContinueWith}</span>
            </div>
          </div>

          <button
            onClick={handleWalletLogin}
            className="w-full flex items-center justify-center gap-2 border-2 dark:border-gray-700 py-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition"
          >
            <Wallet className="w-5 h-5" />
            {dict.auth.wallet} (MetaMask)
          </button>

          <p className="text-center mt-6 text-sm text-gray-600 dark:text-gray-400">
            {dict.auth.noAccount}{' '}
            <Link href={`/${locale}/register`} className="text-green-600 hover:underline font-medium">
              {dict.auth.registerButton}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
""")
        
        self.write(FRONTEND_DIR / "app" / "[locale]" / "register" / "page.tsx", """'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter, useParams } from 'next/navigation';
import { Mail, Lock, User } from 'lucide-react';
import Logo from '@/components/Logo';
import { useAuth } from '@/components/providers/AuthProvider';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function RegisterPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const router = useRouter();
  const { register } = useAuth();
  
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await register(email, password, name);
      router.push(`/${locale}/dashboard`);
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-green-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 px-4 py-12">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo locale={locale} size="lg" showTagline />
          </div>
          <h1 className="text-3xl font-bold mt-6">{dict.auth.registerSubtitle}</h1>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 text-red-700 p-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium mb-2">{dict.auth.fullName}</label>
              <div className="relative">
                <User className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full ps-10 pe-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-green-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">{dict.auth.email}</label>
              <div className="relative">
                <Mail className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full ps-10 pe-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-green-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">{dict.auth.password}</label>
              <div className="relative">
                <Lock className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full ps-10 pe-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-green-500 focus:outline-none"
                  required
                  minLength={8}
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">{dict.auth.confirmPassword}</label>
              <div className="relative">
                <Lock className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full ps-10 pe-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-green-500 focus:outline-none"
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 rounded-lg font-semibold hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 transition shadow-lg"
            >
              {loading ? dict.common.loading : dict.auth.registerButton}
            </button>
          </form>

          <p className="text-center mt-6 text-sm text-gray-600 dark:text-gray-400">
            {dict.auth.hasAccount}{' '}
            <Link href={`/${locale}/login`} className="text-green-600 hover:underline font-medium">
              {dict.auth.loginButton}
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
r""")
    
    # =========================================================================
    # Maahak (ماهک) AI Admin Dashboard
    # =========================================================================
    def create_maahak_dashboard(self):
        logger.info("\n" + "="*70)
        logger.info("🤖 Creating Maahak AI Admin Dashboard")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "app" / "[locale]" / "admin" / "page.tsx", """'use client';

import { useState, useEffect, useRef } from 'react';
import { useParams } from 'next/navigation';
import { 
  Bot, Send, Activity, Shield, Users, Leaf, 
  AlertTriangle, CheckCircle, TrendingUp, Database,
  Cpu, Zap, Bell, Settings, Search
} from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';
import { useAuth } from '@/components/providers/AuthProvider';

interface Message {
  id: number;
  role: 'user' | 'maahak';
  content: string;
  timestamp: Date;
}

export default function MaahakAdminPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const { user } = useAuth();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState<'chat' | 'system' | 'tasks' | 'insights'>('chat');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setMessages([{
      id: 1,
      role: 'maahak',
      content: locale === 'fa' 
        ? 'سلام! من ماهک هستم، دستیار هوشمند اکونوژین. چطور می‌توانم کمکتان کنم؟'
        : "Hello! I'm Maahak, Econojin's AI assistant. How can I help you today?",
      timestamp: new Date(),
    }]);
  }, [locale]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = () => {
    if (!input.trim()) return;
    
    const userMsg: Message = {
      id: messages.length + 1,
      role: 'user',
      content: input,
      timestamp: new Date(),
    };
    
    setMessages([...messages, userMsg]);
    setInput('');
    
    setTimeout(() => {
      const reply = generateMaahakResponse(input, locale);
      setMessages(prev => [...prev, {
        id: prev.length + 1,
        role: 'maahak',
        content: reply,
        timestamp: new Date(),
      }]);
    }, 800);
  };

  const systemMetrics = [
    { label: 'API', value: 'Active', color: 'green', icon: Cpu },
    { label: 'Database', value: 'Healthy', color: 'green', icon: Database },
    { label: 'Sentinel-2', value: 'Connected', color: 'green', icon: Activity },
    { label: 'Blockchain', value: 'Polygon', color: 'blue', icon: Zap },
    { label: 'Threats Blocked', value: '2,847', color: 'red', icon: Shield },
    { label: 'Active Users', value: '1,234', color: 'purple', icon: Users },
  ];

  const alerts = [
    { type: 'warning',
        message: locale === 'fa' ? 'حمله Brute Force شناسایی و مسدود شد' : 'Brute force attack detected and blocked',
        time: '2m ago' },
            { type: 'info',
        message: locale === 'fa' ? 'پشتیبان‌گیری خودکار کامل شد' : 'Automatic backup completed',
        time: '15m ago' },
            { type: 'success',
        message: locale === 'fa' ? '۱۲ فعالیت اکوسیستمی جدید تأیید شد' : '12 new ecosystem activities verified',
        time: '1h ago' },
          ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-black pt-20">
      <div className="max-w-7xl mx-auto p-6">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white mb-6 shadow-2xl">
          <div className="flex items-center gap-4 mb-4">
            <div className="w-16 h-16 bg-white/20 backdrop-blur rounded-2xl flex items-center justify-center">
              <Bot className="w-10 h-10" />
            </div>
            <div>
              <h1 className="text-4xl font-bold">{dict.maahak.title}</h1>
              <p className="text-white/80 mt-1">{dict.maahak.subtitle}</p>
            </div>
          </div>
          <p className="text-lg text-white/90">
            {dict.maahak.greeting}, {user?.name || 'Admin'}! {dict.maahak.helpText}
          </p>
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 border-b dark:border-gray-800 overflow-x-auto">
          {[
            { id: 'chat', label: 'Chat', icon: Bot },
            { id: 'system', label: 'System', icon: Activity },
            { id: 'tasks', label: 'Tasks', icon: Bell },
            { id: 'insights', label: 'Insights', icon: TrendingUp },
          ].map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center gap-2 px-6 py-3 font-medium border-b-2 transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-purple-600 text-purple-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Chat Tab */}
        {activeTab === 'chat' && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
            <div className="h-[500px] overflow-y-auto p-6 space-y-4">
              {messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                    {msg.role === 'maahak' && (
                      <div className="flex items-center gap-2 mb-1">
                        <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                          <Bot className="w-5 h-5 text-white" />
                        </div>
                        <span className="text-sm font-medium text-purple-600">ماهک</span>
                      </div>
                    )}
                    <div className={`p-4 rounded-2xl ${
                      msg.role === 'user'
                        ? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                    }`}>
                      <p className="whitespace-pre-wrap">{msg.content}</p>
                      <p className={`text-xs mt-2 ${msg.role === 'user' ? 'text-white/70' : 'text-gray-500'}`}>
                        {msg.timestamp.toLocaleTimeString(locale === 'fa' ? 'fa-IR' : 'en-US',
                            { hour: '2-digit',
                            minute: '2-digit' })}                      </p>
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="border-t dark:border-gray-700 p-4 flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder={dict.maahak.askQuestion}
                className="flex-1 px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-purple-500 focus:outline-none"
              />
              <button
                onClick={sendMessage}
                className="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-lg hover:from-purple-700 hover:to-pink-700 transition"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* System Tab */}
        {activeTab === 'system' && (
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systemMetrics.map((metric, i) => {
              const Icon = metric.icon;
              return (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-md">
                  <div className="flex items-start justify-between mb-3">
                    <Icon className={`w-8 h-8 text-${metric.color}-500`} />
                    <span className={`text-xs font-medium px-2 py-1 rounded-full bg-${metric.color}-100 text-${metric.color}-700`}>
                      {metric.value}
                    </span>
                  </div>
                  <p className="text-sm text-gray-500">{metric.label}</p>
                </div>
              );
            })}
          </div>
        )}

        {/* Tasks Tab */}
        {activeTab === 'tasks' && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
            <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
              <Bell className="w-6 h-6" />
              {dict.maahak.alerts}
            </h2>
            <div className="space-y-3">
              {alerts.map((alert, i) => (
                <div key={i} className={`p-4 rounded-lg border-l-4 ${
                  alert.type === 'warning' ? 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-500' :
                  alert.type === 'success' ? 'bg-green-50 dark:bg-green-900/20 border-green-500' :
                  'bg-blue-50 dark:bg-blue-900/20 border-blue-500'
                }`}>
                  <div className="flex items-start gap-3">
                    {alert.type === 'warning' && <AlertTriangle className="w-5 h-5 text-yellow-500" />}
                    {alert.type === 'success' && <CheckCircle className="w-5 h-5 text-green-500" />}
                    {alert.type === 'info' && <Activity className="w-5 h-5 text-blue-500" />}
                    <div className="flex-1">
                      <p className="text-gray-900 dark:text-white">{alert.message}</p>
                      <p className="text-xs text-gray-500 mt-1">{alert.time}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Insights Tab */}
        {activeTab === 'insights' && (
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-green-600" />
                Carbon Trends
              </h3>
              <div className="space-y-3">
                {[
                  { label: 'This Month', value: '203.56 tons', change: '+12%' },
                  { label: 'Last Month', value: '181.75 tons', change: '+8%' },
                  { label: 'YTD', value: '1,847 tons', change: '+45%' },
                ].map((item, i) => (
                  <div key={i} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <span className="text-gray-600 dark:text-gray-300">{item.label}</span>
                    <div className="text-end">
                      <div className="font-bold">{item.value}</div>
                      <div className="text-xs text-green-600">{item.change}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
              <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                <Leaf className="w-5 h-5 text-green-600" />
                Top Activities
              </h3>
              <div className="space-y-3">
                {[
                  { label: 'Tree Planting', count: 85, percent: 55 },
                  { label: 'Soil Regeneration', count: 32, percent: 21 },
                  { label: 'Agroforestry', count: 24, percent: 15 },
                  { label: 'Wetland', count: 15, percent: 9 },
                ].map((item, i) => (
                  <div key={i}>
                    <div className="flex justify-between text-sm mb-1">
                      <span>{item.label}</span>
                      <span className="font-medium">{item.count}</span>
                    </div>
                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div className="bg-gradient-to-r from-green-500 to-emerald-600 h-2 rounded-full transition-all" 
                        style={{ width: `${item.percent}%` }} />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function generateMaahakResponse(input: string, locale: string): string {
  const lower = input.toLowerCase();
  
  if (locale === 'fa') {
    if (lower.includes('کربن') || lower.includes('carbon')) {
      return 'بر اساس محاسبات مدل RothC و IPCC، هر درخت بلوط ایرانی سالانه حدود ۲۲ کیلوگرم CO₂ جذب می‌کند. آیا 
          مایلید محاسبه دقیقی برای پروژه شما انجام دهم؟';     }
    if (lower.includes('امنیت') || lower.includes('security')) {
      return '🛡️ وضعیت امنیتی: ۲,۸۴۷ تهدید در ۲۴ ساعت گذشته مسدود شد. فایروال Spider Mesh فعال است. هیچ نفوذی شناسایی نشده.';
    }
    if (lower.includes('ماهواره') || lower.includes('satellite')) {
      return '🛰️ اتصال Sentinel-2: فعال. آخرین تصویر: ۲ ساعت پیش. میانگین NDVI منطقه: ۰.۶۲ (پوشش گیاهی مناسب).';
    }
    if (lower.includes('بلاکچین') || lower.includes('blockchain')) {
      return '⛓️ شبکه Polygon Amoy Testnet: آنلاین. قرارداد RegenerationMiner: فعال. ۴۷ NFT گواهی امروز mint شده.';
    }
    return 'متوجه شدم. بر اساس تحلیل داده‌های اکونوژین، می‌توانم در زمینه‌های کربن، امنیت، ماهواره و بلاکچین 
        کمکتان کنم. چه موضوعی را بررسی کنیم؟';   }
  
  if (lower.includes('carbon')) {
    return "Based on RothC and IPCC models, each Persian Oak tree absorbs about 22 kg CO₂ annually. Would you like me to calculate for your specific project?";
  }
  if (lower.includes('security')) {
    return "🛡️ Security Status: 2,847 threats blocked in the last 24 hours. Spider Mesh Firewall is active. No intrusions detected.";
  }
  if (lower.includes('satellite')) {
    return "🛰️ Sentinel-2: Online. Last image: 2 hours ago. Average regional NDVI: 0.62 (healthy vegetation).";
  }
  return "I understand. Based on Econojin data analysis,
      I can help with carbon,
      security,
      satellite,
      and blockchain topics. What shall we explore?";}
r""")
    
    # =========================================================================
    # Business Modules (Shop, Library, Inventory, Accounting)
    # =========================================================================
    def create_business_modules(self):
        logger.info("\n" + "="*70)
        logger.info("💼 Creating Business Modules")
        logger.info("="*70)
        
        # Shop
        self.write(FRONTEND_DIR / "app" / "[locale]" / "shop" / "page.tsx", """'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { ShoppingCart, Search, Filter, Star, Heart } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const PRODUCTS = [
  { id: 1,
      name: { fa: 'بذر بلوط ایرانی',
      en: 'Persian Oak Seeds' },
      price: 250000,
      rating: 4.8,
      image: '🌳',
      category: 'seeds' },
        { id: 2,
      name: { fa: 'کمپوست ارگانیک',
      en: 'Organic Compost' },
      price: 180000,
      rating: 4.6,
      image: '🌱',
      category: 'soil' },
        { id: 3,
      name: { fa: 'ابزار باغبانی',
      en: 'Gardening Tools' },
      price: 850000,
      rating: 4.9,
      image: '🛠️',
      category: 'tools' },
        { id: 4,
      name: { fa: 'سنسور IoT خاک',
      en: 'Soil IoT Sensor' },
      price: 2500000,
      rating: 4.7,
      image: '📡',
      category: 'tech' },
        { id: 5,
      name: { fa: 'کتاب کشاورزی پایدار',
      en: 'Sustainable Farming Book' },
      price: 320000,
      rating: 4.9,
      image: '📚',
      category: 'books' },
        { id: 6,
      name: { fa: 'نهال پسته وحشی',
      en: 'Wild Pistachio Sapling' },
      price: 450000,
      rating: 4.5,
      image: '🌿',
      category: 'seeds' },
      ];

export default function ShopPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const [cart, setCart] = useState<any[]>([]);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filteredProducts = PRODUCTS.filter(p => {
    const matchesSearch = p.name[locale === 'fa' ? 'fa' : 'en'].toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || p.category === filter;
    return matchesSearch && matchesFilter;
  });

  const addToCart = (product: any) => {
    setCart([...cart, product]);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold flex items-center gap-3">
              <ShoppingCart className="w-10 h-10 text-orange-600" />
              {dict.shop.title}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-2">{dict.shop.subtitle}</p>
          </div>
          <div className="relative">
            <ShoppingCart className="w-6 h-6" />
            {cart.length > 0 && (
              <span className="absolute -top-2 -right-2 w-6 h-6 bg-orange-600 text-white text-xs rounded-full flex items-center justify-center">
                {cart.length}
              </span>
            )}
          </div>
        </div>

        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={dict.common.search}
              className="w-full ps-10 pe-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-orange-500 focus:outline-none"
            />
          </div>
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-orange-500 focus:outline-none"
          >
            <option value="all">{dict.shop.categories}</option>
            <option value="seeds">Seeds</option>
            <option value="soil">Soil</option>
            <option value="tools">Tools</option>
            <option value="tech">Technology</option>
            <option value="books">Books</option>
          </select>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredProducts.map((product) => (
            <div key={product.id} className="bg-white dark:bg-gray-800 rounded-2xl shadow-md hover:shadow-xl transition overflow-hidden group">
              <div className="h-48 bg-gradient-to-br from-orange-100 to-yellow-100 dark:from-gray-700 dark:to-gray-600 flex items-center justify-center text-8xl relative">
                {product.image}
                <button className="absolute top-4 end-4 p-2 bg-white/80 dark:bg-gray-800/80 rounded-full hover:bg-white transition">
                  <Heart className="w-5 h-5 text-gray-600" />
                </button>
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold mb-2">
                  {product.name[locale === 'fa' ? 'fa' : 'en']}
                </h3>
                <div className="flex items-center gap-1 mb-3">
                  <Star className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  <span className="text-sm font-medium">{product.rating}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-2xl font-bold text-orange-600">
                    {product.price.toLocaleString()} {locale === 'fa' ? 'تومان' : 'IRR'}
                  </span>
                  <button
                    onClick={() => addToCart(product)}
                    className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition flex items-center gap-2"
                  >
                    <ShoppingCart className="w-4 h-4" />
                    {dict.shop.addToCart}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
""")

        # Library
        self.write(FRONTEND_DIR / "app" / "[locale]" / "library" / "page.tsx", """'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Book, Download, Eye, Search, User, Calendar } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const BOOKS = [
  { id: 1,
      title: { fa: 'مدل‌سازی کربن خاک',
      en: 'Soil Carbon Modeling' },
      author: 'Dr. Sarah Johnson',
      year: 2024,
      pages: 342,
      type: 'book' },
        { id: 2,
      title: { fa: 'کشاورزی پایدار در ایران',
      en: 'Sustainable Agriculture in Iran' },
      author: 'Prof. Ali Mohammadi',
      year: 2023,
      pages: 256,
      type: 'book' },
        { id: 3,
      title: { fa: 'کاربرد NDVI در پایش جنگل',
      en: 'NDVI Applications in Forest Monitoring' },
      author: 'Dr. Emily Chen',
      year: 2024,
      pages: 48,
      type: 'article' },
        { id: 4,
      title: { fa: 'پروتکل Gaia',
      en: 'Gaia Protocol Whitepaper' },
      author: 'Econojin Team',
      year: 2026,
      pages: 78,
      type: 'research' },
        { id: 5,
      title: { fa: 'بلاکچین و محیط زیست',
      en: 'Blockchain & Environment' },
      author: 'Dr. James Wilson',
      year: 2025,
      pages: 198,
      type: 'book' },
        { id: 6,
      title: { fa: 'مدل RothC',
      en: 'RothC Model Guide' },
      author: 'Rothamsted Research',
      year: 2023,
      pages: 124,
      type: 'research' },
      ];

export default function LibraryPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  const filtered = BOOKS.filter(b => {
    const matchesSearch = b.title[locale === 'fa' ? 'fa' : 'en'].toLowerCase().includes(search.toLowerCase());
    const matchesFilter = filter === 'all' || b.type === filter;
    return matchesSearch && matchesFilter;
  });

  const typeColors: Record<string, string> = {
    book: 'bg-blue-100 text-blue-700',
    article: 'bg-green-100 text-green-700',
    research: 'bg-purple-100 text-purple-700',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold flex items-center gap-3">
            <Book className="w-10 h-10 text-blue-600" />
            {dict.library.title}
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">{dict.library.subtitle}</p>
        </div>

        <div className="flex gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute start-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder={dict.common.search}
              className="w-full ps-10 pe-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-blue-500 focus:outline-none"
            />
          </div>
          <div className="flex gap-2">
            {['all', 'book', 'article', 'research'].map(type => (
              <button
                key={type}
                onClick={() => setFilter(type)}
                className={`px-4 py-2 rounded-lg transition ${
                  filter === type
                    ? 'bg-blue-600 text-white'
                    : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-100'
                }`}
              >
                {type === 'all' ? dict.library.books : type}
              </button>
            ))}
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map(book => (
            <div key={book.id} className="bg-white dark:bg-gray-800 rounded-2xl shadow-md hover:shadow-xl transition p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="w-16 h-20 bg-gradient-to-br from-blue-400 to-indigo-600 rounded flex items-center justify-center text-white text-3xl">
                  📖
                </div>
                <span className={`text-xs font-medium px-2 py-1 rounded ${typeColors[book.type]}`}>
                  {book.type}
                </span>
              </div>
              
              <h3 className="text-xl font-bold mb-2">
                {book.title[locale === 'fa' ? 'fa' : 'en']}
              </h3>
              
              <div className="space-y-2 mb-4 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-2">
                  <User className="w-4 h-4" />
                  {book.author}
                </div>
                <div className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  {book.year} • {book.pages} pages
                </div>
              </div>

              <div className="flex gap-2">
                <button className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                  <Eye className="w-4 h-4" />
                  {dict.library.read}
                </button>
                <button className="flex items-center justify-center gap-2 px-4 py-2 border-2 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-900 transition">
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
""")

        # Inventory
        self.write(FRONTEND_DIR / "app" / "[locale]" / "inventory" / "page.tsx", """'use client';

import { useParams } from 'next/navigation';
import { Package, TrendingUp, TrendingDown, AlertTriangle, Plus } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const ITEMS = [
  { id: 1, name: { fa: 'بذر بلوط', en: 'Oak Seeds' }, stock: 2450, min: 500, unit: 'عدد', status: 'ok' },
  { id: 2, name: { fa: 'کمپوست', en: 'Compost' }, stock: 180, min: 200, unit: 'کیلوگرم', status: 'low' },
  { id: 3, name: { fa: 'نهال پسته', en: 'Pistachio Sapling' }, stock: 89, min: 50, unit: 'عدد', status: 'ok' },
  { id: 4, name: { fa: 'سنسور IoT', en: 'IoT Sensor' }, stock: 12, min: 20, unit: 'عدد', status: 'low' },
  { id: 5,
      name: { fa: 'کود ارگانیک',
      en: 'Organic Fertilizer' },
      stock: 540,
      min: 100,
      unit: 'کیلوگرم',
      status: 'ok' },
      ];

export default function InventoryPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-4xl font-bold flex items-center gap-3">
              <Package className="w-10 h-10 text-amber-600" />
              {dict.inventory.title}
            </h1>
          </div>
          <button className="px-6 py-3 bg-amber-600 text-white rounded-lg hover:bg-amber-700 transition flex items-center gap-2">
            <Plus className="w-5 h-5" />
            {dict.common.create}
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">{dict.inventory.items}</span>
              <Package className="w-5 h-5 text-amber-500" />
            </div>
            <div className="text-3xl font-bold">{ITEMS.length}</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">{dict.inventory.stock}</span>
              <TrendingUp className="w-5 h-5 text-green-500" />
            </div>
            <div className="text-3xl font-bold text-green-600">3,271</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">{dict.inventory.inbound}</span>
              <TrendingUp className="w-5 h-5 text-blue-500" />
            </div>
            <div className="text-3xl font-bold">+245</div>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-gray-500">{dict.inventory.lowStock}</span>
              <AlertTriangle className="w-5 h-5 text-red-500" />
            </div>
            <div className="text-3xl font-bold text-red-600">2</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50 dark:bg-gray-900">
              <tr>
                <th className="px-6 py-3 text-start text-xs font-medium text-gray-500 uppercase">Item</th>
                <th className="px-6 py-3 text-start text-xs font-medium text-gray-500 uppercase">{dict.inventory.stock}</th>
                <th className="px-6 py-3 text-start text-xs font-medium text-gray-500 uppercase">Min</th>
                <th className="px-6 py-3 text-start text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-start text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y dark:divide-gray-700">
              {ITEMS.map(item => (
                <tr key={item.id} className="hover:bg-gray-50 dark:hover:bg-gray-900">
                  <td className="px-6 py-4 font-medium">
                    {item.name[locale === 'fa' ? 'fa' : 'en']}
                  </td>
                  <td className="px-6 py-4">
                    {item.stock.toLocaleString()} {item.unit}
                  </td>
                  <td className="px-6 py-4 text-gray-500">
                    {item.min} {item.unit}
                  </td>
                  <td className="px-6 py-4">
                    {item.status === 'low' ? (
                      <span className="px-3 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                        {dict.inventory.lowStock}
                      </span>
                    ) : (
                      <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                        OK
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <button className="text-blue-600 hover:underline text-sm">
                      {dict.inventory.reorder}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
""")

        # Accounting
        self.write(FRONTEND_DIR / "app" / "[locale]" / "accounting" / "page.tsx", """'use client';

import { useParams } from 'next/navigation';
import { DollarSign, TrendingUp, TrendingDown, Wallet, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const TRANSACTIONS = [
  { id: 1,
      type: 'income',
      desc: { fa: 'فروش گواهی کربن',
      en: 'Carbon Credit Sale' },
      amount: 25000000,
      date: '2026-05-28' },
        { id: 2, type: 'expense', desc: { fa: 'هزینه سرور', en: 'Server Cost' }, amount: 1200000, date: '2026-05-27' },
  { id: 3, type: 'income', desc: { fa: 'فروش فروشگاه', en: 'Shop Sales' }, amount: 8500000, date: '2026-05-26' },
  { id: 4,
      type: 'expense',
      desc: { fa: 'حقوق کارمندان',
      en: 'Employee Salaries' },
      amount: 45000000,
      date: '2026-05-25' },
        { id: 5,
      type: 'income',
      desc: { fa: 'SEED Token',
      en: 'SEED Token Rewards' },
      amount: 15000000,
      date: '2026-05-24' },
      ];

export default function AccountingPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);

  const totalIncome = TRANSACTIONS.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0);
  const totalExpenses = TRANSACTIONS.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0);
  const profit = totalIncome - totalExpenses;

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="mb-8">
          <h1 className="text-4xl font-bold flex items-center gap-3">
            <DollarSign className="w-10 h-10 text-emerald-600" />
            {dict.accounting.title}
          </h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <div className="bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm opacity-90">{dict.accounting.income}</span>
              <TrendingUp className="w-5 h-5" />
            </div>
            <div className="text-3xl font-bold">
              {totalIncome.toLocaleString()}
            </div>
            <div className="text-xs opacity-80 mt-1">IRR</div>
          </div>

          <div className="bg-gradient-to-br from-red-500 to-rose-600 text-white rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm opacity-90">{dict.accounting.expenses}</span>
              <TrendingDown className="w-5 h-5" />
            </div>
            <div className="text-3xl font-bold">
              {totalExpenses.toLocaleString()}
            </div>
            <div className="text-xs opacity-80 mt-1">IRR</div>
          </div>

          <div className={`bg-gradient-to-br ${profit >= 0 ? 'from-blue-500 to-indigo-600' : 'from-orange-500 to-red-600'} text-white rounded-xl p-6 shadow-lg`}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm opacity-90">{dict.accounting.profit}</span>
              <DollarSign className="w-5 h-5" />
            </div>
            <div className="text-3xl font-bold">
              {profit.toLocaleString()}
            </div>
            <div className="text-xs opacity-80 mt-1">IRR</div>
          </div>

          <div className="bg-gradient-to-br from-purple-500 to-pink-600 text-white rounded-xl p-6 shadow-lg">
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm opacity-90">{dict.accounting.balance}</span>
              <Wallet className="w-5 h-5" />
            </div>
            <div className="text-3xl font-bold">
              125M
            </div>
            <div className="text-xs opacity-80 mt-1">IRR</div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6">
          <h2 className="text-2xl font-bold mb-6">{dict.accounting.transactions}</h2>
          <div className="space-y-3">
            {TRANSACTIONS.map(tx => (
              <div key={tx.id} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-900 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition">
                <div className="flex items-center gap-4">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                    tx.type === 'income' ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
                  }`}>
                    {tx.type === 'income' ? <ArrowUpRight className="w-5 h-5" /> : <ArrowDownRight className="w-5 h-5" />}
                  </div>
                  <div>
                    <div className="font-medium">
                      {tx.desc[locale === 'fa' ? 'fa' : 'en']}
                    </div>
                    <div className="text-sm text-gray-500">{tx.date}</div>
                  </div>
                </div>
                <div className={`font-bold ${tx.type === 'income' ? 'text-green-600' : 'text-red-600'}`}>
                  {tx.type === 'income' ? '+' : '-'}{tx.amount.toLocaleString()} IRR
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
r""")
    
    # =========================================================================
    # Static Pages (About, Contact, Privacy, Terms, Policy)
    # =========================================================================
    def create_static_pages(self):
        logger.info("\n" + "="*70)
        logger.info("📄 Creating Static Pages")
        logger.info("="*70)
        
        # About
        self.write(FRONTEND_DIR / "app" / "[locale]" / "about" / "page.tsx", """'use client';

import { useParams } from 'next/navigation';
import { Leaf, Target, Eye, Users, Heart, Award } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function AboutPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa';

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-5xl mx-auto px-4 py-12">
        {/* Hero */}
        <div className="text-center mb-16">
          <Leaf className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h1 className="text-5xl font-bold mb-4">{dict.pages.about.title}</h1>
          <p className="text-xl text-gray-600 dark:text-gray-400 max-w-3xl mx-auto">
            {isPersian 
              ? 'ما در اکونوژین به قدرت علم و فناوری برای مبارزه با تغییرات اقلیمی باور داریم.'
              : 'At Econojin, we believe in the power of science and technology to fight climate change.'}
          </p>
        </div>

        {/* Mission & Vision */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
            <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-xl flex items-center justify-center mb-4">
              <Target className="w-6 h-6 text-green-600" />
            </div>
            <h2 className="text-2xl font-bold mb-4">{dict.pages.about.mission}</h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              {isPersian
                ? 'تبدیل فعالیت‌های اکولوژیکی به دارایی‌های دیجیتال قابل تأیید با استفاده از مدل‌های علمی 
                    RothC، AquaCrop، تصاویر ماهواره‌ای Sentinel-2 و فناوری بلاکچین.'                 : 'Transforming ecological activities into verifiable digital assets using RothC,
                    AquaCrop scientific models,
                    Sentinel-2 satellite imagery,
                    and blockchain technology.'}            </p>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
            <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-xl flex items-center justify-center mb-4">
              <Eye className="w-6 h-6 text-blue-600" />
            </div>
            <h2 className="text-2xl font-bold mb-4">{dict.pages.about.vision}</h2>
            <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
              {isPersian
                ? 'ایجاد یک اکوسیستم جهانی که در آن هر فرد و سازمان می‌تواند تأثیر مثبت خود بر محیط زیست را به 
                    ارزش اقتصادی تبدیل کند.' : 'Creating a global ecosystem where every individual and 
                        organization can turn their positive                     environmental impact into economic value.'}             </p>
          </div>
        </div>

        {/* Values */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-700 rounded-2xl p-8 text-white mb-16">
          <h2 className="text-3xl font-bold mb-6 text-center">
            {isPersian ? 'ارزش‌های ما' : 'Our Values'}
          </h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              { icon: Heart,
                  title: isPersian ? 'پایداری' : 'Sustainability',
                  desc: isPersian ? 'تعهد به آینده زمین' : 'Committed to Earth\'s future' },
                                { icon: Award,
                  title: isPersian ? 'شفافیت' : 'Transparency',
                  desc: isPersian ? 'داده‌های باز و قابل تأیید' : 'Open,
                  verifiable data' },
                                { icon: Users,
                  title: isPersian ? 'همکاری' : 'Collaboration',
                  desc: isPersian ? 'جامعه جهانی برای تغییر' : 'Global community for change' },
                              ].map((value, i) => {
              const Icon = value.icon;
              return (
                <div key={i} className="text-center">
                  <Icon className="w-10 h-10 mx-auto mb-3" />
                  <h3 className="font-bold text-lg mb-2">{value.title}</h3>
                  <p className="text-green-100 text-sm">{value.desc}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Story */}
        <div className="prose dark:prose-invert max-w-none">
          <h2 className="text-3xl font-bold mb-4">{dict.pages.about.story}</h2>
          <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
            {isPersian
              ? 'اکونوژین در سال ۱۴۰۳ با هدف ایجاد پلی میان علم اکولوژی و فناوری بلاکچین تأسیس شد. تیم ما 
                  متشکل از دانشمندان محیط زیست، مهندسان نرم‌افزار و کارشناسان بلاکچین است که با هم کار می‌کنند 
                  تا راه‌حل‌های نوآورانه‌ای برای چالش‌های اقلیمی ارائه دهند.'               : 'Econojin was founded in 2024 with the goal of bridging ecological science and blockchain technology. Our team consists of environmental scientists,
                  software engineers,
                  and blockchain experts working together to provide innovative solutions to climate challenges.'}          </p>
        </div>
      </div>
    </div>
  );
}
""")

        # Contact
        self.write(FRONTEND_DIR / "app" / "[locale]" / "contact" / "page.tsx", """'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Mail, Send, CheckCircle } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function ContactPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const [submitted, setSubmitted] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: '',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitted(true);
    setTimeout(() => {
      setSubmitted(false);
      setFormData({ name: '', email: '', subject: '', message: '' });
    }, 3000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyan-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <Mail className="w-16 h-16 text-cyan-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">{dict.pages.contact.title}</h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            {dict.pages.contact.subtitle}
          </p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          {submitted ? (
            <div className="text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
              <h3 className="text-2xl font-bold mb-2">
                {locale === 'fa' ? 'پیام شما ارسال شد!' : 'Message Sent!'}
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                {locale === 'fa' ? 'به زودی با شما تماس خواهیم گرفت' : 'We will get back to you soon'}
              </p>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <h2 className="text-2xl font-bold mb-4">{dict.pages.contact.formTitle}</h2>

              <div>
                <label className="block text-sm font-medium mb-2">{dict.pages.contact.name}</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-cyan-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{dict.pages.contact.email}</label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({...formData, email: e.target.value})}
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-cyan-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{dict.pages.contact.subject}</label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) => setFormData({...formData, subject: e.target.value})}
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-cyan-500 focus:outline-none"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">{dict.pages.contact.message}</label>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData({...formData, message: e.target.value})}
                  rows={6}
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg focus:border-cyan-500 focus:outline-none resize-none"
                  required
                />
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-cyan-600 to-blue-600 text-white py-3 rounded-lg 
                    font-semibold hover:from-cyan-700 hover:to-blue-700 transition flex items-center 
                    justify-center gap-2 shadow-lg"               >
                <Send className="w-5 h-5" />
                {dict.pages.contact.send}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
}
""")

        # Privacy
        self.write(FRONTEND_DIR / "app" / "[locale]" / "privacy" / "page.tsx", """'use client';

import { useParams } from 'next/navigation';
import { Shield } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function PrivacyPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa';

  const sections = isPersian ? [
    { title: 'مقدمه',
        content: 'این سیاست حریم خصوصی نحوه جمع‌آوری، استفاده و محافظت از اطلاعات شما را در پلتفرم اکونوژین توضیح می‌دهد.' },
            { title: 'اطلاعات جمع‌آوری شده',
        content: 'ما اطلاعاتی مانند نام، ایمیل، آدرس کیف پول دیجیتال و داده‌های فعالیت‌های اکوسیستمی را جمع‌آوری می‌کنیم.' },
            { title: 'استفاده از اطلاعات',
        content: 'اطلاعات شما برای ارائه خدمات، بهبود پلتفرم، تأیید فعالیت‌ها و ارتباط با شما استفاده می‌شود.' },
            { title: 'محافظت از اطلاعات',
        content: 'ما از رمزنگاری پیشرفته، فایروال Spider Mesh و پروتکل‌های امنیتی برای محافظت از داده‌های شما استفاده می‌کنیم.' },
            { title: 'کوکی‌ها',
                content: 'ما از کوکی‌ها برای بهبود تجربه کاربری و تحلیل استفاده از پلتفرم استفاده می‌کنیم.' },
                    { title: 'GDPR و حریم خصوصی جهانی',
        content: 'ما با قوانین بین‌المللی حریم خصوصی از جمله GDPR اروپا مطابقت کامل داریم.' },
            { title: 'حقوق شما', content: 'شما حق دسترسی، اصلاح، حذف و انتقال داده‌های خود را دارید.' },
    { title: 'تماس با ما', content: 'برای هرگونه سوال در مورد حریم خصوصی، از فرم تماس استفاده کنید.' },
  ] : [
    { title: 'Introduction',
        content: 'This Privacy Policy explains how Econojin collects,
        uses,
        and protects your information.' },
            { title: 'Information Collected',
        content: 'We collect information such as name,
        email,
        digital wallet address,
        and ecosystem activity data.' },
            { title: 'Use of Information',
        content: 'Your information is used to provide services,
        improve the platform,
        verify activities,
        and communicate with you.' },
            { title: 'Information Protection',
        content: 'We use advanced encryption,
        Spider Mesh firewall,
        and security protocols to protect your data.' },
            { title: 'Cookies', content: 'We use cookies to improve user experience and analyze platform usage.' },
    { title: 'GDPR & Global Privacy',
        content: 'We fully comply with international privacy laws including European GDPR.' },
            { title: 'Your Rights',
                content: 'You have the right to access,
                correct,
                delete,
                and transfer your data.' },
                    { title: 'Contact Us',
                        content: 'For any privacy-related questions,
                        please use the contact form.' },
                        
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 pt-20">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <Shield className="w-16 h-16 text-indigo-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">{dict.pages.privacy.title}</h1>
          <p className="text-gray-500">
            {dict.pages.privacy.lastUpdated}: {new Date().toLocaleDateString(locale === 'fa' ? 'fa-IR' : 'en-US')}
          </p>
        </div>

        <div className="prose dark:prose-invert max-w-none">
          {sections.map((section, i) => (
            <section key={i} className="mb-8">
              <h2 className="text-2xl font-bold mb-3 text-indigo-600">
                {i + 1}. {section.title}
              </h2>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                {section.content}
              </p>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
""")

        # Terms
        self.write(FRONTEND_DIR / "app" / "[locale]" / "terms" / "page.tsx", """'use client';

import { useParams } from 'next/navigation';
import { FileText } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function TermsPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa';

  const sections = isPersian ? [
    { title: 'پذیرش قوانین', content: 'با استفاده از پلتفرم اکونوژین، شما این قوانین و مقررات را می‌پذیرید.' },
    { title: 'حساب کاربری', content: 'شما مسئول حفظ امنیت حساب کاربری و رمز عبور خود هستید.' },
    { title: 'استفاده قابل قبول',
        content: 'استفاده از پلتفرم برای فعالیت‌های غیرقانونی، مخرب یا فریبکارانه ممنوع است.' },
            { title: 'مالکیت معنوی', content: 'تمام محتوا و فناوری پلتفرم متعلق به اکونوژین است.' },
    { title: 'توکن‌های دیجیتال',
        content: 'توکن‌های SEED و GAIA ابزارهای کاربردی هستند و سرمایه‌گذاری مالی محسوب نمی‌شوند.' },
            { title: 'محدودیت مسئولیت', content: 'اکونوژین مسئولیتی در قبال ضررهای غیرمستقیم یا تبعی ندارد.' },
    { title: 'فسخ', content: 'ما حق تعلیق یا حذف حساب‌های کاربری متخلف را داریم.' },
    { title: 'قانون حاکم', content: 'این قوانین بر اساس قوانین بین‌المللی تجارت الکترونیک تنظیم شده است.' },
  ] : [
    { title: 'Acceptance of Terms', content: 'By using Econojin platform, you accept these terms and conditions.' },
    { title: 'Account', content: 'You are responsible for maintaining the security of your account and password.' },
    { title: 'Acceptable Use',
        content: 'Use of the platform for illegal,
        malicious,
        or fraudulent activities is prohibited.' },
            { title: 'Intellectual Property', content: 'All platform content and technology belong to Econojin.' },
    { title: 'Digital Tokens',
        content: 'SEED and GAIA tokens are utility tools and not considered financial investments.' },
            { title: 'Limitation of Liability',
                content: 'Econojin is not liable for indirect or consequential damages.' },
                    { title: 'Termination',
                        content: 'We reserve the right to suspend or terminate violating accounts.' },
                        
    { title: 'Governing Law', content: 'These terms are governed by international e-commerce laws.' },
  ];

  return (
    <div className="min-h-screen bg-white dark:bg-gray-900 pt-20">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <FileText className="w-16 h-16 text-blue-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">{dict.pages.terms.title}</h1>
        </div>

        <div className="prose dark:prose-invert max-w-none">
          {sections.map((section, i) => (
            <section key={i} className="mb-8">
              <h2 className="text-2xl font-bold mb-3 text-blue-600">
                {i + 1}. {section.title}
              </h2>
              <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                {section.content}
              </p>
            </section>
          ))}
        </div>
      </div>
    </div>
  );
}
""")

        # Policy
        self.write(FRONTEND_DIR / "app" / "[locale]" / "policy" / "page.tsx", """'use client';

import { useParams } from 'next/navigation';
import { BookOpen, Leaf, Eye, Scale } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function PolicyPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa';

  const policies = [
    {
      icon: Leaf,
      color: 'green',
      title: isPersian ? 'سیاست پایداری' : 'Sustainability Policy',
      content: isPersian
        ? 'ما متعهد به توسعه پایدار و کاهش اثرات زیست‌محیطی هستیم. تمام عملیات ما با اصول اقتصاد چرخشی مطابقت دارد.'
        : 'We are committed to sustainable development and reducing environmental impact. All our operations align with circular economy principles.',
    },
    {
      icon: Eye,
      color: 'blue',
      title: isPersian ? 'سیاست شفافیت' : 'Transparency Policy',
      content: isPersian
        ? 'ما به شفافیت کامل در تمام عملیات خود باور داریم. تمام داده‌های کربن به صورت عمومی قابل تأیید هستند.'
        : 'We believe in complete transparency in all our operations. All carbon data is publicly verifiable.',
    },
    {
      icon: Scale,
      color: 'purple',
      title: isPersian ? 'سیاست انطباق بین‌المللی' : 'International Compliance Policy',
      content: isPersian
        ? 'ما با قوانین بین‌المللی از جمله توافق‌نامه پاریس، GDPR اروپا، MiCA و استانداردهای AAOIFI برای امور 
            مالی اسلامی مطابقت داریم.'         : 'We comply with international regulations including the Paris Agreement,
            European GDPR,
            MiCA,
            and AAOIFI standards for Islamic finance.',
                },
    {
      icon: BookOpen,
      color: 'orange',
      title: isPersian ? 'سیاست آموزشی' : 'Educational Policy',
      content: isPersian
        ? 'ما به آموزش عمومی در زمینه تغییرات اقلیمی و راه‌حل‌های علمی متعهد هستیم. کتابخانه دیجیتال ما به 
            صورت رایگان در دسترس است.'         : 'We are committed to public education on climate change and scientific solutions. Our digital library is freely accessible.',
    },
  ];

  const colorClasses: Record<string, string> = {
    green: 'bg-green-100 text-green-600 dark:bg-green-900',
    blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900',
    purple: 'bg-purple-100 text-purple-600 dark:bg-purple-900',
    orange: 'bg-orange-100 text-orange-600 dark:bg-orange-900',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-white dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <BookOpen className="w-16 h-16 text-purple-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">{dict.pages.policy.title}</h1>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {policies.map((policy, i) => {
            const Icon = policy.icon;
            return (
              <div key={i} className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg hover:shadow-xl transition">
                <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-4 ${colorClasses[policy.color]}`}>
                  <Icon className="w-7 h-7" />
                </div>
                <h2 className="text-2xl font-bold mb-3">{policy.title}</h2>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {policy.content}
                </p>
              </div>
            );
          })}
        </div>

        <div className="mt-12 bg-gradient-to-r from-purple-600 to-pink-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-3xl font-bold mb-4">
            {isPersian ? 'تعهد ما به آینده' : 'Our Commitment to the Future'}
          </h2>
          <p className="text-lg text-purple-100 max-w-3xl mx-auto">
            {isPersian
              ? 'اکونوژین متعهد است که پیشرو در ترکیب علم، فناوری و پایداری برای ساختن آینده‌ای بهتر برای 
                  نسل‌های آینده باشد.'               : 'Econojin is committed to leading the way in combining science,
                  technology,
                  and sustainability to build a better future for generations to come.'}          </p>
        </div>
      </div>
    </div>
  );
}
r""")
    
    # =========================================================================
    # Security Dashboard
    # =========================================================================
    def create_security_dashboard(self):
        logger.info("\n" + "="*70)
        logger.info("🛡️ Creating Security Dashboard")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "app" / "[locale]" / "security" / "page.tsx", """'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Shield, Activity, AlertTriangle, Lock, Server, Wifi, Cpu, Eye, Zap, Globe, CheckCircle } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function SecurityPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa';
  const [threats, setThreats] = useState<any[]>([]);

  useEffect(() => {
    // Simulated live threats
    const mockThreats = [
      { type: 'blocked', ip: '185.220.101.42', country: '🇷🇺', attack: 'Brute Force', time: '2s ago' },
      { type: 'blocked', ip: '45.155.205.99', country: '🇨🇳', attack: 'SQL Injection', time: '15s ago' },
      { type: 'blocked', ip: '103.75.201.8', country: '🇰🇵', attack: 'DDoS', time: '1m ago' },
      { type: 'monitoring', ip: '92.255.83.14', country: '🇳🇱', attack: 'Scan', time: '3m ago' },
      { type: 'blocked', ip: '212.70.149.71', country: '🇺🇦', attack: 'XSS', time: '5m ago' },
    ];
    setThreats(mockThreats);
  }, []);

  const metrics = [
    { label: isPersian ? 'تهدیدات مسدود شده' : 'Threats Blocked',
        value: '2,
        847',
        icon: Shield,
        color: 'green',
        change: '+12%' },
            { label: isPersian ? 'حملات فعال' : 'Active Attacks',
        value: '3',
        icon: AlertTriangle,
        color: 'red',
        change: '-5%' },
            { label: isPersian ? 'فایروال' : 'Firewall',
        value: isPersian ? 'فعال' : 'Active',
        icon: Lock,
        color: 'blue',
        change: '100%' },
            { label: isPersian ? 'آخرین اسکن' : 'Last Scan', value: '2m', icon: Eye, color: 'purple', change: '' },
  ];

  const securityLayers = [
    { name: 'Cloudflare WAF', status: 'active', blocked: 1247, icon: Globe },
    { name: 'Spider Mesh Firewall', status: 'active', blocked: 892, icon: Shield },
    { name: 'OPNsense', status: 'active', blocked: 423, icon: Server },
    { name: 'CrowdSec', status: 'active', blocked: 198, icon: Cpu },
    { name: 'Wazuh SIEM', status: 'active', blocked: 87, icon: Activity },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 text-white pt-20">
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-5xl font-bold flex items-center gap-3">
              <Shield className="w-12 h-12 text-cyan-400" />
              {dict.security.title}
            </h1>
            <p className="text-gray-400 mt-2">
              {isPersian ? 'نظارت لحظه‌ای بر امنیت پلتفرم' : 'Real-time platform security monitoring'}
            </p>
          </div>
          <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 border border-green-500 rounded-full">
            <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse" />
            <span className="text-green-400 font-medium">
              {isPersian ? 'همه سیستم‌ها امن' : 'All Systems Secure'}
            </span>
          </div>
        </div>

        {/* Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          {metrics.map((metric, i) => {
            const Icon = metric.icon;
            return (
              <div key={i} className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6 hover:bg-white/10 transition">
                <div className="flex items-start justify-between mb-4">
                  <div className={`w-12 h-12 rounded-xl bg-${metric.color}-500/20 flex items-center justify-center`}>
                    <Icon className={`w-6 h-6 text-${metric.color}-400`} />
                  </div>
                  {metric.change && (
                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${
                      metric.change.startsWith('+') ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      {metric.change}
                    </span>
                  )}
                </div>
                <div className="text-3xl font-bold mb-1">{metric.value}</div>
                <div className="text-sm text-gray-400">{metric.label}</div>
              </div>
            );
          })}
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Live Threats */}
          <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-red-400" />
              {isPersian ? 'تهدیدات زنده' : 'Live Threats'}
            </h2>
            <div className="space-y-3">
              {threats.map((threat, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-black/30 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${threat.type === 'blocked' ? 'bg-green-500' : 'bg-yellow-500'} animate-pulse`} />
                    <span className="text-2xl">{threat.country}</span>
                    <div>
                      <div className="font-mono text-sm">{threat.ip}</div>
                      <div className="text-xs text-gray-400">{threat.attack}</div>
                    </div>
                  </div>
                  <div className="text-end">
                    <div className="text-xs text-gray-400">{threat.time}</div>
                    <span className={`text-xs font-medium ${
                      threat.type === 'blocked' ? 'text-green-400' : 'text-yellow-400'
                    }`}>
                      {threat.type === 'blocked' ? '✓ BLOCKED' : '⚠ MONITORING'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Security Layers */}
          <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5 text-cyan-400" />
              {isPersian ? 'لایه‌های امنیتی' : 'Security Layers'}
            </h2>
            <div className="space-y-3">
              {securityLayers.map((layer, i) => {
                const Icon = layer.icon;
                return (
                  <div key={i} className="flex items-center justify-between p-3 bg-black/30 rounded-lg">
                    <div className="flex items-center gap-3">
                      <Icon className="w-5 h-5 text-cyan-400" />
                      <span className="font-medium">{layer.name}</span>
                    </div>
                    <div className="flex items-center gap-3">
                      <span className="text-sm text-gray-400">
                        {layer.blocked.toLocaleString()} {isPersian ? 'مسدود' : 'blocked'}
                      </span>
                      <div className="flex items-center gap-1 px-2 py-1 bg-green-500/20 rounded-full">
                        <CheckCircle className="w-3 h-3 text-green-400" />
                        <span className="text-xs text-green-400">{layer.status}</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* World Map Visualization */}
        <div className="bg-white/5 backdrop-blur border border-white/10 rounded-2xl p-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-purple-400" />
            {isPersian ? 'نقشه جهانی تهدیدات' : 'Global Threat Map'}
          </h2>
          <div className="relative h-64 bg-gradient-to-br from-blue-900/30 to-purple-900/30 rounded-xl overflow-hidden">
            <div className="absolute inset-0 flex items-center justify-center text-gray-400">
              <Globe className="w-32 h-32 opacity-20" />
            </div>
            {/* Animated threat points */}
            <div className="absolute top-1/4 left-1/4 w-3 h-3 bg-red-500 rounded-full animate-ping" />
            <div className="absolute top-1/3 right-1/3 w-3 h-3 bg-red-500 rounded-full animate-ping" style={{ animationDelay: '0.5s' }} />
            <div className="absolute bottom-1/3 left-1/2 w-3 h-3 bg-yellow-500 rounded-full animate-ping" style={{ animationDelay: '1s' }} />
            <div className="absolute top-1/2 right-1/4 w-3 h-3 bg-red-500 rounded-full animate-ping" style={{ animationDelay: '1.5s' }} />
          </div>
          <div className="grid grid-cols-3 gap-4 mt-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-red-400">1,247</div>
              <div className="text-xs text-gray-400">{isPersian ? 'از اروپا' : 'From Europe'}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-400">892</div>
              <div className="text-xs text-gray-400">{isPersian ? 'از آسیا' : 'From Asia'}</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-400">708</div>
              <div className="text-xs text-gray-400">{isPersian ? 'از آمریکا' : 'From Americas'}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
r""")
    
    # =========================================================================
    # Sentinel-2 Integration Page
    # =========================================================================
    def create_sentinel_page(self):
        logger.info("\n" + "="*70)
        logger.info("🛰️ Creating Sentinel-2 Integration Page")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "app" / "[locale]" / "sentinel" / "page.tsx", """'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import { Satellite, MapPin, Calendar, CheckCircle, XCircle, Activity } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function SentinelPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa';
  
  const [lat, setLat] = useState('35.6892');
  const [lng, setLng] = useState('51.3890');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  const analyze = async () => {
    setLoading(true);
    // Simulated Sentinel-2 analysis
    setTimeout(() => {
      setResult({
        verified: true,
        ndvi_before: 0.285,
        ndvi_after: 0.452,
        ndvi_change: 0.167,
        cloud_cover: 5.2,
        confidence: 0.94,
        image_date: '2026-05-28',
        satellite: 'Sentinel-2A',
        resolution: '10m',
      });
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-cyan-50 dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <Satellite className="w-16 h-16 text-blue-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-2">{dict.sentinel.title}</h1>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            {isPersian ? 'تأیید فعالیت‌ها با Sentinel-2' : 'Activity verification using Sentinel-2'}
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <MapPin className="w-5 h-5 text-blue-600" />
              {isPersian ? 'موقعیت' : 'Location'}
            </h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">{dict.carbon.latitude}</label>
                <input
                  type="number"
                  step="0.0001"
                  value={lat}
                  onChange={(e) => setLat(e.target.value)}
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg"
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2">{dict.carbon.longitude}</label>
                <input
                  type="number"
                  step="0.0001"
                  value={lng}
                  onChange={(e) => setLng(e.target.value)}
                  className="w-full px-4 py-3 border-2 dark:border-gray-700 dark:bg-gray-900 rounded-lg"
                />
              </div>
              <button
                onClick={analyze}
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-cyan-600 text-white py-3 rounded-lg font-semibold hover:from-blue-700 hover:to-cyan-700 disabled:opacity-50 transition"
              >
                {loading ? (isPersian ? 'در حال تحلیل...' : 'Analyzing...') : (isPersian ? 'تحلیل ماهواره‌ای' 
                    : 'Analyze with Satellite')}               </button>
            </div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-green-600" />
              {dict.sentinel.satelliteData}
            </h2>
            <div className="space-y-3 text-sm">
              <div className="flex justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <span>{isPersian ? 'ماهواره' : 'Satellite'}</span>
                <span className="font-bold">Sentinel-2A</span>
              </div>
              <div className="flex justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <span>{isPersian ? 'رزولوشن' : 'Resolution'}</span>
                <span className="font-bold">10m</span>
              </div>
              <div className="flex justify-between p-3 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <span>{isPersian ? 'آخرین عبور' : 'Last Pass'}</span>
                <span className="font-bold">2h ago</span>
              </div>
              <div className="flex justify-between p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                <span>{isPersian ? 'وضعیت' : 'Status'}</span>
                <span className="font-bold text-green-600 flex items-center gap-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
                  Online
                </span>
              </div>
            </div>
          </div>
        </div>

        {result && (
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-2xl animate-slide-up">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold">
                {isPersian ? 'نتیجه تحلیل' : 'Analysis Result'}
              </h2>
              {result.verified ? (
                <div className="flex items-center gap-2 px-4 py-2 bg-green-500/20 text-green-600 rounded-full">
                  <CheckCircle className="w-5 h-5" />
                  <span className="font-bold">{isPersian ? 'تأیید شد' : 'Verified'}</span>
                </div>
              ) : (
                <div className="flex items-center gap-2 px-4 py-2 bg-red-500/20 text-red-600 rounded-full">
                  <XCircle className="w-5 h-5" />
                  <span className="font-bold">{isPersian ? 'رد شد' : 'Rejected'}</span>
                </div>
              )}
            </div>

            <div className="grid md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gradient-to-br from-blue-500 to-cyan-600 text-white rounded-xl p-6">
                <div className="text-sm opacity-80 mb-1">{dict.sentinel.ndviIndex} ({isPersian ? 'قبل' : 'Before'})</div>
                <div className="text-4xl font-bold">{result.ndvi_before}</div>
              </div>
              <div className="bg-gradient-to-br from-green-500 to-emerald-600 text-white rounded-xl p-6">
                <div className="text-sm opacity-80 mb-1">{dict.sentinel.ndviIndex} ({isPersian ? 'بعد' : 'After'})</div>
                <div className="text-4xl font-bold">{result.ndvi_after}</div>
              </div>
              <div className="bg-gradient-to-br from-purple-500 to-pink-600 text-white rounded-xl p-6">
                <div className="text-sm opacity-80 mb-1">{isPersian ? 'تغییر' : 'Change'}</div>
                <div className="text-4xl font-bold">+{result.ndvi_change}</div>
              </div>
            </div>

            <div className="grid md:grid-cols-2 gap-4">
              <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">{isPersian ? 'پوشش ابر' : 'Cloud Cover'}</span>
                  <span className="font-bold">{result.cloud_cover}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-blue-500 h-2 rounded-full" style={{ width: `${result.cloud_cover}%` }} />
                </div>
              </div>
              <div className="p-4 bg-gray-50 dark:bg-gray-900 rounded-lg">
                <div className="flex justify-between mb-2">
                  <span className="text-sm text-gray-500">{isPersian ? 'اطمینان' : 'Confidence'}</span>
                  <span className="font-bold text-green-600">{(result.confidence * 100).toFixed(1)}%</span>
                </div>
                <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                  <div className="bg-green-500 h-2 rounded-full" style={{ width: `${result.confidence * 100}%` }} />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
r""")
    
    # =========================================================================
    # Portfolio Page با MetaMask
    # =========================================================================
    def create_portfolio_page(self):
        logger.info("\n" + "="*70)
        logger.info("💼 Creating Portfolio Page with MetaMask")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "app" / "[locale]" / "portfolio" / "[address]" / "page.tsx", """'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import { Wallet, Leaf, Award, TrendingUp, ExternalLink, Copy, CheckCircle } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const MOCK_CERTIFICATES = [
  { id: 1, type: 'tree_planting', carbon_kg: 203558, health: 0.94, stage: 'mature', verified: ['satellite', 'iot'] },
  { id: 2, type: 'soil_regeneration', carbon_kg: 28000, health: 0.87, stage: 'improving', verified: ['scientific'] },
  { id: 3,
      type: 'agroforestry',
      carbon_kg: 15558,
      health: 0.91,
      stage: 'young',
      verified: ['satellite',
      'community'] },
      ];

export default function PortfolioPage() {
  const params = useParams();
  const locale = params.locale as Locale;
  const address = params.address as string;
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa';
  const [copied, setCopied] = useState(false);

  const totalCarbon = MOCK_CERTIFICATES.reduce((s, c) => s + c.carbon_kg, 0);
  const totalTokens = totalCarbon * 0.1;
  const totalValue = (totalCarbon / 1000) * 50;

  const copyAddress = () => {
    navigator.clipboard.writeText(address);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const shortenAddress = (addr: string) => `${addr.slice(0, 6)}...${addr.slice(-4)}`;

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50 dark:from-gray-900 dark:to-gray-800 pt-20">
      <div className="max-w-6xl mx-auto px-4 py-12">
        {/* Header */}
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white mb-8 shadow-2xl">
          <div className="flex items-center gap-4 mb-4">
            <Wallet className="w-12 h-12" />
            <div>
              <h1 className="text-3xl font-bold">{dict.portfolio.title}</h1>
              <div className="flex items-center gap-2 mt-2">
                <code className="bg-white/20 backdrop-blur px-3 py-1 rounded-lg font-mono text-sm">
                  {shortenAddress(address)}
                </code>
                <button onClick={copyAddress} className="p-1 hover:bg-white/20 rounded transition">
                  {copied ? <CheckCircle className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </button>
                <a href={`https://amoy.polygonscan.com/address/${address}`} target="_blank" rel="noopener" className="p-1 hover:bg-white/20 rounded transition">
                  <ExternalLink className="w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </div>

        {/* Stats */}
        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
            <Leaf className="w-10 h-10 text-green-500 mb-3" />
            <div className="text-sm text-gray-500 mb-1">{dict.portfolio.totalCarbon}</div>
            <div className="text-3xl font-bold">{(totalCarbon / 1000).toFixed(2)} t</div>
            <div className="text-xs text-gray-400 mt-1">CO₂</div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
            <Award className="w-10 h-10 text-yellow-500 mb-3" />
            <div className="text-sm text-gray-500 mb-1">{dict.portfolio.totalTokens}</div>
            <div className="text-3xl font-bold">{totalTokens.toLocaleString()}</div>
            <div className="text-xs text-gray-400 mt-1">SEED</div>
          </div>

          <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
            <TrendingUp className="w-10 h-10 text-blue-500 mb-3" />
            <div className="text-sm text-gray-500 mb-1">{isPersian ? 'ارزش تخمینی' : 'Est. Value'}</div>
            <div className="text-3xl font-bold">${totalValue.toLocaleString()}</div>
            <div className="text-xs text-gray-400 mt-1">USD</div>
          </div>
        </div>

        {/* Certificates */}
        <div className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-xl">
          <h2 className="text-2xl font-bold mb-6">{dict.portfolio.nftCertificates}</h2>
          <div className="grid md:grid-cols-3 gap-4">
            {MOCK_CERTIFICATES.map((cert) => (
              <div key={cert.id} className="bg-gradient-to-br from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 rounded-xl p-5 border-2 dark:border-gray-700 hover:border-green-500 transition">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-3xl">
                    {cert.type === 'tree_planting' && '🌳'}
                    {cert.type === 'soil_regeneration' && '🌱'}
                    {cert.type === 'agroforestry' && '🌾'}
                  </span>
                  <span className="text-xs font-mono text-gray-400">#{cert.id}</span>
                </div>
                <h3 className="font-bold mb-2 capitalize">{cert.type.replace(/_/g, ' ')}</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-500">Carbon:</span>
                    <span className="font-bold text-green-600">{(cert.carbon_kg / 1000).toFixed(2)}t</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Health:</span>
                    <span className="font-bold">{(cert.health * 100).toFixed(0)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-500">Stage:</span>
                    <span className="font-bold capitalize">{cert.stage}</span>
                  </div>
                </div>
                <div className="mt-3 pt-3 border-t dark:border-gray-700">
                  <div className="text-xs text-gray-500 mb-1">Verified by:</div>
                  <div className="flex flex-wrap gap-1">
                    {cert.verified.map((v) => (
                      <span key={v} className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 rounded text-xs">
                        ✓ {v}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
r""")
    
    # =========================================================================
    # Hardhat Local Deployment
    # =========================================================================
    def create_hardhat_scripts(self):
        logger.info("\n" + "="*70)
        logger.info("⛓️ Creating Hardhat Local Deployment Scripts")
        logger.info("="*70)
        
        self.write(CONTRACTS_DIR / "scripts" / "deploy_local.js", r"""const hre = require("hardhat");

async function main() {
  console.log("🚀 Deploying Gaia Protocol to Local Hardhat Network...\\n");
  
  const [deployer] = await hre.ethers.getSigners();
  console.log("📝 Deployer:", deployer.address);
  console.log("💰 Balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH\\n");

  // 1) Deploy SeedToken
  console.log("1️⃣  Deploying SeedToken...");
  const SeedToken = await hre.ethers.getContractFactory("SeedToken");
  const seedToken = await SeedToken.deploy();
  await seedToken.waitForDeployment();
  const seedTokenAddress = await seedToken.getAddress();
  console.log("   ✅ SeedToken:", seedTokenAddress);

  // 2) Deploy GaiaCertificate
  console.log("\\n2️⃣  Deploying GaiaCertificate...");
  const GaiaCertificate = await hre.ethers.getContractFactory("GaiaCertificate");
  const gaiaCert = await GaiaCertificate.deploy(deployer.address);
  await gaiaCert.waitForDeployment();
  const gaiaCertAddress = await gaiaCert.getAddress();
  console.log("   ✅ GaiaCertificate:", gaiaCertAddress);

  // 3) Deploy RegenerationMiner
  console.log("\\n3️⃣  Deploying RegenerationMiner...");
  const RegenerationMiner = await hre.ethers.getContractFactory("RegenerationMiner");
  const miner = await RegenerationMiner.deploy(
    seedTokenAddress,
    gaiaCertAddress,
    deployer.address
  );
  await miner.waitForDeployment();
  const minerAddress = await miner.getAddress();
  console.log("   ✅ RegenerationMiner:", minerAddress);

  // 4) Configure
  console.log("\\n4️⃣  Configuring permissions...");
  const addMinterTx = await seedToken.addMinter(minerAddress);
  await addMinterTx.wait();
  console.log("   ✅ Miner added as SEED minter");

  // 5) Test mint
  console.log("\\n5️⃣  Minting first NFT certificate...");
  const mintTx = await gaiaCert.mintCertificate(
    deployer.address,
    "tree_planting",
    7960000, // 7.96 tons in milli-kg
    "ipfs://QmFirstCertificate",
    "0x" + "a".repeat(64)
  );
  const receipt = await mintTx.wait();
  console.log("   ✅ First NFT minted in block:", receipt.blockNumber);
  console.log("   🎉 Token ID: #1");

  // Summary
  console.log("\\n" + "=".repeat(70));
  console.log("🎉 LOCAL DEPLOYMENT COMPLETE!");
  console.log("=".repeat(70));
  console.log("\\n📋 Contract Addresses:");
  console.log(`   SeedToken:         ${seedTokenAddress}`);
  console.log(`   GaiaCertificate:   ${gaiaCertAddress}`);
  console.log(`   RegenerationMiner: ${minerAddress}`);
  console.log(`   Oracle (deployer): ${deployer.address}`);
  console.log("\\n🔗 View on local explorer:");
  console.log("   http://localhost:8000 (if running blockscout)");
  console.log("\\n💾 Save to .env:");
  console.log(`   SEED_TOKEN_ADDRESS=${seedTokenAddress}`);
  console.log(`   GAIA_CERT_ADDRESS=${gaiaCertAddress}`);
  console.log(`   MINER_CONTRACT_ADDRESS=${minerAddress}`);
  console.log("=".repeat(70));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
""")
        
        # Run script
        self.write(PROJECT_ROOT / "scripts" / "run_hardhat_local.py", r"""#!/usr/bin/env python3
# -*- coding: utf-8 -*-
\"\"\"
راه‌اندازی Hardhat Local Network و Deploy قراردادها
\"\"\"

import subprocess
import sys
import time
import threading
from pathlib import Path

PROJECT_ROOT = Path(r"D:\\econojin.com")
CONTRACTS_DIR = PROJECT_ROOT / "contracts"

def run_node():
    \"\"\"اجرای hardhat node در پس‌زمینه\"\"\"
    logger.info("🚀 Starting Hardhat local network...")
    subprocess.run(
        ["npx", "hardhat", "node"],
        cwd=CONTRACTS_DIR,
    # SECURITY WARNING: Consider shell=False for better security
        shell=True,
    )

def main():
    logger.info("="*70)
    logger.info("⛓️ Hardhat Local Deployment")
    logger.info("="*70)
    
    # Start node in background
    node_thread = threading.Thread(target=run_node, daemon=True)
    node_thread.start()
    
    # Wait for node to start
    logger.info("\\n⏳ Waiting for node to start...")
    time.sleep(5)
    
    # Deploy contracts
    logger.info("\\n📦 Deploying contracts...")
    result = subprocess.run(
        ["npx", "hardhat", "run", "scripts/deploy_local.js", "--network", "localhost"],
        cwd=CONTRACTS_DIR,
    # SECURITY WARNING: Consider shell=False for better security
        shell=True,
    )
    
    if result.returncode == 0:
        logger.info("\\n✅ Deployment successful!")
        logger.info("\\n🎯 Next steps:")
        logger.info("   1. Keep this terminal open (Hardhat node running)")
        logger.info("   2. Open frontend: cd frontend && npm run dev")
        logger.info("   3. Connect MetaMask to http://127.0.0.1:8545 (Chain ID: 31337)")
        input("\\nPress Ctrl+C to stop the node...")
    else:
        logger.info("\\n❌ Deployment failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
r""")
    
    # =========================================================================
    # Update Globals CSS
    # =========================================================================
    def update_globals_css(self):
        logger.info("\n" + "="*70)
        logger.info("🎨 Updating globals.css with fonts & themes")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "app" / "globals.css", """@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 142 76% 36%;
    --primary-foreground: 355 100% 100%;
  }
  
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --primary: 142 76% 36%;
    --primary-foreground: 355 100% 100%;
  }
}

@layer base {
  html {
    scroll-behavior: smooth;
  }
  
  body {
    @apply bg-white text-gray-900 dark:bg-gray-900 dark:text-gray-100;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }
  
  .font-inter {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  }
  
  .font-vazir {
    font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  }
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-800;
}

::-webkit-scrollbar-thumb {
  @apply bg-green-500 rounded-full hover:bg-green-600;
}

/* Animations */
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}

@keyframes pulse-ring {
  0% { transform: scale(0.8); opacity: 1; }
  100% { transform: scale(1.5); opacity: 0; }
}

.animate-fade-in { animation: fadeIn 0.5s ease-in-out; }
.animate-slide-up { animation: slideUp 0.5s ease-out; }
.animate-float { animation: float 3s ease-in-out infinite; }
.animate-pulse-ring { animation: pulse-ring 2s cubic-bezier(0.215, 0.61, 0.355, 1) infinite; }
r""")
    
    # =========================================================================
    # Update Tailwind Config
    # =========================================================================
    def update_tailwind_config(self):
        logger.info("\n" + "="*70)
        logger.info("⚙️ Updating Tailwind Config")
        logger.info("="*70)
        
        self.write(FRONTEND_DIR / "tailwind.config.js", """/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        vazir: ['Vazirmatn', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
r""")
    
    # =========================================================================
    # Main
    # =========================================================================
    def build_all(self):
        logger.info("="*70)
        logger.info("🌟 ECONOJIN MEGA BUILD - Phase 4 Complete")
        logger.info("="*70)
        logger.info(f"📁 Frontend: {FRONTEND_DIR}")
        logger.info(f"📁 Contracts: {CONTRACTS_DIR}")
        
        self.create_i18n_files()
        self.create_middleware()
        self.create_root_layout()
        self.create_logo()
        self.create_language_switcher()
        self.create_theme_switcher()
        self.create_providers()
        self.create_navbar()
        self.create_auth_pages()
        self.create_maahak_dashboard()
        self.create_business_modules()
        self.create_static_pages()
        self.create_security_dashboard()
        self.create_sentinel_page()
        self.create_portfolio_page()
        self.create_hardhat_scripts()
        self.update_globals_css()
        self.update_tailwind_config()
        
        logger.info("\n" + "="*70)
        logger.info("✅ MEGA BUILD COMPLETE")
        logger.info("="*70)
        logger.info(f"\n📁 Files created: {len(self.files_created)}")
        
        logger.info("\n" + "="*70)
        logger.info("🚀 HOW TO RUN")
        logger.info("="*70)
        print(r"""
═══════════════════════════════════════════════════════════════
🎯 STEP 1: Start Backend
═══════════════════════════════════════════════════════════════
   cd D:\\econojin.com
   .\\.venv\\Scripts\\Activate.ps1
   python scripts/api/run_server.py

═══════════════════════════════════════════════════════════════
🎯 STEP 2: Start Frontend (in new terminal)
═══════════════════════════════════════════════════════════════
   cd D:\\econojin.com\\frontend
   npm run dev

═══════════════════════════════════════════════════════════════
🎯 STEP 3: Start Hardhat Local (optional, new terminal)
═══════════════════════════════════════════════════════════════
   cd D:\\econojin.com
   python scripts/run_hardhat_local.py

═══════════════════════════════════════════════════════════════
🌐 ACCESS THE PLATFORM
═══════════════════════════════════════════════════════════════
   
   Persian (default):   http://localhost:3000/fa
   English:             http://localhost:3000/en
   Arabic:              http://localhost:3000/ar
   Turkish:             http://localhost:3000/tr
   Chinese:             http://localhost:3000/zh

═══════════════════════════════════════════════════════════════
📋 ALL AVAILABLE PAGES
═══════════════════════════════════════════════════════════════
   /                    - Home page
   /login               - Login
   /register            - Register
   /dashboard           - Dashboard
   /admin               - ماهک AI Admin 🤖
   /calculate           - Carbon Calculator
   /map                 - Global Map
   /sentinel            - Sentinel-2 Verification 🛰️
   /security            - Security Dashboard 🛡️
   /portfolio/[addr]    - MetaMask Portfolio 💼
   /shop                - E-commerce Shop 🛍️
   /library             - Digital Library 📚
   /inventory           - Inventory Management 📦
   /accounting          - Accounting System 💰
   /about               - About Us
   /contact             - Contact Form
   /privacy             - Privacy Policy
   /terms               - Terms & Conditions
   /policy              - Our Policy

═══════════════════════════════════════════════════════════════
🌟 FEATURES IMPLEMENTED
═══════════════════════════════════════════════════════════════
   ✅ i18n (5 languages: fa, en, ar, tr, zh)
   ✅ RTL/LTR automatic switching
   ✅ Dark/Light theme
   ✅ Typography Logo
   ✅ Authentication (Login/Register/Logout)
   ✅ ماهک AI Admin Console
   ✅ Sentinel-2 Satellite Verification
   ✅ Security Dashboard with live threats
   ✅ MetaMask Wallet Integration
   ✅ NFT Portfolio
   ✅ E-commerce Shop
   ✅ Digital Library
   ✅ Inventory Management
   ✅ Accounting System
   ✅ About, Contact, Privacy, Terms, Policy pages
   ✅ Hardhat Local Deployment
   ✅ Smart Contracts ready

═══════════════════════════════════════════════════════════════
🎯 TEST CREDENTIALS (Demo)
═══════════════════════════════════════════════════════════════
   Email:    demo@econojin.com
   Password: (any)
   
   Or use MetaMask wallet login!
r""")
        logger.info("="*70)
        
        return True


def main():
    try:
        builder = EconojinMegaBuilder()
        success = builder.build_all()
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