# ============================================================================
# افزودن ۴ ماژول جدید: حسابداری، انبارداری، وبلاگ، خبرنامه
# ============================================================================

$ErrorActionPreference = "Stop"
$ROOT = "D:\econojin.com"
$WEB_DIR = "$ROOT\apps\web\src"

Write-Host "🚀 افزودن ۴ ماژول جدید به اکو نوژین" -ForegroundColor Cyan
Write-Host ("=" * 70)

# ============================================================================
# 1. ایجاد صفحه حسابداری (Accounting)
# ============================================================================
Write-Host "`n📊 ایجاد صفحه حسابداری..." -ForegroundColor Yellow

$accountingContent = @'
"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Calculator, Banknote, TrendingUp, FileText, PieChart, Wallet, Clock, CheckCircle } from "lucide-react";

export default function AccountingPage() {
  const features = [
    { icon: FileText, title: "صدور فاکتور", desc: "فاکتورهای رسمی و حرفه‌ای با محاسبات خودکار مالیات و تخفیف" },
    { icon: PieChart, title: "گزارش‌های مالی", desc: "ترازنامه، صورت سود و زیان، جریان وجوه نقد" },
    { icon: Wallet, title: "مدیریت هزینه‌ها", desc: "ردیابی دقیق هزینه‌های کشاورزی، نهاده‌ها و نیروی کار" },
    { icon: TrendingUp, title: "تحلیل سودآوری", desc: "محاسبه سود هر محصول، هر مزرعه و هر فصل" },
    { icon: Banknote, title: "حسابداری تعهدی", desc: "ثبت دقیق درآمدها و هزینه‌ها بر اساس استانداردهای حسابداری" },
    { icon: Calculator, title: "محاسبه بهای تمام‌شده", desc: "محاسبه دقیق بهای تمام‌شده هر کیلوگرم محصول" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600 to-indigo-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-blue-400 hover:text-blue-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-2xl">
                <Calculator className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/20 border border-amber-500/30 rounded-full text-amber-300 text-xs font-bold mb-3">
                  <Clock className="h-3 w-3" /> به زودی
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">ماژول حسابداری</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  سیستم حسابداری تخصصی کشاورزی با قابلیت محاسبه بهای تمام‌شده، 
                  مدیریت هزینه‌های مزرعه و گزارش‌های مالی حرفه‌ای
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Coming Soon */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto text-center bg-gradient-to-br from-blue-900/20 to-indigo-900/20 border border-blue-500/30 rounded-3xl p-12">
          <div className="inline-flex p-6 rounded-full bg-blue-500/10 mb-6">
            <Clock className="h-16 w-16 text-blue-400" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">این ماژول در حال توسعه است</h2>
          <p className="text-lg text-slate-300 leading-relaxed mb-8">
            تیم اکو نوژین در حال ساخت یک سیستم حسابداری پیشرفته است که 
            به‌طور خاص برای نیازهای کشاورزان و تولیدکنندگان طراحی شده است.
            <br />
            به زودی با امکانات کامل در دسترس شما قرار خواهد گرفت.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold transition-colors"
          >
            <ArrowRight className="h-5 w-5" />
            بازگشت به صفحه اصلی
          </Link>
        </div>
      </section>

      {/* Features Preview */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          امکاناتی که <span className="text-blue-400">در راه است</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 opacity-70"
            >
              <div className="p-3 rounded-xl bg-blue-500/10 inline-block mb-4">
                <feature.icon className="h-8 w-8 text-blue-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'@

$accountingPath = "$WEB_DIR\app\accounting\page.tsx"
New-Item -ItemType Directory -Path (Split-Path $accountingPath) -Force | Out-Null
[System.IO.File]::WriteAllText($accountingPath, $accountingContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ صفحه حسابداری ایجاد شد" -ForegroundColor Green


# ============================================================================
# 2. ایجاد صفحه انبارداری (Inventory)
# ============================================================================
Write-Host "`n📦 ایجاد صفحه انبارداری..." -ForegroundColor Yellow

$inventoryContent = @'
"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Package, Warehouse, Boxes, Barcode, Truck, TrendingDown, Clock, Shield } from "lucide-react";

export default function InventoryPage() {
  const features = [
    { icon: Package, title: "مدیریت موجودی", desc: "ردیابی لحظه‌ای موجودی نهاده‌ها، بذر، کود و محصولات" },
    { icon: Warehouse, title: "مدیریت انبار", desc: "مدیریت چند انبار، قفسه‌بندی و جانمایی هوشمند" },
    { icon: Barcode, title: "بارکد و QR Code", desc: "اسکن سریع محصولات و ثبت ورود و خروج خودکار" },
    { icon: Truck, title: "ورود و خروج", desc: "ثبت دقیق تمام تراکنش‌های انبار با جزئیات کامل" },
    { icon: TrendingDown, title: "نقطه سفارش", desc: "هشدار خودکار هنگام رسیدن موجودی به حداقل" },
    { icon: Shield, title: "کنترل تاریخ انقضا", desc: "مدیریت FIFO و جلوگیری از ضایعات محصولات" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-orange-600 to-red-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-orange-400 hover:text-orange-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-orange-500 to-red-600 shadow-2xl">
                <Warehouse className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/20 border border-amber-500/30 rounded-full text-amber-300 text-xs font-bold mb-3">
                  <Clock className="h-3 w-3" /> به زودی
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">ماژول انبارداری</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  سیستم مدیریت انبار هوشمند برای کشاورزان، با قابلیت ردیابی نهاده‌ها، 
                  محصولات و تجهیزات از لحظه ورود تا خروج
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Coming Soon */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto text-center bg-gradient-to-br from-orange-900/20 to-red-900/20 border border-orange-500/30 rounded-3xl p-12">
          <div className="inline-flex p-6 rounded-full bg-orange-500/10 mb-6">
            <Clock className="h-16 w-16 text-orange-400" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">این ماژول در حال توسعه است</h2>
          <p className="text-lg text-slate-300 leading-relaxed mb-8">
            یک سیستم انبارداری مدرن و ساده در حال ساخت است که به شما کمک می‌کند 
            موجودی انبار، نهاده‌ها و محصولات خود را به‌صورت حرفه‌ای مدیریت کنید.
            <br />
            با قابلیت اسکن بارکد، هشدار موجودی و گزارش‌های پیشرفته.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-8 py-4 bg-orange-600 hover:bg-orange-700 text-white rounded-xl font-bold transition-colors"
          >
            <ArrowRight className="h-5 w-5" />
            بازگشت به صفحه اصلی
          </Link>
        </div>
      </section>

      {/* Features Preview */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          امکاناتی که <span className="text-orange-400">در راه است</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {features.map((feature, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 opacity-70"
            >
              <div className="p-3 rounded-xl bg-orange-500/10 inline-block mb-4">
                <feature.icon className="h-8 w-8 text-orange-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'@

$inventoryPath = "$WEB_DIR\app\inventory\page.tsx"
New-Item -ItemType Directory -Path (Split-Path $inventoryPath) -Force | Out-Null
[System.IO.File]::WriteAllText($inventoryPath, $inventoryContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ صفحه انبارداری ایجاد شد" -ForegroundColor Green


# ============================================================================
# 3. ایجاد صفحه وبلاگ (Blog)
# ============================================================================
Write-Host "`n📝 ایجاد صفحه وبلاگ..." -ForegroundColor Yellow

$blogContent = @'
"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, PenLine, BookOpen, Tag, User, Calendar, Clock, MessageSquare } from "lucide-react";

export default function BlogPage() {
  const categories = [
    { name: "کشاورزی پایدار", count: 24, color: "#10b981" },
    { name: "مدیریت آب", count: 18, color: "#3b82f6" },
    { name: "تغییر اقلیم", count: 15, color: "#f59e0b" },
    { name: "فناوری کشاورزی", count: 21, color: "#8b5cf6" },
    { name: "احیای زمین", count: 12, color: "#ec4899" },
    { name: "داستان موفقیت", count: 9, color: "#06b6d4" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-purple-600 to-pink-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-purple-400 hover:text-purple-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-purple-500 to-pink-600 shadow-2xl">
                <PenLine className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/20 border border-amber-500/30 rounded-full text-amber-300 text-xs font-bold mb-3">
                  <Clock className="h-3 w-3" /> به زودی
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">وبلاگ اکو نوژین</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  مقالات تخصصی، تجربیات کشاورزان، آخرین تحقیقات علمی و داستان‌های 
                  موفقیت در حوزه احیای زمین و کشاورزی پایدار
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Coming Soon */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto text-center bg-gradient-to-br from-purple-900/20 to-pink-900/20 border border-purple-500/30 rounded-3xl p-12">
          <div className="inline-flex p-6 rounded-full bg-purple-500/10 mb-6">
            <Clock className="h-16 w-16 text-purple-400" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">این ماژول در حال توسعه است</h2>
          <p className="text-lg text-slate-300 leading-relaxed mb-8">
            وبلاگ اکو نوژین به زودی با مقالات تخصصی از کارشناسان برجسته، 
            تجربیات واقعی کشاورزان و آخرین دستاوردهای علمی در حوزه احیای زمین 
            در دسترس شما قرار خواهد گرفت.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-8 py-4 bg-purple-600 hover:bg-purple-700 text-white rounded-xl font-bold transition-colors"
          >
            <ArrowRight className="h-5 w-5" />
            بازگشت به صفحه اصلی
          </Link>
        </div>
      </section>

      {/* Categories Preview */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          دسته‌بندی‌های <span className="text-purple-400">آینده</span>
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 max-w-4xl mx-auto">
          {categories.map((cat, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.05 }}
              className="bg-slate-900/50 border border-slate-800 rounded-xl p-5 opacity-70"
            >
              <div className="flex items-center justify-between mb-2">
                <Tag className="h-5 w-5" style={{ color: cat.color }} />
                <span className="text-xs text-slate-500">{cat.count} مقاله</span>
              </div>
              <h3 className="font-bold text-white">{cat.name}</h3>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'@

$blogPath = "$WEB_DIR\app\blog\page.tsx"
New-Item -ItemType Directory -Path (Split-Path $blogPath) -Force | Out-Null
[System.IO.File]::WriteAllText($blogPath, $blogContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ صفحه وبلاگ ایجاد شد" -ForegroundColor Green


# ============================================================================
# 4. ایجاد صفحه خبرنامه (Newsletter)
# ============================================================================
Write-Host "`n📧 ایجاد صفحه خبرنامه..." -ForegroundColor Yellow

$newsletterContent = @'
"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, Mail, Newspaper, Bell, Gift, Users, Calendar, Clock, CheckCircle } from "lucide-react";

export default function NewsletterPage() {
  const benefits = [
    { icon: Newspaper, title: "مقالات اختصاصی", desc: "دسترسی زودهنگام به مقالات تخصصی قبل از انتشار عمومی" },
    { icon: Bell, title: "هشدارهای مهم", desc: "اطلاع‌رسانی فوری درباره رویدادها، وبینارها و فرصت‌ها" },
    { icon: Gift, title: "منابع رایگان", desc: "دریافت رایگان کتاب‌های الکترونیکی، گزارش‌ها و ابزارها" },
    { icon: Users, title: "جامعه اختصاصی", desc: "دسترسی به گروه ویژه مشترکان خبرنامه و شبکه‌سازی" },
    { icon: Calendar, title: "تقویم رویدادها", desc: "اطلاع از تمام رویدادهای مرتبط با کشاورزی پایدار" },
    { icon: CheckCircle, title: "بدون اسپم", desc: "فقط محتوای ارزشمند، حداکثر یک ایمیل در هفته" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-pink-600 to-rose-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-pink-400 hover:text-pink-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-pink-500 to-rose-600 shadow-2xl">
                <Mail className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-amber-500/20 border border-amber-500/30 rounded-full text-amber-300 text-xs font-bold mb-3">
                  <Clock className="h-3 w-3" /> به زودی
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">خبرنامه اکو نوژین</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  عضو خانواده اکو نوژین شوید و هر هفته جدیدترین مقالات، 
                  تحقیقات و فرصت‌های یادگیری را در ایمیل خود دریافت کنید
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Coming Soon */}
      <section className="container mx-auto px-6 py-16">
        <div className="max-w-4xl mx-auto text-center bg-gradient-to-br from-pink-900/20 to-rose-900/20 border border-pink-500/30 rounded-3xl p-12">
          <div className="inline-flex p-6 rounded-full bg-pink-500/10 mb-6">
            <Clock className="h-16 w-16 text-pink-400" />
          </div>
          <h2 className="text-4xl font-bold text-white mb-4">این ماژول در حال توسعه است</h2>
          <p className="text-lg text-slate-300 leading-relaxed mb-8">
            سیستم خبرنامه پیشرفته اکو نوژین در حال ساخت است. 
            به زودی می‌توانید با عضویت در خبرنامه، از جدیدترین مطالب، 
            رویدادها و فرصت‌های یادگیری مطلع شوید.
          </p>
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-8 py-4 bg-pink-600 hover:bg-pink-700 text-white rounded-xl font-bold transition-colors"
          >
            <ArrowRight className="h-5 w-5" />
            بازگشت به صفحه اصلی
          </Link>
        </div>
      </section>

      {/* Benefits Preview */}
      <section className="container mx-auto px-6 py-16">
        <h2 className="text-3xl font-bold text-white text-center mb-12">
          مزایای عضویت در <span className="text-pink-400">خبرنامه</span>
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
          {benefits.map((benefit, idx) => (
            <motion.div
              key={idx}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: idx * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 opacity-70"
            >
              <div className="p-3 rounded-xl bg-pink-500/10 inline-block mb-4">
                <benefit.icon className="h-8 w-8 text-pink-400" />
              </div>
              <h3 className="text-xl font-bold text-white mb-2">{benefit.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{benefit.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'@

$newsletterPath = "$WEB_DIR\app\newsletter\page.tsx"
New-Item -ItemType Directory -Path (Split-Path $newsletterPath) -Force | Out-Null
[System.IO.File]::WriteAllText($newsletterPath, $newsletterContent, [System.Text.Encoding]::UTF8)
Write-Host "   ✅ صفحه خبرنامه ایجاد شد" -ForegroundColor Green


# ============================================================================
# 5. به‌روزرسانی Navbar
# ============================================================================
Write-Host "`n🔗 به‌روزرسانی Navbar..." -ForegroundColor Yellow

$navbarPath = "$WEB_DIR\components\layout\Navbar.tsx"

if (Test-Path $navbarPath) {
    $navbarContent = [System.IO.File]::ReadAllText($navbarPath, [System.Text.Encoding]::UTF8)
    
    # بررسی اینکه لینک‌های جدید وجود ندارند
    if ("/blog" -notin $navbarContent) {
        # پیدا کردن محل مناسب برای اضافه کردن لینک‌ها
        # معمولاً قبل از دکمه تماس با ما یا ورود
        
        $newLinks = @'

              <Link href="/blog" className="text-slate-300 hover:text-purple-400 transition-colors">
                وبلاگ
              </Link>
              <Link href="/accounting" className="text-slate-300 hover:text-blue-400 transition-colors">
                حسابداری
              </Link>
              <Link href="/inventory" className="text-slate-300 hover:text-orange-400 transition-colors">
                انبارداری
              </Link>
'@
        
        # تلاش برای اضافه کردن قبل از لینک تماس با ما
        if ($navbarContent -match 'href="/contact"') {
            $navbarContent = $navbarContent -replace '(<Link[^>]*href="/contact"[^>]*>)', "$newLinks`n              `$1"
            Write-Host "   ✅ لینک‌های جدید به Navbar اضافه شد" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  محل دقیق برای اضافه کردن یافت نشد. به صورت دستی بررسی کنید." -ForegroundColor Yellow
        }
        
        [System.IO.File]::WriteAllText($navbarPath, $navbarContent, [System.Text.Encoding]::UTF8)
    } else {
        Write-Host "   ℹ️  لینک‌ها از قبل در Navbar وجود دارند" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ⚠️  Navbar.tsx یافت نشد" -ForegroundColor Yellow
}


# ============================================================================
# 6. به‌روزرسانی Footer
# ============================================================================
Write-Host "`n🔗 به‌روزرسانی Footer..." -ForegroundColor Yellow

$footerPath = "$WEB_DIR\components\layout\Footer.tsx"

if (Test-Path $footerPath) {
    $footerContent = [System.IO.File]::ReadAllText($footerPath, [System.Text.Encoding]::UTF8)
    
    if ("/blog" -notin $footerContent) {
        $newFooterLinks = @'
              <li>
                <Link href="/blog" className="text-slate-400 hover:text-purple-400 transition-colors">
                  وبلاگ
                </Link>
              </li>
              <li>
                <Link href="/newsletter" className="text-slate-400 hover:text-pink-400 transition-colors">
                  خبرنامه
                </Link>
              </li>
              <li>
                <Link href="/accounting" className="text-slate-400 hover:text-blue-400 transition-colors">
                  حسابداری
                </Link>
              </li>
              <li>
                <Link href="/inventory" className="text-slate-400 hover:text-orange-400 transition-colors">
                  انبارداری
                </Link>
              </li>
'@
        
        # اضافه کردن قبل از لینک تماس با ما در Footer
        if ($footerContent -match 'href="/contact"') {
            $footerContent = $footerContent -replace '(<Link[^>]*href="/contact"[^>]*>)', "$newFooterLinks`n              `$1"
            Write-Host "   ✅ لینک‌های جدید به Footer اضافه شد" -ForegroundColor Green
        }
        
        [System.IO.File]::WriteAllText($footerPath, $footerContent, [System.Text.Encoding]::UTF8)
    } else {
        Write-Host "   ℹ️  لینک‌ها از قبل در Footer وجود دارند" -ForegroundColor Cyan
    }
} else {
    Write-Host "   ⚠️  Footer.tsx یافت نشد" -ForegroundColor Yellow
}


# ============================================================================
# 7. پاک‌سازی کش Next.js
# ============================================================================
Write-Host "`n🧹 پاک‌سازی کش Next.js..." -ForegroundColor Yellow
$nextDir = "$ROOT\apps\web\.next"
if (Test-Path $nextDir) {
    Remove-Item -Path $nextDir -Recurse -Force -ErrorAction SilentlyContinue
    Write-Host "   ✅ پوشه .next حذف شد" -ForegroundColor Green
} else {
    Write-Host "   ℹ️  پوشه .next وجود نداشت" -ForegroundColor Cyan
}


# ============================================================================
# خلاصه نهایی
# ============================================================================
Write-Host "`n" -NoNewline
Write-Host ("=" * 70) -ForegroundColor Cyan
Write-Host "✅ تمام ماژول‌های جدید با موفقیت ایجاد شدند!" -ForegroundColor Green
Write-Host ("=" * 70) -ForegroundColor Cyan

Write-Host "`n🎯 ماژول‌های ایجاد شده:" -ForegroundColor Yellow
Write-Host "   📊 حسابداری (Accounting)     → /accounting" -ForegroundColor Blue
Write-Host "   📦 انبارداری (Inventory)     → /inventory" -ForegroundColor DarkYellow
Write-Host "   📝 وبلاگ (Blog)              → /blog" -ForegroundColor Magenta
Write-Host "   📧 خبرنامه (Newsletter)      → /newsletter" -ForegroundColor Pink

Write-Host "`n🔗 لینک‌های اضافه شده به:" -ForegroundColor Yellow
Write-Host "   ✅ Navbar (منوی بالا)" -ForegroundColor Green
Write-Host "   ✅ Footer (پاورقی)" -ForegroundColor Green

Write-Host "`n🚀 گام‌های بعدی:" -ForegroundColor Cyan
Write-Host "   1. سرور فرانت‌اند را اجرا کنید:"
Write-Host "      cd apps\web" -ForegroundColor White
Write-Host "      pnpm run dev -- -p 3001" -ForegroundColor White
Write-Host ""
Write-Host "   2. مشاهده صفحات جدید:" -ForegroundColor White
Write-Host "      • http://localhost:3001/accounting" -ForegroundColor Blue
Write-Host "      • http://localhost:3001/inventory" -ForegroundColor DarkYellow
Write-Host "      • http://localhost:3001/blog" -ForegroundColor Magenta
Write-Host "      • http://localhost:3001/newsletter" -ForegroundColor Pink

Write-Host "`n💡 نکته:" -ForegroundColor Yellow
Write-Host "   این صفحات فعلاً به صورت Placeholder (به زودی) ایجاد شده‌اند." -ForegroundColor White
Write-Host "   بعداً می‌توانید محتوای کامل را به آنها اضافه کنید." -ForegroundColor White

Write-Host ("=" * 70) -ForegroundColor Cyan