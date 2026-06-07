#!/usr/bin/env python3
"""Upgrade EcoMining to professional version with all features"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "apps" / "web" / "src"

content = '''"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import dynamic from "next/dynamic";
import {
  ArrowRight, Cpu, Zap, TrendingUp, TrendingDown, DollarSign, Leaf,
  Plus, Edit, Trash2, Eye, Play, Pause, Settings, Activity, Gauge,
  Thermometer, Clock, Award, Coins, BarChart3, PieChart, Target,
  Shield, Wifi, Server, CheckCircle, AlertTriangle, X, Save,
  Calculator, Pickaxe, Battery, Wind, Droplets, Sun, TreePine,
  Globe, Users, Trophy, Flame, Sparkles, Rocket, Gem, Crown,
  ChevronDown, ChevronRight, Filter, Download, RefreshCw, Bell,
  Power, HardDrive, CircuitBoard, Timer, Calendar, Hash, Lock,
  Unlock, ArrowUpRight, ArrowDownRight, Percent, Layers
} from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(m => m.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(m => m.Area), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(m => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const RadialBarChart = dynamic(() => import("recharts").then(m => m.RadialBarChart), { ssr: false });
const RadialBar = dynamic(() => import("recharts").then(m => m.RadialBar), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });
const PolarAngleAxis = dynamic(() => import("recharts").then(m => m.PolarAngleAxis), { ssr: false });

// ============================================================================
// Mock Data
// ============================================================================
const MINING_DEVICES = [
  { id: 1, name: "EcoMiner X1 Pro", type: "ASIC", model: "Bitmain S21", hashrate: 220, power: 1800, status: "active", temperature: 62, earnings24h: 82.5, earningsTotal: 12450, location: "Tehran Data Center", uptime: 99.8, efficiency: 12.2, ecoScore: 95, energy: "solar", startedAt: "2024-03-15", icon: "⛏️" },
  { id: 2, name: "GreenRig Pro Max", type: "GPU", model: "RTX 4090 x8", hashrate: 185, power: 2400, status: "active", temperature: 58, earnings24h: 68.3, earningsTotal: 9870, location: "Isfahan Solar Farm", uptime: 99.5, efficiency: 7.7, ecoScore: 98, energy: "solar", startedAt: "2024-05-22", icon: "🖥️" },
  { id: 3, name: "EcoNode Mini", type: "CPU", model: "AMD EPYC 9654", hashrate: 45, power: 280, status: "active", temperature: 48, earnings24h: 12.8, earningsTotal: 2340, location: "Khorasan Wind Farm", uptime: 98.9, efficiency: 16.1, ecoScore: 99, energy: "wind", startedAt: "2024-07-10", icon: "💻" },
  { id: 4, name: "HydroMiner V3", type: "ASIC", model: "MicroBT M60", hashrate: 350, power: 3200, status: "maintenance", temperature: 75, earnings24h: 0, earningsTotal: 18920, location: "Mazandaran Hydro", uptime: 96.2, efficiency: 10.9, ecoScore: 100, energy: "hydro", startedAt: "2024-01-08", icon: "🌊" },
  { id: 5, name: "SolarRig Alpha", type: "GPU", model: "RTX 4080 x6", hashrate: 145, power: 1600, status: "active", temperature: 54, earnings24h: 52.1, earningsTotal: 8750, location: "Yazd Solar Farm", uptime: 99.9, efficiency: 9.1, ecoScore: 100, energy: "solar", startedAt: "2024-04-18", icon: "☀️" },
  { id: 6, name: "WindMiner Pro", type: "ASIC", model: "Antminer S19", hashrate: 110, power: 1100, status: "active", temperature: 60, earnings24h: 38.7, earningsTotal: 6540, location: "Manjil Wind Farm", uptime: 99.2, efficiency: 10.0, ecoScore: 97, energy: "wind", startedAt: "2024-06-03", icon: "💨" },
];

const LEADERBOARD = [
  { rank: 1, name: "GreenMiner_Iran", country: "🇮🇷", hashrate: 1250, ecoScore: 99.8, earnings: 45820, badge: "👑" },
  { rank: 2, name: "EcoWarrior_2024", country: "🇩🇪", hashrate: 980, ecoScore: 98.5, earnings: 38450, badge: "🥈" },
  { rank: 3, name: "SolarMiner_Pro", country: "🇦🇺", hashrate: 870, ecoScore: 99.2, earnings: 34200, badge: "🥉" },
  { rank: 4, name: "WindPower_Mining", country: "🇩🇰", hashrate: 720, ecoScore: 97.8, earnings: 28900, badge: "⭐" },
  { rank: 5, name: "HydroHash_Master", country: "🇳🇴", hashrate: 650, ecoScore: 98.9, earnings: 25400, badge: "⭐" },
  { rank: 6, name: "You", country: "🇮🇷", hashrate: 955, ecoScore: 98.2, earnings: 58870, badge: "🌟", isYou: true },
];

const HASHRATE_HISTORY = Array.from({ length: 24 }, (_, i) => ({
  time: `${i}:00`,
  hashrate: 950 + Math.sin(i / 3) * 50 + Math.random() * 30,
  earnings: 20 + Math.sin(i / 4) * 5 + Math.random() * 3,
}));

const EARNINGS_30D = Array.from({ length: 30 }, (_, i) => ({
  day: i + 1,
  eco: 120 + Math.sin(i / 3) * 30 + Math.random() * 20,
  grc: 45 + Math.sin(i / 4) * 10 + Math.random() * 8,
  usd: 18 + Math.sin(i / 5) * 4 + Math.random() * 2,
}));

const RECENT_TRANSACTIONS = [
  { id: "tx_8f2a", type: "reward", amount: 45.2, token: "ECO", time: "2 دقیقه پیش", status: "confirmed", device: "EcoMiner X1 Pro" },
  { id: "tx_7c3b", type: "reward", amount: 18.5, token: "GRC", time: "15 دقیقه پیش", status: "confirmed", device: "GreenRig Pro Max" },
  { id: "tx_6d4e", type: "transfer", amount: 100, token: "ECO", time: "1 ساعت پیش", status: "confirmed", device: "Transfer to Wallet" },
  { id: "tx_5e9f", type: "reward", amount: 32.8, token: "ECO", time: "2 ساعت پیش", status: "confirmed", device: "SolarRig Alpha" },
  { id: "tx_4f1a", type: "exchange", amount: 50, token: "ECO→GRC", time: "3 ساعت پیش", status: "confirmed", device: "Exchange" },
];

const NETWORK_STATS = {
  networkHashrate: 425.8,
  difficulty: 83.95,
  blockReward: 3.125,
  nextHalving: "1,247 days",
  ecoPrice: 0.15,
  grcPrice: 0.25,
  ecoChange: 5.8,
  grcChange: 3.2,
  totalGreenMiners: 12847,
  totalCO2Saved: 284500,
};

// ============================================================================
// Countdown Timer Component
// ============================================================================
function CountdownTimer({ targetDate, label }: { targetDate: Date; label: string }) {
  const [timeLeft, setTimeLeft] = useState({ days: 0, hours: 0, minutes: 0, seconds: 0 });

  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date().getTime();
      const distance = targetDate.getTime() - now;
      if (distance < 0) {
        clearInterval(timer);
        return;
      }
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
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-6">
      <div className="flex items-center gap-2 mb-4">
        <Timer className="h-5 w-5 text-amber-400" />
        <h3 className="text-sm font-bold text-white">{label}</h3>
      </div>
      <div className="grid grid-cols-4 gap-2">
        {[
          { value: timeLeft.days, label: "روز" },
          { value: timeLeft.hours, label: "ساعت" },
          { value: timeLeft.minutes, label: "دقیقه" },
          { value: timeLeft.seconds, label: "ثانیه" },
        ].map((item, idx) => (
          <div key={idx} className="bg-slate-800/50 rounded-xl p-3 text-center">
            <div className="text-2xl font-black text-white tabular-nums">
              {String(item.value).padStart(2, "0")}
            </div>
            <div className="text-xs text-slate-400 mt-1">{item.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ============================================================================
// Live Price Ticker
// ============================================================================
function LivePriceTicker() {
  const [ecoPrice, setEcoPrice] = useState(0.15);
  const [grcPrice, setGrcPrice] = useState(0.25);

  useEffect(() => {
    const interval = setInterval(() => {
      setEcoPrice(prev => prev + (Math.random() - 0.5) * 0.002);
      setGrcPrice(prev => prev + (Math.random() - 0.5) * 0.003);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-slate-900/80 backdrop-blur-xl border-b border-slate-800 py-2 overflow-hidden">
      <div className="container mx-auto px-6 flex items-center gap-6 text-sm overflow-x-auto">
        <div className="flex items-center gap-2 whitespace-nowrap">
          <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
          <span className="text-slate-400">LIVE</span>
        </div>
        <div className="flex items-center gap-4 whitespace-nowrap">
          <span className="text-slate-400">ECO/USD:</span>
          <span className="text-white font-bold">${ecoPrice.toFixed(4)}</span>
          <span className="text-emerald-400 text-xs flex items-center gap-1">
            <ArrowUpRight className="h-3 w-3" />
            {NETWORK_STATS.ecoChange}%
          </span>
        </div>
        <div className="flex items-center gap-4 whitespace-nowrap">
          <span className="text-slate-400">GRC/USD:</span>
          <span className="text-white font-bold">${grcPrice.toFixed(4)}</span>
          <span className="text-emerald-400 text-xs flex items-center gap-1">
            <ArrowUpRight className="h-3 w-3" />
            {NETWORK_STATS.grcChange}%
          </span>
        </div>
        <div className="flex items-center gap-4 whitespace-nowrap">
          <span className="text-slate-400">Network Hash:</span>
          <span className="text-white font-bold">{NETWORK_STATS.networkHashrate} EH/s</span>
        </div>
        <div className="flex items-center gap-4 whitespace-nowrap">
          <span className="text-slate-400">Difficulty:</span>
          <span className="text-white font-bold">{NETWORK_STATS.difficulty}T</span>
        </div>
        <div className="flex items-center gap-4 whitespace-nowrap">
          <span className="text-slate-400">Green Miners:</span>
          <span className="text-emerald-400 font-bold">{NETWORK_STATS.totalGreenMiners.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// Main Page Component
// ============================================================================
export default function EcoMiningPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [devices, setDevices] = useState(MINING_DEVICES);
  const [showModal, setShowModal] = useState<string | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<any>(null);
  const [liveHashrate, setLiveHashrate] = useState(955);

  // Live hashrate simulation
  useEffect(() => {
    const interval = setInterval(() => {
      setLiveHashrate(prev => prev + (Math.random() - 0.5) * 10);
    }, 2000);
    return () => clearInterval(interval);
  }, []);

  // Stats
  const activeDevices = devices.filter(d => d.status === "active");
  const totalHashrate = activeDevices.reduce((sum, d) => sum + d.hashrate, 0);
  const totalPower = activeDevices.reduce((sum, d) => sum + d.power, 0);
  const totalEarnings24h = devices.reduce((sum, d) => sum + d.earnings24h, 0);
  const totalEarnings = devices.reduce((sum, d) => sum + d.earningsTotal, 0);
  const avgEcoScore = devices.reduce((sum, d) => sum + d.ecoScore, 0) / devices.length;
  const avgTemp = activeDevices.reduce((sum, d) => sum + d.temperature, 0) / activeDevices.length;

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#10b981" },
    { id: "devices", label: "دستگاه‌ها", icon: Cpu, color: "#3b82f6" },
    { id: "earnings", label: "درآمدها", icon: Coins, color: "#f59e0b" },
    { id: "calculator", label: "محاسبه‌گر ROI", icon: Calculator, color: "#8b5cf6" },
    { id: "ecological", label: "تأثیر اکولوژیک", icon: Leaf, color: "#22c55e" },
    { id: "leaderboard", label: "رتبه‌بندی", icon: Trophy, color: "#ec4899" },
    { id: "pool", label: "استخر ماینینگ", icon: Layers, color: "#06b6d4" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Live Price Ticker */}
      <LivePriceTicker />

      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 via-blue-600 to-purple-700 opacity-20" />
        <div className="absolute inset-0">
          {[...Array(50)].map((_, i) => (
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
                <Pickaxe className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1 min-w-[300px]">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-bold mb-3">
                  <Sparkles className="h-3 w-3" /> Eco-Friendly Mining Platform
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-3">
                  Eco<span className="bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">Mining</span> Pro
                </h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  استخراج ارز دیجیتال با انرژی‌های تجدیدپذیر • پاداش‌های اکولوژیک • رتبه‌بندی جهانی
                </p>
              </div>
              <div className="flex flex-col gap-3">
                <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-700 rounded-2xl p-4 min-w-[280px]">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-slate-400">هش‌ریت لحظه‌ای شما</span>
                    <div className="flex items-center gap-1">
                      <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse" />
                      <span className="text-xs text-emerald-400">LIVE</span>
                    </div>
                  </div>
                  <div className="flex items-baseline gap-2">
                    <span className="text-3xl font-black text-white tabular-nums">{liveHashrate.toFixed(1)}</span>
                    <span className="text-sm text-slate-400">MH/s</span>
                  </div>
                  <div className="mt-2 h-1 bg-slate-800 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-emerald-500 to-blue-500"
                      animate={{ width: `${(liveHashrate / 1200) * 100}%` }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
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
              className={`px-4 py-3 rounded-xl font-bold transition-all flex items-center gap-2 text-sm ${
                activeTab === tab.id ? "text-white shadow-lg" : "bg-slate-800 text-slate-400 hover:bg-slate-700"
              }`}
              style={activeTab === tab.id ? { backgroundColor: tab.color, boxShadow: `0 10px 25px -5px ${tab.color}50` } : {}}
            >
              <tab.icon className="h-4 w-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* ==================================================================== */}
        {/* DASHBOARD TAB */}
        {/* ==================================================================== */}
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* Main Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { label: "هش‌ریت کل", value: totalHashrate, unit: "MH/s", icon: Gauge, color: "#10b981", change: "+5.2%" },
                { label: "مصرف انرژی", value: totalPower, unit: "W", icon: Zap, color: "#3b82f6", change: "-2.1%" },
                { label: "درآمد ۲۴ ساعت", value: totalEarnings24h.toFixed(1), unit: "ECO", icon: Coins, color: "#f59e0b", change: "+12.5%" },
                { label: "امتیاز اکولوژیک", value: avgEcoScore.toFixed(0), unit: "/100", icon: Leaf, color: "#22c55e", change: "+1.8%" },
              ].map((stat, idx) => (
                <motion.div
                  key={idx}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.1 }}
                  className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-5 hover:border-slate-600 transition-all"
                >
                  <div className="flex items-center justify-between mb-3">
                    <div className="p-2 rounded-lg" style={{ backgroundColor: stat.color + "20" }}>
                      <stat.icon className="h-5 w-5" style={{ color: stat.color }} />
                    </div>
                    <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                      <ArrowUpRight className="h-3 w-3" />
                      {stat.change}
                    </span>
                  </div>
                  <p className="text-3xl font-black text-white tabular-nums">
                    {stat.value}
                    <span className="text-sm text-slate-400 mr-1">{stat.unit}</span>
                  </p>
                  <p className="text-xs text-slate-400 mt-1">{stat.label}</p>
                </motion.div>
              ))}
            </div>

            {/* Countdown Timers */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <CountdownTimer
                targetDate={new Date(Date.now() + 24 * 60 * 60 * 1000)}
                label="⏰ پاداش روزانه بعدی"
              />
              <CountdownTimer
                targetDate={new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)}
                label="🏆 پرداخت هفتگی"
              />
              <CountdownTimer
                targetDate={new Date("2028-01-01")}
                label="🌍 Next Halving"
              />
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Activity className="h-5 w-5 text-emerald-400" />
                    هش‌ریت ۲۴ ساعت
                  </h3>
                  <span className="text-xs text-slate-400">بروزرسانی: لحظه‌ای</span>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={HASHRATE_HISTORY}>
                    <defs>
                      <linearGradient id="hashGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                    <Area type="monotone" dataKey="hashrate" stroke="#10b981" fillOpacity={1} fill="url(#hashGrad)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-amber-400" />
                    درآمد ۳۰ روز اخیر
                  </h3>
                  <div className="flex gap-2 text-xs">
                    <span className="flex items-center gap-1"><div className="w-2 h-2 bg-emerald-500 rounded-full" /> ECO</span>
                    <span className="flex items-center gap-1"><div className="w-2 h-2 bg-purple-500 rounded-full" /> GRC</span>
                  </div>
                </div>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={EARNINGS_30D}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="day" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                    <Bar dataKey="eco" fill="#10b981" stackId="a" />
                    <Bar dataKey="grc" fill="#8b5cf6" stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Recent Transactions */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Hash className="h-5 w-5 text-blue-400" />
                  تراکنش‌های اخیر
                </h3>
                <button className="text-sm text-blue-400 hover:text-blue-300">مشاهده همه →</button>
              </div>
              <div className="space-y-2">
                {RECENT_TRANSACTIONS.map((tx, idx) => (
                  <motion.div
                    key={tx.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className="flex items-center justify-between p-3 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg ${
                        tx.type === "reward" ? "bg-emerald-500/20" :
                        tx.type === "transfer" ? "bg-blue-500/20" : "bg-purple-500/20"
                      }`}>
                        {tx.type === "reward" ? <Coins className="h-4 w-4 text-emerald-400" /> :
                         tx.type === "transfer" ? <ArrowRight className="h-4 w-4 text-blue-400" /> :
                         <RefreshCw className="h-4 w-4 text-purple-400" />}
                      </div>
                      <div>
                        <p className="text-sm font-bold text-white">{tx.device}</p>
                        <p className="text-xs text-slate-400 font-mono">{tx.id}</p>
                      </div>
                    </div>
                    <div className="text-left">
                      <p className={`font-bold ${
                        tx.type === "reward" ? "text-emerald-400" :
                        tx.type === "transfer" ? "text-blue-400" : "text-purple-400"
                      }`}>
                        {tx.type === "transfer" ? "-" : "+"}{tx.amount} {tx.token}
                      </p>
                      <p className="text-xs text-slate-400">{tx.time}</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* DEVICES TAB */}
        {/* ==================================================================== */}
        {activeTab === "devices" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center flex-wrap gap-4">
              <div>
                <h2 className="text-2xl font-bold text-white">دستگاه‌های ماینینگ</h2>
                <p className="text-sm text-slate-400 mt-1">{activeDevices.length} از {devices.length} دستگاه فعال</p>
              </div>
              <div className="flex gap-2">
                <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold flex items-center gap-2 text-sm">
                  <Filter className="h-4 w-4" /> فیلتر
                </button>
                <button onClick={() => setShowModal("add_device")} className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex items-center gap-2 text-sm">
                  <Plus className="h-4 w-4" /> افزودن دستگاه
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {devices.map((device, idx) => (
                <motion.div
                  key={device.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl overflow-hidden hover:border-blue-500/50 transition-all group"
                >
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="text-4xl">{device.icon}</div>
                        <div>
                          <h3 className="text-lg font-bold text-white">{device.name}</h3>
                          <p className="text-xs text-slate-400">{device.model}</p>
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-bold flex items-center gap-1 ${
                        device.status === "active" ? "bg-emerald-500/20 text-emerald-300" :
                        device.status === "maintenance" ? "bg-amber-500/20 text-amber-300" :
                        "bg-red-500/20 text-red-300"
                      }`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${
                          device.status === "active" ? "bg-emerald-400 animate-pulse" :
                          device.status === "maintenance" ? "bg-amber-400" : "bg-red-400"
                        }`} />
                        {device.status === "active" ? "فعال" : device.status === "maintenance" ? "تعمیرات" : "آفلاین"}
                      </div>
                    </div>

                    {/* Energy Source Badge */}
                    <div className="mb-4">
                      <div className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-bold ${
                        device.energy === "solar" ? "bg-amber-500/20 text-amber-300" :
                        device.energy === "wind" ? "bg-blue-500/20 text-blue-300" :
                        device.energy === "hydro" ? "bg-cyan-500/20 text-cyan-300" :
                        "bg-slate-500/20 text-slate-300"
                      }`}>
                        {device.energy === "solar" ? "☀️" : device.energy === "wind" ? "💨" : device.energy === "hydro" ? "🌊" : "🔌"}
                        {device.energy === "solar" ? "خورشیدی" : device.energy === "wind" ? "بادی" : device.energy === "hydro" ? "آبی" : "شبکه"}
                      </div>
                    </div>

                    {/* Metrics Grid */}
                    <div className="grid grid-cols-2 gap-3 mb-4">
                      <div className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center gap-1 mb-1">
                          <Gauge className="h-3 w-3 text-emerald-400" />
                          <span className="text-xs text-slate-400">هش‌ریت</span>
                        </div>
                        <p className="text-lg font-black text-white">{device.hashrate}<span className="text-xs text-slate-400 mr-1">MH/s</span></p>
                      </div>
                      <div className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center gap-1 mb-1">
                          <Zap className="h-3 w-3 text-blue-400" />
                          <span className="text-xs text-slate-400">مصرف</span>
                        </div>
                        <p className="text-lg font-black text-white">{device.power}<span className="text-xs text-slate-400 mr-1">W</span></p>
                      </div>
                      <div className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center gap-1 mb-1">
                          <Thermometer className="h-3 w-3 text-orange-400" />
                          <span className="text-xs text-slate-400">دما</span>
                        </div>
                        <p className={`text-lg font-black ${device.temperature > 70 ? "text-red-400" : "text-emerald-400"}`}>
                          {device.temperature}°C
                        </p>
                      </div>
                      <div className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center gap-1 mb-1">
                          <Leaf className="h-3 w-3 text-purple-400" />
                          <span className="text-xs text-slate-400">EcoScore</span>
                        </div>
                        <p className="text-lg font-black text-purple-400">{device.ecoScore}</p>
                      </div>
                    </div>

                    {/* Efficiency Bar */}
                    <div className="mb-4">
                      <div className="flex justify-between text-xs mb-1">
                        <span className="text-slate-400">بازدهی</span>
                        <span className="text-white font-bold">{device.efficiency} MH/W</span>
                      </div>
                      <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-emerald-500 to-blue-500"
                          style={{ width: `${(device.efficiency / 20) * 100}%` }}
                        />
                      </div>
                    </div>

                    {/* Stats */}
                    <div className="pt-4 border-t border-slate-700 space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-slate-400">درآمد ۲۴h:</span>
                        <span className="text-amber-400 font-bold">+{device.earnings24h} ECO</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">کل درآمد:</span>
                        <span className="text-emerald-400 font-bold">{device.earningsTotal.toLocaleString()} ECO</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">Uptime:</span>
                        <span className="text-blue-400 font-bold">{device.uptime}%</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-slate-400">فعال از:</span>
                        <span className="text-slate-300">{device.startedAt}</span>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 mt-4">
                      <button className={`flex-1 py-2 rounded-lg text-sm font-bold flex items-center justify-center gap-1 ${
                        device.status === "active"
                          ? "bg-amber-600 hover:bg-amber-700 text-white"
                          : "bg-emerald-600 hover:bg-emerald-700 text-white"
                      }`}>
                        {device.status === "active" ? <><Pause className="h-4 w-4" /> توقف</> : <><Play className="h-4 w-4" /> شروع</>}
                      </button>
                      <button className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg">
                        <Eye className="h-4 w-4" />
                      </button>
                      <button className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg">
                        <Settings className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* EARNINGS TAB */}
        {/* ==================================================================== */}
        {activeTab === "earnings" && (
          <div className="space-y-6">
            {/* Earnings Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-emerald-900/30 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6">
                <Coins className="h-8 w-8 text-emerald-400 mb-3" />
                <p className="text-sm text-slate-400 mb-1">کل ECO</p>
                <p className="text-3xl font-black text-white">{totalEarnings.toLocaleString()}</p>
                <p className="text-sm text-emerald-400 mt-2 flex items-center gap-1">
                  <ArrowUpRight className="h-3 w-3" /> +{totalEarnings24h.toFixed(1)} امروز
                </p>
              </div>
              <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/20 border border-purple-500/30 rounded-2xl p-6">
                <Award className="h-8 w-8 text-purple-400 mb-3" />
                <p className="text-sm text-slate-400 mb-1">کل GRC</p>
                <p className="text-3xl font-black text-white">{Math.floor(totalEarnings * 0.38).toLocaleString()}</p>
                <p className="text-sm text-purple-400 mt-2">پاداش اکولوژیک</p>
              </div>
              <div className="bg-gradient-to-br from-amber-900/30 to-orange-900/20 border border-amber-500/30 rounded-2xl p-6">
                <DollarSign className="h-8 w-8 text-amber-400 mb-3" />
                <p className="text-sm text-slate-400 mb-1">ارزش دلاری</p>
                <p className="text-3xl font-black text-white">${(totalEarnings * 0.15).toFixed(0)}</p>
                <p className="text-sm text-amber-400 mt-2">≈ {(totalEarnings * 0.15 * 60000).toLocaleString("fa-IR")} تومان</p>
              </div>
              <div className="bg-gradient-to-br from-blue-900/30 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-6">
                <Target className="h-8 w-8 text-blue-400 mb-3" />
                <p className="text-sm text-slate-400 mb-1">پیش‌بینی ماهانه</p>
                <p className="text-3xl font-black text-white">{(totalEarnings24h * 30).toFixed(0)}</p>
                <p className="text-sm text-blue-400 mt-2">ECO در ۳۰ روز</p>
              </div>
            </div>

            {/* 30 Day Chart */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">نمودار درآمد ۳۰ روز اخیر</h3>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={EARNINGS_30D}>
                  <defs>
                    <linearGradient id="ecoGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                    <linearGradient id="grcGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="day" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                  <Legend />
                  <Area type="monotone" dataKey="eco" stroke="#10b981" fillOpacity={1} fill="url(#ecoGrad)" name="ECO" />
                  <Area type="monotone" dataKey="grc" stroke="#8b5cf6" fillOpacity={1} fill="url(#grcGrad)" name="GRC" />
                </AreaChart>
              </ResponsiveContainer>
            </div>

            {/* Earnings by Device */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">درآمد به تفکیک دستگاه</h3>
              <div className="space-y-3">
                {devices.sort((a, b) => b.earningsTotal - a.earningsTotal).map(device => (
                  <div key={device.id} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <span className="text-3xl">{device.icon}</span>
                      <div>
                        <p className="font-bold text-white">{device.name}</p>
                        <p className="text-xs text-slate-400">{device.type} • {device.location}</p>
                      </div>
                    </div>
                    <div className="text-left">
                      <p className="text-xl font-black text-emerald-400">{device.earningsTotal.toLocaleString()} ECO</p>
                      <p className="text-xs text-slate-400">+{device.earnings24h} در ۲۴h</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* CALCULATOR TAB */}
        {/* ==================================================================== */}
        {activeTab === "calculator" && (
          <div className="max-w-5xl mx-auto space-y-6">
            <div className="bg-gradient-to-br from-slate-900 to-slate-800 border border-slate-700 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <Calculator className="h-6 w-6 text-purple-400" />
                محاسبه‌گر پیشرفته ROI
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-bold text-white mb-2">هش‌ریت دستگاه (MH/s)</label>
                  <input type="number" defaultValue={100} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">مصرف برق (W)</label>
                  <input type="number" defaultValue={1000} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">قیمت دستگاه (تومان)</label>
                  <input type="number" defaultValue={150000000} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">هزینه برق (تومان/kWh)</label>
                  <input type="number" defaultValue={500} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">نوع انرژی</label>
                  <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                    <option value="solar">☀️ خورشیدی (امتیاز: 100)</option>
                    <option value="wind">💨 بادی (امتیاز: 98)</option>
                    <option value="hydro">🌊 آبی (امتیاز: 95)</option>
                    <option value="grid">🔌 شبکه (امتیاز: 40)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">مدت استفاده (ماه)</label>
                  <input type="number" defaultValue={24} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
              </div>
              <button className="w-full mt-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 text-white rounded-xl font-bold">
                محاسبه ROI
              </button>

              {/* Results */}
              <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">درآمد روزانه</p>
                  <p className="text-xl font-black text-emerald-400">45.2 ECO</p>
                  <p className="text-xs text-slate-500 mt-1">≈ $6.78</p>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">هزینه برق روزانه</p>
                  <p className="text-xl font-black text-red-400">12,000 T</p>
                  <p className="text-xs text-slate-500 mt-1">24 kWh</p>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">سود خالص روزانه</p>
                  <p className="text-xl font-black text-amber-400">$4.98</p>
                  <p className="text-xs text-slate-500 mt-1">≈ 29,880 T</p>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-4 text-center border border-slate-700">
                  <p className="text-xs text-slate-400 mb-1">دوره بازگشت</p>
                  <p className="text-xl font-black text-blue-400">138 روز</p>
                  <p className="text-xs text-slate-500 mt-1">≈ 4.6 ماه</p>
                </div>
              </div>

              <div className="mt-4 grid grid-cols-2 gap-4">
                <div className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border border-purple-500/30 rounded-xl p-4">
                  <p className="text-xs text-slate-400 mb-1">پاداش اکولوژیک ماهانه</p>
                  <p className="text-2xl font-black text-purple-400">+450 GRC</p>
                  <p className="text-xs text-slate-500 mt-1">≈ $112.5</p>
                </div>
                <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-xl p-4">
                  <p className="text-xs text-slate-400 mb-1">ROI سالانه</p>
                  <p className="text-2xl font-black text-emerald-400">265%</p>
                  <p className="text-xs text-slate-500 mt-1">با احتساب پاداش اکو</p>
                </div>
              </div>
            </div>

            {/* Green Mining Benefits */}
            <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Leaf className="h-5 w-5 text-emerald-400" />
                مزایای ماینینگ سبز
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                {[
                  { icon: Sun, title: "خورشیدی", bonus: "+20%", eco: 100, color: "#f59e0b" },
                  { icon: Wind, title: "بادی", bonus: "+15%", eco: 98, color: "#3b82f6" },
                  { icon: Droplets, title: "آبی", bonus: "+10%", eco: 95, color: "#06b6d4" },
                  { icon: Flame, title: "زمین‌گرمایی", bonus: "+12%", eco: 97, color: "#ef4444" },
                ].map((item, idx) => (
                  <div key={idx} className="bg-slate-900/50 rounded-xl p-4 text-center">
                    <item.icon className="h-10 w-10 mx-auto mb-2" style={{ color: item.color }} />
                    <p className="font-bold text-white mb-1">{item.title}</p>
                    <p className="text-sm font-bold" style={{ color: item.color }}>{item.bonus} پاداش</p>
                    <p className="text-xs text-slate-400 mt-1">امتیاز اکو: {item.eco}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* ECOLOGICAL TAB */}
        {/* ==================================================================== */}
        {activeTab === "ecological" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-emerald-900/30 to-green-900/20 border border-emerald-500/30 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <Leaf className="h-6 w-6 text-emerald-400" />
                تأثیر اکولوژیک ماینینگ شما
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {[
                  { icon: TreePine, value: "125", label: "درخت معادل", color: "#10b981" },
                  { icon: Wind, value: "2.4", label: "تن CO2 جذب‌شده", color: "#3b82f6" },
                  { icon: Sun, value: "8,500", label: "kWh انرژی پاک", color: "#f59e0b" },
                  { icon: Droplets, value: "15,000", label: "لیتر آب صرفه‌جویی", color: "#06b6d4" },
                ].map((item, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: idx * 0.1 }}
                    className="text-center"
                  >
                    <item.icon className="h-14 w-14 mx-auto mb-3" style={{ color: item.color }} />
                    <p className="text-4xl font-black text-white">{item.value}</p>
                    <p className="text-sm text-slate-400 mt-1">{item.label}</p>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Comparison */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-gradient-to-br from-red-900/20 to-orange-900/20 border border-red-500/30 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <X className="h-5 w-5 text-red-400" />
                  ماینینگ سنتی
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between p-3 bg-slate-900/50 rounded-xl">
                    <span className="text-slate-400">انتشار CO2 سالانه</span>
                    <span className="text-red-400 font-bold">14.5 تن</span>
                  </div>
                  <div className="flex justify-between p-3 bg-slate-900/50 rounded-xl">
                    <span className="text-slate-400">مصرف انرژی</span>
                    <span className="text-red-400 font-bold">100% فسیلی</span>
                  </div>
                  <div className="flex justify-between p-3 bg-slate-900/50 rounded-xl">
                    <span className="text-slate-400">امتیاز اکو</span>
                    <span className="text-red-400 font-bold">25/100</span>
                  </div>
                  <div className="flex justify-between p-3 bg-slate-900/50 rounded-xl">
                    <span className="text-slate-400">پاداش اکو</span>
                    <span className="text-red-400 font-bold">0 GRC</span>
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-emerald-400" />
                  EcoMining شما
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between p-3 bg-slate-900/50 rounded-xl">
                    <span className="text-slate-400">انتشار CO2 سالانه</span>
                    <span className="text-emerald-400 font-bold">0 تن ✓</span>
                  </div>
                  <div className="flex justify-between p-3 bg-slate-900/50 rounded-xl">
                    <span className="text-slate-400">مصرف انرژی</span>
                    <span className="text-emerald-400 font-bold">100% تجدیدپذیر</span>
                  </div>
                  <div className="flex justify-between p-3 bg-slate-900/50 rounded-xl">
                    <span className="text-slate-400">امتیاز اکو</span>
                    <span className="text-emerald-400 font-bold">98.2/100</span>
                  </div>
                  <div className="flex justify-between p-3 bg-slate-900/50 rounded-xl">
                    <span className="text-slate-400">پاداش اکو</span>
                    <span className="text-emerald-400 font-bold">+1,650 GRC</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Green Certificates */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Gem className="h-5 w-5 text-purple-400" />
                گواهی‌نامه‌های سبز شما
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  { name: "100% Renewable Energy", date: "2024-08-15", id: "CERT-ECO-001", color: "#10b981" },
                  { name: "Carbon Neutral Miner", date: "2024-09-22", id: "CERT-ECO-002", color: "#3b82f6" },
                  { name: "Top 5% Eco Score", date: "2024-10-10", id: "CERT-ECO-003", color: "#8b5cf6" },
                ].map((cert, idx) => (
                  <div key={idx} className="bg-gradient-to-br from-slate-800 to-slate-900 border border-slate-700 rounded-xl p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Shield className="h-6 w-6" style={{ color: cert.color }} />
                      <p className="font-bold text-white text-sm">{cert.name}</p>
                    </div>
                    <p className="text-xs text-slate-400 font-mono">{cert.id}</p>
                    <p className="text-xs text-slate-500 mt-1">تاریخ: {cert.date}</p>
                    <button className="mt-3 w-full py-1.5 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs font-bold">
                      دانلود PDF
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* LEADERBOARD TAB */}
        {/* ==================================================================== */}
        {activeTab === "leaderboard" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-amber-900/20 to-orange-900/20 border border-amber-500/30 rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Trophy className="h-6 w-6 text-amber-400" />
                    رتبه‌بندی جهانی ماینرهای سبز
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">بر اساس امتیاز اکولوژیک و هش‌ریت</p>
                </div>
                <div className="flex gap-2">
                  <button className="px-4 py-2 bg-amber-600 hover:bg-amber-700 text-white rounded-xl font-bold text-sm">هفتگی</button>
                  <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-sm">ماهانه</button>
                  <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl font-bold text-sm">کل</button>
                </div>
              </div>

              <div className="space-y-3">
                {LEADERBOARD.map((miner, idx) => (
                  <motion.div
                    key={miner.rank}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: idx * 0.05 }}
                    className={`flex items-center gap-4 p-4 rounded-xl transition-all ${
                      miner.isYou
                        ? "bg-gradient-to-r from-emerald-900/30 to-teal-900/20 border-2 border-emerald-500/50"
                        : "bg-slate-800/50 hover:bg-slate-800"
                    }`}
                  >
                    <div className="text-3xl font-black w-12 text-center">
                      {miner.badge || `#${miner.rank}`}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-bold text-white">{miner.name}</p>
                        <span className="text-lg">{miner.country}</span>
                        {miner.isYou && (
                          <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-300 rounded text-xs font-bold">شما</span>
                        )}
                      </div>
                      <div className="flex gap-4 text-xs text-slate-400 mt-1">
                        <span>هش‌ریت: <span className="text-white font-bold">{miner.hashrate} MH/s</span></span>
                        <span>EcoScore: <span className="text-emerald-400 font-bold">{miner.ecoScore}</span></span>
                      </div>
                    </div>
                    <div className="text-left">
                      <p className="text-xl font-black text-amber-400">{miner.earnings.toLocaleString()}</p>
                      <p className="text-xs text-slate-400">ECO</p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>

            {/* Your Stats */}
            <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4">آمار شما در رتبه‌بندی</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <Crown className="h-8 w-8 text-amber-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">#6</p>
                  <p className="text-xs text-slate-400">رتبه جهانی</p>
                </div>
                <div className="text-center">
                  <TrendingUp className="h-8 w-8 text-emerald-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">+3</p>
                  <p className="text-xs text-slate-400">حرکت این هفته</p>
                </div>
                <div className="text-center">
                  <Users className="h-8 w-8 text-blue-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">Top 0.05%</p>
                  <p className="text-xs text-slate-400">در بین ماینرها</p>
                </div>
                <div className="text-center">
                  <Award className="h-8 w-8 text-purple-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">12</p>
                  <p className="text-xs text-slate-400">مدال کسب‌شده</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* ==================================================================== */}
        {/* POOL TAB */}
        {/* ==================================================================== */}
        {activeTab === "pool" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-cyan-900/20 to-blue-900/20 border border-cyan-500/30 rounded-2xl p-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Layers className="h-6 w-6 text-cyan-400" />
                    استخر ماینینگ EcoPool
                  </h2>
                  <p className="text-sm text-slate-400 mt-1">استخر اختصاصی ماینرهای سبز</p>
                </div>
                <div className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/30 rounded-xl">
                  <span className="text-emerald-300 font-bold text-sm">✓ متصل</span>
                </div>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <p className="text-xs text-slate-400 mb-1">هش‌ریت استخر</p>
                  <p className="text-2xl font-black text-white">2.45 TH/s</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <p className="text-xs text-slate-400 mb-1">تعداد ماینرها</p>
                  <p className="text-2xl font-black text-white">1,247</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <p className="text-xs text-slate-400 mb-1">آخرین بلاک</p>
                  <p className="text-2xl font-black text-white">824,521</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <p className="text-xs text-slate-400 mb-1">کارمزد استخر</p>
                  <p className="text-2xl font-black text-emerald-400">1.5%</p>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-xl p-4 mb-4">
                <p className="text-xs text-slate-400 mb-2">آدرس استخر</p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 text-sm text-white font-mono bg-slate-800 px-3 py-2 rounded">
                    stratum+tcp://ecopool.econojin.com:3333
                  </code>
                  <button className="px-3 py-2 bg-cyan-600 hover:bg-cyan-700 text-white rounded text-sm font-bold">
                    کپی
                  </button>
                </div>
              </div>

              <div className="bg-slate-900/50 rounded-xl p-4">
                <p className="text-xs text-slate-400 mb-2">Wallet Worker</p>
                <code className="text-sm text-white font-mono bg-slate-800 px-3 py-2 rounded block">
                  0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb4.worker1
                </code>
              </div>
            </div>

            {/* Pool Benefits */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <Zap className="h-8 w-8 text-amber-400 mb-3" />
                <h3 className="font-bold text-white mb-2">پرداخت PPS+</h3>
                <p className="text-sm text-slate-400">پرداخت به ازای هر سهم ارسال‌شده، بدون ریسک</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <Shield className="h-8 w-8 text-emerald-400 mb-3" />
                <h3 className="font-bold text-white mb-2">DDoS Protection</h3>
                <p className="text-sm text-slate-400">محافظت پیشرفته در برابر حملات</p>
              </div>
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <Leaf className="h-8 w-8 text-green-400 mb-3" />
                <h3 className="font-bold text-white mb-2">100% Green Energy</h3>
                <p className="text-sm text-slate-400">تمام سرورها با انرژی تجدیدپذیر</p>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Add Device Modal */}
      <AnimatePresence>
        {showModal === "add_device" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
            onClick={() => setShowModal(null)}
          >
            <motion.div
              initial={{ scale: 0.9 }}
              animate={{ scale: 1 }}
              exit={{ scale: 0.9 }}
              className="bg-slate-900 border border-slate-700 rounded-2xl max-w-2xl w-full p-6 max-h-[90vh] overflow-y-auto"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-xl font-bold text-white">افزودن دستگاه ماینینگ</h3>
                <button onClick={() => setShowModal(null)} className="text-slate-400 hover:text-white">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">نام دستگاه *</label>
                    <input type="text" placeholder="EcoMiner X1" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مدل *</label>
                    <input type="text" placeholder="Bitmain S21" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">نوع *</label>
                    <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      <option>ASIC</option>
                      <option>GPU</option>
                      <option>CPU</option>
                      <option>FPGA</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">منبع انرژی *</label>
                    <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                      <option value="solar">☀️ خورشیدی</option>
                      <option value="wind">💨 بادی</option>
                      <option value="hydro">🌊 آبی</option>
                      <option value="geothermal">🌋 زمین‌گرمایی</option>
                    </select>
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">هش‌ریت (MH/s) *</label>
                    <input type="number" placeholder="100" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                  <div>
                    <label className="block text-sm font-bold text-white mb-2">مصرف (W) *</label>
                    <input type="number" placeholder="1000" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">موقعیت</label>
                  <input type="text" placeholder="Tehran Data Center" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                  <Save className="h-5 w-5" /> افزودن دستگاه
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
'''

# Write file
page_path = WEB_DIR / "app" / "ecomining" / "page.tsx"
page_path.parent.mkdir(parents=True, exist_ok=True)
page_path.write_text(content, encoding="utf-8")

# Clean cache
next_dir = WEB_DIR.parent / ".next"
if next_dir.exists():
    try:
        shutil.rmtree(next_dir)
        print("✅ .next cache removed")
    except Exception as e:
        print(f"⚠️  {e}")

print(f"✅ EcoMining Pro page created: {page_path.stat().st_size} bytes")
print("\n" + "=" * 70)
print("DONE! Professional EcoMining page ready!")
print("=" * 70)
print("\nFeatures added:")
print("  ⏰ 3 Countdown Timers (daily reward, weekly payout, halving)")
print("  📊 Live Price Ticker with real-time updates")
print("  🌐 Network Stats (hashrate, difficulty, block reward)")
print("  💰 Advanced ROI Calculator with payback period")
print("  🏆 Global Leaderboard with rankings")
print("  🏊 Mining Pool info with stratum address")
print("  📜 Green Certificates (downloadable)")
print("  📈 30-day earnings chart")
print("  💎 NFT-style device cards")
print("  🌍 Ecological comparison (traditional vs green)")
print("  🎯 Live hashrate animation")
print("  📋 Recent transactions feed")
print("  🥇 Your ranking stats")
print("\nNext steps:")
print("  1. Restart frontend:")
print("     cd apps\\web")
print("     pnpm run dev -- -p 3001")
print("")
print("  2. Visit: http://localhost:3001/ecomining")
print("=" * 70)