"use client";

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
              <button onClick={() => console.log("Button clicked")}  className="absolute bottom-0 left-0 p-2 bg-white rounded-full shadow-lg hover:scale-110 transition-transform">
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
            <button onClick={() => console.log("Button clicked")}  className="px-6 py-3 bg-white/20 backdrop-blur border border-white/30 text-white rounded-xl hover:bg-white/30 transition-all flex items-center gap-2">
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
                  <button onClick={() => console.log("Button clicked")}  className="px-6 py-2 bg-white/20 backdrop-blur rounded-lg text-white hover:bg-white/30">ارسال</button>
                  <button onClick={() => console.log("Button clicked")}  className="px-6 py-2 bg-white/20 backdrop-blur rounded-lg text-white hover:bg-white/30">دریافت</button>
                  <button onClick={() => console.log("Button clicked")}  className="px-6 py-2 bg-white/20 backdrop-blur rounded-lg text-white hover:bg-white/30">تاریخچه</button>
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
                    <button onClick={() => console.log("Button clicked")}  className="px-6 py-2 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700">تغییر رمز</button>
                  </div>
                </div>
                <div className="p-5 bg-slate-800/50 rounded-xl">
                  <h3 className="font-bold text-white mb-3">احراز هویت دو مرحله‌ای</h3>
                  <p className="text-sm text-slate-400 mb-3">امنیت حساب خود را با تایید دو مرحله‌ای افزایش دهید</p>
                  <button onClick={() => console.log("Button clicked")}  className="px-6 py-2 bg-blue-600 text-white rounded-xl hover:bg-blue-700">فعال‌سازی</button>
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
                <button onClick={() => console.log("Button clicked")}  className="px-6 py-3 bg-emerald-600 text-white rounded-xl hover:bg-emerald-700">ذخیره تنظیمات</button>
              </div>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}