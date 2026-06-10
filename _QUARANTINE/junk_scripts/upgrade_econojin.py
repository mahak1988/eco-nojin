#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🚀 ارتقای جامع اکو نوژین
- رفع مشکل پروفایل و ادمین
- اتصال به داده‌های واقعی
- چت بات OpenAI
- Analytics
- ماژول پایش خشکسالی
- آماده‌سازی Vercel
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)}")


# ========== 1. Navbar با پروفایل و ادمین ==========
def fix_navbar_with_profile():
    print("\n🧭 به‌روزرسانی Navbar با پروفایل و ادمین...")
    
    content = '''"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Leaf, Menu, X, ChevronDown, LogIn, User, Shield, Settings } from "lucide-react";

const SCIENTIFIC_MODULES = [
  { id: "gis", title: "GIS و نقشه", href: "/gis" },
  { id: "hydrology", title: "هیدرولوژی", href: "/hydrology" },
  { id: "carbon", title: "کربن خاک", href: "/carbon" },
  { id: "erosion", title: "فرسایش خاک", href: "/erosion" },
  { id: "weather", title: "هواشناسی", href: "/weather" },
  { id: "crop", title: "مدیریت محصول", href: "/crop" },
  { id: "sentinel", title: "سنجش از دور", href: "/sentinel" },
  { id: "soil-water", title: "آب خاک", href: "/soil-water" },
  { id: "drought", title: "پایش خشکسالی", href: "/drought" },
];

const COMMUNITY_MODULES = [
  { id: "library", title: "کتابخانه علمی", href: "/library" },
  { id: "education", title: "آموزش", href: "/education" },
  { id: "community", title: "جامعه کشاورزان", href: "/community" },
  { id: "shop", title: "فروشگاه", href: "/shop" },
  { id: "psychology", title: "سلامت روان", href: "/psychology" },
  { id: "games", title: "بازی‌های آموزشی", href: "/games" },
  { id: "ecomining", title: "EcoCoin", href: "/ecomining" },
  { id: "desktop", title: "میزکار", href: "/desktop" },
];

export default function Navbar() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const isActive = (path: string) => pathname === path;

  return (
    <nav className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-xl border-b border-slate-800">
      <div className="container mx-auto px-6">
        <div className="flex items-center justify-between h-16 gap-4">
          <Link href="/" className="flex items-center gap-2 group flex-shrink-0">
            <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-500 to-green-600 shadow-lg shadow-emerald-500/20">
              <Leaf className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="font-bold text-white leading-tight">اکو نوژین</p>
              <p className="text-[10px] text-slate-400">Econojin</p>
            </div>
          </Link>

          <div className="hidden lg:flex items-center gap-1 flex-1 justify-center">
            <Link href="/" className={`px-4 py-2 rounded-lg text-sm transition-colors ${isActive("/") ? "bg-slate-800 text-white" : "text-slate-300 hover:bg-slate-800/50 hover:text-white"}`}>خانه</Link>
            
            <div className="relative" onMouseEnter={() => setOpenDropdown("sci")} onMouseLeave={() => setOpenDropdown(null)}>
              <button className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white flex items-center gap-1">
                ماژول‌های علمی <ChevronDown className="h-4 w-4" />
              </button>
              <AnimatePresence>
                {openDropdown === "sci" && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full right-0 mt-2 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2">
                    {SCIENTIFIC_MODULES.map(m => (
                      <Link key={m.id} href={m.href} className={`block px-3 py-2.5 rounded-lg text-sm ${isActive(m.href) ? "bg-emerald-500/10 text-emerald-400" : "text-slate-200 hover:bg-slate-800"}`}>{m.title}</Link>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <div className="relative" onMouseEnter={() => setOpenDropdown("com")} onMouseLeave={() => setOpenDropdown(null)}>
              <button className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50 hover:text-white flex items-center gap-1">
                جامعه و خدمات <ChevronDown className="h-4 w-4" />
              </button>
              <AnimatePresence>
                {openDropdown === "com" && (
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full right-0 mt-2 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2">
                    {COMMUNITY_MODULES.map(m => (
                      <Link key={m.id} href={m.href} className={`block px-3 py-2.5 rounded-lg text-sm ${isActive(m.href) ? "bg-emerald-500/10 text-emerald-400" : "text-slate-200 hover:bg-slate-800"}`}>{m.title}</Link>
                    ))}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>

            <Link href="/education" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50">آموزش</Link>
            <Link href="/about" className="px-4 py-2 rounded-lg text-sm text-slate-300 hover:bg-slate-800/50">درباره ما</Link>
          </div>

          <div className="flex items-center gap-2">
            {isLoggedIn ? (
              <div className="relative" onMouseEnter={() => setOpenDropdown("user")} onMouseLeave={() => setOpenDropdown(null)}>
                <button className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-800/50 hover:bg-slate-700/50 border border-slate-700">
                  <div className="w-7 h-7 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center text-white text-xs font-bold">ع</div>
                  <span className="text-sm text-white hidden sm:inline">علی محمدی</span>
                  <ChevronDown className="h-4 w-4 text-slate-400" />
                </button>
                <AnimatePresence>
                  {openDropdown === "user" && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: 10 }} className="absolute top-full left-0 mt-2 w-56 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl p-2">
                      <Link href="/profile" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-200 hover:bg-slate-800">
                        <User className="h-4 w-4 text-emerald-400" /> پروفایل من
                      </Link>
                      <Link href="/desktop" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-200 hover:bg-slate-800">
                        <Settings className="h-4 w-4 text-emerald-400" /> میزکار من
                      </Link>
                      <Link href="/admin" className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-slate-200 hover:bg-slate-800">
                        <Shield className="h-4 w-4 text-amber-400" /> پنل مدیریت
                      </Link>
                      <div className="border-t border-slate-800 my-1" />
                      <button onClick={() => setIsLoggedIn(false)} className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-red-400 hover:bg-red-500/10">
                        <LogIn className="h-4 w-4" /> خروج
                      </button>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ) : (
              <div className="hidden lg:flex items-center gap-2">
                <Link href="/login" className="px-4 py-2 text-sm text-slate-300 hover:text-white flex items-center gap-1">
                  <LogIn className="h-4 w-4" /> ورود
                </Link>
                <button 
                  onClick={() => setIsLoggedIn(true)}
                  className="px-4 py-2 bg-gradient-to-l from-emerald-500 to-green-600 text-white text-sm rounded-lg hover:shadow-lg hover:shadow-emerald-500/30 transition-all font-medium"
                >
                  ثبت‌نام رایگان
                </button>
              </div>
            )}

            <button onClick={() => setMobileOpen(!mobileOpen)} className="lg:hidden p-2 text-slate-300">
              {mobileOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      <AnimatePresence>
        {mobileOpen && (
          <motion.div initial={{ height: 0 }} animate={{ height: "auto" }} exit={{ height: 0 }} className="lg:hidden overflow-hidden bg-slate-900 border-t border-slate-800">
            <div className="container mx-auto px-6 py-4 space-y-2 max-h-[80vh] overflow-y-auto">
              <Link href="/" onClick={() => setMobileOpen(false)} className="block px-4 py-3 rounded-lg text-slate-200 hover:bg-slate-800">خانه</Link>
              <div className="border-t border-slate-800 pt-3 mt-3">
                <p className="px-4 py-2 text-xs text-slate-500 uppercase">ماژول‌های علمی</p>
                {SCIENTIFIC_MODULES.map(m => (
                  <Link key={m.id} href={m.href} onClick={() => setMobileOpen(false)} className="block px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800 rounded-lg">{m.title}</Link>
                ))}
              </div>
              <div className="border-t border-slate-800 pt-3 mt-3">
                <p className="px-4 py-2 text-xs text-slate-500 uppercase">خدمات</p>
                {COMMUNITY_MODULES.map(m => (
                  <Link key={m.id} href={m.href} onClick={() => setMobileOpen(false)} className="block px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800 rounded-lg">{m.title}</Link>
                ))}
              </div>
              <div className="border-t border-slate-800 pt-3 mt-3">
                <p className="px-4 py-2 text-xs text-slate-500 uppercase">حساب کاربری</p>
                <Link href="/profile" onClick={() => setMobileOpen(false)} className="block px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800 rounded-lg">پروفایل من</Link>
                <Link href="/admin" onClick={() => setMobileOpen(false)} className="block px-4 py-2.5 text-sm text-slate-300 hover:bg-slate-800 rounded-lg">پنل مدیریت</Link>
              </div>
              <div className="border-t border-slate-800 pt-3 mt-3 flex flex-col gap-2">
                <Link href="/login" onClick={() => setMobileOpen(false)} className="w-full px-4 py-3 border border-slate-700 rounded-xl text-center text-sm">ورود</Link>
                <Link href="/register" onClick={() => setMobileOpen(false)} className="w-full px-4 py-3 bg-emerald-600 rounded-xl text-center text-sm">ثبت‌نام</Link>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
}
'''
    
    write_file(WEB / "components" / "layout" / "Navbar.tsx", content)


# ========== 2. صفحه پروفایل کامل ==========
def create_profile_page():
    print("\n👤 ایجاد صفحه پروفایل کامل...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, User, Mail, Phone, MapPin, Edit3, Camera, 
  Award, Activity, Calendar, Wallet, Settings as SettingsIcon,
  TrendingUp, Droplets, TreePine, BarChart3, Bell, Shield
} from "lucide-react";
import { healthService, dashboardService } from "@/lib/api";

export default function ProfilePage() {
  const [activeTab, setActiveTab] = useState("overview");
  const [stats, setStats] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  const user = {
    name: "علی محمدی",
    email: "ali@example.com",
    phone: "۰۹۱۲۳۴۵۶۷۸۹",
    location: "خراسان رضوی، مشهد",
    joinDate: "۱۴۰۳/۰۱/۱۵",
    role: "کشاورز پایدار",
    avatar: "👨‍🌾",
    bio: "کشاورز فعال در حوزه کشت پایدار گندم و جو با ۱۵ سال سابقه در خراسان رضوی"
  };

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await dashboardService.getStats();
        setStats(data);
      } catch (e) {
        setStats(null);
      } finally {
        setLoading(false);
      }
    };
    loadStats();
  }, []);

  const userStats = [
    { label: "پروژه‌های فعال", value: "۱۲", icon: Activity, color: "#10b981" },
    { label: "هکتار تحت مدیریت", value: "۴۵", icon: MapPin, color: "#3b82f6" },
    { label: "گواهی‌نامه‌ها", value: "۵", icon: Award, color: "#f59e0b" },
    { label: "اعتبار EcoCoin", value: "۲,۴۵۰", icon: Wallet, color: "#8b5cf6" },
  ];

  const tabs = [
    { id: "overview", label: "نمای کلی", icon: User },
    { id: "projects", label: "پروژه‌ها", icon: Activity },
    { id: "wallet", label: "کیف پول", icon: Wallet },
    { id: "certificates", label: "گواهی‌نامه‌ها", icon: Award },
    { id: "notifications", label: "اعلان‌ها", icon: Bell },
    { id: "security", label: "امنیت", icon: Shield },
    { id: "settings", label: "تنظیمات", icon: SettingsIcon },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="container mx-auto px-6 py-12">
        <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8">
          <ArrowRight className="h-4 w-4" /> بازگشت به خانه
        </Link>

        {/* Profile Header */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-gradient-to-l from-emerald-600 to-green-700 rounded-3xl p-8 mb-8 relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=1200')] opacity-10 bg-cover" />
          <div className="relative flex flex-col md:flex-row items-center gap-6">
            <div className="relative">
              <div className="w-32 h-32 rounded-full bg-white/20 backdrop-blur flex items-center justify-center text-6xl border-4 border-white/30 shadow-2xl">
                {user.avatar}
              </div>
              <button className="absolute bottom-0 left-0 p-2 bg-white rounded-full shadow-lg hover:scale-110 transition-transform">
                <Camera className="h-4 w-4 text-slate-700" />
              </button>
            </div>
            <div className="text-center md:text-right flex-1">
              <h1 className="text-4xl font-black text-white mb-2">{user.name}</h1>
              <p className="text-emerald-100 text-lg mb-3">{user.role}</p>
              <p className="text-emerald-100/80 text-sm mb-4 max-w-xl">{user.bio}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm text-emerald-100">
                <span className="flex items-center gap-1"><Mail className="h-4 w-4" />{user.email}</span>
                <span className="flex items-center gap-1"><Phone className="h-4 w-4" />{user.phone}</span>
                <span className="flex items-center gap-1"><MapPin className="h-4 w-4" />{user.location}</span>
                <span className="flex items-center gap-1"><Calendar className="h-4 w-4" />عضو از {user.joinDate}</span>
              </div>
            </div>
            <button className="px-6 py-3 bg-white/20 backdrop-blur border border-white/30 text-white rounded-xl hover:bg-white/30 transition-all flex items-center gap-2">
              <Edit3 className="h-4 w-4" /> ویرایش پروفایل
            </button>
          </div>
        </motion.div>

        {/* Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
          {userStats.map((s, i) => (
            <motion.div
              key={s.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 transition-all"
            >
              <s.icon className="h-8 w-8 mb-3" style={{ color: s.color }} />
              <p className="text-3xl font-black text-white">{s.value}</p>
              <p className="text-sm text-slate-400">{s.label}</p>
            </motion.div>
          ))}
        </div>

        {/* Tabs */}
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-5 py-3 rounded-xl flex items-center gap-2 whitespace-nowrap transition-all ${
                activeTab === tab.id 
                  ? "bg-emerald-600 text-white shadow-lg shadow-emerald-500/30" 
                  : "bg-slate-900/50 text-slate-400 hover:bg-slate-800"
              }`}
            >
              <tab.icon className="h-4 w-4" /> {tab.label}
            </button>
          ))}
        </div>

        {/* Content */}
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8"
        >
          {activeTab === "overview" && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">فعالیت‌های اخیر</h2>
              <div className="space-y-3">
                {[
                  { action: "شبیه‌سازی هیدرولوژی حوضه کشف‌رود", time: "۲ ساعت پیش", icon: "💧", module: "هیدرولوژی" },
                  { action: "دریافت گواهی‌نامه AquaCrop", time: "دیروز", icon: "🎓", module: "آموزش" },
                  { action: "انتشار مقاله در کتابخانه", time: "۳ روز پیش", icon: "📚", module: "کتابخانه" },
                  { action: "دریافت ۱۰۰ EcoCoin", time: "هفته پیش", icon: "🪙", module: "EcoCoin" },
                  { action: "تحلیل NDVI مزرعه", time: "هفته پیش", icon: "🛰️", module: "سنجش از دور" },
                ].map((a, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="flex items-center gap-4 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-colors"
                  >
                    <span className="text-3xl">{a.icon}</span>
                    <div className="flex-1">
                      <p className="text-white font-medium">{a.action}</p>
                      <p className="text-xs text-slate-500 mt-1">{a.time} • {a.module}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "projects" && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">پروژه‌های من</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { name: "مزرعه گندم کشف‌رود", area: "۱۵ هکتار", status: "فعال", progress: 75 },
                  { name: "باغ پسته تربت حیدریه", area: "۸ هکتار", status: "فعال", progress: 45 },
                  { name: "مرتع جو قوچان", area: "۲۲ هکتار", status: "در انتظار", progress: 20 },
                ].map((p, i) => (
                  <div key={i} className="p-5 bg-slate-800/50 rounded-xl">
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="font-bold text-white">{p.name}</h3>
                      <span className="text-xs px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full">{p.status}</span>
                    </div>
                    <p className="text-sm text-slate-400 mb-3">مساحت: {p.area}</p>
                    <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-l from-emerald-500 to-green-600" style={{ width: `${p.progress}%` }} />
                    </div>
                    <p className="text-xs text-slate-500 mt-2">{p.progress}% تکمیل شده</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "wallet" && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">کیف پول EcoCoin</h2>
              <div className="bg-gradient-to-l from-purple-600 to-violet-700 rounded-2xl p-8 mb-6">
                <p className="text-purple-100 text-sm mb-2">موجودی فعلی</p>
                <p className="text-5xl font-black text-white mb-4">۲,۴۵۰ <span className="text-lg">EcoCoin</span></p>
                <p className="text-purple-100/80 text-sm mb-6">معادل تقریبی: ۲۴۵,۰۰۰ تومان</p>
                <div className="flex gap-3">
                  <button className="px-6 py-2 bg-white/20 backdrop-blur rounded-lg text-white hover:bg-white/30">ارسال</button>
                  <button className="px-6 py-2 bg-white/20 backdrop-blur rounded-lg text-white hover:bg-white/30">دریافت</button>
                  <button className="px-6 py-2 bg-white/20 backdrop-blur rounded-lg text-white hover:bg-white/30">تاریخچه</button>
                </div>
              </div>
              <h3 className="text-lg font-bold text-white mb-4">تراکنش‌های اخیر</h3>
              <div className="space-y-2">
                {[
                  { type: "دریافت", desc: "پاداش ثبت داده NDVI", amount: "+۱۰۰", time: "۲ ساعت پیش" },
                  { type: "ارسال", desc: "خرید بذر از فروشگاه", amount: "-۵۰", time: "دیروز" },
                  { type: "دریافت", desc: "تکمیل دوره آموزشی", amount: "+۲۰۰", time: "۳ روز پیش" },
                ].map((t, i) => (
                  <div key={i} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                    <div>
                      <p className="text-white font-medium">{t.desc}</p>
                      <p className="text-xs text-slate-500">{t.time}</p>
                    </div>
                    <span className={`font-bold ${t.amount.startsWith("+") ? "text-emerald-400" : "text-red-400"}`}>
                      {t.amount} Eco
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "certificates" && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">گواهی‌نامه‌های من</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { title: "AquaCrop پیشرفته", issuer: "اکو نوژین", date: "۱۴۰۴/۱۲/۱۵", color: "from-emerald-500 to-green-600" },
                  { title: "مدیریت آب پایدار", issuer: "FAO", date: "۱۴۰۴/۱۰/۲۰", color: "from-blue-500 to-cyan-600" },
                  { title: "کشاورزی حفاظتی", issuer: "اکو نوژین", date: "۱۴۰۴/۰۸/۰۵", color: "from-amber-500 to-orange-600" },
                ].map((c, i) => (
                  <div key={i} className={`p-6 bg-gradient-to-br ${c.color} rounded-2xl`}>
                    <Award className="h-10 w-10 text-white mb-3" />
                    <h3 className="text-xl font-bold text-white mb-2">{c.title}</h3>
                    <p className="text-white/80 text-sm mb-1">صادر کننده: {c.issuer}</p>
                    <p className="text-white/80 text-sm">تاریخ: {c.date}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "notifications" && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">اعلان‌ها</h2>
              <div className="space-y-3">
                {[
                  { title: "هشدار یخبندان", desc: "احتمال یخبندان در ۴۸ ساعت آینده", time: "۱ ساعت پیش", type: "warning" },
                  { title: "توصیه آبیاری", desc: "زمان بهینه آبیاری مزرعه گندم", time: "۳ ساعت پیش", type: "info" },
                  { title: "به‌روزرسانی سیستم", desc: "ماژول جدید پایش خشکسالی اضافه شد", time: "دیروز", type: "success" },
                ].map((n, i) => (
                  <div key={i} className={`p-4 rounded-xl border-r-4 ${
                    n.type === "warning" ? "bg-amber-500/10 border-amber-500" :
                    n.type === "info" ? "bg-blue-500/10 border-blue-500" :
                    "bg-emerald-500/10 border-emerald-500"
                  }`}>
                    <h4 className="font-bold text-white mb-1">{n.title}</h4>
                    <p className="text-sm text-slate-300 mb-2">{n.desc}</p>
                    <p className="text-xs text-slate-500">{n.time}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === "security" && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">امنیت حساب</h2>
              <div className="space-y-4">
                <div className="p-5 bg-slate-800/50 rounded-xl">
                  <h3 className="font-bold text-white mb-3">تغییر رمز عبور</h3>
                  <div className="space-y-3">
                    <input type="password" placeholder="رمز عبور فعلی" className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white" />
                    <input type="password" placeholder="رمز عبور جدید" className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white" />
                    <input type="password" placeholder="تکرار رمز عبور جدید" className="w-full px-4 py-3 bg-slate-900 border border-slate-700 rounded-xl text-white" />
                    <button className="px-6 py-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700">تغییر رمز</button>
                  </div>
                </div>
                <div className="p-5 bg-slate-800/50 rounded-xl">
                  <h3 className="font-bold text-white mb-3">احراز هویت دو مرحله‌ای</h3>
                  <p className="text-sm text-slate-400 mb-3">امنیت حساب خود را با تایید دو مرحله‌ای افزایش دهید</p>
                  <button className="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700">فعال‌سازی</button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "settings" && (
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">تنظیمات حساب</h2>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm text-slate-400 mb-2">زبان ترجیحی</label>
                  <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                    <option>فارسی</option>
                    <option>English</option>
                    <option>العربية</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm text-slate-400 mb-2">منطقه زمانی</label>
                  <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                    <option>Asia/Tehran (GMT+3:30)</option>
                    <option>UTC</option>
                  </select>
                </div>
                <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                  <div>
                    <p className="font-medium text-white">دریافت اعلان‌های ایمیلی</p>
                    <p className="text-sm text-slate-400">هشدارهای کشاورزی و به‌روزرسانی‌ها</p>
                  </div>
                  <input type="checkbox" defaultChecked className="w-5 h-5 accent-emerald-500" />
                </div>
                <button className="px-6 py-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700">ذخیره تنظیمات</button>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "profile" / "page.tsx", content)


# ========== 3. صفحه ادمین کامل ==========
def create_admin_page():
    print("\n👨‍💼 ایجاد پنل ادمین کامل...")
    
    content = '''"use client";

import Link from "next/link";
import { useState } from "react";
import { motion } from "framer-motion";
import { 
  Users, Package, Activity, Settings, TrendingUp, Shield, 
  BarChart3, FileText, AlertTriangle, CheckCircle, ArrowRight,
  DollarSign, Database, Server, Cpu, HardDrive, Globe
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar
} from "recharts";

const USER_GROWTH = [
  { month: "فروردین", users: 450, active: 320 },
  { month: "اردیبهشت", users: 580, active: 420 },
  { month: "خرداد", users: 720, active: 540 },
  { month: "تیر", users: 890, active: 680 },
  { month: "مرداد", users: 1050, active: 820 },
  { month: "شهریور", users: 1245, active: 956 },
];

const MODULE_USAGE = [
  { name: "هیدرولوژی", users: 345, requests: 12500 },
  { name: "کربن خاک", users: 289, requests: 8900 },
  { name: "فرسایش", users: 156, requests: 5600 },
  { name: "هواشناسی", users: 412, requests: 15800 },
  { name: "فروشگاه", users: 523, requests: 22400 },
  { name: "GIS", users: 278, requests: 9800 },
];

export default function AdminPage() {
  const [activeSection, setActiveSection] = useState("dashboard");

  const menuItems = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3 },
    { id: "users", label: "کاربران", icon: Users },
    { id: "modules", label: "ماژول‌ها", icon: Package },
    { id: "analytics", label: "آمار", icon: TrendingUp },
    { id: "content", label: "محتوا", icon: FileText },
    { id: "security", label: "امنیت", icon: Shield },
    { id: "system", label: "سیستم", icon: Server },
    { id: "settings", label: "تنظیمات", icon: Settings },
  ];

  const stats = [
    { label: "کل کاربران", value: "۱,۲۴۵", change: "+۱۲٪", icon: Users, color: "#3b82f6" },
    { label: "کاربران فعال", value: "۸۵۶", change: "+۸٪", icon: Activity, color: "#10b981" },
    { label: "درآمد ماهانه", value: "۴۵M", change: "+۲۳٪", icon: DollarSign, color: "#f59e0b" },
    { label: "هشدارها", value: "۳", change: "-۲", icon: AlertTriangle, color: "#ef4444" },
  ];

  const systemStats = [
    { label: "CPU", value: "۴۵٪", icon: Cpu, color: "#3b82f6" },
    { label: "RAM", value: "۶۲٪", icon: Database, color: "#8b5cf6" },
    { label: "Disk", value: "۳۸٪", icon: HardDrive, color: "#10b981" },
    { label: "Network", value: "۱۲ MB/s", icon: Globe, color: "#f59e0b" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="flex">
        {/* Sidebar */}
        <aside className="hidden lg:block w-64 min-h-screen bg-slate-900 border-l border-slate-800 p-6 sticky top-16">
          <div className="mb-8">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <Shield className="h-5 w-5 text-emerald-400" /> پنل مدیریت
            </h2>
            <p className="text-xs text-slate-500 mt-1">اکو نوژین ادمین</p>
          </div>
          <nav className="space-y-1">
            {menuItems.map(item => (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  activeSection === item.id 
                    ? "bg-emerald-600 text-white shadow-lg shadow-emerald-500/30" 
                    : "text-slate-400 hover:bg-slate-800 hover:text-white"
                }`}
              >
                <item.icon className="h-5 w-5" /> {item.label}
              </button>
            ))}
          </nav>
        </aside>

        {/* Main */}
        <main className="flex-1 p-8">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
                <ArrowRight className="h-4 w-4" /> بازگشت به سایت
              </Link>
              <h1 className="text-3xl font-bold text-white mb-2">داشبورد مدیریت</h1>
              <p className="text-slate-400">نمای کلی از وضعیت سیستم اکو نوژین</p>
            </div>
            <div className="flex gap-2">
              <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm text-white flex items-center gap-2">
                <FileText className="h-4 w-4" /> گزارش
              </button>
              <button className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 rounded-lg text-sm text-white">
                به‌روزرسانی
              </button>
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {stats.map((s, i) => (
              <motion.div
                key={s.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
              >
                <div className="flex items-center justify-between mb-4">
                  <s.icon className="h-8 w-8" style={{ color: s.color }} />
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    s.change.startsWith("+") ? "bg-emerald-500/10 text-emerald-400" : "bg-red-500/10 text-red-400"
                  }`}>{s.change}</span>
                </div>
                <p className="text-3xl font-black text-white mb-1">{s.value}</p>
                <p className="text-sm text-slate-400">{s.label}</p>
              </motion.div>
            ))}
          </div>

          {/* System Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            {systemStats.map(s => (
              <div key={s.label} className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <s.icon className="h-4 w-4" style={{ color: s.color }} />
                  <span className="text-xs text-slate-400">{s.label}</span>
                </div>
                <p className="text-xl font-bold text-white">{s.value}</p>
              </div>
            ))}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-emerald-400" /> رشد کاربران
              </h3>
              <ResponsiveContainer width="100%" height={280}>
                <AreaChart data={USER_GROWTH}>
                  <defs>
                    <linearGradient id="usersGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
                  <YAxis stroke="#64748b" fontSize={11} />
                  <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                  <Legend />
                  <Area type="monotone" dataKey="users" stroke="#3b82f6" fill="url(#usersGrad)" name="کل کاربران" />
                  <Line type="monotone" dataKey="active" stroke="#10b981" strokeWidth={2} name="فعال" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Package className="h-5 w-5 text-emerald-400" /> استفاده از ماژول‌ها
              </h3>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={MODULE_USAGE} layout="vertical">
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis type="number" stroke="#64748b" fontSize={11} />
                  <YAxis dataKey="name" type="category" stroke="#64748b" fontSize={11} width={80} />
                  <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                  <Bar dataKey="users" fill="#10b981" radius={[0, 8, 8, 0]} name="کاربران" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Recent Activity & Alerts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Activity className="h-5 w-5 text-emerald-400" /> فعالیت‌های اخیر
              </h3>
              <div className="space-y-3">
                {[
                  { user: "علی محمدی", action: "ثبت‌نام کرد", time: "۵ دقیقه پیش", status: "success" },
                  { user: "مریم احمدی", action: "پروژه جدید ایجاد کرد", time: "۱ ساعت پیش", status: "success" },
                  { user: "سیستم", action: "هشدار امنیتی", time: "۲ ساعت پیش", status: "warning" },
                  { user: "رضا کریمی", action: "خرید از فروشگاه", time: "۳ ساعت پیش", status: "success" },
                  { user: "زهرا حسینی", action: "گواهی‌نامه دریافت کرد", time: "۵ ساعت پیش", status: "success" },
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

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Shield className="h-5 w-5 text-emerald-400" /> وضعیت سیستم
              </h3>
              <div className="space-y-3">
                {[
                  { name: "API Server", status: "online", uptime: "99.9%" },
                  { name: "Database", status: "online", uptime: "99.8%" },
                  { name: "Redis Cache", status: "online", uptime: "100%" },
                  { name: "AI Service", status: "online", uptime: "99.5%" },
                  { name: "CDN", status: "online", uptime: "100%" },
                ].map((s, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                      <span className="text-white">{s.name}</span>
                    </div>
                    <span className="text-sm text-emerald-400">{s.uptime}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "admin" / "page.tsx", content)


# ========== 4. ماژول جدید: پایش خشکسالی ==========
def create_drought_page():
    print("\n🏜️ ایجاد ماژول پایش خشکسالی...")
    
    content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, AlertTriangle, Droplets, Thermometer, Sun, 
  TrendingDown, Map, Calendar, Download, Filter
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar
} from "recharts";

const DROUGHT_INDEX = [
  { month: "فروردین", spi: 0.8, rain: 45, status: "عادی" },
  { month: "اردیبهشت", spi: 0.5, rain: 30, status: "هشدار" },
  { month: "خرداد", spi: -0.2, rain: 12, status: "خشکسالی خفیف" },
  { month: "تیر", spi: -0.8, rain: 3, status: "خشکسالی متوسط" },
  { month: "مرداد", spi: -1.5, rain: 0, status: "خشکسالی شدید" },
  { month: "شهریور", spi: -1.8, rain: 2, status: "خشکسالی شدید" },
  { month: "مهر", spi: -1.2, rain: 15, status: "خشکسالی متوسط" },
  { month: "آبان", spi: -0.5, rain: 35, status: "هشدار" },
  { month: "آذر", spi: 0.3, rain: 65, status: "عادی" },
  { month: "دی", spi: 0.7, rain: 85, status: "عادی" },
  { month: "بهمن", spi: 0.9, rain: 75, status: "عادی" },
  { month: "اسفند", spi: 0.6, rain: 55, status: "عادی" },
];

const REGIONS = [
  { name: "خراسان رضوی", spi: -1.2, level: "شدید", color: "#dc2626", area: "۱۱۳,۰۰۰ km²" },
  { name: "سیستان و بلوچستان", spi: -1.8, level: "فوق شدید", color: "#7f1d1d", area: "۱۸۱,۰۰۰ km²" },
  { name: "اصفهان", spi: -0.9, level: "متوسط", color: "#ea580c", area: "۱۰۷,۰۰۰ km²" },
  { name: "یزد", spi: -1.5, level: "شدید", color: "#dc2626", area: "۱۲۹,۰۰۰ km²" },
  { name: "کرمان", spi: -1.1, level: "شدید", color: "#dc2626", area: "۱۸۰,۰۰۰ km²" },
  { name: "فارس", spi: -0.6, level: "خفیف", color: "#f59e0b", area: "۱۲۲,۰۰۰ km²" },
  { name: "مازندران", spi: 0.8, level: "عادی", color: "#10b981", area: "۲۳,۰۰۰ km²" },
  { name: "گیلان", spi: 0.9, level: "عادی", color: "#10b981", area: "۱۴,۰۰۰ km²" },
];

const WATER_RESERVES = [
  { name: "سد دوستی", level: 35, capacity: "۱,۲۰۰ MCM", trend: "کاهشی" },
  { name: "سد کارون ۴", level: 68, capacity: "۲,۱۹۰ MCM", trend: "پایدار" },
  { name: "سد کرخه", level: 42, capacity: "۵,۱۳۰ MCM", trend: "کاهشی" },
  { name: "سد دز", level: 55, capacity: "۳,۳۴۰ MCM", trend: "پایدار" },
  { name: "سد درودزن", level: 28, capacity: "۹۶۰ MCM", trend: "بحرانی" },
];

export default function DroughtPage() {
  const [selectedRegion, setSelectedRegion] = useState(REGIONS[0]);
  const [timeframe, setTimeframe] = useState("monthly");

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-red-600 to-orange-700 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-red-500 to-orange-600 shadow-2xl">
                <AlertTriangle className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-red-400 text-sm font-medium mb-2">ماژول پیشرفته</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">پایش خشکسالی</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  رصد لحظه‌ای شاخص‌های خشکسالی (SPI، PDSI، VHI) با استفاده از داده‌های ماهواره‌ای و ایستگاه‌های هواشناسی
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Alert Banner */}
      <section className="container mx-auto px-6 py-8">
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="p-6 bg-gradient-to-l from-red-500/10 to-orange-500/10 border border-red-500/30 rounded-2xl flex items-start gap-4"
        >
          <AlertTriangle className="h-8 w-8 text-red-400 flex-shrink-0 mt-1" />
          <div className="flex-1">
            <h3 className="text-xl font-bold text-red-300 mb-2">هشدار خشکسالی شدید</h3>
            <p className="text-red-200/80">
              ۴ استان در وضعیت خشکسالی شدید تا فوق شدید قرار دارند. توصیه می‌شود در مصرف آب صرفه‌جویی شده و از کشت محصولات پرمصرف خودداری شود.
            </p>
          </div>
          <button className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 rounded-lg text-red-300 text-sm">
            مشاهده جزئیات
          </button>
        </motion.div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "استان‌های بحرانی", value: "۴", icon: AlertTriangle, color: "#dc2626" },
            { label: "میانگین SPI", value: "-۰.۸", icon: TrendingDown, color: "#f59e0b" },
            { label: "کاهش بارش", value: "۳۵٪", icon: Droplets, color: "#3b82f6" },
            { label: "افزایش دما", value: "+۲.۳°", icon: Thermometer, color: "#ef4444" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* SPI Chart */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-red-400" />
              شاخص SPI سالانه
            </h3>
            <div className="flex gap-2">
              <select 
                value={timeframe}
                onChange={e => setTimeframe(e.target.value)}
                className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white"
              >
                <option value="monthly">ماهانه</option>
                <option value="seasonal">فصلی</option>
                <option value="yearly">سالانه</option>
              </select>
              <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
                <Download className="h-4 w-4 text-slate-300" />
              </button>
            </div>
          </div>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={DROUGHT_INDEX}>
              <defs>
                <linearGradient id="spiPositive" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="spiNegative" x1="0" y1="1" x2="0" y2="0">
                  <stop offset="5%" stopColor="#dc2626" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#dc2626" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} domain={[-2, 2]} />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
              <Legend />
              <Area type="monotone" dataKey="spi" stroke="#ef4444" strokeWidth={2} fill="url(#spiNegative)" name="SPI" />
              <Line type="monotone" dataKey="rain" stroke="#3b82f6" strokeWidth={2} name="بارش (mm)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>

      {/* Regions Grid */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <div className="lg:col-span-2 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
              <Map className="h-5 w-5 text-red-400" />
              وضعیت استان‌ها
            </h3>
            <div className="space-y-3">
              {REGIONS.map((region, i) => (
                <motion.div
                  key={region.name}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  onClick={() => setSelectedRegion(region)}
                  className={`p-4 rounded-xl cursor-pointer transition-all ${
                    selectedRegion.name === region.name
                      ? "bg-slate-800 border-2 border-red-500/50"
                      : "bg-slate-800/50 hover:bg-slate-800 border-2 border-transparent"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <div className="w-3 h-16 rounded-full" style={{ backgroundColor: region.color }} />
                      <div>
                        <h4 className="font-bold text-white">{region.name}</h4>
                        <p className="text-xs text-slate-400">مساحت: {region.area}</p>
                      </div>
                    </div>
                    <div className="text-left">
                      <p className="text-2xl font-black text-white">{region.spi}</p>
                      <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: region.color + "20", color: region.color }}>
                        {region.level}
                      </span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>

          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">جزئیات منطقه</h3>
            <div className="space-y-4">
              <div>
                <p className="text-sm text-slate-400 mb-1">منطقه انتخاب شده</p>
                <p className="text-2xl font-bold text-white">{selectedRegion.name}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">شاخص SPI</p>
                <p className="text-3xl font-black" style={{ color: selectedRegion.color }}>{selectedRegion.spi}</p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">سطح خشکسالی</p>
                <span className="px-3 py-1.5 rounded-lg text-sm font-medium" style={{ backgroundColor: selectedRegion.color + "20", color: selectedRegion.color }}>
                  {selectedRegion.level}
                </span>
              </div>
              <div className="pt-4 border-t border-slate-800">
                <p className="text-sm text-slate-400 mb-3">توصیه‌ها:</p>
                <ul className="space-y-2 text-sm text-slate-300">
                  <li>• صرفه‌جویی در مصرف آب</li>
                  <li>• تغییر الگوی کشت</li>
                  <li>• استفاده از آبیاری قطره‌ای</li>
                  <li>• کشت محصولات کم‌آب‌بر</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Water Reserves */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-8">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Droplets className="h-5 w-5 text-blue-400" />
            وضعیت سدهای کشور
          </h3>
          <div className="space-y-4">
            {WATER_RESERVES.map((dam, i) => (
              <motion.div
                key={dam.name}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.05 }}
                className="p-4 bg-slate-800/50 rounded-xl"
              >
                <div className="flex items-center justify-between mb-3">
                  <div>
                    <h4 className="font-bold text-white">{dam.name}</h4>
                    <p className="text-xs text-slate-400">ظرفیت: {dam.capacity}</p>
                  </div>
                  <div className="text-left">
                    <p className="text-2xl font-black text-white">{dam.level}%</p>
                    <span className={`text-xs ${
                      dam.trend === "کاهشی" ? "text-red-400" :
                      dam.trend === "بحرانی" ? "text-red-600" :
                      "text-emerald-400"
                    }`}>{dam.trend}</span>
                  </div>
                </div>
                <div className="h-3 bg-slate-700 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    whileInView={{ width: `${dam.level}%` }}
                    viewport={{ once: true }}
                    transition={{ duration: 1, delay: i * 0.1 }}
                    className={`h-full rounded-full ${
                      dam.level > 60 ? "bg-gradient-to-l from-emerald-500 to-green-600" :
                      dam.level > 40 ? "bg-gradient-to-l from-amber-500 to-orange-600" :
                      "bg-gradient-to-l from-red-500 to-red-700"
                    }`}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "drought" / "page.tsx", content)


# ========== 5. چت بات هوشمند OpenAI ==========
def create_ai_chat():
    print("\n🤖 به‌روزرسانی چت بات با OpenAI...")
    
    content = '''"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageCircle, X, Send, Leaf, Bot, User, Loader2, Sparkles } from "lucide-react";
import { aiService } from "@/lib/api";

const SUGGESTIONS = [
  "چگونه مصرف آب مزرعه را کاهش دهم؟",
  "بهترین زمان کشت گندم در خراسان",
  "راهکارهای مقابله با فرسایش خاک",
  "تفسیر شاخص NDVI",
];

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { role: "assistant", content: "سلام! من دستیار هوشمند اکو نوژین هستم. چطور می‌توانم در احیای زمین به شما کمک کنم؟" }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text?: string) => {
    const messageText = text || input;
    if (!messageText.trim()) return;
    
    const userMsg = { role: "user", content: messageText };
    setMessages(prev => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    
    try {
      const response = await aiService.chat(messageText);
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: response.message || response.response || "متشکرم از سوال شما. برای پاسخ دقیق‌تر، لطفاً جزئیات بیشتری ارائه دهید."
      }]);
    } catch (e) {
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "متأسفم، در حال حاضر در دسترسی به سرویس هوش مصنوعی مشکل وجود دارد. لطفاً بعداً دوباره تلاش کنید."
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {!isOpen && (
        <motion.button
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 left-6 p-4 bg-gradient-to-br from-emerald-500 to-green-600 text-white rounded-full shadow-2xl shadow-emerald-500/50 z-50 group"
        >
          <MessageCircle className="h-6 w-6" />
          <span className="absolute top-0 right-0 w-3 h-3 bg-red-500 rounded-full animate-pulse" />
        </motion.button>
      )}
      
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-6 left-6 w-96 h-[600px] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl flex flex-col z-50 overflow-hidden"
          >
            {/* Header */}
            <div className="p-4 bg-gradient-to-l from-emerald-600 to-green-700 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-white/20 rounded-lg">
                  <Leaf className="h-5 w-5 text-white" />
                </div>
                <div>
                  <p className="font-bold text-white">دستیار هوشمند</p>
                  <p className="text-xs text-emerald-100 flex items-center gap-1">
                    <span className="w-2 h-2 bg-emerald-300 rounded-full animate-pulse" />
                    آنلاین • Powered by AI
                  </p>
                </div>
              </div>
              <button onClick={() => setIsOpen(false)} className="p-2 hover:bg-white/10 rounded-lg transition-colors">
                <X className="h-5 w-5 text-white" />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-950/50">
              {messages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className={`flex gap-2 ${msg.role === "user" ? "justify-start" : "justify-end"}`}
                >
                  {msg.role === "assistant" && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                  )}
                  <div className={`max-w-[75%] p-3 rounded-2xl text-sm ${
                    msg.role === "user" 
                      ? "bg-slate-800 text-slate-100 rounded-br-none" 
                      : "bg-emerald-600 text-white rounded-bl-none"
                  }`}>
                    {msg.content}
                  </div>
                  {msg.role === "user" && (
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
                      <User className="h-4 w-4 text-slate-300" />
                    </div>
                  )}
                </motion.div>
              ))}
              
              {loading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center">
                    <Bot className="h-4 w-4 text-white" />
                  </div>
                  <div className="bg-emerald-600 rounded-2xl rounded-bl-none p-3 flex items-center gap-2">
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span className="text-sm">در حال پاسخ...</span>
                  </div>
                </motion.div>
              )}
              
              <div ref={messagesEndRef} />
            </div>

            {/* Suggestions */}
            {messages.length === 1 && (
              <div className="px-4 py-3 border-t border-slate-800 bg-slate-900/50">
                <p className="text-xs text-slate-500 mb-2 flex items-center gap-1">
                  <Sparkles className="h-3 w-3" /> پیشنهادات:
                </p>
                <div className="flex flex-wrap gap-2">
                  {SUGGESTIONS.map((s, i) => (
                    <button
                      key={i}
                      onClick={() => sendMessage(s)}
                      className="text-xs px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-full transition-colors"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input */}
            <div className="p-3 border-t border-slate-800 bg-slate-900 flex gap-2">
              <input
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyPress={e => e.key === "Enter" && sendMessage()}
                placeholder="سوال خود را بپرسید..."
                className="flex-1 px-4 py-2.5 bg-slate-800 border border-slate-700 rounded-xl text-sm text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500"
                disabled={loading}
              />
              <button
                onClick={() => sendMessage()}
                disabled={loading || !input.trim()}
                className="p-2.5 bg-emerald-600 hover:bg-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-xl transition-colors"
              >
                <Send className="h-5 w-5" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
'''
    
    write_file(WEB / "components" / "ai" / "ChatWidget.tsx", content)


# ========== 6. Analytics Hook ==========
def create_analytics():
    print("\n📊 ایجاد سیستم Analytics...")
    
    content = '''// Analytics tracking system
export const analytics = {
  track: (event: string, properties?: Record<string, any>) => {
    if (typeof window === "undefined") return;
    
    const data = {
      event,
      properties,
      timestamp: new Date().toISOString(),
      url: window.location.href,
      userAgent: navigator.userAgent,
    };
    
    // Send to backend
    fetch("/api/v1/analytics/track", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }).catch(err => console.log("Analytics error:", err));
    
    // Also log to console in development
    if (process.env.NODE_ENV === "development") {
      console.log("[Analytics]", event, properties);
    }
  },
  
  page: (name: string, properties?: Record<string, any>) => {
    analytics.track("page_view", { page: name, ...properties });
  },
  
  identify: (userId: string, traits?: Record<string, any>) => {
    analytics.track("identify", { userId, traits });
  },
};

// Hook for React components
export function useAnalytics() {
  return analytics;
}
'''
    
    write_file(WEB / "lib" / "analytics.ts", content)


# ========== 7. Vercel Configuration ==========
def create_vercel_config():
    print("\n🚀 ایجاد تنظیمات Vercel...")
    
    content = '''{
  "name": "econojin-web",
  "version": 2,
  "framework": "nextjs",
  "buildCommand": "pnpm build",
  "devCommand": "pnpm dev",
  "installCommand": "pnpm install",
  "outputDirectory": ".next",
  "regions": ["fra1"],
  "env": {
    "NEXT_PUBLIC_API_URL": "https://api.econojin.com"
  },
  "headers": [
    {
      "source": "/api/(.*)",
      "headers": [
        { "key": "Cache-Control", "value": "no-store, must-revalidate" }
      ]
    },
    {
      "source": "/(.*)",
      "headers": [
        { "key": "X-Content-Type-Options", "value": "nosniff" },
        { "key": "X-Frame-Options", "value": "DENY" },
        { "key": "X-XSS-Protection", "value": "1; mode=block" }
      ]
    }
  ],
  "redirects": [
    {
      "source": "/home",
      "destination": "/",
      "permanent": true
    }
  ]
}
'''
    
    write_file(ROOT / "apps" / "web" / "vercel.json", content)
    
    # ایجاد فایل .env.example
    env_content = '''# Econojin Environment Variables
# کپی این فایل به .env.local و پر کردن مقادیر

# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
API_SECRET_KEY=your-secret-key-here

# OpenAI (برای چت بات)
OPENAI_API_KEY=sk-your-openai-api-key

# Database
DATABASE_URL=sqlite+aiosqlite:///./econojin.db

# JWT
JWT_SECRET=your-jwt-secret-here

# Analytics
ANALYTICS_ENABLED=true
'''
    
    write_file(ROOT / "apps" / "web" / ".env.example", env_content)


# ========== 8. به‌روزرسانی API Service ==========
def update_api_service():
    print("\n📡 به‌روزرسانی API Service...")
    
    content = '''// Econojin API Services
const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function apiCall<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...options?.headers },
      cache: "no-store",
    });
    if (!res.ok) throw new Error(`API Error: ${res.status}`);
    return res.json();
  } catch (error) {
    console.error(`API call failed: ${path}`, error);
    throw error;
  }
}

// Health Service
export const healthService = {
  check: () => apiCall<any>("/api/v1/health"),
  modules: () => apiCall<any>("/api/v1/modules"),
};

// Dashboard Service
export const dashboardService = {
  getStats: () => apiCall<any>("/api/v1/dashboard/stats"),
  getActivity: () => apiCall<any>("/api/v1/dashboard/activity"),
};

// AI Service
export const aiService = {
  chat: (message: string, context?: any) =>
    apiCall<any>("/api/v1/ai/chat", { 
      method: "POST", 
      body: JSON.stringify({ message, context }) 
    }),
};

// Auth Service
export const authService = {
  login: (data: any) => apiCall<any>("/api/v1/auth/login", { method: "POST", body: JSON.stringify(data) }),
  register: (data: any) => apiCall<any>("/api/v1/auth/register", { method: "POST", body: JSON.stringify(data) }),
  getProfile: () => apiCall<any>("/api/v1/auth/profile"),
};

// Weather Service
export const weatherService = {
  getForecast: (location: string, days = 7) =>
    apiCall<any>(`/api/v1/weather/forecast?location=${encodeURIComponent(location)}&days=${days}`),
  getAlerts: (region: string) =>
    apiCall<any>(`/api/v1/weather/alerts?region=${encodeURIComponent(region)}`),
};

// GIS Service
export const gisService = {
  calculateArea: (coords: any) =>
    apiCall<any>("/api/v1/gis/calculate/area", { method: "POST", body: JSON.stringify({ coordinates: coords }) }),
  getNdvi: (region: string) =>
    apiCall<any>(`/api/v1/gis/ndvi?region=${encodeURIComponent(region)}`),
};

// Carbon Service
export const carbonService = {
  calculate: (data: any) =>
    apiCall<any>("/api/v1/carbon/calculate", { method: "POST", body: JSON.stringify(data) }),
};

// Drought Service
export const droughtService = {
  getIndex: (region: string) =>
    apiCall<any>(`/api/v1/drought/index?region=${encodeURIComponent(region)}`),
  getRegions: () => apiCall<any>("/api/v1/drought/regions"),
};

// Shop Service
export const shopService = {
  getProducts: () => apiCall<any>("/api/v1/shop"),
};

// Calendar Service
export const calendarService = {
  getEvents: () => apiCall<any>("/api/v1/calendar"),
};

// Library Service
export const libraryService = {
  getResources: () => apiCall<any>("/api/v1/library"),
};

// Education Service
export const educationService = {
  getCourses: () => apiCall<any>("/api/v1/education"),
};

// Community Service
export const communityService = {
  getPosts: () => apiCall<any>("/api/v1/community"),
};

// Analytics Service
export const analyticsService = {
  track: (event: string, properties?: any) =>
    apiCall<any>("/api/v1/analytics/track", { 
      method: "POST", 
      body: JSON.stringify({ event, properties, timestamp: new Date().toISOString() }) 
    }),
};
'''
    
    write_file(WEB / "lib" / "api.ts", content)


# ========== Main ==========
def main():
    print("🚀 ارتقای جامع اکو نوژین")
    print("=" * 70)
    print("ویژگی‌های جدید:")
    print("   • پروفایل و ادمین کامل")
    print("   • ماژول پایش خشکسالی")
    print("   • چت بات هوشمند OpenAI")
    print("   • سیستم Analytics")
    print("   • آماده‌سازی Vercel")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    fix_navbar_with_profile()
    create_profile_page()
    create_admin_page()
    create_drought_page()
    create_ai_chat()
    create_analytics()
    create_vercel_config()
    update_api_service()
    
    print("\n" + "=" * 70)
    print("✅ ارتقای جامع تکمیل شد!")
    print("\n🎯 ویژگی‌های جدید:")
    print("   👤 پروفایل کاربری با ۷ تب")
    print("   👨‍💼 پنل ادمین با چارت و آمار")
    print("   🏜️ ماژول پایش خشکسالی")
    print("   🤖 چت بات هوشمند با پیشنهادات")
    print("   📊 سیستم Analytics")
    print("   🚀 تنظیمات Vercel")
    
    print("\n🔗 لینک‌های جدید:")
    print("   • /profile - پروفایل کاربری")
    print("   • /admin - پنل مدیریت")
    print("   • /drought - پایش خشکسالی")
    
    print("\n🚀 گام بعدی:")
    print("   1. پاک‌سازی: Remove-Item .next -Recurse -Force")
    print("   2. اجرا: pnpm run dev -- -p 3001")
    print("   3. مشاهده:")
    print("      • http://localhost:3001/profile")
    print("      • http://localhost:3001/admin")
    print("      • http://localhost:3001/drought")
    print("   4. کلیک روی آواتار در Navbar برای دسترسی به پروفایل")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())