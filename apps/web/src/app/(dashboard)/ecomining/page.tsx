"use client";

﻿import { useState, useEffect } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";
import { ArrowRight, Coins, Zap, TrendingUp, Leaf, Globe, Shield, Award, Activity, Gauge, Thermometer, Clock, Target, BarChart3, PieChart, Rocket, Gem, Crown, Calculator, Pickaxe, Wind, Droplets, Sun, TreePine, Users, Trophy, Sparkles, Database, Cpu, Server, CheckCircle, AlertTriangle, X, Save, Hash, Lock, Unlock, ArrowUpRight, ArrowDownRight, Percent, Layers, Building2, FileText, Scale, Landmark, Wallet, PiggyBank, Briefcase, Network, Radio, Satellite, Eye, Brain, UserCheck, Factory, Flame, Mountain, Fish, Bird, Bug, Sprout, Flower2, Waves, CircleDollarSign, Banknote, CreditCard, Receipt, Scroll, Calendar, MapPin, Flag, Compass, Microscope, Lightbulb, Heart, Star, Medal, BadgeCheck, Mail } from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(m => m.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(m => m.Area), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(m => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const PieChartChart = dynamic(() => import("recharts").then(m => m.PieChart), { ssr: false });
const Pie = dynamic(() => import("recharts").then(m => m.Pie), { ssr: false });
const Cell = dynamic(() => import("recharts").then(m => m.Cell), { ssr: false });
const RadialBarChart = dynamic(() => import("recharts").then(m => m.RadialBarChart), { ssr: false });
const RadialBar = dynamic(() => import("recharts").then(m => m.RadialBar), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });
const PolarAngleAxis = dynamic(() => import("recharts").then(m => m.PolarAngleAxis), { ssr: false });

// ============================================================================
// Live Data
// ============================================================================
const HASHRATE_HISTORY = Array.from({ length: 24 }, (_, i) => ({
  time: `${String(i).padStart(2, "0")}:00`,
  hashrate: 950 + Math.sin(i / 3) * 50 + Math.random() * 30,
  ecoMinted: 20 + Math.sin(i / 4) * 5 + Math.random() * 3,
}));

const BACKING_ASSETS = [
  { name: "زمین احیاشده", value: 10000000000, percent: 86.2, icon: Mountain, color: "#10b981", unit: "$10B", desc: "1M هکتار" },
  { name: "اعتبارات کربن", value: 500000000, percent: 4.3, icon: Wind, color: "#3b82f6", unit: "$500M", desc: "10M تن CO2" },
  { name: "تنوع زیستی", value: 1000000000, percent: 8.6, icon: Bird, color: "#8b5cf6", unit: "$1B", desc: "10K گونه" },
  { name: "حقوق آب", value: 100000000, percent: 0.9, icon: Droplets, color: "#06b6d4", unit: "$100M", desc: "100B لیتر" },
];

const TOKEN_DISTRIBUTION = [
  { name: "پاداش‌های اکولوژیک", value: 40, color: "#10b981" },
  { name: "توسعه اکوسیستم", value: 20, color: "#3b82f6" },
  { name: "تیم و مشاوران", value: 15, color: "#8b5cf6" },
  { name: "خزانه جامعه", value: 15, color: "#f59e0b" },
  { name: "نقدینگی اولیه", value: 10, color: "#ec4899" },
];

const ORACLE_NETWORK = [
  { type: "ماهواره‌ای", icon: Satellite, count: 12, accuracy: 99.8, providers: ["Sentinel-2", "Landsat-9", "Planet Labs", "Maxar"], color: "#3b82f6" },
  { type: "IoT سنسورها", icon: Radio, count: 45000, accuracy: 98.5, providers: ["Soil Sensors", "Air Monitors", "Water Meters", "Weather Stations"], color: "#10b981" },
  { type: "هوش مصنوعی", icon: Brain, count: 28, accuracy: 97.2, providers: ["Computer Vision", "NDVI Analysis", "Carbon Modeling", "Biodiversity AI"], color: "#8b5cf6" },
  { type: "تأیید انسانی", icon: UserCheck, count: 2500, accuracy: 99.5, providers: ["Ecologists", "Local Communities", "Government", "NGOs"], color: "#f59e0b" },
];

const ROADMAP = [
  {
    phase: "فاز ۱",
    title: "Foundation",
    period: "Q1-Q2 2026",
    status: "in_progress",
    progress: 75,
    color: "#10b981",
    items: [
      { text: "انتشار وایت‌پیپر", done: true },
      { text: "توسعه Smart Contract", done: true },
      { text: "راه‌اندازی شبکه اوراکل", done: true },
      { text: "تأسیس ساختار حقوقی", done: true },
      { text: "جذب سرمایه اولیه ($2M)", done: false },
      { text: "۱۰ پروژه پایلوت", done: false },
    ]
  },
  {
    phase: "فاز ۲",
    title: "Launch",
    period: "Q3-Q4 2026",
    status: "upcoming",
    progress: 0,
    color: "#3b82f6",
    items: [
      { text: "راه‌اندازی Mainnet", done: false },
      { text: "STO (Security Token Offering)", done: false },
      { text: "همکاری‌های بانکی", done: false },
      { text: "لیست شدن در صرافی‌ها", done: false },
      { text: "اپلیکیشن موبایل", done: false },
      { text: "۱۰۰M ECO ضرب‌شده", done: false },
    ]
  },
  {
    phase: "فاز ۳",
    title: "Growth",
    period: "2027",
    status: "upcoming",
    progress: 0,
    color: "#8b5cf6",
    items: [
      { text: "گسترش جهانی", done: false },
      { text: "۱۰۰+ پروژه اکولوژیک", done: false },
      { text: "۱۰K+ کاربر فعال", done: false },
      { text: "Market Cap $100M", done: false },
      { text: "۱M هکتار احیاشده", done: false },
      { text: "۱۰M تن CO2 جذب‌شده", done: false },
    ]
  },
  {
    phase: "فاز ۴",
    title: "Scale",
    period: "2028-2030",
    status: "upcoming",
    progress: 0,
    color: "#f59e0b",
    items: [
      { text: "عرضه ۱B ECO", done: false },
      { text: "۱۰۰K+ کاربر فعال", done: false },
      { text: "Market Cap $1B", done: false },
      { text: "استاندارد جهانی", done: false },
      { text: "ادغام با CBDCها", done: false },
      { text: "۱۰M هکتار احیاشده", done: false },
    ]
  },
];

const KPIS = {
  ecological: [
    { label: "هکتار احیاشده", current: 125000, target: 1000000, unit: "ha", icon: Mountain, color: "#10b981" },
    { label: "تن CO2 جذب‌شده", current: 2400000, target: 10000000, unit: "t", icon: Wind, color: "#3b82f6" },
    { label: "لیتر آب حفظ‌شده", current: 15000000000, target: 100000000000, unit: "L", icon: Droplets, color: "#06b6d4" },
    { label: "گونه حفاظت‌شده", current: 125, target: 1000, unit: "", icon: Bird, color: "#8b5cf6" },
  ],
  economic: [
    { label: "Market Cap", current: 15000000, target: 1000000000, unit: "$", icon: CircleDollarSign, color: "#f59e0b" },
    { label: "قیمت ECO", current: 0.15, target: 1.0, unit: "$", icon: Coins, color: "#10b981" },
    { label: "TVL", current: 2500000, target: 100000000, unit: "$", icon: Lock, color: "#3b82f6" },
    { label: "حجم روزانه", current: 850000, target: 10000000, unit: "$", icon: Activity, color: "#ec4899" },
  ],
  users: [
    { label: "کاربران فعال", current: 12500, target: 100000, unit: "", icon: Users, color: "#8b5cf6" },
    { label: "پروژه‌های اکو", current: 85, target: 1000, unit: "", icon: Sprout, color: "#10b981" },
    { label: "کشورهای فعال", current: 18, target: 50, unit: "", icon: Globe, color: "#3b82f6" },
    { label: "اعضای جامعه", current: 45000, target: 500000, unit: "", icon: Heart, color: "#ec4899" },
  ]
};

const BANKING_PARTNERS = [
  { name: "Triodos Bank", country: "Netherlands", type: "Sustainable Bank", services: ["Fiat Ramp", "Custody", "Green Bonds"], logo: "🏦" },
  { name: "GLS Bank", country: "Germany", type: "Ethical Banking", services: ["Green Finance", "Impact Investing"], logo: "🏛️" },
  { name: "Bank Mishkan", country: "Israel", type: "Green Finance", services: ["Sustainable Loans", "ESG Advisory"], logo: "💰" },
  { name: "Amalgamated Bank", country: "USA", type: "Social Banking", services: ["Community Investment", "Green Deposits"], logo: "🏦" },
];

// ============================================================================
// Components
// ============================================================================
function CountdownTimer({ targetDate, label, icon: Icon }: any) {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date().getTime();
      const distance = targetDate.getTime() - now;
      if (distance < 0) { clearInterval(timer); return; }
      setTimeLeft({
        days: Math.floor(distance / (1000 * 60 * 60 * 24)),
        hours: Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60)),
        minutes: Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60)),
        seconds: Math.floor((distance % (1000 * 60)) / 1000),
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [targetDate]);

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-5">
      <div className="flex items-center gap-2 mb-3">
        <Icon className="h-5 w-5 text-amber-400" />
        <h3 className="text-sm font-bold text-white">{label}</h3>
      </div>
      <div className="grid grid-cols-4 gap-2">
        {[
          { value: timeLeft.days, label: "روز" },
          { value: timeLeft.hours, label: "ساعت" },
          { value: timeLeft.minutes, label: "دقیقه" },
          { value: timeLeft.seconds, label: "ثانیه" },
        ].map((item, idx) => (
          <div key={idx} className="bg-slate-800/50 rounded-lg p-2 text-center">
            <div className="text-xl font-black text-white tabular-nums">{String(item.value).padStart(2, "0")}</div>
            <div className="text-[10px] text-slate-400 mt-0.5">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

function ProgressBar({ value, max, color }: { value: number; max: number; color: string }) {
  const percent = Math.min(100, (value / max) * 100);
  return (
    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
      <motion.div
        initial={{ width: 0 }}
        animate={{ width: `${percent}%` }}
        transition={{ duration: 1, ease: "easeOut" }}
        className="h-full rounded-full"
        style={{ backgroundColor: color }}
      />
    </div>
  );
}

function LivePriceTicker() {
  const [ecoPrice, setEcoPrice] = useState(0.15);
  const [grcPrice, setGrcPrice] = useState(0.25);
  const [marketCap, setMarketCap] = useState(15000000);

  useEffect(() => {
    const interval = setInterval(() => {
      setEcoPrice(prev => prev + (Math.random() - 0.5) * 0.002);
      setGrcPrice(prev => prev + (Math.random() - 0.5) * 0.003);
      setMarketCap(prev => prev + (Math.random() - 0.5) * 50000);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900/90 backdrop-blur-xl border-b border-slate-800 py-2 overflow-hidden sticky top-0 z-40">
      <div className="container mx-auto px-6 flex items-center gap-6 text-sm overflow-x-auto">
        <div className="flex items-center gap-2 whitespace-nowrap">
          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          <span className="text-slate-400 font-bold">LIVE</span>
        </div>
        <div className="flex items-center gap-2 whitespace-nowrap">
          <Coins className="h-4 w-4 text-emerald-400" />
          <span className="text-slate-400">ECO:</span>
          <span className="text-white font-bold">${ecoPrice.toFixed(4)}</span>
          <span className="text-emerald-400 text-xs flex items-center gap-0.5">
            <ArrowUpRight className="h-3 w-3" />5.8%
          </span>
        </div>
        <div className="flex items-center gap-2 whitespace-nowrap">
          <Gem className="h-4 w-4 text-purple-400" />
          <span className="text-slate-400">GRC:</span>
          <span className="text-white font-bold">${grcPrice.toFixed(4)}</span>
          <span className="text-emerald-400 text-xs flex items-center gap-0.5">
            <ArrowUpRight className="h-3 w-3" />3.2%
          </span>
        </div>
        <div className="flex items-center gap-2 whitespace-nowrap">
          <CircleDollarSign className="h-4 w-4 text-amber-400" />
          <span className="text-slate-400">MCap:</span>
          <span className="text-white font-bold">${(marketCap / 1000000).toFixed(2)}M</span>
        </div>
        <div className="flex items-center gap-2 whitespace-nowrap">
          <Shield className="h-4 w-4 text-blue-400" />
          <span className="text-slate-400">Backing:</span>
          <span className="text-emerald-400 font-bold">$11.6B</span>
        </div>
        <div className="flex items-center gap-2 whitespace-nowrap">
          <Leaf className="h-4 w-4 text-green-400" />
          <span className="text-slate-400">CO2:</span>
          <span className="text-emerald-400 font-bold">2.4M tons</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Main Page
// ============================================================================
export default function EcoMiningPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [liveHashrate, setLiveHashrate] = useState(955);

  useEffect(() => {
    const interval = setInterval(() => {
      setLiveHashrate(prev => prev + (Math.random() - 0.5) * 10);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#10b981" },
    { id: "philosophy", label: "فلسفه PoER", icon: Lightbulb, color: "#3b82f6" },
    { id: "backing", label: "پشتوانه اکوسیستم", icon: Shield, color: "#8b5cf6" },
    { id: "tokenomics", label: "توکنومیکس", icon: Coins, color: "#f59e0b" },
    { id: "oracle", label: "شبکه اوراکل", icon: Satellite, color: "#06b6d4" },
    { id: "banking", label: "چارچوب بانکی", icon: Landmark, color: "#ec4899" },
    { id: "roadmap", label: "نقشه راه", icon: MapPin, color: "#14b8a6" },
    { id: "kpi", label: "شاخص‌های کلیدی", icon: Target, color: "#f97316" },
    { id: "vision", label: "چشم‌انداز 2030", icon: Compass, color: "#a855f7" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      <LivePriceTicker />

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 via-blue-600 to-purple-700 opacity-20" />
        <div className="absolute inset-0">
          {[...Array(60)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-emerald-400 rounded-full"
              style={{ left: `${Math.random() * 100}%`, top: `${Math.random() * 100}%` }}
              animate={{ opacity: [0.2, 1, 0.2], scale: [1, 1.5, 1] }}
              transition={{ duration: Math.random() * 3 + 2, repeat: Infinity, delay: Math.random() * 2 }}
            />
          ))}
        </div>
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            <div className="flex items-start gap-6 flex-wrap">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-emerald-500 via-blue-500 to-purple-600 shadow-2xl shadow-emerald-500/30">
                <Leaf className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1 min-w-[300px]">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-bold mb-3">
                  <Sparkles className="h-3 w-3" /> Whitepaper v1.0 • Asset-Backed Cryptocurrency
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-3">
                  Eco<span className="bg-gradient-to-r from-emerald-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">Coin</span>
                </h1>
                <p className="text-lg text-slate-300 max-w-3xl leading-relaxed">
                  اولین ارز دیجیتال با پشتوانه اکوسیستم • Proof of Ecological Restoration
                  <br />
                  <span className="text-emerald-400 font-bold">هر توکن = یک واحد احیای اکوسیستم تأییدشده</span>
                </p>
              </div>
              <div className="flex flex-col gap-3">
                <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-700 rounded-2xl p-4 min-w-[280px]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-slate-400">هش‌ریت لحظه‌ای</span>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                      <span className="text-xs text-emerald-400">LIVE</span>
                    </div>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-white tabular-nums">{liveHashrate.toFixed(1)}</span>
                    <span className="text-sm text-slate-400">MH/s</span>
                  </div>
                  <ProgressBar value={liveHashrate} max={1200} color="#10b981" />
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6 flex-wrap">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2.5 rounded-xl font-bold transition-all flex items-center gap-2 text-sm ${
                activeTab === tab.id ? "text-white shadow-lg" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
              style={activeTab === tab.id ? { backgroundColor: tab.color, boxShadow: `0 10px 25px -5px ${tab.color}50` } : {}}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* ================================================================== */}
        {/* DASHBOARD */}
        {/* ================================================================== */}
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "پشتوانه کل", value: "$11.6B", icon: Shield, color: "#10b981", sub: "دارایی اکولوژیک" },
                { label: "عرضه در گردش", value: "150M ECO", icon: Coins, color: "#3b82f6", sub: "از 1B کل" },
                { label: "Market Cap", value: "$15M", icon: CircleDollarSign, color: "#f59e0b", sub: "+5.8% امروز" },
                { label: "CO2 جذب‌شده", value: "2.4M t", icon: Wind, color: "#8b5cf6", sub: "تأثیر اکولوژیک" },
              ].map((stat, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-5"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2 rounded-lg" style={{ backgroundColor: stat.color + "20" }}>
                      <stat.icon className="h-5 w-5" style={{ color: stat.color }} />
                    </div>
                  </div>
                  <p className="text-2xl font-black text-white">{stat.value}</p>
                  <p className="text-xs text-slate-400 mt-1">{stat.label}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{stat.sub}</p>
                </motion.div>
              ))}
            </div>

            {/* Countdowns */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <CountdownTimer targetDate={new Date(Date.now() + 24 * 60 * 60 * 1000)} label="پاداش روزانه بعدی" icon={Clock} />
              <CountdownTimer targetDate={new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)} label="پرداخت هفتگی" icon={Calendar} />
              <CountdownTimer targetDate={new Date("2028-01-01")} label="Next Halving" icon={Rocket} />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Activity className="h-5 w-5 text-emerald-400" />
                  هش‌ریت و ECO ضرب‌شده (۲۴ ساعت)
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={HASHRATE_HISTORY}>
                    <defs>
                      <linearGradient id="hashGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="ecoGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                    <Legend />
                    <Area type="monotone" dataKey="hashrate" stroke="#10b981" fillOpacity={1} fill="url(#hashGrad)" name="هش‌ریت" />
                    <Area type="monotone" dataKey="ecoMinted" stroke="#3b82f6" fillOpacity={1} fill="url(#ecoGrad)" name="ECO Minted" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Shield className="h-5 w-5 text-purple-400" />
                  ترکیب پشتوانه اکوسیستم
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChartChart>
                    <Pie
                      data={BACKING_ASSETS}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={3}
                      dataKey="value"
                    >
                      {BACKING_ASSETS.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                    <Legend />
                  </PieChartChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Core Principles */}
            <div className="bg-gradient-to-br from-emerald-900/20 to-blue-900/20 border border-emerald-500/30 rounded-2xl p-8">
              <h2 className="text-2xl font-black text-white mb-6 text-center">
                🌍 پارادایم جدید: <span className="text-emerald-400">Proof of Ecological Restoration</span>
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-slate-900/50 rounded-xl p-5 text-center">
                  <div className="text-5xl mb-3">⛏️</div>
                  <h3 className="font-bold text-white mb-2">ماینینگ سنتی</h3>
                  <p className="text-sm text-slate-400">مصرف انرژی عظیم</p>
                  <p className="text-sm text-slate-400">تخریب محیط زیست</p>
                  <p className="text-sm text-red-400 font-bold mt-2">بدون پشتوانه</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-5 text-center flex items-center justify-center">
                  <ArrowRight className="h-12 w-12 text-emerald-400" />
                </div>
                <div className="bg-gradient-to-br from-emerald-900/30 to-teal-900/20 border border-emerald-500/30 rounded-xl p-5 text-center">
                  <div className="text-5xl mb-3">🌱</div>
                  <h3 className="font-bold text-white mb-2">EcoCoin Mining</h3>
                  <p className="text-sm text-slate-300">احیای اکوسیستم</p>
                  <p className="text-sm text-slate-300">انرژی تجدیدپذیر</p>
                  <p className="text-sm text-emerald-400 font-bold mt-2">پشتوانه ۷۷۳۰٪</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* PHILOSOPHY - PoER */}
        {/* ================================================================== */}
        {activeTab === "philosophy" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-blue-900/20 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Lightbulb className="h-8 w-8 text-amber-400" />
                <h2 className="text-3xl font-black text-white">فلسفه پایه EcoCoin</h2>
              </div>
              <div className="bg-slate-900/50 rounded-xl p-6 border-r-4 border-emerald-500 mb-6">
                <p className="text-xl text-slate-200 italic leading-relaxed">
                  "ما از زمین ارث نبرده‌ایم، آن را از فرزندانمان قرض گرفته‌ایم."
                  <br />
                  <span className="text-emerald-400 font-bold">EcoCoin راهی است برای بازپرداخت این قرض، توکن به توکن، درخت به درخت، هکتار به هکتار.</span>
                </p>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {[
                  { icon: AlertTriangle, title: "مشکل بیت‌کوین", items: ["مصرف انرژی = آرژانتین", "تولید بدون پشتوانه", "سفته‌بازی محض", "تخریب محیط زیست"], color: "#ef4444" },
                  { icon: CheckCircle, title: "راه‌حل EcoCoin", items: ["استخراج = احیا", "پشتوانه اکوسیستم", "ارزش‌آفرینی واقعی", "حفاظت از زمین"], color: "#10b981" },
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-900/50 rounded-xl p-5">
                    <div className="flex items-center gap-2 mb-3">
                      <item.icon className="h-5 w-5" style={{ color: item.color }} />
                      <h3 className="font-bold text-white">{item.title}</h3>
                    </div>
                    <ul className="space-y-2">
                      {item.items.map((text, i) => (
                        <li key={i} className="flex items-center gap-2 text-sm text-slate-300">
                          <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: item.color }} />
                          {text}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* PoER Protocol Flow */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
              <h3 className="text-2xl font-black text-white mb-6 text-center">
                ⚙️ چرخه Proof of Ecological Restoration
              </h3>
              <div className="space-y-4">
                {[
                  { step: 1, title: "اقدام اکولوژیک", desc: "کاشت درخت، احیای زمین، صرفه‌جویی آب", icon: Sprout, color: "#10b981" },
                  { step: 2, title: "جمع‌آوری داده", desc: "IoT + ماهواره + پهپاد + اپلیکیشن موبایل", icon: Database, color: "#3b82f6" },
                  { step: 3, title: "تأیید چندلایه", desc: "Oracle Network + AI + کارشناسان انسانی", icon: Shield, color: "#8b5cf6" },
                  { step: 4, title: "پروتکل MRV", desc: "Measurement → Reporting → Verification", icon: FileText, color: "#f59e0b" },
                  { step: 5, title: "ضرب توکن", desc: "Smart Contract → توزیع EcoCoin", icon: Coins, color: "#ec4899" },
                  { step: 6, title: "ثبت دارایی", desc: "NFT Certificate + Geolocation + Timestamp", icon: BadgeCheck, color: "#06b6d4" },
                ].map((item, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.1 }}
                    className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl hover:bg-slate-800 transition-colors"
                  >
                    <div className="flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center font-black text-white text-lg" style={{ backgroundColor: item.color }}>
                      {item.step}
                    </div>
                    <div className="flex-shrink-0 p-3 rounded-xl" style={{ backgroundColor: item.color + "20" }}>
                      <item.icon className="h-6 w-6" style={{ color: item.color }} />
                    </div>
                    <div className="flex-1">
                      <h4 className="font-bold text-white">{item.title}</h4>
                      <p className="text-sm text-slate-400">{item.desc}</p>
                    </div>
                    {idx < 5 && <ArrowRight className="h-5 w-5 text-slate-600 rotate-180" />}
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Reward Formula */}
            <div className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border border-purple-500/30 rounded-2xl p-8">
              <h3 className="text-2xl font-black text-white mb-6 flex items-center gap-2">
                <Calculator className="h-6 w-6 text-purple-400" />
                فرمول محاسبه پاداش
              </h3>
              <div className="bg-slate-900/80 rounded-xl p-6 mb-6 border border-slate-700">
                <code className="text-emerald-400 font-mono text-sm md:text-base block">
                  Reward = Base_Rate × Quantity × Quality × Time × Location
                </code>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
                {[
                  { name: "Base_Rate", desc: "نرخ پایه نوع اقدام", example: "۱۰ ECO/درخت" },
                  { name: "Quantity", desc: "مقدار اقدام", example: "۱۰۰ درخت" },
                  { name: "Quality", desc: "ضریب کیفیت", example: "۰.۸ تا ۱.۵" },
                  { name: "Time", desc: "ضریب زمان", example: "۱.۰ تا ۲.۰" },
                  { name: "Location", desc: "ضریب موقعیت", example: "۰.۹ تا ۱.۳" },
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-900/50 rounded-xl p-4">
                    <p className="font-mono text-sm font-bold text-purple-400 mb-1">{item.name}</p>
                    <p className="text-xs text-slate-400 mb-2">{item.desc}</p>
                    <p className="text-xs text-emerald-400 font-bold">{item.example}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* BACKING */}
        {/* ================================================================== */}
        {activeTab === "backing" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-emerald-900/30 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Shield className="h-8 w-8 text-emerald-400" />
                <div>
                  <h2 className="text-3xl font-black text-white">پشتوانه اکوسیستم</h2>
                  <p className="text-sm text-slate-400 mt-1">طبیعت به عنوان خزانه‌داری • Natural Treasury</p>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/50 rounded-xl p-5 text-center">
                  <p className="text-3xl font-black text-emerald-400">$11.6B</p>
                  <p className="text-sm text-slate-400 mt-1">ارزش کل پشتوانه</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-5 text-center">
                  <p className="text-3xl font-black text-blue-400">7730%</p>
                  <p className="text-sm text-slate-400 mt-1">نسبت پشتوانه</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-5 text-center">
                  <p className="text-3xl font-black text-amber-400">$11.6</p>
                  <p className="text-sm text-slate-400 mt-1">ارزش هر ECO</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-5 text-center">
                  <p className="text-3xl font-black text-purple-400">AAA</p>
                  <p className="text-sm text-slate-400 mt-1">رتبه اعتباری</p>
                </div>
              </div>
            </div>

            {/* Backing Assets */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {BACKING_ASSETS.map((asset, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 rounded-xl" style={{ backgroundColor: asset.color + "20" }}>
                        <asset.icon className="h-8 w-8" style={{ color: asset.color }} />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-white">{asset.name}</h3>
                        <p className="text-xs text-slate-400">{asset.desc}</p>
                      </div>
                    </div>
                    <div className="text-left">
                      <p className="text-2xl font-black" style={{ color: asset.color }}>{asset.unit}</p>
                      <p className="text-xs text-slate-400">{asset.percent}%</p>
                    </div>
                  </div>
                  <ProgressBar value={asset.percent} max={100} color={asset.color} />
                </motion.div>
              ))}
            </div>

            {/* Natural Capital Bonds */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
              <h3 className="text-2xl font-black text-white mb-6 flex items-center gap-2">
                <Scroll className="h-6 w-6 text-amber-400" />
                اوراق قرضه سرمایه طبیعی
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { name: "Forest Bond", backing: "جنگل‌های حفاظت‌شده", yield: "5%", maturity: "20 سال", rating: "AAA", color: "#10b981" },
                  { name: "Water Bond", backing: "منابع آب حفاظت‌شده", yield: "4%", maturity: "30 سال", rating: "AA+", color: "#06b6d4" },
                  { name: "Biodiversity Bond", backing: "تنوع زیستی", yield: "6%", maturity: "50 سال", rating: "AA", color: "#8b5cf6" },
                ].map((bond, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-xl p-5 border-t-4" style={{ borderColor: bond.color }}>
                    <h4 className="font-bold text-white mb-3">{bond.name}</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between"><span className="text-slate-400">پشتوانه:</span><span className="text-white">{bond.backing}</span></div>
                      <div className="flex justify-between"><span className="text-slate-400">بازده:</span><span className="text-emerald-400 font-bold">{bond.yield} سالانه</span></div>
                      <div className="flex justify-between"><span className="text-slate-400">سررسید:</span><span className="text-white">{bond.maturity}</span></div>
                      <div className="flex justify-between"><span className="text-slate-400">رتبه:</span><span className="text-amber-400 font-bold">{bond.rating}</span></div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* TOKENOMICS */}
        {/* ================================================================== */}
        {activeTab === "tokenomics" && (
          <div className="space-y-6">
            {/* Two Token Model */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-emerald-900/30 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Coins className="h-8 w-8 text-emerald-400" />
                  <div>
                    <h3 className="text-xl font-black text-white">EcoCoin (ECO)</h3>
                    <p className="text-xs text-emerald-300">Utility + Asset-Backed Token</p>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">نوع:</span><span className="text-white">Utility</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">عرضه کل:</span><span className="text-white font-bold">1,000,000,000</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">در گردش:</span><span className="text-emerald-400 font-bold">150,000,000</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">پشتوانه:</span><span className="text-emerald-400 font-bold">100% Ecological</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">بلاکچین:</span><span className="text-white">Polygon + ETH L2</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">Consensus:</span><span className="text-white">PoER</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">Staking APY:</span><span className="text-amber-400 font-bold">10%</span></div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/20 border border-purple-500/30 rounded-2xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Gem className="h-8 w-8 text-purple-400" />
                  <div>
                    <h3 className="text-xl font-black text-white">GreenCredit (GRC)</h3>
                    <p className="text-xs text-purple-300">Governance + Staking Token</p>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">نوع:</span><span className="text-white">Governance</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">عرضه:</span><span className="text-white font-bold">Unlimited (Dynamic)</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">Burn:</span><span className="text-emerald-400 font-bold">Yes (Deflationary)</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">کاربرد:</span><span className="text-white">Voting + Staking</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">بلاکچین:</span><span className="text-white">Polygon</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">Consensus:</span><span className="text-white">PoS</span></div>
                  <div className="flex justify-between p-2 bg-slate-900/50 rounded"><span className="text-slate-400">Staking APY:</span><span className="text-amber-400 font-bold">15%</span></div>
                </div>
              </div>
            </div>

            {/* Distribution */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
              <h3 className="text-2xl font-black text-white mb-6 text-center">توزیع عرضه ECO</h3>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <ResponsiveContainer width="100%" height={300}>
                  <PieChartChart>
                    <Pie data={TOKEN_DISTRIBUTION} cx="50%" cy="50%" outerRadius={120} dataKey="value" label>
                      {TOKEN_DISTRIBUTION.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                  </PieChartChart>
                </ResponsiveContainer>
                <div className="space-y-3">
                  {TOKEN_DISTRIBUTION.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-3 p-3 bg-slate-800/50 rounded-xl">
                      <div className="w-4 h-4 rounded-full" style={{ backgroundColor: item.color }} />
                      <div className="flex-1">
                        <p className="font-bold text-white">{item.name}</p>
                      </div>
                      <p className="text-xl font-black" style={{ color: item.color }}>{item.value}%</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Economic Mechanisms */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-red-900/20 to-orange-900/20 border border-red-500/30 rounded-2xl p-6">
                <Flame className="h-8 w-8 text-red-400 mb-3" />
                <h4 className="font-bold text-white mb-2">Deflationary Burn</h4>
                <p className="text-sm text-slate-400 mb-3">سوزاندن توکن در صورت تخریب اکوسیستم</p>
                <div className="bg-slate-900/50 rounded p-3 text-xs">
                  <p className="text-slate-400">Burn Rate:</p>
                  <p className="text-red-400 font-bold">0.5% quarterly</p>
                </div>
              </div>
              <div className="bg-gradient-to-br from-blue-900/20 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-6">
                <Activity className="h-8 w-8 text-blue-400 mb-3" />
                <h4 className="font-bold text-white mb-2">Dynamic Supply</h4>
                <p className="text-sm text-slate-400 mb-3">تنظیم عرضه بر اساس نیاز اکولوژیک</p>
                <div className="bg-slate-900/50 rounded p-3 text-xs">
                  <p className="text-slate-400">Mint Trigger:</p>
                  <p className="text-blue-400 font-bold">Ecological Need Score</p>
                </div>
              </div>
              <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6">
                <Lock className="h-8 w-8 text-emerald-400 mb-3" />
                <h4 className="font-bold text-white mb-2">Conservation Staking</h4>
                <p className="text-sm text-slate-400 mb-3">سپرده‌گذاری برای حفاظت</p>
                <div className="bg-slate-900/50 rounded p-3 text-xs">
                  <p className="text-slate-400">APY Range:</p>
                  <p className="text-emerald-400 font-bold">12% - 18%</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* ORACLE NETWORK */}
        {/* ================================================================== */}
        {activeTab === "oracle" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-cyan-900/20 to-blue-900/20 border border-cyan-500/30 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Satellite className="h-8 w-8 text-cyan-400" />
                <div>
                  <h2 className="text-3xl font-black text-white">شبکه اوراکل چندلایه</h2>
                  <p className="text-sm text-slate-400 mt-1">تأیید چندمنبعی برای اطمینان از صحت داده‌ها</p>
                </div>
              </div>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                  <p className="text-3xl font-black text-cyan-400">45K+</p>
                  <p className="text-xs text-slate-400 mt-1">اوراکل فعال</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                  <p className="text-3xl font-black text-emerald-400">99.2%</p>
                  <p className="text-xs text-slate-400 mt-1">دقت میانگین</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                  <p className="text-3xl font-black text-amber-400">4</p>
                  <p className="text-xs text-slate-400 mt-1">نوع اوراکل</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4 text-center">
                  <p className="text-3xl font-black text-purple-400">24/7</p>
                  <p className="text-xs text-slate-400 mt-1">مانیتورینگ</p>
                </div>
              </div>
            </div>

            {/* Oracle Types */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {ORACLE_NETWORK.map((oracle, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-6"
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="p-3 rounded-xl" style={{ backgroundColor: oracle.color + "20" }}>
                        <oracle.icon className="h-8 w-8" style={{ color: oracle.color }} />
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-white">{oracle.type}</h3>
                        <p className="text-xs text-slate-400">{oracle.count.toLocaleString()} نود فعال</p>
                      </div>
                    </div>
                    <div className="text-left">
                      <p className="text-2xl font-black" style={{ color: oracle.color }}>{oracle.accuracy}%</p>
                      <p className="text-xs text-slate-400">دقت</p>
                    </div>
                  </div>
                  <div className="space-y-2">
                    {oracle.providers.map((provider, i) => (
                      <div key={i} className="flex items-center gap-2 p-2 bg-slate-800/50 rounded text-sm">
                        <CheckCircle className="h-4 w-4" style={{ color: oracle.color }} />
                        <span className="text-slate-300">{provider}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>

            {/* Consensus Mechanism */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
              <h3 className="text-2xl font-black text-white mb-6 text-center">
                🔐 مکانیزم اجماع اوراکل
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { step: 1, title: "جمع‌آوری", desc: "داده از ۴ منبع مختلف", icon: Database },
                  { step: 2, title: "تأیید متقاطع", desc: "مقایسه داده‌ها بین منابع", icon: Shield },
                  { step: 3, title: "اجماع", desc: "حداقل ۳ از ۴ منبع موافق", icon: CheckCircle },
                  { step: 4, title: "ثبت نهایی", desc: "ضرب توکن روی بلاکچین", icon: Coins },
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-xl p-4 text-center">
                    <div className="inline-flex w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 items-center justify-center text-white font-black text-lg mb-3">
                      {item.step}
                    </div>
                    <item.icon className="h-6 w-6 text-cyan-400 mx-auto mb-2" />
                    <h4 className="font-bold text-white mb-1">{item.title}</h4>
                    <p className="text-xs text-slate-400">{item.desc}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* BANKING FRAMEWORK */}
        {/* ================================================================== */}
        {activeTab === "banking" && (
          <div className="space-y-6">
            {/* Legal Structure */}
            <div className="bg-gradient-to-br from-pink-900/20 to-rose-900/20 border border-pink-500/30 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Building2 className="h-8 w-8 text-pink-400" />
                <h2 className="text-3xl font-black text-white">ساختار حقوقی</h2>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {[
                  { name: "EcoCoin Foundation", location: "Switzerland", type: "Non-profit", desc: "Governance & Treasury", icon: Landmark, color: "#10b981" },
                  { name: "EcoCoin Treasury AG", location: "Switzerland", type: "Licensed FI", desc: "Asset Custody", icon: Building2, color: "#3b82f6" },
                  { name: "EcoCoin Labs", location: "USA", type: "Technology", desc: "R&D PoER", icon: Cpu, color: "#8b5cf6" },
                  { name: "Regional Entities", location: "Global", type: "Operations", desc: "UAE, EU, Asia, Americas", icon: Globe, color: "#f59e0b" },
                ].map((entity, idx) => (
                  <div key={idx} className="bg-slate-900/50 rounded-xl p-5 border-t-4" style={{ borderColor: entity.color }}>
                    <entity.icon className="h-8 w-8 mb-3" style={{ color: entity.color }} />
                    <h4 className="font-bold text-white mb-1">{entity.name}</h4>
                    <p className="text-xs text-slate-400 mb-2">{entity.location} • {entity.type}</p>
                    <p className="text-xs text-slate-500">{entity.desc}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Banking Partners */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
              <h3 className="text-2xl font-black text-white mb-6 flex items-center gap-2">
                <Landmark className="h-6 w-6 text-emerald-400" />
                شرکای بانکی
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {BANKING_PARTNERS.map((bank, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-xl p-5 flex items-start gap-4">
                    <div className="text-4xl">{bank.logo}</div>
                    <div className="flex-1">
                      <h4 className="font-bold text-white">{bank.name}</h4>
                      <p className="text-xs text-slate-400 mb-2">{bank.country} • {bank.type}</p>
                      <div className="flex flex-wrap gap-1">
                        {bank.services.map((service, i) => (
                          <span key={i} className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded text-xs">{service}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Compliance */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
              <h3 className="text-2xl font-black text-white mb-6 flex items-center gap-2">
                <Scale className="h-6 w-6 text-amber-400" />
                انطباق قانونی (Compliance)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { region: "EU", regulation: "MiCA", status: "Compliant", license: "CASPs License", color: "#3b82f6" },
                  { region: "USA", regulation: "SEC", status: "STO (Reg A+)", license: "Form C Filed", color: "#ef4444" },
                  { region: "UAE", regulation: "VARA", status: "Licensed", license: "MVP License", color: "#10b981" },
                ].map((comp, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-xl p-5 border-t-4" style={{ borderColor: comp.color }}>
                    <div className="flex items-center justify-between mb-3">
                      <Flag className="h-6 w-6" style={{ color: comp.color }} />
                      <span className="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded text-xs font-bold">{comp.status}</span>
                    </div>
                    <h4 className="font-bold text-white text-lg mb-1">{comp.region}</h4>
                    <p className="text-sm text-slate-400 mb-2">{comp.regulation}</p>
                    <p className="text-xs text-slate-500">{comp.license}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* STO Structure */}
            <div className="bg-gradient-to-br from-amber-900/20 to-orange-900/20 border border-amber-500/30 rounded-2xl p-8">
              <h3 className="text-2xl font-black text-white mb-6 flex items-center gap-2">
                <Receipt className="h-6 w-6 text-amber-400" />
                ساختار STO (Security Token Offering)
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-900/50 rounded-xl p-5">
                  <h4 className="font-bold text-amber-400 mb-3">Private Sale</h4>
                  <p className="text-3xl font-black text-white mb-1">20%</p>
                  <p className="text-sm text-slate-400">$10M @ $0.10/ECO</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-5">
                  <h4 className="font-bold text-amber-400 mb-3">Public STO</h4>
                  <p className="text-3xl font-black text-white mb-1">30%</p>
                  <p className="text-sm text-slate-400">$30M @ $0.15/ECO</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-5">
                  <h4 className="font-bold text-amber-400 mb-3">Ecosystem</h4>
                  <p className="text-3xl font-black text-white mb-1">50%</p>
                  <p className="text-sm text-slate-400">Strategic Partnerships</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* ROADMAP */}
        {/* ================================================================== */}
        {activeTab === "roadmap" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-teal-900/20 to-cyan-900/20 border border-teal-500/30 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <MapPin className="h-8 w-8 text-teal-400" />
                <div>
                  <h2 className="text-3xl font-black text-white">نقشه راه EcoCoin</h2>
                  <p className="text-sm text-slate-400 mt-1">از ایده تا استاندارد جهانی</p>
                </div>
              </div>
            </div>

            <div className="space-y-6">
              {ROADMAP.map((phase, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-6"
                >
                  <div className="flex items-center justify-between mb-4 flex-wrap gap-3">
                    <div className="flex items-center gap-4">
                      <div className="flex-shrink-0 w-16 h-16 rounded-2xl flex items-center justify-center font-black text-white text-xl" style={{ backgroundColor: phase.color }}>
                        {phase.phase}
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-white">{phase.title}</h3>
                        <p className="text-sm text-slate-400">{phase.period}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right">
                        <p className="text-2xl font-black" style={{ color: phase.color }}>{phase.progress}%</p>
                        <p className="text-xs text-slate-400">{phase.status === "in_progress" ? "در حال اجرا" : "آینده"}</p>
                      </div>
                      {phase.status === "in_progress" && (
                        <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                      )}
                    </div>
                  </div>
                  <ProgressBar value={phase.progress} max={100} color={phase.color} />
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mt-4">
                    {phase.items.map((item, i) => (
                      <div key={i} className="flex items-center gap-2 p-2 bg-slate-800/50 rounded text-sm">
                        {item.done ? (
                          <CheckCircle className="h-4 w-4 text-emerald-400 flex-shrink-0" />
                        ) : (
                          <div className="h-4 w-4 rounded-full border-2 border-slate-600 flex-shrink-0" />
                        )}
                        <span className={item.done ? "text-slate-300" : "text-slate-500"}>{item.text}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* KPIs */}
        {/* ================================================================== */}
        {activeTab === "kpi" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-orange-900/20 to-red-900/20 border border-orange-500/30 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Target className="h-8 w-8 text-orange-400" />
                <div>
                  <h2 className="text-3xl font-black text-white">شاخص‌های کلیدی عملکرد (KPIs)</h2>
                  <p className="text-sm text-slate-400 mt-1">پیشرفت به سمت اهداف ۲۰۳۰</p>
                </div>
              </div>
            </div>

            {/* Ecological KPIs */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Leaf className="h-5 w-5 text-emerald-400" />
                شاخص‌های اکولوژیک
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {KPIS.ecological.map((kpi, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <kpi.icon className="h-5 w-5" style={{ color: kpi.color }} />
                        <span className="font-bold text-white">{kpi.label}</span>
                      </div>
                      <span className="text-xs text-slate-400">{((kpi.current / kpi.target) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-baseline gap-2 mb-2">
                      <span className="text-2xl font-black" style={{ color: kpi.color }}>
                        {kpi.unit === "$" ? "$" : ""}{(kpi.current / (kpi.current > 1000000 ? 1000000 : kpi.current > 1000 ? 1000 : 1)).toFixed(kpi.current > 1000000 ? 2 : 0)}
                        {kpi.current > 1000000 ? "M" : kpi.current > 1000 ? "K" : ""}{kpi.unit !== "$" ? kpi.unit : ""}
                      </span>
                      <span className="text-sm text-slate-400">/ {kpi.target.toLocaleString()} {kpi.unit}</span>
                    </div>
                    <ProgressBar value={kpi.current} max={kpi.target} color={kpi.color} />
                  </div>
                ))}
              </div>
            </div>

            {/* Economic KPIs */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <CircleDollarSign className="h-5 w-5 text-amber-400" />
                شاخص‌های اقتصادی
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {KPIS.economic.map((kpi, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <kpi.icon className="h-5 w-5" style={{ color: kpi.color }} />
                        <span className="font-bold text-white">{kpi.label}</span>
                      </div>
                      <span className="text-xs text-slate-400">{((kpi.current / kpi.target) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-baseline gap-2 mb-2">
                      <span className="text-2xl font-black" style={{ color: kpi.color }}>
                        ${kpi.current >= 1000000 ? (kpi.current / 1000000).toFixed(2) + "M" : kpi.current >= 1000 ? (kpi.current / 1000).toFixed(1) + "K" : kpi.current}
                      </span>
                      <span className="text-sm text-slate-400">/ ${kpi.target >= 1000000000 ? "1B" : kpi.target >= 1000000 ? (kpi.target / 1000000) + "M" : kpi.target}</span>
                    </div>
                    <ProgressBar value={kpi.current} max={kpi.target} color={kpi.color} />
                  </div>
                ))}
              </div>
            </div>

            {/* User KPIs */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Users className="h-5 w-5 text-purple-400" />
                شاخص‌های کاربران
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {KPIS.users.map((kpi, idx) => (
                  <div key={idx} className="bg-slate-800/50 rounded-xl p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <kpi.icon className="h-5 w-5" style={{ color: kpi.color }} />
                        <span className="font-bold text-white">{kpi.label}</span>
                      </div>
                      <span className="text-xs text-slate-400">{((kpi.current / kpi.target) * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex items-baseline gap-2 mb-2">
                      <span className="text-2xl font-black" style={{ color: kpi.color }}>
                        {kpi.current >= 1000 ? (kpi.current / 1000).toFixed(1) + "K" : kpi.current}
                      </span>
                      <span className="text-sm text-slate-400">/ {kpi.target >= 1000 ? (kpi.target / 1000) + "K" : kpi.target}</span>
                    </div>
                    <ProgressBar value={kpi.current} max={kpi.target} color={kpi.color} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ================================================================== */}
        {/* VISION 2030 */}
        {/* ================================================================== */}
        {activeTab === "vision" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-purple-900/30 via-pink-900/20 to-amber-900/20 border border-purple-500/30 rounded-2xl p-8">
              <div className="flex items-center gap-3 mb-6">
                <Compass className="h-8 w-8 text-purple-400" />
                <div>
                  <h2 className="text-3xl font-black text-white">چشم‌انداز ۲۰۳۰</h2>
                  <p className="text-sm text-slate-400 mt-1">EcoCoin در سال ۲۰۳۰</p>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {[
                  { icon: Globe, title: "استاندارد جهانی", desc: "تأیید شده توسط UN، World Bank، IMF", color: "#10b981" },
                  { icon: CircleDollarSign, title: "Market Cap $10B+", desc: "در بین ۲۰ ارز دیجیتال برتر", color: "#3b82f6" },
                  { icon: Mountain, title: "۱۰۰M هکتار احیاشده", desc: "معادل مساحت مصر", color: "#10b981" },
                  { icon: Wind, title: "۱B تن CO2 جذب‌شده", desc: "۲.۵٪ انتشار سالانه جهان", color: "#06b6d4" },
                  { icon: Users, title: "۱۰M کاربر فعال", desc: "در ۱۵۰+ کشور", color: "#8b5cf6" },
                  { icon: Landmark, title: "ادغام با بانکداری جهانی", desc: "CBDC bridges، SWIFT", color: "#f59e0b" },
                  { icon: Award, title: "استاندارد آکادمیک", desc: "تدریس در ۱۰۰۰+ دانشگاه", color: "#ec4899" },
                  { icon: Users, title: "۱۰۰۰+ شریک استراتژیک", desc: "دولت‌ها، NGOها، شرکت‌ها", color: "#14b8a6" },
                  { icon: Heart, title: "تغییر پارادایم جهانی", desc: "از استخراج به احیا", color: "#ef4444" },
                ].map((item, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.05 }}
                    className="bg-slate-900/50 rounded-xl p-5 border-t-4"
                    style={{ borderColor: item.color }}
                  >
                    <item.icon className="h-8 w-8 mb-3" style={{ color: item.color }} />
                    <h4 className="font-bold text-white mb-1">{item.title}</h4>
                    <p className="text-xs text-slate-400">{item.desc}</p>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Final Message */}
            <div className="bg-gradient-to-br from-emerald-900/30 via-blue-900/30 to-purple-900/30 border border-emerald-500/30 rounded-2xl p-12 text-center">
              <Leaf className="h-16 w-16 text-emerald-400 mx-auto mb-6" />
              <h3 className="text-3xl md:text-4xl font-black text-white mb-6 leading-tight">
                EcoCoin: <span className="bg-gradient-to-r from-emerald-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">More Than a Cryptocurrency</span>
              </h3>
              <p className="text-lg text-slate-300 leading-relaxed max-w-3xl mx-auto mb-8">
                EcoCoin یک ارز دیجیتال معمولی نیست. این یک <span className="text-emerald-400 font-bold">جنبش جهانی</span> برای:
              </p>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3 mb-8">
                {[
                  "تغییر پارادایم",
                  "ایجاد ارزش واقعی",
                  "دموکراتیک کردن حفاظت",
                  "شفافیت کامل",
                  "اقتصاد چرخشی",
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-900/50 rounded-xl p-3">
                    <p className="text-sm font-bold text-emerald-400">{item}</p>
                  </div>
                ))}
              </div>
              <div className="bg-slate-900/50 rounded-2xl p-6 border-r-4 border-emerald-500 max-w-3xl mx-auto">
                <p className="text-xl text-slate-200 italic leading-relaxed">
                  "ما از زمین ارث نبرده‌ایم، آن را از فرزندانمان قرض گرفته‌ایم."
                  <br />
                  <span className="text-emerald-400 font-bold not-italic block mt-3">
                    EcoCoin راهی است برای بازپرداخت این قرض،<br />
                    توکن به توکن، درخت به درخت، هکتار به هکتار.
                  </span>
                </p>
              </div>
            </div>

            {/* Call to Action */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Link href="/ecocoin" className="bg-gradient-to-br from-emerald-600 to-teal-600 hover:opacity-90 rounded-2xl p-6 text-center transition-opacity">
                <Coins className="h-10 w-10 text-white mx-auto mb-3" />
                <h4 className="font-bold text-white text-lg mb-1">خرید EcoCoin</h4>
                <p className="text-sm text-emerald-100">شروع سرمایه‌گذاری سبز</p>
              </Link>
              <Link href="/newsletter" className="bg-gradient-to-br from-purple-600 to-pink-600 hover:opacity-90 rounded-2xl p-6 text-center transition-opacity">
                <Mail className="h-10 w-10 text-white mx-auto mb-3" />
                <h4 className="font-bold text-white text-lg mb-1">عضویت در خبرنامه</h4>
                <p className="text-sm text-purple-100">دریافت به‌روزرسانی‌ها</p>
              </Link>
              <Link href="/contact" className="bg-gradient-to-br from-amber-600 to-orange-600 hover:opacity-90 rounded-2xl p-6 text-center transition-opacity">
                <Users className="h-10 w-10 text-white mx-auto mb-3" />
                <h4 className="font-bold text-white text-lg mb-1">همکاری با ما</h4>
                <p className="text-sm text-amber-100">شریک استراتژیک شوید</p>
              </Link>
            </div>
          </div>
        )}
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 mt-12">
        <div className="container mx-auto px-6 text-center">
          <p className="text-sm text-slate-400">
            © 2026 EcoCoin Foundation • Whitepaper v1.0 • Proof of Ecological Restoration
          </p>
          <p className="text-xs text-slate-500 mt-2">
            Asset-Backed Cryptocurrency • Regulated in EU, USA, UAE
          </p>
        </div>
      </footer>
    </div>
  );
}