"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import {
  Leaf, Globe, ArrowRight, Sparkles, Coins, Pickaxe, Map, BookOpen,
  PenLine, Mail, Calculator, Package, Building2, Gamepad2, Users,
  ShoppingBag, Brain, Cloud, Droplets, Mountain, Sun, Wifi, Scale,
  Wrench, Satellite, Landmark, Sprout, Flower2, TrendingUp, Shield,
  Zap, Award, Target, Rocket, Heart, CheckCircle, Play, Star,
  ArrowUpRight, BarChart3, Activity, Eye, Clock, Calendar
} from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(m => m.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(m => m.Area), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });

// ============================================================================
// Data
// ============================================================================
const HERO_STATS = [
  { label: "هکتار احیاشده", value: "125K", icon: Mountain, color: "#10b981" },
  { label: "تن CO2 جذب‌شده", value: "2.4M", icon: Cloud, color: "#3b82f6" },
  { label: "کاربر فعال", value: "12.5K", icon: Users, color: "#8b5cf6" },
  { label: "کشورهای فعال", value: "18", icon: Globe, color: "#f59e0b" },
];

const FEATURED_MODULES = [
  {
    name: "اکو کوین",
    href: "/ecocoin",
    icon: Coins,
    color: "#10b981",
    gradient: "from-emerald-600 to-teal-600",
    badge: "Asset-Backed",
    title: "ارز دیجیتال با پشتوانه اکوسیستم",
    desc: "اولین توکن با پشتوانه طبیعی • Proof of Ecological Restoration",
    stats: [
      { label: "پشتوانه", value: "$11.6B" },
      { label: "Market Cap", value: "$15M" },
      { label: "قیمت", value: "$0.15" },
    ],
    cta: "مشاهده وایت‌پیپر"
  },
  {
    name: "اکو ماینینگ",
    href: "/ecomining",
    icon: Pickaxe,
    color: "#8b5cf6",
    gradient: "from-purple-600 to-pink-600",
    badge: "Green Mining",
    title: "استخراج سبز با انرژی تجدیدپذیر",
    desc: "هر چه سبزتر ماین کنید، بیشتر پاداش می‌گیرید",
    stats: [
      { label: "هش‌ریت", value: "955 MH/s" },
      { label: "EcoScore", value: "98.2" },
      { label: "درآمد ۲۴h", value: "289 ECO" },
    ],
    cta: "شروع ماینینگ"
  },
];

const ALL_MODULES = [
  { name: "نقشه و GIS", href: "/gis", icon: Map, color: "#10b981", category: "پلتفرم" },
  { name: "آکادمی آموزشی", href: "/academy", icon: BookOpen, color: "#3b82f6", category: "آموزش" },
  { name: "وبلاگ", href: "/blog", icon: PenLine, color: "#8b5cf6", category: "محتوا" },
  { name: "خبرنامه", href: "/newsletter", icon: Mail, color: "#ec4899", category: "محتوا" },
  { name: "حسابداری", href: "/accounting", icon: Calculator, color: "#f59e0b", category: "مالی" },
  { name: "انبارداری", href: "/inventory", icon: Package, color: "#ef4444", category: "مالی" },
  { name: "حسابداری شرکتی", href: "/financial", icon: Building2, color: "#06b6d4", category: "مالی" },
  { name: "اکو کوین", href: "/ecocoin", icon: Coins, color: "#10b981", category: "کریپتو" },
  { name: "اکو ماینینگ", href: "/ecomining", icon: Pickaxe, color: "#8b5cf6", category: "کریپتو" },
  { name: "بازی‌های آموزشی", href: "/games", icon: Gamepad2, color: "#ec4899", category: "آموزش" },
  { name: "جامعه کشاورزان", href: "/community", icon: Users, color: "#10b981", category: "جامعه" },
  { name: "فروشگاه", href: "/store", icon: ShoppingBag, color: "#f59e0b", category: "تجاری" },
  { name: "سلامت روان", href: "/psychology", icon: Brain, color: "#8b5cf6", category: "سلامت" },
  { name: "پایش خشکسالی", href: "/drought", icon: Sun, color: "#f59e0b", category: "محیط" },
  { name: "آب و خاک", href: "/soil-water", icon: Droplets, color: "#3b82f6", category: "محیط" },
  { name: "فرسایش خاک", href: "/erosion", icon: Mountain, color: "#8b5cf6", category: "محیط" },
  { name: "هواشناسی", href: "/weather", icon: Cloud, color: "#06b6d4", category: "محیط" },
  { name: "اینترنت اشیا", href: "/iot", icon: Wifi, color: "#3b82f6", category: "فناوری" },
  { name: "MRV", href: "/mrv", icon: Scale, color: "#10b981", category: "فناوری" },
  { name: "نگهداری", href: "/maintenance", icon: Wrench, color: "#f59e0b", category: "فناوری" },
  { name: "Sentinel", href: "/sentinel", icon: Satellite, color: "#06b6d4", category: "فناوری" },
  { name: "هیدرولوژی", href: "/hydrology", icon: Droplets, color: "#3b82f6", category: "علمی" },
  { name: "کربن", href: "/carbon", icon: Leaf, color: "#10b981", category: "علمی" },
  { name: "محصولات زراعی", href: "/crop", icon: Sprout, color: "#84cc16", category: "علمی" },
];

const LIVE_CHART_DATA = Array.from({ length: 24 }, (_, i) => ({
  time: `${String(i).padStart(2, "0")}:00`,
  eco: 20 + Math.sin(i / 3) * 5 + Math.random() * 3,
  grc: 8 + Math.sin(i / 4) * 2 + Math.random() * 1,
}));

const LATEST_NEWS = [
  {
    title: "احیای ۵۰ هکتار زمین شور در دشت مغان",
    excerpt: "گزارش کامل از پروژه ۳ ساله احیای زمین‌های شور با استفاده از گیاهان شورپسند",
    category: "داستان موفقیت",
    date: "۱۴۰۳/۰۹/۱۵",
    views: 3420,
    color: "#10b981",
    href: "/blog"
  },
  {
    title: "تکنیک‌های نوین آبیاری قطره‌ای زیرسطحی",
    excerpt: "کاهش ۶۰٪ مصرف آب با روش‌های نوین آبیاری در باغ‌های پسته",
    category: "مدیریت آب",
    date: "۱۴۰۳/۰۹/۱۰",
    views: 2890,
    color: "#3b82f6",
    href: "/blog"
  },
  {
    title: "تأثیر تغییر اقلیم بر حوضه زاینده‌رود",
    excerpt: "تحلیل آماری ۳۰ ساله داده‌های بارش و دما در حوضه آبریز",
    category: "تغییر اقلیم",
    date: "۱۴۰۳/۰۹/۰۵",
    views: 4120,
    color: "#f59e0b",
    href: "/blog"
  },
];

const PARTNERS = [
  { name: "FAO", logo: "🌾" },
  { name: "UNEP", logo: "🌍" },
  { name: "World Bank", logo: "🏦" },
  { name: "IPCC", logo: "🌡️" },
  { name: "IUCN", logo: "🦁" },
  { name: "CGIAR", logo: "🌱" },
];

// ============================================================================
// Main Component
// ============================================================================
export default function HomePage() {
  const [livePrice, setLivePrice] = useState(0.15);
  const [liveHashrate, setLiveHashrate] = useState(955);

  useEffect(() => {
    const interval = setInterval(() => {
      setLivePrice(prev => prev + (Math.random() - 0.5) * 0.002);
      setLiveHashrate(prev => prev + (Math.random() - 0.5) * 10);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* ================================================================== */}
      {/* HERO SECTION */}
      {/* ================================================================== */}
      <section className="relative min-h-screen flex items-center overflow-hidden pt-20">
        {/* Background */}
        <div className="absolute inset-0">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-900/30 via-slate-950 to-blue-900/30" />
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-emerald-900/20 via-transparent to-transparent" />
          {[...Array(80)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-emerald-400 rounded-full"
              style={{ left: `${Math.random() * 100}%`, top: `${Math.random() * 100}%` }}
              animate={{ opacity: [0.1, 0.8, 0.1], scale: [1, 1.5, 1] }}
              transition={{ duration: Math.random() * 3 + 2, repeat: Infinity, delay: Math.random() * 2 }}
            />
          ))}
        </div>

        <div className="relative container mx-auto px-6 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            {/* Left Content */}
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8 }}
            >
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-bold mb-6">
                <Sparkles className="h-3 w-3" />
                پلتفرم جامع احیای زمین
                <span className="px-2 py-0.5 bg-emerald-500/20 rounded text-[10px]">v2.0</span>
              </div>

              <h1 className="text-5xl md:text-7xl font-black leading-tight mb-6">
                ساکن زمین هستیم،
                <br />
                <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-blue-400 bg-clip-text text-transparent">
                  احیاگر اکوسیستم
                </span>
              </h1>

              <p className="text-lg text-slate-300 leading-relaxed mb-8 max-w-xl">
                اولین پلتفرم جامع علمی-فناورانه برای احیای مناظر خشک و نیمه‌خشک با
                سیستم ارز دیجیتال اکولوژیک و ماینینگ سبز
              </p>

              <div className="flex flex-wrap gap-4 mb-10">
                <Link
                  href="/ecocoin"
                  className="group px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-xl font-bold flex items-center gap-2 transition-all shadow-lg shadow-emerald-500/30"
                >
                  <Coins className="h-5 w-5" />
                  شروع با اکو کوین
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/ecomining"
                  className="px-6 py-3 bg-slate-800/50 backdrop-blur border border-slate-700 hover:bg-slate-800 rounded-xl font-bold flex items-center gap-2 transition-all"
                >
                  <Pickaxe className="h-5 w-5 text-purple-400" />
                  اکو ماینینگ
                </Link>
              </div>

              {/* Live Stats */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {HERO_STATS.map((stat, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 + idx * 0.1 }}
                    className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-3"
                  >
                    <stat.icon className="h-5 w-5 mb-2" style={{ color: stat.color }} />
                    <p className="text-2xl font-black text-white">{stat.value}</p>
                    <p className="text-xs text-slate-400">{stat.label}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Right - Live Dashboard Card */}
            <motion.div
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="relative"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-emerald-500 to-blue-500 rounded-3xl blur-3xl opacity-20" />
              <div className="relative bg-slate-900/80 backdrop-blur-xl border border-slate-700 rounded-3xl p-6 shadow-2xl">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                    <span className="text-xs font-bold text-emerald-400">LIVE DASHBOARD</span>
                  </div>
                  <span className="text-xs text-slate-500">Real-time</span>
                </div>

                {/* Live Prices */}
                <div className="grid grid-cols-2 gap-3 mb-4">
                  <div className="bg-slate-800/50 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-slate-400">ECO/USD</span>
                      <span className="text-xs text-emerald-400 flex items-center gap-0.5">
                        <ArrowUpRight className="h-3 w-3" />5.8%
                      </span>
                    </div>
                    <p className="text-2xl font-black text-white tabular-nums">${livePrice.toFixed(4)}</p>
                  </div>
                  <div className="bg-slate-800/50 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-xs text-slate-400">Hashrate</span>
                      <span className="text-xs text-emerald-400">LIVE</span>
                    </div>
                    <p className="text-2xl font-black text-white tabular-nums">{liveHashrate.toFixed(0)} <span className="text-xs text-slate-400">MH/s</span></p>
                  </div>
                </div>

                {/* Chart */}
                <div className="bg-slate-800/30 rounded-xl p-3 mb-4">
                  <p className="text-xs text-slate-400 mb-2">درآمد ۲۴ ساعت اخیر</p>
                  <ResponsiveContainer width="100%" height={120}>
                    <AreaChart data={LIVE_CHART_DATA}>
                      <defs>
                        <linearGradient id="ecoGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                          <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="time" hide />
                      <YAxis hide />
                      <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", fontSize: "12px" }} />
                      <Area type="monotone" dataKey="eco" stroke="#10b981" fillOpacity={1} fill="url(#ecoGrad)" />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-2">
                  <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                    <p className="text-xs text-slate-400">پشتوانه</p>
                    <p className="text-sm font-black text-emerald-400">$11.6B</p>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                    <p className="text-xs text-slate-400">CO2</p>
                    <p className="text-sm font-black text-blue-400">2.4M t</p>
                  </div>
                  <div className="bg-slate-800/50 rounded-lg p-2 text-center">
                    <p className="text-xs text-slate-400">EcoScore</p>
                    <p className="text-sm font-black text-purple-400">98.2</p>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* PARTNERS */}
      {/* ================================================================== */}
      <section className="py-12 border-y border-slate-800 bg-slate-900/30">
        <div className="container mx-auto px-6">
          <p className="text-center text-xs text-slate-500 mb-6 tracking-wider">شرکای استراتژیک و همکاران علمی</p>
          <div className="flex flex-wrap justify-center items-center gap-8">
            {PARTNERS.map((partner, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0 }}
                whileInView={{ opacity: 1 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
              >
                <span className="text-3xl">{partner.logo}</span>
                <span className="font-bold text-sm">{partner.name}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* FEATURED MODULES - EcoCoin & EcoMining */}
      {/* ================================================================== */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-bold mb-4">
              <Sparkles className="h-3 w-3" />
              ویژگی‌های منحصربه‌فرد
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              انقلاب در <span className="bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">اقتصاد اکولوژیک</span>
            </h2>
            <p className="text-lg text-slate-400 max-w-2xl mx-auto">
              اولین پلتفرمی که استخراج ارز دیجیتال را به احیای زمین تبدیل می‌کند
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {FEATURED_MODULES.map((mod, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.2 }}
              >
                <Link href={mod.href} className="block group">
                  <div className={`relative bg-gradient-to-br ${mod.gradient} rounded-3xl p-8 overflow-hidden h-full`}>
                    <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />
                    <div className="relative">
                      <div className="flex items-start justify-between mb-6">
                        <div className="p-4 rounded-2xl bg-white/10 backdrop-blur">
                          <mod.icon className="h-10 w-10 text-white" />
                        </div>
                        <span className="px-3 py-1 bg-white/20 backdrop-blur rounded-full text-xs font-bold text-white">
                          {mod.badge}
                        </span>
                      </div>

                      <h3 className="text-3xl font-black text-white mb-2">{mod.title}</h3>
                      <p className="text-white/80 mb-6">{mod.desc}</p>

                      <div className="grid grid-cols-3 gap-3 mb-6">
                        {mod.stats.map((stat, i) => (
                          <div key={i} className="bg-white/10 backdrop-blur rounded-xl p-3">
                            <p className="text-xs text-white/60 mb-1">{stat.label}</p>
                            <p className="text-lg font-black text-white">{stat.value}</p>
                          </div>
                        ))}
                      </div>

                      <div className="flex items-center gap-2 text-white font-bold group-hover:gap-3 transition-all">
                        {mod.cta}
                        <ArrowRight className="h-5 w-5" />
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* ALL MODULES GRID */}
      {/* ================================================================== */}
      <section className="py-20 bg-gradient-to-b from-slate-950 via-slate-900/30 to-slate-950">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              ۲۴ ماژول <span className="text-emerald-400">تخصصی</span>
            </h2>
            <p className="text-lg text-slate-400">هر آنچه برای احیای زمین نیاز دارید، در یک پلتفرم</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {ALL_MODULES.map((mod, idx) => {
              const Icon = mod.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.9 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.03 }}
                >
                  <Link
                    href={mod.href}
                    className="group block bg-slate-900/50 border border-slate-800 rounded-2xl p-5 hover:border-slate-700 hover:bg-slate-900 transition-all"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div className="p-2.5 rounded-xl transition-transform group-hover:scale-110" style={{ backgroundColor: mod.color + "20" }}>
                        <Icon className="h-5 w-5" style={{ color: mod.color }} />
                      </div>
                      <ArrowRight className="h-4 w-4 text-slate-600 group-hover:text-white group-hover:translate-x-1 transition-all" />
                    </div>
                    <h3 className="font-bold text-white mb-1 group-hover:text-emerald-400 transition-colors">{mod.name}</h3>
                    <span className="text-xs text-slate-500">{mod.category}</span>
                  </Link>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* LATEST NEWS */}
      {/* ================================================================== */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="flex items-center justify-between mb-10">
            <div>
              <h2 className="text-4xl font-black text-white mb-2">آخرین مقالات</h2>
              <p className="text-slate-400">از وبلاگ تخصصی اکو نوژین</p>
            </div>
            <Link href="/blog" className="hidden md:flex items-center gap-2 px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-xl font-bold text-sm transition-all">
              مشاهده همه
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {LATEST_NEWS.map((news, idx) => (
              <motion.article
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
              >
                <Link href={news.href} className="group block bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all h-full">
                  <div className="h-48 bg-gradient-to-br from-slate-800 to-slate-900 relative overflow-hidden">
                    <div className="absolute inset-0 bg-gradient-to-br opacity-30" style={{ backgroundColor: news.color }} />
                    <div className="absolute top-4 right-4">
                      <span className="px-3 py-1 bg-slate-900/80 backdrop-blur rounded-full text-xs font-bold text-white">
                        {news.category}
                      </span>
                    </div>
                  </div>
                  <div className="p-6">
                    <div className="flex items-center gap-3 text-xs text-slate-500 mb-3">
                      <span className="flex items-center gap-1"><Calendar className="h-3 w-3" />{news.date}</span>
                      <span className="flex items-center gap-1"><Eye className="h-3 w-3" />{news.views.toLocaleString()}</span>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2 group-hover:text-emerald-400 transition-colors line-clamp-2">
                      {news.title}
                    </h3>
                    <p className="text-sm text-slate-400 line-clamp-2">{news.excerpt}</p>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* WHY ECONOJIN */}
      {/* ================================================================== */}
      <section className="py-20 bg-gradient-to-b from-slate-950 to-emerald-950/20">
        <div className="container mx-auto px-6">
          <div className="text-center mb-12">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              چرا <span className="text-emerald-400">اکو نوژین</span>؟
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Shield, title: "پشتوانه واقعی", desc: "هر توکن با دارایی اکولوژیک تأییدشده پشتیبانی می‌شود", color: "#10b981" },
              { icon: Zap, title: "فناوری پیشرفته", desc: "بلاکچین، AI، ماهواره و IoT در یک پلتفرم یکپارچه", color: "#3b82f6" },
              { icon: Award, title: "استاندارد جهانی", desc: "مطابق با استانداردهای FAO، IPCC و Verra", color: "#f59e0b" },
              { icon: Heart, title: "تأثیر واقعی", desc: "هر اقدام شما مستقیماً به احیای زمین کمک می‌کند", color: "#ec4899" },
            ].map((item, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6"
              >
                <div className="p-3 rounded-xl inline-block mb-4" style={{ backgroundColor: item.color + "20" }}>
                  <item.icon className="h-8 w-8" style={{ color: item.color }} />
                </div>
                <h3 className="text-xl font-bold text-white mb-2">{item.title}</h3>
                <p className="text-sm text-slate-400 leading-relaxed">{item.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* NEWSLETTER CTA */}
      {/* ================================================================== */}
      <section className="py-20">
        <div className="container mx-auto px-6">
          <div className="relative bg-gradient-to-br from-emerald-900/40 via-teal-900/40 to-blue-900/40 border border-emerald-500/30 rounded-3xl p-12 overflow-hidden">
            <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
            <div className="relative max-w-3xl mx-auto text-center">
              <Mail className="h-12 w-12 text-emerald-400 mx-auto mb-6" />
              <h2 className="text-3xl md:text-4xl font-black text-white mb-4">
                به خانواده اکو نوژین بپیوندید
              </h2>
              <p className="text-lg text-slate-300 mb-8">
                هر هفته جدیدترین مقالات، تحقیقات و فرصت‌های یادگیری را در ایمیل خود دریافت کنید
              </p>
              <div className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
                <input
                  type="email"
                  placeholder="ایمیل شما"
                  className="flex-1 px-4 py-3 bg-slate-900/80 backdrop-blur border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:border-emerald-500 focus:outline-none"
                />
                <button onClick={() => console.log("Button clicked")}  className="px-6 py-3 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 rounded-xl font-bold text-white transition-all">
                  عضویت
                </button>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}