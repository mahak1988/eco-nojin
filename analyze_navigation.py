#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 آنالیز و اصلاح کامل ناوبری اکو نوژین - نسخه بدون f-string
"""
import sys
import re
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)}")


def fix_middleware():
    print("\n" + "=" * 70)
    print("🚨 رفع خطای ERR_TOO_MANY_REDIRECTS")
    print("=" * 70)
    
    middleware_paths = [
        ROOT / "apps" / "web" / "middleware.ts",
        ROOT / "apps" / "web" / "src" / "middleware.ts",
    ]
    
    for path in middleware_paths:
        if path.exists():
            print(f"\n📄 یافت شد: {path.relative_to(ROOT)}")
            disabled_path = path.with_suffix(".ts.disabled")
            try:
                path.rename(disabled_path)
                print(f"   ✅ غیرفعال شد: {path.name} → {disabled_path.name}")
            except Exception as e:
                path.write_text("// Disabled\nexport const config = { matcher: [] };\n", encoding="utf-8")
                print(f"   ✅ محتوا پاک شد")
    
    if not any(p.exists() for p in middleware_paths):
        print("\n✅ هیچ middleware.ts یافت نشد - عالی!")


def analyze_routes():
    print("\n" + "=" * 70)
    print("📂 آنالیز ساختار صفحات")
    print("=" * 70)
    
    app_dir = WEB / "app"
    if not app_dir.exists():
        print(f"❌ app یافت نشد")
        return {}
    
    pages = {}
    for page_file in app_dir.rglob("page.tsx"):
        rel_path = page_file.relative_to(app_dir)
        route = "/" + str(rel_path.parent).replace("\\", "/")
        if route == "/.":
            route = "/"
        pages[route] = page_file
        print(f"   ✅ {route}")
    
    print(f"\n📊 تعداد صفحات: {len(pages)}")
    return pages


def create_module_page(route: str, title: str, icon: str, color: str):
    component_name = "".join(word.capitalize() for word in route.split("-")) + "Page"
    
    # استفاده از string concatenation به جای f-string
    return '''"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ''' + icon + ''', ArrowRight, ArrowLeft, Sparkles, TrendingUp, Users, BarChart3 } from "lucide-react";

export default function ''' + component_name + '''() {
  return (
    <div className="min-h-screen bg-slate-950">
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className={"absolute inset-0 bg-gradient-to-br ''' + color + ''' opacity-20"} />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" />
              بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className={"p-5 rounded-3xl bg-gradient-to-br ''' + color + ''' shadow-2xl"}>
                <''' + icon + ''' className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-emerald-400 text-sm font-medium mb-2">ماژول تخصصی</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">''' + title + '''</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  ابزارهای پیشرفته و تخصصی برای ''' + title + ''' در اکو نوژین
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      <section className="container mx-auto px-6 py-12">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-12">
          {[
            { label: "پروژه فعال", value: "۲۴", icon: Sparkles, color: "#10b981" },
            { label: "کاربر فعال", value: "۱,۲۰۰", icon: Users, color: "#3b82f6" },
            { label: "دقت تحلیل", value: "۹۵٪", icon: TrendingUp, color: "#f59e0b" },
            { label: "گزارش ماهانه", value: "۱۲۸", icon: BarChart3, color: "#8b5cf6" },
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

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map(i => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all group"
            >
              <div className={"h-40 bg-gradient-to-br ''' + color + ''' opacity-60 group-hover:opacity-80 transition-opacity"} />
              <div className="p-6">
                <h3 className="text-xl font-bold text-white mb-2">پروژه نمونه {i}</h3>
                <p className="text-slate-400 mb-4 leading-relaxed">
                  توضیحات مربوط به پروژه نمونه شماره {i} در بخش ''' + title + '''
                </p>
                <button className="text-emerald-400 hover:text-emerald-300 text-sm font-medium flex items-center gap-2">
                  مشاهده جزئیات
                  <ArrowLeft className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'''


def create_login_page():
    return '''"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Leaf, Mail, Lock, Eye, EyeOff } from "lucide-react";

export default function LoginPage() {
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 py-12 bg-gradient-to-br from-slate-950 to-emerald-950/30">
      <div className="w-full max-w-md">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 mb-4">
            <Leaf className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">ورود به اکو نوژین</h1>
          <p className="text-slate-400">به جمع کشاورزان پایدار بپیوندید</p>
        </motion.div>

        <form className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-2xl p-8 space-y-5">
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">ایمیل</label>
            <div className="relative">
              <Mail className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type="email" required className="w-full pr-10 pl-4 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" placeholder="you@example.com" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">رمز عبور</label>
            <div className="relative">
              <Lock className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type={showPass ? "text" : "password"} required className="w-full pr-10 pl-10 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" placeholder="••••••••" />
              <button type="button" onClick={() => setShowPass(!showPass)} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                {showPass ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading} className="w-full py-3 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50">
            {loading ? "در حال ورود..." : "ورود"}
          </button>

          <p className="text-center text-sm text-slate-400">
            حساب ندارید؟ 
            <Link href="/register" className="text-emerald-400 hover:text-emerald-300 font-medium mr-1">ثبت‌نام کنید</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
'''


def create_register_page():
    return '''"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Leaf, Mail, Lock, User, Eye, EyeOff } from "lucide-react";

export default function RegisterPage() {
  const [showPass, setShowPass] = useState(false);
  const [loading, setLoading] = useState(false);

  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-6 py-12 bg-gradient-to-br from-slate-950 to-emerald-950/30">
      <div className="w-full max-w-md">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
          <div className="inline-flex p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-green-600 mb-4">
            <Leaf className="h-8 w-8 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">ثبت‌نام در اکو نوژین</h1>
          <p className="text-slate-400">رایگان و برای همیشه</p>
        </motion.div>

        <form className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-2xl p-8 space-y-4">
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
            <label className="block text-sm font-medium text-slate-300 mb-2">رمز عبور</label>
            <div className="relative">
              <Lock className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input type={showPass ? "text" : "password"} required className="w-full pr-10 pl-10 py-3 bg-slate-800/50 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500" placeholder="حداقل ۸ کاراکتر" />
              <button type="button" onClick={() => setShowPass(!showPass)} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-slate-300">
                {showPass ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
              </button>
            </div>
          </div>

          <button type="submit" disabled={loading} className="w-full py-3 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-semibold hover:shadow-lg hover:shadow-emerald-500/30 transition-all disabled:opacity-50">
            {loading ? "در حال ثبت‌نام..." : "ایجاد حساب"}
          </button>

          <p className="text-center text-sm text-slate-400">
            حساب دارید؟ 
            <Link href="/login" className="text-emerald-400 hover:text-emerald-300 font-medium mr-1">وارد شوید</Link>
          </p>
        </form>
      </div>
    </div>
  );
}
'''


def create_profile_page():
    return '''"use client";

import Link from "next/link";
import { ArrowRight, Leaf, Mail, Phone, MapPin, Award, Activity, Wallet, TrendingUp } from "lucide-react";

export default function ProfilePage() {
  const user = {
    name: "علی محمدی",
    email: "ali@example.com",
    phone: "۰۹۱۲۳۴۵۶۷۸۹",
    location: "خراسان رضوی، مشهد",
    role: "کشاورز پایدار",
    avatar: "👨‍🌾"
  };

  const stats = [
    { label: "پروژه‌های فعال", value: "۱۲", icon: Activity, color: "#10b981" },
    { label: "هکتار تحت مدیریت", value: "۴۵", icon: MapPin, color: "#3b82f6" },
    { label: "گواهی‌نامه‌ها", value: "۵", icon: Award, color: "#f59e0b" },
    { label: "اعتبار EcoCoin", value: "۲,۴۵۰", icon: Wallet, color: "#8b5cf6" },
  ];

  return (
    <div className="container mx-auto px-6 py-12">
      <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8">
        <ArrowRight className="h-4 w-4" /> بازگشت به خانه
      </Link>

      <div className="bg-gradient-to-l from-emerald-600 to-green-700 rounded-2xl p-8 mb-8">
        <div className="flex flex-col md:flex-row items-center gap-6">
          <div className="w-24 h-24 rounded-full bg-white/20 backdrop-blur flex items-center justify-center text-5xl border-4 border-white/30">
            {user.avatar}
          </div>
          <div className="text-center md:text-right flex-1">
            <h1 className="text-3xl font-bold text-white mb-1">{user.name}</h1>
            <p className="text-emerald-100 mb-3">{user.role}</p>
            <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm text-emerald-100">
              <span className="flex items-center gap-1"><Mail className="h-4 w-4" />{user.email}</span>
              <span className="flex items-center gap-1"><Phone className="h-4 w-4" />{user.phone}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {stats.map(s => (
          <div key={s.label} className="bg-slate-900/50 border border-slate-800 rounded-xl p-5">
            <s.icon className="h-6 w-6 mb-3" style={{ color: s.color }} />
            <p className="text-2xl font-bold text-white">{s.value}</p>
            <p className="text-sm text-slate-400">{s.label}</p>
          </div>
        ))}
      </div>

      <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
        <h2 className="text-xl font-bold text-white mb-4">فعالیت‌های اخیر</h2>
        <div className="space-y-3">
          {[
            { action: "شبیه‌سازی هیدرولوژی حوضه کشف‌رود", time: "۲ ساعت پیش", icon: "💧" },
            { action: "دریافت گواهی‌نامه AquaCrop", time: "دیروز", icon: "🎓" },
            { action: "انتشار مقاله در کتابخانه", time: "۳ روز پیش", icon: "📚" },
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
    </div>
  );
}
'''


def create_admin_page():
    return '''"use client";

import Link from "next/link";
import { useState } from "react";
import { Users, Package, Activity, Settings, TrendingUp, Shield, BarChart3, FileText, AlertTriangle, CheckCircle, ArrowRight } from "lucide-react";

export default function AdminPage() {
  const stats = [
    { label: "کل کاربران", value: "۱,۲۴۵", change: "+۱۲٪", icon: Users, color: "#3b82f6" },
    { label: "کاربران فعال", value: "۸۵۶", change: "+۸٪", icon: Activity, color: "#10b981" },
    { label: "درآمد ماهانه", value: "۴۵M", change: "+۲۳٪", icon: TrendingUp, color: "#f59e0b" },
    { label: "هشدارها", value: "۳", change: "-۲", icon: AlertTriangle, color: "#ef4444" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      <div className="container mx-auto px-6 py-8">
        <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8">
          <ArrowRight className="h-4 w-4" /> بازگشت به خانه
        </Link>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-2">پنل مدیریت اکو نوژین</h1>
          <p className="text-slate-400">نمای کلی از وضعیت سیستم</p>
        </div>

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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
              <Activity className="h-5 w-5 text-emerald-400" /> فعالیت‌های اخیر
            </h3>
            <div className="space-y-3">
              {[
                { user: "علی محمدی", action: "ثبت‌نام کرد", time: "۵ دقیقه پیش", status: "success" },
                { user: "مریم احمدی", action: "پروژه جدید", time: "۱ ساعت پیش", status: "success" },
                { user: "سیستم", action: "هشدار امنیتی", time: "۲ ساعت پیش", status: "warning" },
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
                { name: "هیدرولوژی", users: "۳۴۵" },
                { name: "کربن خاک", users: "۲۸۹" },
                { name: "فرسایش", users: "۱۵۶" },
                { name: "هواشناسی", users: "۴۱۲" },
                { name: "فروشگاه", users: "۵۲۳" },
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
      </div>
    </div>
  );
}
'''


def create_static_page(route: str, title: str):
    component_name = title.replace(" ", "") + "Page"
    contents = {
        "about": "اکو نوژین یک پلتفرم علمی رایگان است که با هدف مدیریت هوشمند یکپارچه احیای مناظر خشک و نیمه‌خشک زمین طراحی شده است.",
        "contact": "ما همیشه آماده پاسخگویی به سوالات، پیشنهادات و همکاری با شما هستیم.",
        "privacy": "حریم خصوصی کاربران برای ما بسیار مهم است. ما اطلاعات شخصی شما را فقط برای ارائه خدمات بهتر استفاده می‌کنیم.",
        "terms": "با استفاده از اکو نوژین، شما با قوانین و مقررات زیر موافقت می‌کنید.",
        "policy": "خط مشی اکو نوژین بر پایه اصول علمی، شفافیت، و احترام به کاربران استوار است.",
    }
    content_text = contents.get(route, f"اطلاعات بیشتر درباره {title}")
    
    return '''"use client";

import Link from "next/link";
import { ArrowRight, Mail, Phone, MapPin } from "lucide-react";

export default function ''' + component_name + '''() {
  return (
    <div className="container mx-auto px-6 py-16">
      <div className="max-w-3xl mx-auto">
        <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8">
          <ArrowRight className="h-4 w-4" /> بازگشت به خانه
        </Link>
        
        <h1 className="text-5xl font-black text-white mb-6">''' + title + '''</h1>
        <p className="text-lg text-slate-300 leading-relaxed mb-8">''' + content_text + '''</p>
        
        <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8 mt-8">
          <h2 className="text-xl font-bold text-white mb-4">اطلاعات تماس</h2>
          <div className="space-y-3">
            <div className="flex items-center gap-3 text-slate-300">
              <Mail className="h-5 w-5 text-emerald-400" />
              <a href="mailto:info@econojin.com" className="hover:text-emerald-400">info@econojin.com</a>
            </div>
            <div className="flex items-center gap-3 text-slate-300">
              <Phone className="h-5 w-5 text-emerald-400" />
              <a href="tel:+985138000000" className="hover:text-emerald-400">۰۵۱-۳۸۰۰۰۰۰۰</a>
            </div>
            <div className="flex items-center gap-3 text-slate-300">
              <MapPin className="h-5 w-5 text-emerald-400" />
              <span>ایران، مشهد، پارک علم و فناوری</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
'''


def create_missing_pages(pages: dict):
    print("\n" + "=" * 70)
    print("🔨 ایجاد صفحات مفقود")
    print("=" * 70)
    
    scientific = {
        "/gis": ("GIS و نقشه", "Map", "from-violet-500 to-purple-600"),
        "/hydrology": ("هیدرولوژی", "Droplets", "from-blue-500 to-cyan-600"),
        "/carbon": ("کربن خاک", "TreePine", "from-emerald-500 to-green-600"),
        "/erosion": ("فرسایش خاک", "Mountain", "from-amber-500 to-orange-600"),
        "/weather": ("هواشناسی", "CloudSun", "from-sky-400 to-blue-600"),
        "/crop": ("مدیریت محصول", "Sprout", "from-lime-500 to-green-600"),
        "/sentinel": ("سنجش از دور", "Satellite", "from-indigo-500 to-purple-600"),
        "/soil-water": ("آب خاک", "Wind", "from-sky-500 to-blue-600"),
    }
    
    community = {
        "/library": ("کتابخانه علمی", "BookOpen", "from-rose-500 to-pink-500"),
        "/education": ("آموزش", "GraduationCap", "from-yellow-500 to-amber-500"),
        "/community": ("جامعه کشاورزان", "Users", "from-teal-500 to-cyan-500"),
        "/shop": ("فروشگاه", "ShoppingCart", "from-green-500 to-emerald-500"),
        "/psychology": ("سلامت روان", "Heart", "from-pink-500 to-rose-500"),
        "/games": ("بازی‌های آموزشی", "Gamepad2", "from-purple-500 to-violet-500"),
        "/ecomining": ("EcoCoin", "Coins", "from-yellow-400 to-orange-500"),
        "/desktop": ("میزکار", "Monitor", "from-slate-500 to-gray-500"),
    }
    
    auth_pages = {
        "/login": create_login_page,
        "/register": create_register_page,
    }
    
    user_pages = {
        "/profile": create_profile_page,
        "/admin": create_admin_page,
    }
    
    static_pages = {
        "/about": "درباره ما",
        "/contact": "تماس با ما",
        "/privacy": "حریم خصوصی",
        "/terms": "قوانین",
        "/policy": "خط مشی",
    }
    
    created = 0
    
    # ماژول‌های علمی و جامعه
    for route, (title, icon, color) in {**scientific, **community}.items():
        if route not in pages:
            page_path = WEB / "app" / route.strip("/") / "page.tsx"
            if not page_path.exists():
                content = create_module_page(route.strip("/"), title, icon, color)
                write_file(page_path, content)
                created += 1
    
    # صفحات احراز هویت
    for route, creator in auth_pages.items():
        if route not in pages:
            page_path = WEB / "app" / route.strip("/") / "page.tsx"
            if not page_path.exists():
                write_file(page_path, creator())
                created += 1
    
    # صفحات کاربری
    for route, creator in user_pages.items():
        if route not in pages:
            page_path = WEB / "app" / route.strip("/") / "page.tsx"
            if not page_path.exists():
                write_file(page_path, creator())
                created += 1
    
    # صفحات استاتیک
    for route, title in static_pages.items():
        if route not in pages:
            page_path = WEB / "app" / route.strip("/") / "page.tsx"
            if not page_path.exists():
                write_file(page_path, create_static_page(route.strip("/"), title))
                created += 1
    
    print(f"\n✅ {created} صفحه جدید ایجاد شد")


def main():
    print("🔍 آنالیز و اصلاح کامل ناوبری اکو نوژین")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    # مرحله 1: رفع middleware
    fix_middleware()
    
    # مرحله 2: آنالیز مسیرها
    pages = analyze_routes()
    
    # مرحله 3: ایجاد صفحات مفقود
    create_missing_pages(pages)
    
    print("\n" + "=" * 70)
    print("✅ عملیات تکمیل شد!")
    print("\n🚀 گام بعدی:")
    print("   1. پاک‌سازی کش: Remove-Item .next -Recurse -Force")
    print("   2. پاک‌سازی کوکی‌ها: Ctrl+Shift+Delete در مرورگر")
    print("   3. اجرا: pnpm run dev -- -p 3001")
    print("   4. مشاهده: http://localhost:3001")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())