"use client";

import { useState, useEffect, useMemo } from "react";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import dynamic from "next/dynamic";
import {
  Leaf, Globe, ArrowRight, Sparkles, Coins, Pickaxe, Map, BookOpen,
  PenLine, Mail, Calculator, Package, Building2, Gamepad2, Users,
  ShoppingBag, Brain, Cloud, Droplets, Mountain, Sun, Wifi, Scale,
  Wrench, Satellite, Landmark, Sprout, Flower2, TrendingUp, Shield,
  Zap, Award, Target, Rocket, Heart, CheckCircle, Play, Star,
  ArrowUpRight, BarChart3, Activity, Eye, Clock, Calendar, ArrowLeft
} from "lucide-react";

// Dynamic import برای Recharts (جلوگیری از SSR hydration)
const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(m => m.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(m => m.Area), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });

// ============================================================================
// 🎨 Design System: Nature Distilled Palette (2026)
// ============================================================================
const PALETTE = {
  emerald: { light: "#34d399", base: "#10b981", deep: "#047857", glow: "rgba(16, 185, 129, 0.4)" },
  teal: { light: "#2dd4bf", base: "#14b8a6", deep: "#0d9488" },
  blue: { light: "#60a5fa", base: "#3b82f6", deep: "#2563eb" },
  purple: { light: "#a78bfa", base: "#8b5cf6", deep: "#7c3aed" },
  amber: { light: "#fbbf24", base: "#f59e0b", deep: "#d97706" },
  rose: { light: "#fb7185", base: "#f43f5e", deep: "#e11d48" },
};

// ============================================================================
// 📊 Data Layer (Memoized برای Sustainable UX)
// ============================================================================
const HERO_STATS = [
  { label: "هکتار احیاشده", value: "125K", icon: Mountain, color: PALETTE.emerald.base, accent: "from-emerald-500/20" },
  { label: "تن CO2 جذب‌شده", value: "2.4M", icon: Cloud, color: PALETTE.blue.base, accent: "from-blue-500/20" },
  { label: "کاربر فعال", value: "12.5K", icon: Users, color: PALETTE.purple.base, accent: "from-purple-500/20" },
  { label: "کشورهای فعال", value: "18", icon: Globe, color: PALETTE.amber.base, accent: "from-amber-500/20" },
];

const FEATURED_MODULES = [
  {
    name: "اکو کوین",
    href: "/ecocoin",
    icon: Coins,
    gradient: "from-emerald-500 via-teal-500 to-cyan-500",
    meshGradient: "radial-gradient(at 20% 20%, rgba(16, 185, 129, 0.4) 0px, transparent 50%), radial-gradient(at 80% 80%, rgba(6, 182, 212, 0.3) 0px, transparent 50%)",
    badge: "Asset-Backed",
    badgeColor: "bg-white/20 backdrop-blur-md",
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
    gradient: "from-purple-500 via-fuchsia-500 to-pink-500",
    meshGradient: "radial-gradient(at 20% 20%, rgba(168, 85, 247, 0.4) 0px, transparent 50%), radial-gradient(at 80% 80%, rgba(236, 72, 153, 0.3) 0px, transparent 50%)",
    badge: "Green Mining",
    badgeColor: "bg-white/20 backdrop-blur-md",
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
  { name: "نقشه و GIS", href: "/gis", icon: Map, color: PALETTE.emerald.base, category: "پلتفرم" },
  { name: "آکادمی آموزشی", href: "/academy", icon: BookOpen, color: PALETTE.blue.base, category: "آموزش" },
  { name: "وبلاگ", href: "/blog", icon: PenLine, color: PALETTE.purple.base, category: "محتوا" },
  { name: "خبرنامه", href: "/newsletter", icon: Mail, color: PALETTE.rose.base, category: "محتوا" },
  { name: "حسابداری", href: "/accounting", icon: Calculator, color: PALETTE.amber.base, category: "مالی" },
  { name: "انبارداری", href: "/inventory", icon: Package, color: PALETTE.rose.base, category: "مالی" },
  { name: "حسابداری شرکتی", href: "/financial", icon: Building2, color: PALETTE.teal.base, category: "مالی" },
  { name: "اکو کوین", href: "/ecocoin", icon: Coins, color: PALETTE.emerald.base, category: "کریپتو" },
  { name: "اکو ماینینگ", href: "/ecomining", icon: Pickaxe, color: PALETTE.purple.base, category: "کریپتو" },
  { name: "بازی‌های آموزشی", href: "/games", icon: Gamepad2, color: PALETTE.rose.base, category: "آموزش" },
  { name: "جامعه کشاورزان", href: "/community", icon: Users, color: PALETTE.emerald.base, category: "جامعه" },
  { name: "فروشگاه", href: "/store", icon: ShoppingBag, color: PALETTE.amber.base, category: "تجاری" },
  { name: "سلامت روان", href: "/psychology", icon: Brain, color: PALETTE.purple.base, category: "سلامت" },
  { name: "پایش خشکسالی", href: "/drought", icon: Sun, color: PALETTE.amber.base, category: "محیط" },
  { name: "آب و خاک", href: "/soil-water", icon: Droplets, color: PALETTE.blue.base, category: "محیط" },
  { name: "فرسایش خاک", href: "/erosion", icon: Mountain, color: PALETTE.purple.base, category: "محیط" },
  { name: "هواشناسی", href: "/weather", icon: Cloud, color: PALETTE.teal.base, category: "محیط" },
  { name: "اینترنت اشیا", href: "/iot", icon: Wifi, color: PALETTE.blue.base, category: "فناوری" },
  { name: "MRV", href: "/mrv", icon: Scale, color: PALETTE.emerald.base, category: "فناوری" },
  { name: "نگهداری", href: "/maintenance", icon: Wrench, color: PALETTE.amber.base, category: "فناوری" },
  { name: "Sentinel", href: "/sentinel", icon: Satellite, color: PALETTE.teal.base, category: "فناوری" },
  { name: "هیدرولوژی", href: "/hydrology", icon: Droplets, color: PALETTE.blue.base, category: "علمی" },
  { name: "کربن", href: "/carbon", icon: Leaf, color: PALETTE.emerald.base, category: "علمی" },
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
    color: PALETTE.emerald.base,
    gradient: "from-emerald-600/40 to-teal-600/20",
    href: "/blog"
  },
  {
    title: "تکنیک‌های نوین آبیاری قطره‌ای زیرسطحی",
    excerpt: "کاهش ۶۰٪ مصرف آب با روش‌های نوین آبیاری در باغ‌های پسته",
    category: "مدیریت آب",
    date: "۱۴۰۳/۰۹/۱۰",
    views: 2890,
    color: PALETTE.blue.base,
    gradient: "from-blue-600/40 to-cyan-600/20",
    href: "/blog"
  },
  {
    title: "تأثیر تغییر اقلیم بر حوضه زاینده‌رود",
    excerpt: "تحلیل آماری ۳۰ ساله داده‌های بارش و دما در حوضه آبریز",
    category: "تغییر اقلیم",
    date: "۱۴۰۳/۰۹/۰۵",
    views: 4120,
    color: PALETTE.amber.base,
    gradient: "from-amber-600/40 to-orange-600/20",
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
// 🎭 Main Component with 2026 Design System
// ============================================================================
export default function HomePage() {
  const [livePrice, setLivePrice] = useState(0.15);
  const [liveHashrate, setLiveHashrate] = useState(955);
  const shouldReduceMotion = useReducedMotion();

  // Memoization برای پایداری و عملکرد بهتر
  const particlePositions = useMemo(
    () => Array.from({ length: 30 }, () => ({
      left: Math.random() * 100,
      top: Math.random() * 100,
      duration: Math.random() * 3 + 2,
      delay: Math.random() * 2,
    })),
    []
  );

  useEffect(() => {
    const interval = setInterval(() => {
      setLivePrice(prev => Math.max(0.1, prev + (Math.random() - 0.5) * 0.002));
      setLiveHashrate(prev => Math.max(800, prev + (Math.random() - 0.5) * 10));
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* ================================================================== */}
      {/* 🌿 Global Ambient Background (Nature Distilled) */}
      {/* ================================================================== */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        {/* Mesh gradient ارگانیک */}
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div 
          className="absolute inset-0 opacity-60"
          style={{
            backgroundImage: `
              radial-gradient(at 15% 10%, rgba(16, 185, 129, 0.15) 0px, transparent 50%),
              radial-gradient(at 85% 20%, rgba(59, 130, 246, 0.12) 0px, transparent 50%),
              radial-gradient(at 70% 85%, rgba(139, 92, 246, 0.1) 0px, transparent 50%),
              radial-gradient(at 20% 90%, rgba(20, 184, 166, 0.12) 0px, transparent 50%)
            `
          }}
        />
        {/* Noise texture برای حس لمسی */}
        <div 
          className="absolute inset-0 opacity-[0.025] mix-blend-overlay"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
          }}
        />
      </div>

      {/* ================================================================== */}
      {/* 🚀 HERO SECTION (Exaggerated Hierarchy) */}
      {/* ================================================================== */}
      <section className="relative min-h-screen flex items-center pt-24 pb-16">
        {/* Particles با بهینه‌سازی برای reduce-motion */}
        {!shouldReduceMotion && (
          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            {particlePositions.map((pos, i) => (
              <motion.div
                key={i}
                className="absolute w-1 h-1 bg-emerald-400/60 rounded-full blur-[1px]"
                style={{ left: `${pos.left}%`, top: `${pos.top}%` }}
                animate={{ opacity: [0.2, 1, 0.2], scale: [1, 1.5, 1] }}
                transition={{ duration: pos.duration, repeat: Infinity, delay: pos.delay }}
              />
            ))}
          </div>
        )}

        <div className="container mx-auto px-6 lg:px-12">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* محتوا */}
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="lg:col-span-7"
            >
              {/* Badge با glassmorphism */}
              <motion.div 
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.2 }}
                className="inline-flex items-center gap-2.5 px-5 py-2.5 mb-8 bg-white/[0.03] backdrop-blur-xl border border-white/10 rounded-full"
              >
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
                <span className="text-sm font-medium text-zinc-300">پلتفرم جامع احیای زمین</span>
                <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded text-[10px] font-bold tracking-wider">v2.0</span>
              </motion.div>

              {/* هدر غول‌پیکر - Exaggerated Hierarchy */}
              <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-black leading-[1.05] tracking-tight mb-8">
                <span className="block text-zinc-100">ساکن زمین هستیم،</span>
                <span className="block mt-2 bg-gradient-to-r from-emerald-300 via-teal-300 to-cyan-300 bg-clip-text text-transparent">
                  احیاگر اکوسیستم
                </span>
              </h1>

              {/* توضیحات با فاصله تنفس‌پذیر */}
              <p className="text-lg sm:text-xl text-zinc-400 leading-relaxed mb-10 max-w-2xl font-light">
                اولین پلتفرم جامع <span className="text-emerald-400 font-medium">علمی-فناورانه</span> برای احیای مناظر خشک و نیمه‌خشک با
                سیستم ارز دیجیتال اکولوژیک و ماینینگ سبز
              </p>

              {/* CTA Buttons با طراحی 2026 */}
              <div className="flex flex-wrap gap-4 mb-14">
                <Link
                  href="/ecocoin"
                  className="group relative px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-2xl font-bold text-white flex items-center gap-3 transition-all shadow-[0_0_40px_rgba(16,185,129,0.3)] hover:shadow-[0_0_60px_rgba(16,185,129,0.5)] hover:-translate-y-0.5"
                >
                  <Coins className="h-5 w-5" />
                  شروع با اکو کوین
                  <ArrowRight className="h-4 w-4 group-hover:translate-x-1 transition-transform" />
                </Link>
                <Link
                  href="/ecomining"
                  className="group px-8 py-4 bg-white/[0.03] backdrop-blur-xl border border-white/10 hover:bg-white/[0.06] hover:border-white/20 rounded-2xl font-bold text-white flex items-center gap-3 transition-all"
                >
                  <Pickaxe className="h-5 w-5 text-purple-400" />
                  اکو ماینینگ
                  <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                </Link>
              </div>

              {/* آمار Hero با Tactile Maximalism */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {HERO_STATS.map((stat, idx) => {
                  const Icon = stat.icon;
                  return (
                    <motion.div
                      key={idx}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + idx * 0.1 }}
                      className={`relative bg-gradient-to-br ${stat.accent} to-transparent backdrop-blur-xl border border-white/10 rounded-2xl p-4 hover:border-white/20 transition-all group`}
                    >
                      <div 
                        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity"
                        style={{ boxShadow: `0 0 30px ${stat.color}40` }}
                      />
                      <div className="relative">
                        <Icon className="h-5 w-5 mb-2.5" style={{ color: stat.color }} />
                        <p className="text-2xl sm:text-3xl font-black text-white tabular-nums tracking-tight">{stat.value}</p>
                        <p className="text-xs text-zinc-400 mt-1">{stat.label}</p>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            </motion.div>

            {/* Live Dashboard Card - Glassmorphism پیشرفته */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.8, delay: 0.3 }}
              className="lg:col-span-5 relative"
            >
              {/* Glow پشت کارت */}
              <div className="absolute -inset-4 bg-gradient-to-br from-emerald-500/30 via-teal-500/20 to-blue-500/30 rounded-[2rem] blur-3xl opacity-50" />
              
              {/* کارت اصلی با Glassmorphism */}
              <div className="relative bg-white/[0.04] backdrop-blur-2xl border border-white/10 rounded-3xl p-6 shadow-2xl">
                {/* Header داشبورد */}
                <div className="flex items-center justify-between mb-6">
                  <div className="flex items-center gap-2.5">
                    <span className="relative flex h-2.5 w-2.5">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
                    </span>
                    <span className="text-xs font-bold text-emerald-400 tracking-wider">LIVE DASHBOARD</span>
                  </div>
                  <span className="text-[10px] text-zinc-500 font-mono uppercase tracking-wider">Real-time</span>
                </div>

                {/* Live Prices */}
                <div className="grid grid-cols-2 gap-3 mb-5">
                  <div className="relative bg-gradient-to-br from-emerald-500/10 to-transparent border border-emerald-500/20 rounded-2xl p-4 overflow-hidden">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-emerald-500/20 rounded-full blur-2xl" />
                    <div className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-zinc-400">ECO/USD</span>
                        <span className="text-xs text-emerald-400 flex items-center gap-0.5 font-bold">
                          <ArrowUpRight className="h-3 w-3" />5.8%
                        </span>
                      </div>
                      <p className="text-2xl font-black text-white tabular-nums">${livePrice.toFixed(4)}</p>
                    </div>
                  </div>
                  <div className="relative bg-gradient-to-br from-purple-500/10 to-transparent border border-purple-500/20 rounded-2xl p-4 overflow-hidden">
                    <div className="absolute top-0 right-0 w-20 h-20 bg-purple-500/20 rounded-full blur-2xl" />
                    <div className="relative">
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-zinc-400">Hashrate</span>
                        <span className="text-[10px] text-purple-400 font-bold tracking-wider">LIVE</span>
                      </div>
                      <p className="text-2xl font-black text-white tabular-nums">{liveHashrate.toFixed(0)} <span className="text-xs text-zinc-400 font-normal">MH/s</span></p>
                    </div>
                  </div>
                </div>

                {/* Chart */}
                <div className="bg-black/20 rounded-2xl p-4 mb-5 border border-white/5">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-xs text-zinc-400">درآمد ۲۴ ساعت اخیر</p>
                    <div className="flex items-center gap-1.5">
                      <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                      <span className="text-[10px] text-zinc-500">ECO</span>
                    </div>
                  </div>
                  <ResponsiveContainer width="100%" height={120}>
                    <AreaChart data={LIVE_CHART_DATA}>
                      <defs>
                        <linearGradient id="ecoGrad" x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor="#10b981" stopOpacity={0.6}/>
                          <stop offset="100%" stopColor="#10b981" stopOpacity={0}/>
                        </linearGradient>
                      </defs>
                      <XAxis dataKey="time" hide />
                      <YAxis hide />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: "rgba(10, 10, 12, 0.95)", 
                          border: "1px solid rgba(255, 255, 255, 0.1)", 
                          fontSize: "12px",
                          borderRadius: "12px",
                          backdropFilter: "blur(10px)"
                        }} 
                        labelStyle={{ color: "#71717a" }}
                      />
                      <Area 
                        type="monotone" 
                        dataKey="eco" 
                        stroke="#10b981" 
                        strokeWidth={2}
                        fillOpacity={1} 
                        fill="url(#ecoGrad)" 
                      />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>

                {/* Quick Stats */}
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { label: "پشتوانه", value: "$11.6B", color: PALETTE.emerald.base },
                    { label: "CO2", value: "2.4M t", color: PALETTE.blue.base },
                    { label: "EcoScore", value: "98.2", color: PALETTE.purple.base },
                  ].map((s, i) => (
                    <div key={i} className="bg-white/[0.03] border border-white/5 rounded-xl p-3 text-center hover:bg-white/[0.06] transition-colors">
                      <p className="text-[10px] text-zinc-500 mb-1">{s.label}</p>
                      <p className="text-base font-black tabular-nums" style={{ color: s.color }}>{s.value}</p>
                    </div>
                  ))}
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* 🤝 PARTNERS */}
      {/* ================================================================== */}
      <section className="py-16 border-y border-white/5">
        <div className="container mx-auto px-6 lg:px-12">
          <p className="text-center text-xs text-zinc-500 mb-10 tracking-[0.2em] uppercase font-light">
            شرکای استراتژیک و همکاران علمی
          </p>
          <div className="flex flex-wrap justify-center items-center gap-x-12 gap-y-6">
            {PARTNERS.map((partner, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 10 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.05 }}
                className="group flex items-center gap-3 text-zinc-500 hover:text-white transition-all cursor-pointer"
              >
                <span className="text-3xl group-hover:scale-110 transition-transform">{partner.logo}</span>
                <span className="font-bold text-sm tracking-wide">{partner.name}</span>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* 💎 FEATURED MODULES - 3D Cards with Mesh Gradients */}
      {/* ================================================================== */}
      <section className="py-32">
        <div className="container mx-auto px-6 lg:px-12">
          {/* Header با Exaggerated Hierarchy */}
          <div className="text-center mb-20">
            <motion.div 
              initial={{ opacity: 0, y: 10 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className="inline-flex items-center gap-2 px-4 py-2 bg-white/[0.03] border border-white/10 rounded-full text-emerald-300 text-xs font-medium mb-6"
            >
              <Sparkles className="h-3 w-3" />
              ویژگی‌های منحصربه‌فرد
            </motion.div>
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white mb-6 tracking-tight">
              انقلاب در <span className="bg-gradient-to-r from-emerald-300 to-cyan-300 bg-clip-text text-transparent">اقتصاد اکولوژیک</span>
            </h2>
            <p className="text-lg text-zinc-400 max-w-2xl mx-auto font-light">
              اولین پلتفرمی که استخراج ارز دیجیتال را به احیای زمین تبدیل می‌کند
            </p>
          </div>

          {/* کارت‌های 3D */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {FEATURED_MODULES.map((mod, idx) => {
              const Icon = mod.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 40 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.15 }}
                >
                  <Link href={mod.href} className="block group">
                    <div className={`relative bg-gradient-to-br ${mod.gradient} rounded-[2rem] p-1 overflow-hidden transition-all hover:-translate-y-1 duration-500`}>
                      {/* Inner glassmorphism layer */}
                      <div className="relative bg-black/40 backdrop-blur-xl rounded-[calc(2rem-4px)] p-8 h-full overflow-hidden">
                        {/* Mesh gradient داخلی */}
                        <div 
                          className="absolute inset-0 opacity-80"
                          style={{ backgroundImage: mod.meshGradient }}
                        />
                        
                        {/* Decorative circle */}
                        <div className="absolute top-0 right-0 w-80 h-80 bg-white/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3" />
                        
                        <div className="relative">
                          <div className="flex items-start justify-between mb-8">
                            <div className="p-5 rounded-3xl bg-white/10 backdrop-blur-xl border border-white/20 shadow-2xl group-hover:scale-110 transition-transform duration-500">
                              <Icon className="h-10 w-10 text-white" />
                            </div>
                            <span className={`px-4 py-1.5 ${mod.badgeColor} rounded-full text-xs font-bold text-white tracking-wider`}>
                              {mod.badge}
                            </span>
                          </div>

                          <h3 className="text-3xl sm:text-4xl font-black text-white mb-3 tracking-tight">{mod.title}</h3>
                          <p className="text-white/80 mb-8 text-base">{mod.desc}</p>

                          <div className="grid grid-cols-3 gap-3 mb-8">
                            {mod.stats.map((stat, i) => (
                              <div key={i} className="bg-white/10 backdrop-blur-xl rounded-2xl p-4 border border-white/10">
                                <p className="text-xs text-white/60 mb-1.5">{stat.label}</p>
                                <p className="text-lg font-black text-white tabular-nums">{stat.value}</p>
                              </div>
                            ))}
                          </div>

                          <div className="flex items-center gap-3 text-white font-bold group-hover:gap-4 transition-all duration-300">
                            <span>{mod.cta}</span>
                            <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
                          </div>
                        </div>
                      </div>
                    </div>
                  </Link>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* 🧩 ALL MODULES GRID - BENTO STYLE */}
      {/* ================================================================== */}
      <section className="py-32 relative">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="text-center mb-20">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white mb-6 tracking-tight">
              ۲۴ ماژول <span className="text-emerald-400">تخصصی</span>
            </h2>
            <p className="text-lg text-zinc-400 max-w-2xl mx-auto font-light">
              هر آنچه برای احیای زمین نیاز دارید، در یک پلتفرم
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {ALL_MODULES.map((mod, idx) => {
              const Icon = mod.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, scale: 0.95 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.02 }}
                >
                  <Link
                    href={mod.href}
                    className="group relative block bg-white/[0.02] backdrop-blur-sm border border-white/5 rounded-2xl p-5 hover:bg-white/[0.05] hover:border-white/10 transition-all duration-300 overflow-hidden"
                  >
                    {/* Glow effect on hover */}
                    <div 
                      className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500"
                      style={{ 
                        background: `radial-gradient(circle at center, ${mod.color}20 0%, transparent 70%)`
                      }}
                    />
                    
                    <div className="relative">
                      <div className="flex items-start justify-between mb-4">
                        <div 
                          className="p-3 rounded-2xl transition-all duration-300 group-hover:scale-110 group-hover:rotate-3"
                          style={{ 
                            backgroundColor: `${mod.color}15`,
                            boxShadow: `0 0 20px ${mod.color}20`
                          }}
                        >
                          <Icon className="h-5 w-5" style={{ color: mod.color }} />
                        </div>
                        <ArrowLeft className="h-4 w-4 text-zinc-700 group-hover:text-white group-hover:-translate-x-1 transition-all" />
                      </div>
                      <h3 className="font-bold text-white mb-1.5 group-hover:text-emerald-300 transition-colors">{mod.name}</h3>
                      <span className="text-xs text-zinc-500">{mod.category}</span>
                    </div>
                  </Link>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* 📰 LATEST NEWS - EDITORIAL STYLE */}
      {/* ================================================================== */}
      <section className="py-32">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between mb-16 gap-6">
            <div>
              <h2 className="text-4xl sm:text-5xl font-black text-white mb-3 tracking-tight">آخرین مقالات</h2>
              <p className="text-zinc-400">از وبلاگ تخصصی اکو نوژین</p>
            </div>
            <Link href="/blog" className="inline-flex items-center gap-2 px-5 py-2.5 bg-white/[0.03] border border-white/10 hover:bg-white/[0.06] hover:border-white/20 rounded-xl font-medium text-sm transition-all group">
              مشاهده همه
              <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {LATEST_NEWS.map((news, idx) => (
              <motion.article
                key={idx}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
              >
                <Link href={news.href} className="group block h-full">
                  <div className="bg-white/[0.02] backdrop-blur-sm border border-white/5 rounded-3xl overflow-hidden hover:border-white/10 hover:bg-white/[0.04] transition-all h-full flex flex-col">
                    {/* Image placeholder با gradient هنری */}
                    <div className={`relative h-56 bg-gradient-to-br ${news.gradient} overflow-hidden`}>
                      <div 
                        className="absolute inset-0 opacity-30"
                        style={{
                          backgroundImage: `radial-gradient(circle at 30% 50%, ${news.color}40 0%, transparent 60%)`
                        }}
                      />
                      {/* Decorative blobs */}
                      <div className="absolute top-6 right-6 w-24 h-24 rounded-full bg-white/10 blur-2xl" />
                      <div className="absolute bottom-6 left-6 w-16 h-16 rounded-full bg-white/10 blur-xl" />
                      
                      <div className="absolute top-5 right-5">
                        <span className="px-3 py-1.5 bg-black/40 backdrop-blur-xl border border-white/10 rounded-full text-xs font-bold text-white">
                          {news.category}
                        </span>
                      </div>
                    </div>
                    
                    <div className="p-6 flex-1 flex flex-col">
                      <div className="flex items-center gap-4 text-xs text-zinc-500 mb-4">
                        <span className="flex items-center gap-1.5">
                          <Calendar className="h-3.5 w-3.5" />
                          {news.date}
                        </span>
                        <span className="flex items-center gap-1.5">
                          <Eye className="h-3.5 w-3.5" />
                          {news.views.toLocaleString()}
                        </span>
                      </div>
                      <h3 className="text-xl font-bold text-white mb-3 group-hover:text-emerald-300 transition-colors leading-tight line-clamp-2">
                        {news.title}
                      </h3>
                      <p className="text-sm text-zinc-400 line-clamp-2 leading-relaxed flex-1">{news.excerpt}</p>
                      <div className="mt-6 flex items-center gap-2 text-sm font-medium text-emerald-400 group-hover:gap-3 transition-all">
                        ادامه مطلب
                        <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
                      </div>
                    </div>
                  </div>
                </Link>
              </motion.article>
            ))}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* 💚 WHY ECONOJIN - Feature Grid */}
      {/* ================================================================== */}
      <section className="py-32 relative">
        {/* Background accent */}
        <div className="absolute inset-0 -z-10 bg-gradient-to-b from-transparent via-emerald-950/10 to-transparent" />
        
        <div className="container mx-auto px-6 lg:px-12">
          <div className="text-center mb-20">
            <h2 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white mb-6 tracking-tight">
              چرا <span className="bg-gradient-to-r from-emerald-300 to-teal-300 bg-clip-text text-transparent">اکو نوژین</span>؟
            </h2>
            <p className="text-lg text-zinc-400 max-w-2xl mx-auto font-light">
              چهار دلیل که ما را از بقیه متمایز می‌کند
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[
              { icon: Shield, title: "پشتوانه واقعی", desc: "هر توکن با دارایی اکولوژیک تأییدشده پشتیبانی می‌شود", color: PALETTE.emerald.base },
              { icon: Zap, title: "فناوری پیشرفته", desc: "بلاکچین، AI، ماهواره و IoT در یک پلتفرم یکپارچه", color: PALETTE.blue.base },
              { icon: Award, title: "استاندارد جهانی", desc: "مطابق با استانداردهای FAO، IPCC و Verra", color: PALETTE.amber.base },
              { icon: Heart, title: "تأثیر واقعی", desc: "هر اقدام شما مستقیماً به احیای زمین کمک می‌کند", color: PALETTE.rose.base },
            ].map((item, idx) => {
              const Icon = item.icon;
              return (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: idx * 0.1 }}
                  className="group relative bg-white/[0.02] backdrop-blur-sm border border-white/5 rounded-3xl p-8 hover:bg-white/[0.04] hover:border-white/10 transition-all duration-300"
                >
                  <div 
                    className="p-4 rounded-2xl inline-block mb-6 group-hover:scale-110 transition-transform"
                    style={{ 
                      backgroundColor: `${item.color}15`,
                      boxShadow: `0 0 30px ${item.color}20`
                    }}
                  >
                    <Icon className="h-8 w-8" style={{ color: item.color }} />
                  </div>
                  <h3 className="text-2xl font-bold text-white mb-3 tracking-tight">{item.title}</h3>
                  <p className="text-sm text-zinc-400 leading-relaxed">{item.desc}</p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* ================================================================== */}
      {/* 📧 NEWSLETTER CTA - Modern Design */}
      {/* ================================================================== */}
      <section className="py-32">
        <div className="container mx-auto px-6 lg:px-12">
          <div className="relative bg-white/[0.02] backdrop-blur-xl border border-white/10 rounded-[2.5rem] p-12 md:p-16 overflow-hidden">
            {/* Mesh gradient پس‌زمینه */}
            <div 
              className="absolute inset-0 opacity-60"
              style={{
                backgroundImage: `
                  radial-gradient(at 10% 10%, rgba(16, 185, 129, 0.3) 0px, transparent 50%),
                  radial-gradient(at 90% 90%, rgba(59, 130, 246, 0.25) 0px, transparent 50%)
                `
              }}
            />
            {/* Decorative blobs */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-emerald-500/10 rounded-full blur-3xl" />
            <div className="absolute bottom-0 left-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
            
            <div className="relative max-w-3xl mx-auto text-center">
              <div className="inline-flex p-5 rounded-3xl bg-white/10 backdrop-blur-xl border border-white/20 mb-8">
                <Mail className="h-10 w-10 text-emerald-400" />
              </div>
              <h2 className="text-4xl md:text-5xl font-black text-white mb-6 tracking-tight">
                به خانواده اکو نوژین بپیوندید
              </h2>
              <p className="text-lg text-zinc-300 mb-10 font-light leading-relaxed">
                هر هفته جدیدترین مقالات، تحقیقات و فرصت‌های یادگیری را در ایمیل خود دریافت کنید
              </p>
              <form className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto" onSubmit={(e) => e.preventDefault()}>
                <input
                  type="email"
                  placeholder="ایمیل شما"
                  className="flex-1 px-5 py-4 bg-black/30 backdrop-blur-xl border border-white/10 rounded-2xl text-white placeholder-zinc-500 focus:border-emerald-500/50 focus:outline-none focus:ring-2 focus:ring-emerald-500/20 transition-all"
                />
                <button 
                  type="submit" 
                  className="px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 rounded-2xl font-bold text-white transition-all shadow-[0_0_40px_rgba(16,185,129,0.3)] hover:shadow-[0_0_60px_rgba(16,185,129,0.5)] hover:-translate-y-0.5 whitespace-nowrap"
                >
                  عضویت
                </button>
              </form>
              <p className="mt-6 text-xs text-zinc-500">
                بدون اسپم. هر زمان می‌توانید لغو اشتراک کنید.
              </p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}