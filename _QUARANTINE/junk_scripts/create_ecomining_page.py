#!/usr/bin/env python3
"""Create complete EcoMining page"""
import shutil
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB_DIR = ROOT / "apps" / "web" / "src"

content = '''"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";
import {
  ArrowRight, Cpu, Zap, TrendingUp, DollarSign, Leaf,
  Plus, Edit, Trash2, Eye, Play, Pause, Settings,
  Activity, Gauge, Thermometer, Clock, Award, Coins,
  BarChart3, PieChart, Target, Shield, Wifi, Server,
  CheckCircle, AlertTriangle, X, Save, Calculator,
  Pickaxe, Battery, Wind, Droplets, Sun, TreePine
} from "lucide-react";

const ResponsiveContainer = dynamic(() => import("recharts").then(m => m.ResponsiveContainer), { ssr: false });
const LineChart = dynamic(() => import("recharts").then(m => m.LineChart), { ssr: false });
const Line = dynamic(() => import("recharts").then(m => m.Line), { ssr: false });
const AreaChart = dynamic(() => import("recharts").then(m => m.AreaChart), { ssr: false });
const Area = dynamic(() => import("recharts").then(m => m.Area), { ssr: false });
const BarChart = dynamic(() => import("recharts").then(m => m.BarChart), { ssr: false });
const Bar = dynamic(() => import("recharts").then(m => m.Bar), { ssr: false });
const XAxis = dynamic(() => import("recharts").then(m => m.XAxis), { ssr: false });
const YAxis = dynamic(() => import("recharts").then(m => m.YAxis), { ssr: false });
const CartesianGrid = dynamic(() => import("recharts").then(m => m.CartesianGrid), { ssr: false });
const Tooltip = dynamic(() => import("recharts").then(m => m.Tooltip), { ssr: false });
const Legend = dynamic(() => import("recharts").then(m => m.Legend), { ssr: false });

// Mock data for demo
const MINING_DEVICES = [
  {
    id: 1,
    name: "EcoMiner X1",
    type: "ASIC",
    hashrate: 120,
    power: 1200,
    status: "active",
    temperature: 65,
    earnings24h: 45.2,
    earningsTotal: 1250,
    location: "Data Center Tehran",
    uptime: 99.2,
    efficiency: 10.0,
    ecoScore: 95,
    image: "⛏️"
  },
  {
    id: 2,
    name: "GreenRig Pro",
    type: "GPU",
    hashrate: 85,
    power: 800,
    status: "active",
    temperature: 58,
    earnings24h: 32.8,
    earningsTotal: 890,
    location: "Solar Farm Isfahan",
    uptime: 98.5,
    efficiency: 10.6,
    ecoScore: 98,
    image: "🖥️"
  },
  {
    id: 3,
    name: "EcoNode Mini",
    type: "CPU",
    hashrate: 15,
    power: 150,
    status: "active",
    temperature: 45,
    earnings24h: 5.4,
    earningsTotal: 180,
    location: "Wind Farm Khorasan",
    uptime: 97.8,
    efficiency: 10.0,
    ecoScore: 99,
    image: "💻"
  },
  {
    id: 4,
    name: "HydroMiner V2",
    type: "ASIC",
    hashrate: 200,
    power: 1800,
    status: "maintenance",
    temperature: 72,
    earnings24h: 0,
    earningsTotal: 3420,
    location: "Hydro Plant Mazandaran",
    uptime: 95.2,
    efficiency: 11.1,
    ecoScore: 100,
    image: "🌊"
  },
  {
    id: 5,
    name: "SolarRig Alpha",
    type: "GPU",
    hashrate: 95,
    power: 900,
    status: "active",
    temperature: 52,
    earnings24h: 38.5,
    earningsTotal: 2100,
    location: "Solar Farm Yazd",
    uptime: 99.8,
    efficiency: 10.6,
    ecoScore: 100,
    image: "☀️"
  },
];

const EARNINGS_DATA = [
  { day: "Mon", eco: 120, grc: 45, usd: 18.5 },
  { day: "Tue", eco: 145, grc: 52, usd: 22.3 },
  { day: "Wed", eco: 132, grc: 48, usd: 20.1 },
  { day: "Thu", eco: 168, grc: 62, usd: 25.8 },
  { day: "Fri", eco: 155, grc: 58, usd: 24.2 },
  { day: "Sat", eco: 180, grc: 68, usd: 28.5 },
  { day: "Sun", eco: 175, grc: 65, usd: 27.8 },
];

const HASHRATE_DATA = [
  { time: "00:00", hashrate: 515 },
  { time: "04:00", hashrate: 520 },
  { time: "08:00", hashrate: 510 },
  { time: "12:00", hashrate: 525 },
  { time: "16:00", hashrate: 518 },
  { time: "20:00", hashrate: 522 },
  { time: "Now", hashrate: 515 },
];

export default function EcoMiningPage() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [devices, setDevices] = useState(MINING_DEVICES);
  const [showModal, setShowModal] = useState<string | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<any>(null);

  // Stats
  const totalHashrate = devices.filter(d => d.status === "active").reduce((sum, d) => sum + d.hashrate, 0);
  const totalPower = devices.filter(d => d.status === "active").reduce((sum, d) => sum + d.power, 0);
  const totalEarnings24h = devices.reduce((sum, d) => sum + d.earnings24h, 0);
  const totalEarnings = devices.reduce((sum, d) => sum + d.earningsTotal, 0);
  const activeDevices = devices.filter(d => d.status === "active").length;
  const avgTemp = devices.filter(d => d.status === "active").reduce((sum, d) => sum + d.temperature, 0) / activeDevices;
  const avgEcoScore = devices.reduce((sum, d) => sum + d.ecoScore, 0) / devices.length;

  const tabs = [
    { id: "dashboard", label: "داشبورد", icon: BarChart3, color: "#10b981" },
    { id: "devices", label: "دستگاه‌ها", icon: Cpu, color: "#3b82f6" },
    { id: "earnings", label: "درآمدها", icon: Coins, color: "#f59e0b" },
    { id: "calculator", label: "محاسبه‌گر سود", icon: Calculator, color: "#8b5cf6" },
    { id: "ecological", label: "تأثیر اکولوژیک", icon: Leaf, color: "#22c55e" },
  ];

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-emerald-600 via-blue-600 to-purple-700 opacity-20" />
        <div className="absolute inset-0">
          {[...Array(30)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-emerald-400 rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                opacity: [0.2, 1, 0.2],
                scale: [1, 1.5, 1],
              }}
              transition={{
                duration: Math.random() * 3 + 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            <div className="flex items-start gap-6">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-emerald-500 via-blue-500 to-purple-600 shadow-2xl shadow-emerald-500/30">
                <Pickaxe className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 bg-emerald-500/20 border border-emerald-500/30 rounded-full text-emerald-300 text-xs font-bold mb-3">
                  <Zap className="h-3 w-3" /> Eco-Friendly Mining
                </div>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-3">
                  Eco<span className="bg-gradient-to-r from-emerald-400 to-blue-400 bg-clip-text text-transparent">Mining</span>
                </h1>
                <p className="text-lg text-slate-300 max-w-3xl">
                  استخراج ارز دیجیتال با انرژی‌های تجدیدپذیر و پاداش‌های اکولوژیک
                  <br />
                  <span className="text-emerald-400 font-bold">هر چه سبزتر ماین کنید، بیشتر پاداش می‌گیرید!</span>
                </p>
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

        {/* Dashboard */}
        {activeTab === "dashboard" && (
          <div className="space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-gradient-to-br from-emerald-900/30 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-5">
                <Gauge className="h-6 w-6 mb-2 text-emerald-400" />
                <p className="text-2xl font-black text-white">{totalHashrate} <span className="text-sm text-slate-400">MH/s</span></p>
                <p className="text-xs text-slate-400">هش‌ریت کل</p>
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="bg-gradient-to-br from-blue-900/30 to-indigo-900/20 border border-blue-500/30 rounded-2xl p-5">
                <Zap className="h-6 w-6 mb-2 text-blue-400" />
                <p className="text-2xl font-black text-white">{totalPower} <span className="text-sm text-slate-400">W</span></p>
                <p className="text-xs text-slate-400">مصرف انرژی</p>
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="bg-gradient-to-br from-amber-900/30 to-orange-900/20 border border-amber-500/30 rounded-2xl p-5">
                <Coins className="h-6 w-6 mb-2 text-amber-400" />
                <p className="text-2xl font-black text-white">{totalEarnings24h.toFixed(1)}</p>
                <p className="text-xs text-slate-400">درآمد ۲۴ ساعت (ECO)</p>
              </motion.div>
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }} className="bg-gradient-to-br from-purple-900/30 to-pink-900/20 border border-purple-500/30 rounded-2xl p-5">
                <Leaf className="h-6 w-6 mb-2 text-purple-400" />
                <p className="text-2xl font-black text-white">{avgEcoScore.toFixed(0)}<span className="text-sm text-slate-400">/100</span></p>
                <p className="text-xs text-slate-400">امتیاز اکولوژیک</p>
              </motion.div>
            </div>

            {/* Charts */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <Activity className="h-5 w-5 text-emerald-400" />
                  هش‌ریت ۲۴ ساعت اخیر
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={HASHRATE_DATA}>
                    <defs>
                      <linearGradient id="hashrateGradient" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                    <Area type="monotone" dataKey="hashrate" stroke="#10b981" fillOpacity={1} fill="url(#hashrateGradient)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>

              <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
                <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                  <TrendingUp className="h-5 w-5 text-amber-400" />
                  درآمدهای هفتگی
                </h3>
                <ResponsiveContainer width="100%" height={250}>
                  <BarChart data={EARNINGS_DATA}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="day" stroke="#94a3b8" />
                    <YAxis stroke="#94a3b8" />
                    <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                    <Legend />
                    <Bar dataKey="eco" fill="#10b981" name="ECO" />
                    <Bar dataKey="grc" fill="#8b5cf6" name="GRC" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Active Devices Quick View */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                  <Cpu className="h-5 w-5 text-blue-400" />
                  وضعیت دستگاه‌ها
                </h3>
                <span className="text-sm text-slate-400">{activeDevices} از {devices.length} فعال</span>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {devices.slice(0, 3).map(device => (
                  <div key={device.id} className="bg-slate-800/50 rounded-xl p-4 border border-slate-700">
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <span className="text-2xl">{device.image}</span>
                        <div>
                          <p className="font-bold text-white text-sm">{device.name}</p>
                          <p className="text-xs text-slate-400">{device.type}</p>
                        </div>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${device.status === "active" ? "bg-emerald-400 animate-pulse" : "bg-amber-400"}`} />
                    </div>
                    <div className="grid grid-cols-2 gap-2 text-xs">
                      <div>
                        <p className="text-slate-400">هش‌ریت</p>
                        <p className="text-white font-bold">{device.hashrate} MH/s</p>
                      </div>
                      <div>
                        <p className="text-slate-400">دما</p>
                        <p className={`font-bold ${device.temperature > 70 ? "text-red-400" : "text-emerald-400"}`}>{device.temperature}°C</p>
                      </div>
                      <div>
                        <p className="text-slate-400">درآمد ۲۴h</p>
                        <p className="text-amber-400 font-bold">{device.earnings24h} ECO</p>
                      </div>
                      <div>
                        <p className="text-slate-400">Uptime</p>
                        <p className="text-blue-400 font-bold">{device.uptime}%</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Devices */}
        {activeTab === "devices" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-2xl font-bold text-white">دستگاه‌های ماینینگ</h2>
              <button onClick={() => setShowModal("add_device")} className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex items-center gap-2">
                <Plus className="h-5 w-5" /> افزودن دستگاه
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {devices.map((device, idx) => (
                <motion.div
                  key={device.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: idx * 0.05 }}
                  className="bg-slate-900/50 border border-slate-800 rounded-2xl overflow-hidden hover:border-blue-500/50 transition-all"
                >
                  <div className="p-6">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center gap-3">
                        <div className="text-4xl">{device.image}</div>
                        <div>
                          <h3 className="text-lg font-bold text-white">{device.name}</h3>
                          <p className="text-sm text-slate-400">{device.type} • {device.location}</p>
                        </div>
                      </div>
                      <div className={`px-2 py-1 rounded text-xs font-bold ${
                        device.status === "active" ? "bg-emerald-500/20 text-emerald-300" :
                        device.status === "maintenance" ? "bg-amber-500/20 text-amber-300" :
                        "bg-red-500/20 text-red-300"
                      }`}>
                        {device.status === "active" ? "فعال" : device.status === "maintenance" ? "تعمیرات" : "آفلاین"}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-3 mb-4">
                      <div className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Gauge className="h-4 w-4 text-emerald-400" />
                          <span className="text-xs text-slate-400">هش‌ریت</span>
                        </div>
                        <p className="text-lg font-black text-white">{device.hashrate} <span className="text-xs text-slate-400">MH/s</span></p>
                      </div>
                      <div className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Zap className="h-4 w-4 text-blue-400" />
                          <span className="text-xs text-slate-400">مصرف</span>
                        </div>
                        <p className="text-lg font-black text-white">{device.power} <span className="text-xs text-slate-400">W</span></p>
                      </div>
                      <div className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Thermometer className="h-4 w-4 text-orange-400" />
                          <span className="text-xs text-slate-400">دما</span>
                        </div>
                        <p className={`text-lg font-black ${device.temperature > 70 ? "text-red-400" : "text-emerald-400"}`}>
                          {device.temperature}°C
                        </p>
                      </div>
                      <div className="bg-slate-800/50 rounded-lg p-3">
                        <div className="flex items-center gap-2 mb-1">
                          <Leaf className="h-4 w-4 text-purple-400" />
                          <span className="text-xs text-slate-400">امتیاز اکو</span>
                        </div>
                        <p className="text-lg font-black text-purple-400">{device.ecoScore}</p>
                      </div>
                    </div>

                    <div className="pt-4 border-t border-slate-700 space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">درآمد ۲۴ ساعت:</span>
                        <span className="text-amber-400 font-bold">{device.earnings24h} ECO</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">کل درآمد:</span>
                        <span className="text-emerald-400 font-bold">{device.earningsTotal} ECO</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">Uptime:</span>
                        <span className="text-blue-400 font-bold">{device.uptime}%</span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-slate-400">بازدهی:</span>
                        <span className="text-white font-bold">{device.efficiency} MH/W</span>
                      </div>
                    </div>

                    <div className="flex gap-2 mt-4">
                      <button className="flex-1 py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold flex items-center justify-center gap-1">
                        {device.status === "active" ? <><Pause className="h-4 w-4" /> توقف</> : <><Play className="h-4 w-4" /> شروع</>}
                      </button>
                      <button className="p-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg">
                        <Settings className="h-4 w-4" />
                      </button>
                      <button className="p-2 bg-slate-800 hover:bg-slate-700 text-red-400 rounded-lg">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        )}

        {/* Earnings */}
        {activeTab === "earnings" && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-br from-emerald-900/30 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6">
                <Coins className="h-8 w-8 text-emerald-400 mb-3" />
                <p className="text-sm text-slate-400 mb-1">کل درآمد ECO</p>
                <p className="text-4xl font-black text-white">{totalEarnings.toLocaleString()}</p>
                <p className="text-sm text-emerald-400 mt-2">+{totalEarnings24h.toFixed(1)} در ۲۴ ساعت</p>
              </div>
              <div className="bg-gradient-to-br from-purple-900/30 to-pink-900/20 border border-purple-500/30 rounded-2xl p-6">
                <Award className="h-8 w-8 text-purple-400 mb-3" />
                <p className="text-sm text-slate-400 mb-1">کل درآمد GRC</p>
                <p className="text-4xl font-black text-white">{Math.floor(totalEarnings * 0.38).toLocaleString()}</p>
                <p className="text-sm text-purple-400 mt-2">پاداش اکولوژیک</p>
              </div>
              <div className="bg-gradient-to-br from-amber-900/30 to-orange-900/20 border border-amber-500/30 rounded-2xl p-6">
                <DollarSign className="h-8 w-8 text-amber-400 mb-3" />
                <p className="text-sm text-slate-400 mb-1">ارزش دلاری</p>
                <p className="text-4xl font-black text-white">${(totalEarnings * 0.15).toFixed(0)}</p>
                <p className="text-sm text-amber-400 mt-2">بر اساس قیمت فعلی</p>
              </div>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">نمودار درآمد ۳۰ روز اخیر</h3>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={[...EARNINGS_DATA, ...EARNINGS_DATA, ...EARNINGS_DATA, ...EARNINGS_DATA].slice(0, 30)}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="day" stroke="#94a3b8" />
                  <YAxis stroke="#94a3b8" />
                  <Tooltip contentStyle={{ backgroundColor: "#1e293b", border: "1px solid #334155" }} />
                  <Legend />
                  <Line type="monotone" dataKey="eco" stroke="#10b981" strokeWidth={2} name="ECO" />
                  <Line type="monotone" dataKey="grc" stroke="#8b5cf6" strokeWidth={2} name="GRC" />
                  <Line type="monotone" dataKey="usd" stroke="#f59e0b" strokeWidth={2} name="USD" />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">درآمد به تفکیک دستگاه</h3>
              <div className="space-y-3">
                {devices.map(device => (
                  <div key={device.id} className="flex items-center justify-between p-4 bg-slate-800/50 rounded-xl">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{device.image}</span>
                      <div>
                        <p className="font-bold text-white">{device.name}</p>
                        <p className="text-xs text-slate-400">{device.type} • {device.location}</p>
                      </div>
                    </div>
                    <div className="text-left">
                      <p className="text-lg font-black text-emerald-400">{device.earningsTotal} ECO</p>
                      <p className="text-xs text-slate-400">+{device.earnings24h} در ۲۴h</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Calculator */}
        {activeTab === "calculator" && (
          <div className="max-w-4xl mx-auto space-y-6">
            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <Calculator className="h-6 w-6 text-purple-400" />
                محاسبه‌گر سودآوری ماینینگ
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-bold text-white mb-2">هش‌ریت (MH/s)</label>
                  <input type="number" defaultValue={100} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">مصرف برق (W)</label>
                  <input type="number" defaultValue={1000} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">هزینه برق (تومان/kWh)</label>
                  <input type="number" defaultValue={500} className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">نوع انرژی</label>
                  <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                    <option value="solar">☀️ خورشیدی (امتیاز اکو: 100)</option>
                    <option value="wind">💨 بادی (امتیاز اکو: 98)</option>
                    <option value="hydro">🌊 آبی (امتیاز اکو: 95)</option>
                    <option value="grid">🔌 شبکه (امتیاز اکو: 40)</option>
                  </select>
                </div>
              </div>
              <button className="w-full mt-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:opacity-90 text-white rounded-xl font-bold">
                محاسبه سودآوری
              </button>

              <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-800/50 rounded-xl p-4 text-center">
                  <p className="text-xs text-slate-400 mb-1">درآمد روزانه</p>
                  <p className="text-xl font-black text-emerald-400">45.2 ECO</p>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-4 text-center">
                  <p className="text-xs text-slate-400 mb-1">هزینه برق</p>
                  <p className="text-xl font-black text-red-400">12,000 T</p>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-4 text-center">
                  <p className="text-xs text-slate-400 mb-1">سود خالص</p>
                  <p className="text-xl font-black text-amber-400">$1.8</p>
                </div>
                <div className="bg-slate-800/50 rounded-xl p-4 text-center">
                  <p className="text-xs text-slate-400 mb-1">پاداش اکو</p>
                  <p className="text-xl font-black text-purple-400">+15 GRC</p>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-emerald-900/20 to-teal-900/20 border border-emerald-500/30 rounded-2xl p-6">
              <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                <Leaf className="h-5 w-5 text-emerald-400" />
                مزایای ماینینگ سبز
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <Sun className="h-8 w-8 text-amber-400 mb-2" />
                  <p className="font-bold text-white mb-1">انرژی خورشیدی</p>
                  <p className="text-sm text-slate-400">۲۰٪ پاداش بیشتر + امتیاز اکو ۱۰۰</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <Wind className="h-8 w-8 text-blue-400 mb-2" />
                  <p className="font-bold text-white mb-1">انرژی بادی</p>
                  <p className="text-sm text-slate-400">۱۵٪ پاداش بیشتر + امتیاز اکو ۹۸</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <Droplets className="h-8 w-8 text-cyan-400 mb-2" />
                  <p className="font-bold text-white mb-1">انرژی آبی</p>
                  <p className="text-sm text-slate-400">۱۰٪ پاداش بیشتر + امتیاز اکو ۹۵</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Ecological Impact */}
        {activeTab === "ecological" && (
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-emerald-900/30 to-green-900/20 border border-emerald-500/30 rounded-2xl p-8">
              <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                <Leaf className="h-6 w-6 text-emerald-400" />
                تأثیر اکولوژیک ماینینگ شما
              </h2>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <TreePine className="h-12 w-12 text-emerald-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">125</p>
                  <p className="text-sm text-slate-400">درخت معادل</p>
                </div>
                <div className="text-center">
                  <Wind className="h-12 w-12 text-blue-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">2.4</p>
                  <p className="text-sm text-slate-400">تن CO2 جذب‌شده</p>
                </div>
                <div className="text-center">
                  <Sun className="h-12 w-12 text-amber-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">8,500</p>
                  <p className="text-sm text-slate-400">kWh انرژی پاک</p>
                </div>
                <div className="text-center">
                  <Droplets className="h-12 w-12 text-cyan-400 mx-auto mb-2" />
                  <p className="text-3xl font-black text-white">15,000</p>
                  <p className="text-sm text-slate-400">لیتر آب صرفه‌جویی</p>
                </div>
              </div>
            </div>

            <div className="bg-slate-900/50 border border-slate-800 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4">رتبه‌بندی اکولوژیک</h3>
              <div className="space-y-4">
                {devices.sort((a, b) => b.ecoScore - a.ecoScore).map((device, idx) => (
                  <div key={device.id} className="flex items-center gap-4 p-4 bg-slate-800/50 rounded-xl">
                    <div className="text-2xl font-black text-slate-400 w-8">#{idx + 1}</div>
                    <span className="text-3xl">{device.image}</span>
                    <div className="flex-1">
                      <p className="font-bold text-white">{device.name}</p>
                      <p className="text-xs text-slate-400">{device.location}</p>
                    </div>
                    <div className="text-left">
                      <p className="text-2xl font-black text-emerald-400">{device.ecoScore}</p>
                      <p className="text-xs text-slate-400">امتیاز اکو</p>
                    </div>
                    <div className="w-32">
                      <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-gradient-to-r from-emerald-500 to-teal-500"
                          style={{ width: `${device.ecoScore}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="bg-gradient-to-br from-purple-900/20 to-pink-900/20 border border-purple-500/30 rounded-2xl p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Award className="h-5 w-5 text-purple-400" />
                پاداش‌های اکولوژیک شما
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <p className="text-sm text-slate-400 mb-1">پاداش انرژی پاک</p>
                  <p className="text-2xl font-black text-emerald-400">+850 GRC</p>
                  <p className="text-xs text-slate-500">استفاده از ۱۰۰٪ انرژی تجدیدپذیر</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <p className="text-sm text-slate-400 mb-1">پاداش کاهش کربن</p>
                  <p className="text-2xl font-black text-blue-400">+480 GRC</p>
                  <p className="text-xs text-slate-500">جذب ۲.۴ تن CO2</p>
                </div>
                <div className="bg-slate-900/50 rounded-xl p-4">
                  <p className="text-sm text-slate-400 mb-1">پاداش بهره‌وری</p>
                  <p className="text-2xl font-black text-amber-400">+320 GRC</p>
                  <p className="text-xs text-slate-500">بازدهی بالای ۱۰ MH/W</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </section>

      {/* Add Device Modal */}
      {showModal === "add_device" && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50 flex items-center justify-center p-4"
          onClick={() => setShowModal(null)}
        >
          <motion.div
            initial={{ scale: 0.9 }}
            animate={{ scale: 1 }}
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
                  <input type="text" placeholder="مثال: EcoMiner X1" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">نوع دستگاه *</label>
                  <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                    <option value="ASIC">ASIC</option>
                    <option value="GPU">GPU</option>
                    <option value="CPU">CPU</option>
                    <option value="FPGA">FPGA</option>
                  </select>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-bold text-white mb-2">هش‌ریت (MH/s) *</label>
                  <input type="number" placeholder="100" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
                <div>
                  <label className="block text-sm font-bold text-white mb-2">مصرف برق (W) *</label>
                  <input type="number" placeholder="1000" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
                </div>
              </div>
              <div>
                <label className="block text-sm font-bold text-white mb-2">موقعیت مکانی</label>
                <input type="text" placeholder="مثال: Data Center Tehran" className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white" />
              </div>
              <div>
                <label className="block text-sm font-bold text-white mb-2">منبع انرژی</label>
                <select className="w-full px-4 py-2 bg-slate-800 border border-slate-700 rounded-xl text-white">
                  <option value="solar">☀️ خورشیدی</option>
                  <option value="wind">💨 بادی</option>
                  <option value="hydro">🌊 آبی</option>
                  <option value="geothermal">🌋 زمین‌گرمایی</option>
                  <option value="grid">🔌 شبکه برق</option>
                </select>
              </div>
              <button className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-bold flex items-center justify-center gap-2">
                <Save className="h-5 w-5" /> افزودن دستگاه
              </button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
}
'''

# Write the file
page_path = WEB_DIR / "app" / "ecomining" / "page.tsx"
page_path.parent.mkdir(parents=True, exist_ok=True)
page_path.write_text(content, encoding="utf-8")

# Clean Next.js cache
next_dir = WEB_DIR.parent / ".next"
if next_dir.exists():
    try:
        import shutil
        shutil.rmtree(next_dir)
        print("✅ .next cache removed")
    except Exception as e:
        print(f"⚠️  Cache cleanup: {e}")

print(f"✅ EcoMining page created: {page_path.relative_to(ROOT)}")
print(f"   Size: {page_path.stat().st_size} bytes")
print("\n" + "=" * 70)
print("DONE! EcoMining page is ready!")
print("=" * 70)
print("\nNext steps:")
print("  1. Restart frontend:")
print("     cd apps\\web")
print("     pnpm run dev -- -p 3001")
print("")
print("  2. Visit: http://localhost:3001/ecomining")
print("=" * 70)