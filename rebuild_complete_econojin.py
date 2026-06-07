#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌍 بازسازی کامل اکو نوژین
وبسایت حرفه‌ای جامع با تمام ماژول‌ها و پنل‌ها
"""
import sys
import shutil
from pathlib import Path

def find_web_dir():
    candidates = [Path.cwd() / "apps" / "web", Path.cwd() / "web"]
    for c in candidates:
        if c.exists() and (c / "package.json").exists():
            return c
    return Path.cwd() / "apps" / "web"

def write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(path.parent.parent.parent)}")

# ========== Navbar حرفه‌ای ==========
def create_navbar(web_dir):
    print("\n🧭 ایجاد Navbar حرفه‌ای...")
    content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Leaf, Menu, X, ChevronDown, User, LogIn,
  Droplets, Wind, TreePine, Mountain, Sprout, CloudSun,
  Map, Satellite, BookOpen, GraduationCap, Users, ShoppingCart,
  Brain, Gamepad2, Coins, Monitor, Settings, Heart
} from "lucide-react";

const SCIENTIFIC_MODULES = [
  { id: "hydrology", title: "هیدرولوژی", icon: Droplets, href: "/hydrology" },
  { id: "soil-water", title: "آب خاک", icon: Wind, href: "/soil-water" },
  { id: "carbon", title: "کربن خاک", icon: TreePine, href: "/carbon" },
  { id: "erosion", title: "فرسایش خاک", icon: Mountain, href: "/erosion" },
  { id: "crop", title: "مدیریت محصول", icon: Sprout, href: "/crop" },
  { id: "weather", title: "هواشناسی", icon: CloudSun, href: "/weather" },
  { id: "gis", title: "GIS و نقشه", icon: Map, href: "/gis" },
  { id: "sentinel", title: "سنجش از دور", icon: Satellite, href: "/sentinel" },
];

const COMMUNITY_MODULES = [
  { id: "library", title: "کتابخانه علمی", icon: BookOpen, href: "/library" },
  { id: "education", title: "آموزش", icon: GraduationCap, href: "/education" },
  { id: "community", title: "جامعه کشاورزان", icon: Users, href: "/community" },
  { id: "shop", title: "فروشگاه", icon: ShoppingCart, href: "/shop" },
  { id: "psychology", title: "سلامت روان", icon: Heart, href: "/psychology" },
  { id: "games", title: "بازی‌های آموزشی", icon: Gamepad2, href: "/games" },
  { id: "ecomining", title: "EcoCoin", icon: Coins, href: "/ecomining" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);

  const isActive = (path: string) => pathname === path || pathname?.startsWith(path + "/");

  return (
    <nav className="sticky top-0 z-40 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-2 group">
            <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500 to-green-600 group-hover:shadow-lg group-hover:shadow-emerald-500/30 transition-all">
              <Leaf className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="font-bold text-white leading-tight">اکو نوژین</p>
              <p className="text-[10px] text-slate-400 leading-tight">احیای زمین</p>
            </div>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden lg:flex items-center gap-1">
            <Link href="/" className={`px-4 py-2 rounded-lg text-sm transition-colors ${isActive("/") && !pathname?.includes("/") ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800/50 hover:text-white"}`}>
              خانه
            </Link>

            {/* Scientific Dropdown */}
            <div className="relative" onMouseEnter={() => setOpenDropdown("scientific")} onMouseLeave={() => setOpenDropdown(null)}>
              <button className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white flex items-center gap-1 transition-colors">
                ماژول‌های علمی <ChevronDown className="h-4 w-4" />
              </button>
              <AnimatePresence>
                {openDropdown === "scientific" && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full right-0 mt-2 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2 grid grid-cols-1 gap-1">
                    {SCIENTIFIC_MODULES.map(mod => (
                      <Link key={mod.id} href={mod.href} className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors">
                        <mod.icon className="h-4 w-4 text-emerald-400" />
                        <span className="text-sm text-slate-200">{mod.title}</span>
                      </Link>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            {/* Community Dropdown */}
            <div className="relative" onMouseEnter={() => setOpenDropdown("community")} onMouseLeave={() => setOpenDropdown(null)}>
              <button className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white flex items-center gap-1 transition-colors">
                جامعه و خدمات <ChevronDown className="h-4 w-4" />
              </button>
              <AnimatePresence>
                {openDropdown === "community" && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full right-0 mt-2 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2 grid grid-cols-1 gap-1">
                    {COMMUNITY_MODULES.map(mod => (
                      <Link key={mod.id} href={mod.href} className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-slate-800 transition-colors">
                        <mod.icon className="h-4 w-4 text-emerald-400" />
                        <span className="text-sm text-slate-200">{mod.title}</span>
                      </Link>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <Link href="/education" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors">آموزش</Link>
            <Link href="/about" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors">درباره ما</Link>
            <Link href="/contact" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white transition-colors">تماس</Link>
          </div>

          {/* Auth Buttons */}
          <div className="hidden lg:flex items-center gap-2">
            <Link href="/login" className="px-4 py-2 text-sm text-slate-300 hover:text-white transition-colors flex items-center gap-1">
              <LogIn className="h-4 w-4" /> ورود
            </Link>
            <Link href="/register" className="px-4 py-2 bg-gradient-to-l from-emerald-500 to-green-600 text-white text-sm rounded-lg hover:shadow-lg hover:shadow-emerald-500/30 transition-all">
              ثبت‌نام رایگان
            </Link>
          </div>

          {/* Mobile Menu Button */}
          <button onClick={() => setMobileOpen(!mobileOpen)} className="lg:hidden p-2 text-slate-300 hover:text-white">
            {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div initial={{ height: 0 }} animate={{ height: "auto" }} exit={{ height: 0 }} className="lg:hidden overflow-hidden bg-slate-900 border-t border-slate-800">
            <div className="container mx-auto px-6 py-4 space-y-2">
              <Link href="/" onClick={() => setMobileOpen(false)} className="block px-4 py-2 rounded-lg text-slate-200 hover:bg-slate-800">خانه</Link>
              <div className="border-t border-slate-800 pt-2 mt-2">
                <p className="px-4 py-1 text-xs text-slate-500 uppercase">ماژول‌های علمی</p>
                {SCIENTIFIC_MODULES.map(mod => (
                  <Link key={mod.id} href={mod.href} onClick={() => setMobileOpen(false)} className="flex items-center gap-2 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded-lg">
                    <mod.icon className="h-4 w-4 text-emerald-400" /> {mod.title}
                  </Link>
                ))}
              </div>
              <div className="border-t border-slate-800 pt-2 mt-2">
                <p className="px-4 py-1 text-xs text-slate-500 uppercase">جامعه و خدمات</p>
                {COMMUNITY_MODULES.map(mod => (
                  <Link key={mod.id} href={mod.href} onClick={() => setMobileOpen(false)} className="flex items-center gap-2 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 rounded-lg">
                    <mod.icon className="h-4 w-4 text-emerald-400" /> {mod.title}
                  </Link>
                ))}
              </div>
              <div className="border-t border-slate-800 pt-2 mt-2 flex gap-2">
                <Link href="/login" onClick={() => setMobileOpen(false)} className="flex-1 px-4 py-2 border border-slate-700 rounded-lg text-center text-sm">ورود</Link>
                <Link href="/register" onClick={() => setMobileOpen(false)} className="flex-1 px-4 py-2 bg-emerald-600 rounded-lg text-center text-sm">ثبت‌نام</Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
'''
    write_file(web_dir / "src" / "components" / "layout" / "Navbar.tsx", content)

# ========== Footer حرفه‌ای ==========
def create_footer(web_dir):
    print("\n🦶 ایجاد Footer حرفه‌ای...")
    content = '''"use client";

import Link from "next/link";
import { Leaf, Mail, Phone, MapPin, Github, Twitter, Linkedin, Instagram } from "lucide-react";

export default function Footer() {
  return (
    <footer className="bg-slate-950 border-t border-slate-800 mt-20">
      <div className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-10">
          {/* About */}
          <div>
            <div className="flex items-center gap-2 mb-4">
              <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500 to-green-600">
                <Leaf className="h-5 w-5 text-white" />
              </div>
              <div>
                <p className="font-bold text-white">اکو نوژین</p>
                <p className="text-xs text-slate-400">احیای زمین</p>
              </div>
            </div>
            <p className="text-sm text-slate-400 leading-relaxed mb-4">
              پلتفرم علمی رایگان برای مدیریت هوشمند یکپارچه احیای مناظر خشک و نیمه‌خشک زمین
            </p>
            <div className="flex gap-3">
              {[Github, Twitter, Linkedin, Instagram].map((Icon, i) => (
                <a key={i} href="#" className="p-2 bg-slate-900 hover:bg-slate-800 rounded-lg transition-colors">
                  <Icon className="h-4 w-4 text-slate-400" />
                </a>
              ))}
            </div>
          </div>

          {/* Scientific */}
          <div>
            <h3 className="font-bold text-white mb-4">ماژول‌های علمی</h3>
            <ul className="space-y-2 text-sm">
              {[["هیدرولوژی", "/hydrology"], ["آب خاک", "/soil-water"], ["کربن خاک", "/carbon"], ["فرسایش", "/erosion"], ["محصول", "/crop"], ["هواشناسی", "/weather"]].map(([t, h]) => (
                <li key={h}><Link href={h} className="text-slate-400 hover:text-emerald-400 transition-colors">{t}</Link></li>
              ))}
            </ul>
          </div>

          {/* Services */}
          <div>
            <h3 className="font-bold text-white mb-4">خدمات</h3>
            <ul className="space-y-2 text-sm">
              {[["کتابخانه", "/library"], ["آموزش", "/education"], ["فروشگاه", "/shop"], ["جامعه", "/community"], ["پنل ادمین", "/admin"], ["پروفایل", "/profile"]].map(([t, h]) => (
                <li key={h}><Link href={h} className="text-slate-400 hover:text-emerald-400 transition-colors">{t}</Link></li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h3 className="font-bold text-white mb-4">تماس با ما</h3>
            <ul className="space-y-3 text-sm">
              <li className="flex items-start gap-2 text-slate-400">
                <MapPin className="h-4 w-4 mt-0.5 text-emerald-400 flex-shrink-0" />
                <span>ایران، مشهد، پارک علم و فناوری</span>
              </li>
              <li className="flex items-center gap-2 text-slate-400">
                <Mail className="h-4 w-4 text-emerald-400" />
                <a href="mailto:info@econojin.com" className="hover:text-emerald-400">info@econojin.com</a>
              </li>
              <li className="flex items-center gap-2 text-slate-400">
                <Phone className="h-4 w-4 text-emerald-400" />
                <a href="tel:+985138000000" className="hover:text-emerald-400">۰۵۱-۳۸۰۰۰۰۰۰</a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom */}
        <div className="border-t border-slate-800 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm text-slate-500">© ۲۰۲۶ اکو نوژین - تمامی حقوق محفوظ است</p>
          <div className="flex gap-6 text-sm">
            <Link href="/privacy" className="text-slate-500 hover:text-emerald-400">حریم خصوصی</Link>
            <Link href="/terms" className="text-slate-500 hover:text-emerald-400">قوانین</Link>
            <Link href="/policy" className="text-slate-500 hover:text-emerald-400">خط مشی</Link>
            <Link href="/blog" className="text-slate-500 hover:text-emerald-400">وبلاگ</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
'''
    write_file(web_dir / "src" / "components" / "layout" / "Footer.tsx", content)

# ========== Layout اصلی ==========
def create_main_layout(web_dir):
    print("\n🎨 ایجاد Layout اصلی...")
    content = '''import "@/styles/globals.css";
import type { Metadata } from "next";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import ChatWidget from "@/components/ai/ChatWidget";

export const metadata: Metadata = {
  title: "اکو نوژین | مدیریت هوشمند احیای مناظر خشک",
  description: "پلتفرم علمی رایگان برای احیای زمین‌های خشک و نیمه‌خشک",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fa" dir="rtl">
      <body className="bg-slate-950 text-slate-100 antialiased min-h-screen flex flex-col">
        <Navbar />
        <main className="flex-1">{children}</main>
        <Footer />
        <ChatWidget />
      </body>
    </html>
  );
}
'''
    write_file(web_dir / "src" / "app" / "layout.tsx", content)

# ========== صفحه اصلی ==========
def create_homepage(web_dir):
    print("\n🏠 ایجاد صفحه اصلی...")
    content = '''"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import {
  Droplets, TreePine, Mountain, CloudSun, Sprout,
  Map, Satellite, BookOpen, Users, TrendingUp,
  Leaf, Sun, Wind, BarChart3, ArrowLeft, Heart,
  Gamepad2, Coins, Monitor, Settings, ShoppingCart,
  GraduationCap, Zap, Shield, Globe
} from "lucide-react";

const SCIENTIFIC_MODULES = [
  { id: "hydrology", title: "هیدرولوژی", subtitle: "شبیه‌سازی رواناب و حوضه آبریز", icon: Droplets, color: "from-blue-500 to-cyan-500", href: "/hydrology", stats: "۱۲ حوضه" },
  { id: "soil-water", title: "آب خاک", subtitle: "تحلیل رطوبت خاک", icon: Wind, color: "from-sky-500 to-blue-500", href: "/soil-water", stats: "۸۵ نقطه" },
  { id: "carbon", title: "کربن خاک", subtitle: "مدل RothC و جذب کربن", icon: TreePine, color: "from-emerald-500 to-green-500", href: "/carbon", stats: "۲,۴۵۰ تن" },
  { id: "erosion", title: "فرسایش خاک", subtitle: "مدل RUSLE و ریسک", icon: Mountain, color: "from-amber-600 to-orange-500", href: "/erosion", stats: "۳۴ منطقه" },
  { id: "crop", title: "مدیریت محصول", subtitle: "شبیه‌سازی AquaCrop", icon: Sprout, color: "from-lime-500 to-green-500", href: "/crop", stats: "۱۸ محصول" },
  { id: "weather", title: "هواشناسی", subtitle: "پیش‌بینی کشاورزی", icon: CloudSun, color: "from-sky-400 to-blue-400", href: "/weather", stats: "۷ روزه" },
  { id: "gis", title: "GIS و نقشه", subtitle: "تحلیل مکانی و NDVI", icon: Map, color: "from-violet-500 to-purple-500", href: "/gis", stats: "۱۲۰ لایه" },
  { id: "sentinel", title: "سنجش از دور", subtitle: "تصاویر Sentinel-2", icon: Satellite, color: "from-indigo-500 to-blue-500", href: "/sentinel", stats: "روزانه" },
];

const COMMUNITY_MODULES = [
  { id: "library", title: "کتابخانه علمی", icon: BookOpen, color: "from-rose-500 to-pink-500", href: "/library" },
  { id: "education", title: "آموزش", icon: GraduationCap, color: "from-yellow-500 to-amber-500", href: "/education" },
  { id: "community", title: "جامعه کشاورزان", icon: Users, color: "from-teal-500 to-cyan-500", href: "/community" },
  { id: "shop", title: "فروشگاه", icon: ShoppingCart, color: "from-green-500 to-emerald-500", href: "/shop" },
  { id: "psychology", title: "سلامت روان", icon: Heart, color: "from-pink-500 to-rose-500", href: "/psychology" },
  { id: "games", title: "بازی‌های آموزشی", icon: Gamepad2, color: "from-purple-500 to-violet-500", href: "/games" },
  { id: "ecomining", title: "EcoCoin", icon: Coins, color: "from-yellow-400 to-orange-500", href: "/ecomining" },
  { id: "desktop", title: "میزکار", icon: Monitor, color: "from-slate-500 to-gray-500", href: "/desktop" },
];

const KEY_STATS = [
  { label: "هکتار احیا شده", value: "۱۲,۴۵۰", icon: TreePine, color: "#10b981" },
  { label: "تن کربن جذب شده", value: "۲۴,۸۰۰", icon: Leaf, color: "#059669" },
  { label: "کشاورز فعال", value: "۱,۲۰۰", icon: Users, color: "#0ea5e9" },
  { label: "حوضه آبریز", value: "۴۸", icon: Droplets, color: "#3b82f6" },
];

const FEATURES = [
  { title: "رایگان و آزاد", desc: "تمامی خدمات علمی به صورت رایگان", icon: Gift },
  { title: "هوش مصنوعی", desc: "تحلیل هوشمند با AI پیشرفته", icon: Zap },
  { title: "امن و مطمئن", desc: "حفاظت از داده‌های شما", icon: Shield },
  { title: "جهانی", desc: "دسترسی از هر نقطه جهان", icon: Globe },
];

function Gift(props: any) {
  return <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 12 20 22 4 22 4 12"/><rect width="20" height="5" x="2" y="7"/><line x1="12" x2="12" y1="22" y2="7"/><path d="M12 7H7.5a2.5 2.5 0 0 1 0-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 0 0 0-5C13 2 12 7 12 7z"/></svg>;
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-900/20 via-transparent to-transparent" />
        <div className="container mx-auto px-6 py-24 relative">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.8 }} className="max-w-4xl">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/20 mb-6">
              <Leaf className="h-4 w-4 text-emerald-400" />
              <span className="text-sm text-emerald-300">پلتفرم علمی احیای زمین</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-black mb-6 leading-tight">
              <span className="bg-gradient-to-l from-emerald-400 via-green-300 to-teal-400 bg-clip-text text-transparent">اکو نوژین</span>
            </h1>
            <p className="text-2xl md:text-3xl text-slate-300 mb-4 font-light">مدیریت هوشمند یکپارچه</p>
            <p className="text-xl text-slate-400 mb-8 max-w-2xl leading-relaxed">
              احیای مناظر خشک و نیمه‌خشک زمین با ترکیب علم هیدرولوژی، مدل‌سازی کربن، سنجش از دور و هوش مصنوعی
            </p>
            <div className="flex flex-wrap gap-4">
              <Link href="/hydrology">
                <button className="px-8 py-4 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-semibold hover:shadow-2xl hover:shadow-emerald-500/30 transition-all hover:-translate-y-1">شروع شبیه‌سازی</button>
              </Link>
              <Link href="/education">
                <button className="px-8 py-4 bg-slate-800/50 backdrop-blur border border-slate-700 text-white rounded-xl font-semibold hover:bg-slate-700/50 transition-all">آموزش رایگان</button>
              </Link>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {KEY_STATS.map((stat, i) => (
            <motion.div key={stat.label} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 + i * 0.1 }} className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all">
              <div className="flex items-center justify-between mb-3">
                <stat.icon className="h-6 w-6" style={{ color: stat.color }} />
                <TrendingUp className="h-4 w-4 text-emerald-400" />
              </div>
              <p className="text-3xl font-bold text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Scientific Modules */}
      <section className="container mx-auto px-6 py-16">
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-white mb-3">ماژول‌های علمی</h2>
          <p className="text-lg text-slate-400">ابزارهای تخصصی برای احیای زمین‌های خشک و نیمه‌خشک</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
          {SCIENTIFIC_MODULES.map((mod, i) => (
            <motion.div key={mod.id} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.05 }}>
              <Link href={mod.href}>
                <div className="group relative bg-slate-900/50 backdrop-blur border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all hover:-translate-y-1 h-full">
                  <div className={`absolute inset-0 bg-gradient-to-br ${mod.color} opacity-0 group-hover:opacity-5 rounded-2xl transition-opacity`} />
                  <div className="relative">
                    <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${mod.color} mb-4 shadow-lg`}>
                      <mod.icon className="h-6 w-6 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">{mod.title}</h3>
                    <p className="text-sm text-slate-400 mb-4 leading-relaxed">{mod.subtitle}</p>
                    <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                      <span className="text-xs text-slate-500">{mod.stats}</span>
                      <ArrowLeft className="h-4 w-4 text-slate-500 group-hover:text-emerald-400 group-hover:-translate-x-1 transition-all" />
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Community Modules */}
      <section className="container mx-auto px-6 py-16">
        <div className="mb-12">
          <h2 className="text-4xl font-bold text-white mb-3">جامعه و خدمات</h2>
          <p className="text-lg text-slate-400">همه آنچه برای یک کشاورز پایدار نیاز دارید</p>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {COMMUNITY_MODULES.map((mod, i) => (
            <motion.div key={mod.id} initial={{ opacity: 0, scale: 0.95 }} whileInView={{ opacity: 1, scale: 1 }} viewport={{ once: true }} transition={{ delay: i * 0.05 }}>
              <Link href={mod.href}>
                <div className="group bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-5 hover:border-slate-700 transition-all hover:-translate-y-1">
                  <div className={`inline-flex p-2.5 rounded-lg bg-gradient-to-br ${mod.color} mb-3`}>
                    <mod.icon className="h-5 w-5 text-white" />
                  </div>
                  <h3 className="font-bold text-white group-hover:text-emerald-300 transition-colors">{mod.title}</h3>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {FEATURES.map((f, i) => (
            <motion.div key={f.title} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }} className="text-center p-6 bg-slate-900/30 border border-slate-800 rounded-2xl">
              <div className="inline-flex p-3 rounded-xl bg-emerald-500/10 mb-4">
                <f.icon className="h-6 w-6 text-emerald-400" />
              </div>
              <h3 className="font-bold text-white mb-2">{f.title}</h3>
              <p className="text-sm text-slate-400">{f.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'''
    write_file(web_dir / "src" / "app" / "page.tsx", content)

# ========== صفحات استاتیک ==========
def create_static_pages(web_dir):
    print("\n📄 ایجاد صفحات استاتیک...")
    
    pages = {
        "about": {
            "title": "درباره اکو نوژین",
            "content": "اکو نوژین یک پلتفرم علمی رایگان است که با هدف مدیریت هوشمند یکپارچه احیای مناظر خشک و نیمه‌خشک زمین طراحی شده است. ما با ترکیب دانش هیدرولوژی، مدل‌سازی کربن، سنجش از دور و هوش مصنوعی، ابزارهای پیشرفته‌ای را در اختیار کشاورزان، پژوهشگران و علاقه‌مندان قرار می‌دهیم.",
            "mission": "ماموریت ما توانمندسازی جوامع روستایی و کشاورزان در سراسر جهان برای مقابله با بیابان‌زایی، حفظ منابع آب و خاک، و ایجاد آینده‌ای پایدار برای نسل‌های آینده است."
        },
        "contact": {
            "title": "تماس با ما",
            "content": "ما همیشه آماده پاسخگویی به سوالات، پیشنهادات و همکاری با شما هستیم."
        },
        "privacy": {
            "title": "حریم خصوصی",
            "content": "حریم خصوصی کاربران برای ما بسیار مهم است. ما اطلاعات شخصی شما را فقط برای ارائه خدمات بهتر استفاده می‌کنیم و هرگز آن را به اشخاص ثالث نمی‌فروشیم."
        },
        "terms": {
            "title": "قوانین و مقررات",
            "content": "با استفاده از اکو نوژین، شما با قوانین و مقررات زیر موافقت می‌کنید. لطفاً این قوانین را به دقت مطالعه کنید."
        },
        "policy": {
            "title": "خط مشی",
            "content": "خط مشی اکو نوژین بر پایه اصول علمی، شفافیت، و احترام به کاربران استوار است."
        },
    }
    
    for slug, data in pages.items():
        content = f'''import Link from "next/link";
import {{ ArrowRight }} from "lucide-react";

export default function {slug.capitalize()}Page() {{
  return (
    <div className="container mx-auto px-6 py-16">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8">
          <ArrowRight className="h-4 w-4" /> بازگشت به خانه
        </Link>
        <h1 className="text-4xl font-bold text-white mb-6">{data["title"]}</h1>
        <div className="prose prose-invert max-w-none">
          <p className="text-lg text-slate-300 leading-relaxed mb-6">{data["content"]}</p>
          {f'<p className="text-lg text-slate-300 leading-relaxed mb-6">{data["mission"]}</p>' if "mission" in data else ""}
          <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8 mt-8">
            <h2 className="text-xl font-bold text-white mb-4">اطلاعات تماس</h2>
            <p className="text-slate-400 mb-2">📧 ایمیل: info@econojin.com</p>
            <p className="text-slate-400 mb-2">📞 تلفن: ۰۵۱-۳۸۰۰۰۰۰۰</p>
            <p className="text-slate-400">📍 آدرس: مشهد، پارک علم و فناوری</p>
          </div>
        </div>
      </div>
    </div>
  );
}}
'''
        write_file(web_dir / "src" / "app" / slug / "page.tsx", content)
    
    # Blog page
    blog_content = '''import Link from "next/link";
import { ArrowRight } from "lucide-react";

const POSTS = [
  { id: 1, title: "احیای زمین‌های خشک با مدل RothC", date: "۱۴۰۵/۰۳/۱۰", category: "کربن خاک", excerpt: "مدل RothC یکی از معتبرترین مدل‌ها برای شبیه‌سازی دینامیک کربن آلی خاک است..." },
  { id: 2, title: "مدیریت پایدار آب در مناطق خشک", date: "۱۴۰۵/۰۳/۰۵", category: "هیدرولوژی", excerpt: "راهکارهای نوین برای مدیریت منابع آب در شرایط کم‌آبی..." },
  { id: 3, title: "استفاده از Sentinel-2 در پایش Vegetation", date: "۱۴۰۵/۰۲/۲۸", category: "سنجش از دور", excerpt: "تحلیل تصاویر ماهواره‌ای برای پایش سلامت پوشش گیاهی..." },
];

export default function BlogPage() {
  return (
    <div className="container mx-auto px-6 py-16">
      <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8">
        <ArrowRight className="h-4 w-4" /> بازگشت
      </Link>
      <h1 className="text-4xl font-bold text-white mb-3">وبلاگ اکو نوژین</h1>
      <p className="text-lg text-slate-400 mb-12">آخرین مقالات و اخبار علمی</p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {POSTS.map(post => (
          <article key={post.id} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xs px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded">{post.category}</span>
              <span className="text-xs text-slate-500">{post.date}</span>
            </div>
            <h2 className="text-xl font-bold text-white mb-3">{post.title}</h2>
            <p className="text-sm text-slate-400 mb-4 leading-relaxed">{post.excerpt}</p>
            <Link href={`/blog/${post.id}`} className="text-emerald-400 hover:text-emerald-300 text-sm font-medium">ادامه مطلب ←</Link>
          </article>
        ))}
      </div>
    </div>
  );
}
'''
    write_file(web_dir / "src" / "app" / "blog" / "page.tsx", blog_content)

# ========== صفحات احراز هویت ==========
def create_auth_pages(web_dir):
    print("\n🔐 ایجاد صفحات احراز هویت...")
    
    login_content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { Leaf, Mail, Lock, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => { setLoading(false); window.location.href = "/profile"; }, 1500);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 py-12 bg-gradient-to-br from-slate-950 to-emerald-950/30">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 mb-4">
            <Leaf className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">ورود به اکو نوژین</h1>
          <p className="text-slate-400">به جمع کشاورزان پایدار بپیوندید</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-2xl p-8 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">ایمیل</label>
            <div className="relative">
              <Mail className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type="email" required className="w-full pr-10 pl-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors" placeholder="you@example.com" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">رمز عبور</label>
            <div className="relative">
              <Lock className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type={showPass ? "text" : "password"} required className="w-full pr-10 pl-10 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors" placeholder="••••••••" />
              <button type="button" onClick={() => setShowPass(!showPass)} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                {showPass ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          <div className="flex items-center justify-between text-sm">
            <label className="flex items-center gap-2 text-slate-400">
              <input type="checkbox" className="rounded border-slate-700 bg-slate-800" /> مرا به خاطر بسپار
            </label>
            <Link href="/forgot-password" className="text-emerald-400 hover:text-emerald-300">فراموشی رمز؟</Link>
          </div>

          <button type="submit" disabled={loading} className="w-full py-3 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50">
            {loading ? "در حال ورود..." : "ورود"}
          </button>

          <p className="text-center text-sm text-slate-400">
            حساب ندارید؟ <Link href="/register" className="text-emerald-400 hover:text-emerald-300 font-medium">ثبت‌نام کنید</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
'''
    
    register_content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { Leaf, Mail, Lock, User, Phone } from "lucide-react";

export default function RegisterPage() {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setTimeout(() => { setLoading(false); window.location.href = "/profile"; }, 1500);
  };

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 py-12 bg-gradient-to-br from-slate-950 to-emerald-950/30">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 mb-4">
            <Leaf className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">ثبت‌نام در اکو نوژین</h1>
          <p className="text-slate-400">رایگان و برای همیشه</p>
        </div>

        <form onSubmit={handleSubmit} className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-2xl p-8 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">نام کامل</label>
            <div className="relative">
              <User className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type="text" required className="w-full pr-10 pl-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" placeholder="نام و نام خانوادگی" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">ایمیل</label>
            <div className="relative">
              <Mail className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type="email" required className="w-full pr-10 pl-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" placeholder="you@example.com" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">شماره موبایل</label>
            <div className="relative">
              <Phone className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type="tel" className="w-full pr-10 pl-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" placeholder="۰۹۱۲۳۴۵۶۷۸۹" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">رمز عبور</label>
            <div className="relative">
              <Lock className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type="password" required minLength={8} className="w-full pr-10 pl-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" placeholder="حداقل ۸ کاراکتر" />
            </div>
          </div>

          <label className="flex items-start gap-2 text-sm text-slate-400">
            <input type="checkbox" required className="mt-1 rounded border-slate-700 bg-slate-800" />
            <span>با <Link href="/terms" className="text-emerald-400">قوانین</Link> و <Link href="/privacy" className="text-emerald-400">حریم خصوصی</Link> موافقم</span>
          </label>

          <button type="submit" disabled={loading} className="w-full py-3 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50">
            {loading ? "در حال ثبت‌نام..." : "ایجاد حساب"}
          </button>

          <p className="text-center text-sm text-slate-400">
            حساب دارید؟ <Link href="/login" className="text-emerald-400 hover:text-emerald-300 font-medium">وارد شوید</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
'''
    
    write_file(web_dir / "src" / "app" / "login" / "page.tsx", login_content)
    write_file(web_dir / "src" / "app" / "register" / "page.tsx", register_content)

# ========== پروفایل کاربر ==========
def create_profile_page(web_dir):
    print("\n👤 ایجاد پروفایل کاربر...")
    content = '''"use client";

import { useState } from "react";
import { User, Mail, Phone, MapPin, Edit3, Camera, Award, Activity, Calendar, Wallet, Settings as SettingsIcon } from "lucide-react";

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState("overview");

  const user = {
    name: "علی محمدی",
    email: "ali@example.com",
    phone: "۰۹۱۲۳۴۵۶۷۸۹",
    location: "خراسان رضوی، مشهد",
    joinDate: "۱۴۰۳/۰۱/۱۵",
    role: "کشاورز پایدار",
    avatar: "👨‍🌾"
  };

  const stats = [
    { label: "پروژه‌های فعال", value: "۱۲", icon: Activity, color: "#10b981" },
    { label: "هکتار تحت مدیریت", value: "۴۵", icon: MapPin, color: "#3b82f6" },
    { label: "گواهی‌نامه‌ها", value: "۵", icon: Award, color: "#f59e0b" },
    { label: "اعتبار EcoCoin", value: "۲,۴۵۰", icon: Wallet, color: "#8b5cf6" },
  ];

  const tabs = [
    { id: "overview", label: "نمای کلی", icon: User },
    { id: "activities", label: "فعالیت‌ها", icon: Activity },
    { id: "wallet", label: "کیف پول", icon: Wallet },
    { id: "certificates", label: "گواهی‌نامه‌ها", icon: Award },
    { id: "settings", label: "تنظیمات", icon: SettingsIcon },
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      {/* Header */}
      <div className="bg-gradient-to-l from-emerald-600 to-green-700 rounded-2xl p-8 mb-8 relative overflow-hidden">
        <div className="absolute inset-0 bg-[url('/pattern.svg')] opacity-10" />
        <div className="relative flex flex-col md:flex-row items-center gap-6">
          <div className="relative">
            <div className="w-24 h-24 rounded-full bg-white/20 backdrop-blur flex items-center justify-center text-5xl border-4 border-white/30">
              {user.avatar}
            </div>
            <button className="absolute bottom-0 left-0 p-2 bg-white rounded-full shadow-lg">
              <Camera className="h-4 w-4 text-slate-700" />
            </button>
          </div>
          <div className="text-center md:text-right flex-1">
            <h1 className="text-3xl font-bold text-white mb-1">{user.name}</h1>
            <p className="text-emerald-100 mb-3">{user.role}</p>
            <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm text-emerald-100">
              <span className="flex items-center gap-1"><Mail className="h-4 w-4" />{user.email}</span>
              <span className="flex items-center gap-1"><Phone className="h-4 w-4" />{user.phone}</span>
              <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{user.location}</span>
              <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />عضو از {user.joinDate}</span>
            </div>
          </div>
          <button className="px-6 py-2 bg-white/20 backdrop-blur border border-white/30 text-white rounded-xl hover:bg-white/30 transition-all flex items-center gap-2">
            <Edit3 className="h-4 w-4" /> ویرایش پروفایل
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map(s => (
          <div key={s.label} className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <s.icon className="h-6 w-6" style={{ color: s.color }} />
            </div>
            <p className="text-2xl font-bold text-white">{s.value}</p>
            <p className="text-sm text-slate-400">{s.label}</p>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {tabs.map(tab => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)} className={`px-5 py-2.5 rounded-xl flex items-center gap-2 whitespace-nowrap transition-all ${activeTab === tab.id ? "bg-emerald-600 text-white" : "bg-slate-900/50 text-slate-400 hover:bg-slate-800"}`}>
            <tab.icon className="h-4 w-4" /> {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
        {activeTab === "overview" && (
          <div>
            <h2 className="text-xl font-bold text-white mb-4">فعالیت‌های اخیر</h2>
            <div className="space-y-3">
              {[
                { action: "شبیه‌سازی هیدرولوژی حوضه کشف‌رود", time: "۲ ساعت پیش", icon: "💧" },
                { action: "دریافت گواهی‌نامه AquaCrop", time: "دیروز", icon: "🎓" },
                { action: "انتشار مقاله در کتابخانه", time: "۳ روز پیش", icon: "📚" },
                { action: "دریافت ۱۰۰ EcoCoin", time: "هفته پیش", icon: "🪙" },
              ].map((a, i) => (
                <div key={i} className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl">
                  <span className="text-2xl">{a.icon}</span>
                  <div className="flex-1">
                    <p className="text-white">{a.action}</p>
                    <p className="text-xs text-slate-500">{a.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
        {activeTab === "wallet" && (
          <div>
            <h2 className="text-xl font-bold text-white mb-4">کیف پول EcoCoin</h2>
            <div className="bg-gradient-to-l from-purple-600 to-violet-700 rounded-xl p-6 mb-6">
              <p className="text-purple-100 text-sm mb-2">موجودی فعلی</p>
              <p className="text-4xl font-bold text-white mb-4">۲,۴۵۰ <span className="text-lg">EcoCoin</span></p>
              <div className="flex gap-3">
                <button className="px-4 py-2 bg-white/20 backdrop-blur rounded-lg text-white text-sm hover:bg-white/30">ارسال</button>
                <button className="px-4 py-2 bg-white/20 backdrop-blur rounded-lg text-white text-sm hover:bg-white/30">دریافت</button>
              </div>
            </div>
          </div>
        )}
        {activeTab !== "overview" && activeTab !== "wallet" && (
          <div className="text-center py-16 text-slate-500">
            <p>این بخش به زودی فعال می‌شود</p>
          </div>
        )}
      </div>
    </div>
  );
}
'''
    write_file(web_dir / "src" / "app" / "profile" / "page.tsx", content)

# ========== پنل ادمین ==========
def create_admin_page(web_dir):
    print("\n👨‍💼 ایجاد پنل ادمین...")
    content = '''"use client";

import { useState } from "react";
import { Users, Package, Activity, Settings, TrendingUp, Shield, BarChart3, FileText, AlertTriangle, CheckCircle } from "lucide-react";
import Link from "next/link";

export default function AdminPage() {
  const [activeSection, setActiveSection] = useState("dashboard");

  const menuItems = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3 },
    { id: "users", label: "کاربران", icon: Users },
    { id: "modules", label: "ماژول‌ها", icon: Package },
    { id: "content", label: "محتوا", icon: FileText },
    { id: "security", label: "امنیت", icon: Shield },
    { id: "settings", label: "تنظیمات", icon: Settings },
  ];

  const stats = [
    { label: "کل کاربران", value: "۱,۲۴۵", change: "+۱۲٪", icon: Users, color: "#3b82f6" },
    { label: "کاربران فعال", value: "۸۵۶", change: "+۸٪", icon: Activity, color: "#10b981" },
    { label: "درآمد ماهانه", value: "۴۵M", change: "+۲۳٪", icon: TrendingUp, color: "#f59e0b" },
    { label: "هشدارهای سیستم", value: "۳", change: "-۲", icon: AlertTriangle, color: "#ef4444" },
  ];

  return (
    <div className="min-h-screen bg-slate-950 flex">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-l border-slate-800 p-6 hidden lg:block">
        <div className="mb-8">
          <h2 className="text-xl font-bold text-white flex items-center gap-2">
            <Shield className="h-5 w-5 text-emerald-400" /> پنل مدیریت
          </h2>
          <p className="text-xs text-slate-500 mt-1">اکو نوژین ادمین</p>
        </div>
        <nav className="space-y-1">
          {menuItems.map(item => (
            <button key={item.id} onClick={() => setActiveSection(item.id)} className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${activeSection === item.id ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800 hover:text-white"}`}>
              <item.icon className="h-5 w-5" /> {item.label}
            </button>
          ))}
        </nav>
      </aside>

      {/* Main */}
      <main className="flex-1 p-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">داشبورد مدیریت</h1>
          <p className="text-slate-400">نمای کلی از وضعیت سیستم</p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          {stats.map(s => (
            <div key={s.label} className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <s.icon className="h-8 w-8" style={{ color: s.color }} />
                <span className={`text-xs px-2 py-1 rounded-full ${s.change.startsWith("+") ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"}`}>{s.change}</span>
              </div>
              <p className="text-3xl font-bold text-white mb-1">{s.value}</p>
              <p className="text-sm text-slate-400">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5 text-emerald-400" /> فعالیت‌های اخیر
            </h3>
            <div className="space-y-3">
              {[
                { user: "علی محمدی", action: "ثبت‌نام کرد", time: "۵ دقیقه پیش", status: "success" },
                { user: "مریم احمدی", action: "پروژه جدید ایجاد کرد", time: "۱ ساعت پیش", status: "success" },
                { user: "سیستم", action: "هشدار امنیتی", time: "۲ ساعت پیش", status: "warning" },
                { user: "رضا کریمی", action: "خرید از فروشگاه", time: "۳ ساعت پیش", status: "success" },
              ].map((a, i) => (
                <div key={i} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-lg">
                  {a.status === "success" ? <CheckCircle className="h-5 w-5 text-emerald-400" /> : <AlertTriangle className="h-5 w-5 text-amber-400" />}
                  <div className="flex-1">
                    <p className="text-sm text-white"><span className="font-medium">{a.user}</span> {a.action}</p>
                    <p className="text-xs text-slate-500">{a.time}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Package className="h-5 w-5 text-emerald-400" /> وضعیت ماژول‌ها
            </h3>
            <div className="space-y-3">
              {[
                { name: "هیدرولوژی", users: "۳۴۵", status: "active" },
                { name: "کربن خاک", users: "۲۸۹", status: "active" },
                { name: "فرسایش", users: "۱۵۶", status: "active" },
                { name: "هواشناسی", users: "۴۱۲", status: "active" },
                { name: "فروشگاه", users: "۵۲۳", status: "active" },
              ].map((m, i) => (
                <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-emerald-400" />
                    <span className="text-white">{m.name}</span>
                  </div>
                  <span className="text-sm text-slate-400">{m.users} کاربر</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
'''
    write_file(web_dir / "src" / "app" / "admin" / "page.tsx", content)

# ========== فروشگاه ==========
def create_shop_page(web_dir):
    print("\n🛒 ایجاد فروشگاه...")
    content = '''"use client";

import { useState } from "react";
import { ShoppingCart, Search, Filter, Star, Heart, Leaf, Droplets, Sprout } from "lucide-react";

const PRODUCTS = [
  { id: 1, name: "بذر گندم پایدار", price: "۴۵۰,۰۰۰", category: "بذر", rating: 4.8, icon: Sprout, color: "from-lime-500 to-green-500" },
  { id: 2, name: "کود آلی طبیعی", price: "۲۸۰,۰۰۰", category: "کود", rating: 4.9, icon: Leaf, color: "from-emerald-500 to-green-600" },
  { id: 3, name: "سیستم آبیاری قطره‌ای", price: "۲,۵۰۰,۰۰۰", category: "تجهیزات", rating: 4.7, icon: Droplets, color: "from-blue-500 to-cyan-500" },
  { id: 4, name: "بذر جو مقاوم به خشکی", price: "۳۸۰,۰۰۰", category: "بذر", rating: 4.6, icon: Sprout, color: "from-amber-500 to-orange-500" },
  { id: 5, name: "کمپوست حرفه‌ای", price: "۱۵۰,۰۰۰", category: "کود", rating: 4.8, icon: Leaf, color: "from-green-500 to-emerald-500" },
  { id: 6, name: "سنسور رطوبت خاک", price: "۱,۲۰۰,۰۰۰", category: "تجهیزات", rating: 4.9, icon: Droplets, color: "from-sky-500 to-blue-500" },
  { id: 7, name: "بذر ذرت هیبریدی", price: "۵۲۰,۰۰۰", category: "بذر", rating: 4.5, icon: Sprout, color: "from-yellow-500 to-amber-500" },
  { id: 8, name: "پمپ آب خورشیدی", price: "۸,۵۰۰,۰۰۰", category: "تجهیزات", rating: 4.9, icon: Droplets, color: "from-orange-500 to-red-500" },
];

const CATEGORIES = ["همه", "بذر", "کود", "تجهیزات"];

export default function ShopPage() {
  const [category, setCategory] = useState("همه");
  const [search, setSearch] = useState("");

  const filtered = PRODUCTS.filter(p =>
    (category === "همه" || p.category === category) &&
    p.name.includes(search)
  );

  return (
    <div className="container mx-auto px-6 py-12">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-4xl font-bold text-white mb-3">فروشگاه اکو نوژین</h1>
        <p className="text-lg text-slate-400">محصولات پایدار برای کشاورزی مدرن</p>
      </div>

      {/* Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-8">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
          <input value={search} onChange={e => setSearch(e.target.value)} placeholder="جستجوی محصول..." className="w-full pr-10 pl-4 py-3 bg-slate-900/50 border border-slate-800 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" />
        </div>
        <div className="flex gap-2">
          {CATEGORIES.map(c => (
            <button key={c} onClick={() => setCategory(c)} className={`px-5 py-3 rounded-xl transition-all ${category === c ? "bg-emerald-600 text-white" : "bg-slate-900/50 text-slate-400 hover:bg-slate-800"}`}>
              {c}
            </button>
          ))}
        </div>
      </div>

      {/* Products Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {filtered.map(product => (
          <div key={product.id} className="group bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all">
            <div className={`relative h-48 bg-gradient-to-br ${product.color} flex items-center justify-center`}>
              <product.icon className="h-20 w-20 text-white/80" />
              <button className="absolute top-3 left-3 p-2 bg-white/20 backdrop-blur rounded-full hover:bg-white/30">
                <Heart className="h-4 w-4 text-white" />
              </button>
              <span className="absolute top-3 right-3 px-2 py-1 bg-black/30 backdrop-blur rounded text-xs text-white">{product.category}</span>
            </div>
            <div className="p-5">
              <h3 className="font-bold text-white mb-2 group-hover:text-emerald-300 transition-colors">{product.name}</h3>
              <div className="flex items-center gap-1 mb-3">
                <Star className="h-4 w-4 fill-amber-400 text-amber-400" />
                <span className="text-sm text-slate-300">{product.rating}</span>
              </div>
              <div className="flex items-center justify-between">
                <p className="text-lg font-bold text-emerald-400">{product.price} <span className="text-xs text-slate-500">تومان</span></p>
                <button className="p-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg transition-colors">
                  <ShoppingCart className="h-4 w-4 text-white" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
'''
    write_file(web_dir / "src" / "app" / "shop" / "page.tsx", content)

# ========== ChatWidget ==========
def create_chat_widget(web_dir):
    print("\n🤖 ایجاد ChatWidget...")
    content = '''"use client";

import { useState } from "react";
import { MessageCircle, X, Send, Leaf } from "lucide-react";

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "سلام! من دستیار هوشمند اکو نوژین هستم. چطور می‌توانم در احیای زمین به شما کمک کنم؟" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", content: input };
    setMessages(prev => [...prev, userMsg]);
    const q = input;
    setInput("");
    setLoading(true);
    setTimeout(() => {
      setMessages(prev => [...prev, { role: "assistant", content: `متشکرم از سوال شما درباره "${q}". تیم اکو نوژین به زودی پاسخ کاملی ارائه خواهد داد.` }]);
      setLoading(false);
    }, 1000);
  };

  return (
    <>
      {!isOpen && (
        <button onClick={() => setIsOpen(true)} className="fixed bottom-6 left-6 p-4 bg-gradient-to-br from-emerald-500 to-green-600 text-white rounded-full shadow-2xl hover:shadow-emerald-500/50 transition-all z-50 group">
          <MessageCircle className="h-6 w-6 group-hover:scale-110 transition-transform" />
        </button>
      )}
      {isOpen && (
        <div className="fixed bottom-6 left-6 w-96 h-[550px] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col z-50">
          <div className="p-4 border-b border-slate-700 flex items-center justify-between bg-gradient-to-l from-emerald-600 to-green-700 rounded-t-2xl">
            <div className="flex items-center gap-2">
              <Leaf className="h-5 w-5" />
              <div>
                <p className="font-semibold text-white">دستیار اکو نوژین</p>
                <p className="text-xs text-emerald-100">آنلاین</p>
              </div>
            </div>
            <button onClick={() => setIsOpen(false)} className="hover:bg-white/10 p-1 rounded"><X className="h-5 w-5" /></button>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {messages.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === "user" ? "justify-start" : "justify-end"}`}>
                <div className={`max-w-[80%] p-3 rounded-2xl text-sm ${msg.role === "user" ? "bg-slate-800 text-slate-100" : "bg-emerald-600 text-white"}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && <div className="text-center text-slate-500 text-sm">در حال پاسخ...</div>}
          </div>
          <div className="p-3 border-t border-slate-700 flex gap-2">
            <input value={input} onChange={e => setInput(e.target.value)} onKeyPress={e => e.key === "Enter" && sendMessage()} placeholder="سوال خود را بپرسید..." className="flex-1 px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-sm focus:outline-none focus:border-emerald-500" />
            <button onClick={sendMessage} disabled={loading} className="p-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700"><Send className="h-5 w-5" /></button>
          </div>
        </div>
      )}
    </>
  );
}
'''
    write_file(web_dir / "src" / "components" / "ai" / "ChatWidget.tsx", content)

# ========== API Service ==========
def create_api_service(web_dir):
    print("\n📡 ایجاد سرویس API...")
    content = '''// Econojin API Services
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiCall<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json", ...options?.headers },
  });
  if (!res.ok) throw new Error(`API Error: ${res.status}`);
  return res.json();
}

export const healthService = {
  check: () => apiCall<any>("/api/v1/health"),
  modules: () => apiCall<any>("/api/v1/modules"),
};

export const dashboardService = {
  getStats: () => apiCall<any>("/api/v1/dashboard/stats"),
  getActivity: () => apiCall<any>("/api/v1/dashboard/activity"),
};

export const aiService = {
  chat: (message: string, context?: any) => apiCall<any>("/api/v1/ai/chat", { method: "POST", body: JSON.stringify({ message, context }) }),
};

export const authService = {
  login: (data: any) => apiCall<any>("/api/v1/auth/login", { method: "POST", body: JSON.stringify(data) }),
  register: (data: any) => apiCall<any>("/api/v1/auth/register", { method: "POST", body: JSON.stringify(data) }),
  getProfile: () => apiCall<any>("/api/v1/auth/profile"),
};

export const weatherService = {
  getForecast: (location: string, days = 7) => apiCall<any>(`/api/v1/weather/forecast?location=${location}&days=${days}`),
  getAlerts: (region: string) => apiCall<any>(`/api/v1/weather/alerts?region=${region}`),
};

export const gisService = {
  calculateArea: (coords: any) => apiCall<any>("/api/v1/gis/calculate/area", { method: "POST", body: JSON.stringify({ coordinates: coords }) }),
  getNdvi: (region: string) => apiCall<any>(`/api/v1/gis/ndvi?region=${region}`),
};

export const carbonService = {
  calculate: (data: any) => apiCall<any>("/api/v1/carbon/calculate", { method: "POST", body: JSON.stringify(data) }),
};

export const shopService = {
  getProducts: () => apiCall<any>("/api/v1/shop"),
  createOrder: (data: any) => apiCall<any>("/api/v1/shop/order", { method: "POST", body: JSON.stringify(data) }),
};
'''
    write_file(web_dir / "src" / "lib" / "api.ts", content)

# ========== Module Template ==========
def create_module_template(web_dir, module_id: str, title: str, icon: str, color: str, desc: str):
    """ایجاد ماژول استاندارد"""
    content = f'''"use client";

import Link from "next/link";
import {{ ArrowRight, {icon} }} from "lucide-react";

export default function {module_id.replace("-", "").capitalize()}Page() {{
  return (
    <div className="container mx-auto px-6 py-12">
      <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8">
        <ArrowRight className="h-4 w-4" /> بازگشت به خانه
      </Link>
      
      <div className="mb-10">
        <div className="inline-flex p-4 rounded-2xl bg-gradient-to-br {color} mb-4">
          <{icon} className="h-10 w-10 text-white" />
        </div>
        <h1 className="text-4xl font-bold text-white mb-3">{title}</h1>
        <p className="text-lg text-slate-400">{desc}</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {{[1, 2, 3, 4, 5, 6].map(i => (
          <div key={{i}} className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all">
            <div className="h-32 bg-gradient-to-br {color} rounded-xl mb-4 opacity-20" />
            <h3 className="text-lg font-bold text-white mb-2">پروژه {{i}}</h3>
            <p className="text-sm text-slate-400 mb-4">توضیحات پروژه {title} شماره {{i}}</p>
            <button className="text-emerald-400 hover:text-emerald-300 text-sm font-medium">مشاهده جزئیات ←</button>
          </div>
        ))}}
      </div>
    </div>
  );
}}
'''
    write_file(web_dir / "src" / "app" / module_id / "page.tsx", content)

# ========== Main ==========
def main():
    print("🌍 بازسازی کامل اکو نوژین")
    print("=" * 70)
    print("وبسایت حرفه‌ای جامع با تمام ماژول‌ها و پنل‌ها")
    print("=" * 70)
    
    web_dir = find_web_dir()
    print(f"\n📁 دایرکتوری web: {web_dir}")
    
    if not web_dir.exists():
        print("❌ دایرکتوری web یافت نشد!")
        return 1
    
    # ایجاد ساختار اصلی
    create_api_service(web_dir)
    create_navbar(web_dir)
    create_footer(web_dir)
    create_main_layout(web_dir)
    create_chat_widget(web_dir)
    
    # صفحات اصلی
    create_homepage(web_dir)
    create_auth_pages(web_dir)
    create_profile_page(web_dir)
    create_admin_page(web_dir)
    create_shop_page(web_dir)
    
    # صفحات استاتیک
    create_static_pages(web_dir)
    
    # ماژول‌های علمی
    print("\n🔬 ایجاد ماژول‌های علمی...")
    scientific_modules = [
        ("hydrology", "هیدرولوژی", "Droplets", "from-blue-500 to-cyan-500", "شبیه‌سازی رواناب و مدیریت حوضه آبریز"),
        ("soil-water", "آب خاک", "Wind", "from-sky-500 to-blue-500", "تحلیل رطوبت و حرکت آب در خاک"),
        ("carbon", "کربن خاک", "TreePine", "from-emerald-500 to-green-500", "مدل‌سازی RothC و جذب کربن"),
        ("erosion", "فرسایش خاک", "Mountain", "from-amber-600 to-orange-500", "مدل RUSLE و ارزیابی ریسک"),
        ("crop", "مدیریت محصول", "Sprout", "from-lime-500 to-green-500", "شبیه‌سازی AquaCrop"),
        ("weather", "هواشناسی", "CloudSun", "from-sky-400 to-blue-400", "پیش‌بینی و هشدارهای کشاورزی"),
        ("gis", "GIS و نقشه", "Map", "from-violet-500 to-purple-500", "تحلیل مکانی و NDVI"),
        ("sentinel", "سنجش از دور", "Satellite", "from-indigo-500 to-blue-500", "تصاویر Sentinel-2"),
    ]
    for m in scientific_modules:
        create_module_template(web_dir, *m)
    
    # ماژول‌های جامعه
    print("\n👥 ایجاد ماژول‌های جامعه...")
    community_modules = [
        ("library", "کتابخانه علمی", "BookOpen", "from-rose-500 to-pink-500", "منابع و مقالات تخصصی"),
        ("education", "آموزش", "GraduationCap", "from-yellow-500 to-amber-500", "دوره‌های تخصصی"),
        ("community", "جامعه کشاورزان", "Users", "from-teal-500 to-cyan-500", "اشتراک تجربه و دانش"),
        ("psychology", "سلامت روان", "Heart", "from-pink-500 to-rose-500", "مشاوره و آزمون‌های روانشناسی"),
        ("games", "بازی‌های آموزشی", "Gamepad2", "from-purple-500 to-violet-500", "یادگیری از طریق بازی"),
        ("ecomining", "EcoCoin", "Coins", "from-yellow-400 to-orange-500", "پاداش‌های اکولوژیک"),
        ("desktop", "میزکار", "Monitor", "from-slate-500 to-gray-500", "داشبورد شخصی‌سازی‌شده"),
    ]
    for m in community_modules:
        create_module_template(web_dir, *m)
    
    print("\n" + "=" * 70)
    print("✅ بازسازی کامل اکو نوژین تکمیل شد!")
    print("\n🎯 صفحات ایجاد شده:")
    print("   🏠 صفحه اصلی با طراحی حرفه‌ای")
    print("   🔐 ورود و ثبت‌نام")
    print("   👤 پروفایل کاربر")
    print("   👨‍💼 پنل ادمین")
    print("   🛒 فروشگاه")
    print("   📄 درباره ما، تماس، حریم خصوصی، قوانین، خط مشی")
    print("   📝 وبلاگ")
    print("   🤖 چت‌بات هوشمند")
    print("   🧭 Navbar و Footer حرفه‌ای")
    print("   🔬 ۸ ماژول علمی")
    print("   👥 ۷ ماژول جامعه")
    
    print("\n🚀 گام بعدی:")
    print("   1. Remove-Item .next -Recurse -Force")
    print("   2. pnpm run dev -- -p 3001")
    print("   3. مشاهده: http://localhost:3001")
    print("=" * 70)
    
    return 0

if __name__ == "__main__":
    sys.exit(main())