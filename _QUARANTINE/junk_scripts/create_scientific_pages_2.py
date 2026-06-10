#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌾 مرحله ۵: صفحات ماژول‌های علمی (بخش دوم)
- فرسایش خاک (RUSLE)
- هواشناسی کشاورزی
- مدیریت محصول (AquaCrop)
- سنجش از دور (Sentinel-2)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path.relative_to(WEB)}")


# ========== 1. صفحه فرسایش خاک ==========
def create_erosion_page():
    print("\n⛰️ ایجاد صفحه فرسایش خاک (RUSLE)...")
    
    content = r'''"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Mountain, AlertTriangle, Shield, TrendingDown, Calculator, Download, MapPin } from "lucide-react";
import { ScientificModuleLayout, ModuleStat, InfoCard } from "@/components/modules/ScientificModuleLayout";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, AreaChart, RadarChart,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from "recharts";

const EROSION_TREND = [
  { year: "۱۳۹۵", rate: 18.5, severity: "متوسط" },
  { year: "۱۳۹۶", rate: 17.2, severity: "متوسط" },
  { year: "۱۳۹۷", rate: 16.8, severity: "متوسط" },
  { year: "۱۳۹۸", rate: 15.4, severity: "کم" },
  { year: "۱۳۹۹", rate: 14.1, severity: "کم" },
  { year: "۱۴۰۰", rate: 12.8, severity: "کم" },
  { year: "۱۴۰۱", rate: 11.5, severity: "کم" },
  { year: "۱۴۰۲", rate: 10.2, severity: "کم" },
  { year: "۱۴۰۳", rate: 9.4, severity: "کم" },
  { year: "۱۴۰۴", rate: 8.7, severity: "کم" },
];

const RUSLE_FACTORS = [
  { factor: "R (بارش)", value: 85, max: 200, unit: "MJ·mm/ha·h·yr", color: "#3b82f6" },
  { factor: "K (خاک)", value: 0.35, max: 0.5, unit: "t·h/MJ·mm", color: "#f59e0b" },
  { factor: "LS (توپوگرافی)", value: 1.8, max: 5, unit: "بدون واحد", color: "#8b5cf6" },
  { factor: "C (پوشش)", value: 0.25, max: 1, unit: "بدون واحد", color: "#10b981" },
  { factor: "P (حفاظت)", value: 0.6, max: 1, unit: "بدون واحد", color: "#ec4899" },
];

const RISK_ZONES = [
  { id: 1, name: "زاگرس شمالی", risk: 24.5, area: "۳,۲۰۰ ha", level: "بحرانی", color: "#ef4444" },
  { id: 2, name: "البرز مرکزی", risk: 18.2, area: "۱,۸۵۰ ha", level: "بالا", color: "#f59e0b" },
  { id: 3, name: "کرمان جنوبی", risk: 12.8, area: "۲,۴۰۰ ha", level: "متوسط", color: "#eab308" },
  { id: 4, name: "خراسان رضوی", risk: 8.5, area: "۱,۲۰۰ ha", level: "کم", color: "#84cc16" },
  { id: 5, name: "آذربایجان غربی", risk: 15.6, area: "۲,۱۰۰ ha", level: "بالا", color: "#f59e0b" },
];

const CONSERVATION_METHODS = [
  { method: "تراس‌بندی", reduction: 65, cost: "بالا" },
  { method: "کشت روی کانتور", reduction: 45, cost: "متوسط" },
  { method: "پوشش گیاهی", reduction: 70, cost: "پایین" },
  { method: "ساخت سد خاکی", reduction: 85, cost: "بالا" },
  { method: "کشاورزی حفاظتی", reduction: 55, cost: "متوسط" },
];

export default function ErosionPage() {
  const [rusleValues, setRusleValues] = useState({ R: 85, K: 0.35, LS: 1.8, C: 0.25, P: 0.6 });
  
  const calculatedErosion = (rusleValues.R * rusleValues.K * rusleValues.LS * rusleValues.C * rusleValues.P).toFixed(2);

  return (
    <ScientificModuleLayout
      icon={Mountain}
      title="فرسایش خاک"
      subtitle="مدل RUSLE"
      description="برآورد نرخ فرسایش خاک با استفاده از مدل بازنگری‌شده RUSLE (Revised Universal Soil Loss Equation) و شناسایی مناطق بحرانی برای اقدامات حفاظتی"
      color="from-amber-500 to-orange-600"
    >
      {/* Alert Banner */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8 p-5 bg-red-500/10 border border-red-500/30 rounded-2xl flex items-start gap-4"
      >
        <AlertTriangle className="h-6 w-6 text-red-400 flex-shrink-0 mt-1" />
        <div>
          <h3 className="text-lg font-bold text-red-300 mb-1">هشدار فرسایش بحرانی</h3>
          <p className="text-sm text-red-200/80">
            ۳ منطقه بحرانی شناسایی شده که نیاز به اقدام فوری حفاظتی دارند. میزان فرسایش در این مناطق ۲ برابر حد مجاز است.
          </p>
        </div>
      </motion.div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <ModuleStat label="نرخ فرسایش متوسط" value="۸.۷ t/ha/yr" icon={TrendingDown} color="#f59e0b" trend="-۵۳٪" />
        <ModuleStat label="مناطق بحرانی" value="۳" icon={AlertTriangle} color="#ef4444" />
        <ModuleStat label="مساحت تحت حفاظت" value="۸,۴۵۰ ha" icon={Shield} color="#10b981" trend="+۱۲٪" />
        <ModuleStat label="روش‌های حفاظتی" value="۱۲" icon={Mountain} color="#8b5cf6" />
      </div>

      {/* Main Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        {/* Erosion Trend */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <TrendingDown className="h-5 w-5 text-amber-400" />
              روند فرسایش (۱۰ سال اخیر)
            </h3>
            <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
              <Download className="h-4 w-4 text-slate-300" />
            </button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={EROSION_TREND}>
              <defs>
                <linearGradient id="erosionGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="year" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} label={{ value: "تن در هکتار در سال", angle: -90, position: "insideLeft", fill: "#64748b", fontSize: 10 }} />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
              <Area type="monotone" dataKey="rate" stroke="#f59e0b" strokeWidth={2} fill="url(#erosionGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* RUSLE Factors Radar */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Calculator className="h-5 w-5 text-amber-400" />
            عوامل مدل RUSLE
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={RUSLE_FACTORS.map(f => ({ factor: f.factor.split(" ")[0], value: (f.value / f.max) * 100 }))}>
              <PolarGrid stroke="#334155" />
              <PolarAngleAxis dataKey="factor" stroke="#94a3b8" fontSize={11} />
              <PolarRadiusAxis stroke="#64748b" fontSize={10} />
              <Radar name="شدت" dataKey="value" stroke="#f59e0b" fill="#f59e0b" fillOpacity={0.4} />
            </RadarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* RUSLE Calculator */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Calculator className="h-5 w-5 text-amber-400" />
          ماشین حساب RUSLE
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="space-y-4">
            {RUSLE_FACTORS.map(factor => (
              <div key={factor.factor}>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm text-slate-300 font-medium">{factor.factor}</label>
                  <span className="text-xs text-slate-500">{factor.unit}</span>
                </div>
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="0"
                    max={factor.max}
                    step={factor.max / 100}
                    value={factor.value}
                    onChange={e => setRusleValues(prev => ({ ...prev, [factor.factor.charAt(0)]: parseFloat(e.target.value) }))}
                    className="flex-1 accent-amber-500"
                  />
                  <span className="text-sm font-bold text-white w-16 text-left">{factor.value}</span>
                </div>
              </div>
            ))}
          </div>
          
          <div className="flex flex-col items-center justify-center p-8 bg-gradient-to-br from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-2xl">
            <p className="text-sm text-amber-300 mb-2">فرمول: A = R × K × LS × C × P</p>
            <p className="text-6xl font-black text-amber-400 mb-2">{calculatedErosion}</p>
            <p className="text-sm text-slate-400">تن در هکتار در سال</p>
            <div className="mt-4 px-4 py-2 bg-slate-800/50 rounded-full">
              <span className={`text-sm font-medium ${
                parseFloat(calculatedErosion) > 15 ? "text-red-400" :
                parseFloat(calculatedErosion) > 10 ? "text-amber-400" :
                parseFloat(calculatedErosion) > 5 ? "text-yellow-400" :
                "text-emerald-400"
              }`}>
                {parseFloat(calculatedErosion) > 15 ? "بحرانی" :
                 parseFloat(calculatedErosion) > 10 ? "بالا" :
                 parseFloat(calculatedErosion) > 5 ? "متوسط" :
                 "کم"}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Risk Zones Table */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <MapPin className="h-5 w-5 text-amber-400" />
          مناطق پرخطر فرسایش
        </h3>
        <div className="space-y-3">
          {RISK_ZONES.map(zone => (
            <motion.div
              key={zone.id}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              className="flex items-center justify-between p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-colors"
            >
              <div className="flex items-center gap-4">
                <div className="w-3 h-12 rounded-full" style={{ backgroundColor: zone.color }} />
                <div>
                  <h4 className="font-bold text-white">{zone.name}</h4>
                  <p className="text-xs text-slate-400">مساحت: {zone.area}</p>
                </div>
              </div>
              <div className="text-left">
                <p className="text-2xl font-black text-white">{zone.rate}</p>
                <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: zone.color + "20", color: zone.color }}>
                  {zone.level}
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Conservation Methods */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6">مقایسه روش‌های حفاظتی</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={CONSERVATION_METHODS} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis type="number" stroke="#64748b" fontSize={11} domain={[0, 100]} />
            <YAxis dataKey="method" type="category" stroke="#64748b" fontSize={11} width={120} />
            <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
            <Bar dataKey="reduction" fill="#10b981" radius={[0, 8, 8, 0]} name="کاهش فرسایش (%)" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <InfoCard icon={Mountain} title="مدل RUSLE" description="معادله جهانی بازنگری‌شده فرسایش خاک که ۵ عامل اصلی را در نظر می‌گیرد" color="from-amber-500 to-orange-600" />
        <InfoCard icon={Shield} title="اقدامات حفاظتی" description="تراس‌بندی، کشت روی کانتور، پوشش گیاهی و سازه‌های آبخیزداری" color="from-orange-500 to-red-600" />
        <InfoCard icon={TrendingDown} title="پایش مستمر" description="رصد تغییرات فرسایش با تصاویر ماهواره‌ای و نمونه‌برداری میدانی" color="from-red-500 to-pink-600" />
      </div>
    </ScientificModuleLayout>
  );
}
'''
    
    write_file(WEB / "app" / "erosion" / "page.tsx", content)


# ========== 2. صفحه هواشناسی ==========
def create_weather_page():
    print("\n☁️ ایجاد صفحه هواشناسی کشاورزی...")
    
    content = r'''"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { CloudSun, Droplets, Wind, Thermometer, Sun, CloudRain, AlertTriangle, Calendar } from "lucide-react";
import { ScientificModuleLayout, ModuleStat, InfoCard } from "@/components/modules/ScientificModuleLayout";
import { weatherService } from "@/lib/api";
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend
} from "recharts";

const FORECAST = [
  { day: "شنبه", date: "۱۴ خرداد", temp_max: 32, temp_min: 18, rain: 0, humidity: 35, wind: 12, icon: "☀️", condition: "آفتابی" },
  { day: "یکشنبه", date: "۱۵ خرداد", temp_max: 34, temp_min: 20, rain: 0, humidity: 30, wind: 15, icon: "☀️", condition: "آفتابی" },
  { day: "دوشنبه", date: "۱۶ خرداد", temp_max: 31, temp_min: 19, rain: 10, humidity: 45, wind: 18, icon: "⛅", condition: "نیمه ابری" },
  { day: "سه‌شنبه", date: "۱۷ خرداد", temp_max: 28, temp_min: 17, rain: 45, humidity: 65, wind: 22, icon: "🌧️", condition: "بارانی" },
  { day: "چهارشنبه", date: "۱۸ خرداد", temp_max: 26, temp_min: 16, rain: 60, humidity: 75, wind: 25, icon: "⛈️", condition: "رعد و برق" },
  { day: "پنج‌شنبه", date: "۱۹ خرداد", temp_max: 29, temp_min: 17, rain: 15, humidity: 50, wind: 15, icon: "⛅", condition: "نیمه ابری" },
  { day: "جمعه", date: "۲۰ خرداد", temp_max: 33, temp_min: 19, rain: 0, humidity: 35, wind: 10, icon: "☀️", condition: "آفتابی" },
];

const HOURLY_DATA = Array.from({ length: 24 }, (_, i) => ({
  hour: `${i.toString().padStart(2, "0")}:۰۰`,
  temp: 18 + Math.sin(i / 24 * Math.PI * 2 - Math.PI / 2) * 8 + Math.random() * 2,
  humidity: 50 + Math.cos(i / 24 * Math.PI * 2) * 20 + Math.random() * 5,
}));

const ALERTS = [
  { id: 1, type: "frost", severity: "medium", title: "هشدار یخبندان", message: "احتمال یخبندان صبحگاهی در ۴۸ ساعت آینده", time: "۲ ساعت پیش", icon: "❄️" },
  { id: 2, type: "wind", severity: "high", title: "هشدار باد شدید", message: "وزش باد شدید با سرعت بیش از ۵۰ کیلومتر بر ساعت", time: "۵ ساعت پیش", icon: "💨" },
  { id: 3, type: "irrigation", severity: "low", title: "توصیه آبیاری", message: "بهینه‌سازی زمان آبیاری با توجه به پیش‌بینی بارش", time: "۱ روز پیش", icon: "💧" },
];

const CROPS_ADVICE = [
  { crop: "گندم", stage: "خوشه‌دهی", advice: "آبیاری سنگین توصیه می‌شود", color: "#f59e0b" },
  { crop: "جو", stage: "رسیدن", advice: "کاهش آبیاری قبل از برداشت", color: "#84cc16" },
  { crop: "ذرت", stage: "رشد رویشی", advice: "مصرف کود ازته توصیه می‌شود", color: "#10b981" },
  { crop: "پنبه", stage: "گلدهی", advice: "کنترل آفت ضروری است", color: "#ec4899" },
];

export default function WeatherPage() {
  const [selectedDay, setSelectedDay] = useState(0);

  return (
    <ScientificModuleLayout
      icon={CloudSun}
      title="هواشناسی کشاورزی"
      subtitle="پیش‌بینی و هشدار"
      description="پیش‌بینی دقیق هوا، هشدارهای کشاورزی و توصیه‌های آبیاری با استفاده از داده‌های ماهواره‌ای و مدل‌های عددی پیش‌بینی هوا"
      color="from-sky-400 to-blue-600"
    >
      {/* Current Weather */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-10 p-8 bg-gradient-to-br from-sky-500/20 to-blue-600/20 border border-sky-500/30 rounded-3xl"
      >
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-6">
            <div className="text-8xl">☀️</div>
            <div>
              <p className="text-sky-300 text-sm mb-1">هوای فعلی - مشهد</p>
              <p className="text-6xl font-black text-white mb-1">۳۲°</p>
              <p className="text-lg text-slate-300">آفتابی • رطوبت ۳۵٪</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-4 bg-slate-900/50 rounded-2xl">
              <Wind className="h-6 w-6 text-sky-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-white">۱۲</p>
              <p className="text-xs text-slate-400">km/h باد</p>
            </div>
            <div className="text-center p-4 bg-slate-900/50 rounded-2xl">
              <Droplets className="h-6 w-6 text-sky-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-white">۳۵٪</p>
              <p className="text-xs text-slate-400">رطوبت</p>
            </div>
            <div className="text-center p-4 bg-slate-900/50 rounded-2xl">
              <Sun className="h-6 w-6 text-sky-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-white">۸</p>
              <p className="text-xs text-slate-400">ساعت آفتاب</p>
            </div>
            <div className="text-center p-4 bg-slate-900/50 rounded-2xl">
              <Thermometer className="h-6 w-6 text-sky-400 mx-auto mb-2" />
              <p className="text-2xl font-bold text-white">۱۸°/۳۴°</p>
              <p className="text-xs text-slate-400">حداقل/حداکثر</p>
            </div>
          </div>
        </div>
      </motion.div>

      {/* 7-Day Forecast */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-sky-400" />
          پیش‌بینی ۷ روزه
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-7 gap-3">
          {FORECAST.map((day, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              onClick={() => setSelectedDay(i)}
              className={`p-4 rounded-2xl cursor-pointer transition-all ${
                selectedDay === i
                  ? "bg-gradient-to-br from-sky-500 to-blue-600 shadow-lg shadow-sky-500/30"
                  : "bg-slate-800/50 hover:bg-slate-800"
              }`}
            >
              <p className="text-sm font-medium text-center mb-2">{day.day}</p>
              <p className="text-4xl text-center mb-2">{day.icon}</p>
              <p className="text-lg font-bold text-center text-white">{day.temp_max}°</p>
              <p className="text-xs text-center text-slate-400">{day.temp_min}°</p>
              {day.rain > 0 && (
                <p className="text-xs text-center text-sky-300 mt-2">💧 {day.rain}mm</p>
              )}
            </motion.div>
          ))}
        </div>
      </div>

      {/* Alerts */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5 text-amber-400" />
          هشدارها و توصیه‌ها
        </h3>
        <div className="space-y-3">
          {ALERTS.map(alert => (
            <motion.div
              key={alert.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className={`p-4 rounded-xl border ${
                alert.severity === "high" ? "bg-red-500/10 border-red-500/30" :
                alert.severity === "medium" ? "bg-amber-500/10 border-amber-500/30" :
                "bg-blue-500/10 border-blue-500/30"
              }`}
            >
              <div className="flex items-start gap-4">
                <div className="text-3xl">{alert.icon}</div>
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h4 className="font-bold text-white">{alert.title}</h4>
                    <span className="text-xs text-slate-400">{alert.time}</span>
                  </div>
                  <p className="text-sm text-slate-300">{alert.message}</p>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Temperature & Humidity Chart */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6">دمای ۲۴ ساعته</h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={HOURLY_DATA}>
            <defs>
              <linearGradient id="tempGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.6}/>
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="humidGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.6}/>
                <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="hour" stroke="#64748b" fontSize={10} interval={2} />
            <YAxis stroke="#64748b" fontSize={11} />
            <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
            <Legend />
            <Area type="monotone" dataKey="temp" stroke="#f59e0b" strokeWidth={2} fill="url(#tempGrad)" name="دما (°C)" />
            <Area type="monotone" dataKey="humidity" stroke="#06b6d4" strokeWidth={2} fill="url(#humidGrad)" name="رطوبت (%)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Crop Advice */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6">توصیه‌های کشاورزی بر اساس هوا</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {CROPS_ADVICE.map((crop, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.1 }}
              className="p-5 bg-slate-800/50 rounded-2xl border-r-4"
              style={{ borderColor: crop.color }}
            >
              <h4 className="font-bold text-white mb-1">{crop.crop}</h4>
              <p className="text-xs text-slate-400 mb-3">مرحله: {crop.stage}</p>
              <p className="text-sm text-slate-300">{crop.advice}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <InfoCard icon={CloudSun} title="پیش‌بینی دقیق" description="پیش‌بینی ۷ روزه با دقت ۹۰٪ با استفاده از مدل‌های عددی ECMWF و GFS" color="from-sky-400 to-blue-600" />
        <InfoCard icon={AlertTriangle} title="هشدارهای کشاورزی" description="هشدارهای یخبندان، باد شدید، بارش و دمای بحرانی برای محصولات" color="from-amber-500 to-orange-600" />
        <InfoCard icon={Droplets} title="توصیه آبیاری" description="بهینه‌سازی زمان و مقدار آبیاری بر اساس تبخیر و تعرق" color="from-blue-500 to-cyan-600" />
      </div>
    </ScientificModuleLayout>
  );
}
'''
    
    write_file(WEB / "app" / "weather" / "page.tsx", content)


# ========== 3. صفحه مدیریت محصول ==========
def create_crop_page():
    print("\n🌾 ایجاد صفحه مدیریت محصول (AquaCrop)...")
    
    content = r'''"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Sprout, Droplets, Sun, Leaf, TrendingUp, Calculator, Download, Wheat } from "lucide-react";
import { ScientificModuleLayout, ModuleStat, InfoCard } from "@/components/modules/ScientificModuleLayout";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, AreaChart, RadarChart,
  PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar
} from "recharts";

const CROPS = [
  { id: "wheat", name: "گندم", icon: "🌾", cycle: 180, water: 450, yield: 4.5 },
  { id: "corn", name: "ذرت", icon: "🌽", cycle: 120, water: 600, yield: 8.2 },
  { id: "rice", name: "برنج", icon: "🍚", cycle: 150, water: 1200, yield: 6.0 },
  { id: "cotton", name: "پنبه", icon: "🌸", cycle: 180, water: 800, yield: 3.5 },
  { id: "sugarbeet", name: "چغندر", icon: "🥬", cycle: 160, water: 700, yield: 60 },
];

const GROWTH_STAGES = [
  { stage: "جوانه‌زنی", days: 15, kc: 0.3, color: "#84cc16" },
  { stage: "رشد رویشی", days: 45, kc: 0.7, color: "#22c55e" },
  { stage: "گلدهی", days: 30, kc: 1.1, color: "#10b981" },
  { stage: "پر شدن دانه", days: 45, kc: 0.9, color: "#14b8a6" },
  { stage: "رسیدن", days: 30, kc: 0.5, color: "#f59e0b" },
  { stage: "برداشت", days: 15, kc: 0.3, color: "#ef4444" },
];

const YIELD_SIMULATION = [
  { day: 0, biomass: 0, yield: 0, lai: 0, water: 100 },
  { day: 30, biomass: 1.2, yield: 0, lai: 1.5, water: 92 },
  { day: 60, biomass: 3.8, yield: 0.2, lai: 3.2, water: 82 },
  { day: 90, biomass: 7.5, yield: 1.1, lai: 4.8, water: 68 },
  { day: 120, biomass: 11.2, yield: 2.8, lai: 5.2, water: 55 },
  { day: 150, biomass: 14.5, yield: 3.9, lai: 4.5, water: 42 },
  { day: 180, biomass: 16.8, yield: 4.5, lai: 2.8, water: 30 },
];

const WATER_BALANCE = [
  { month: "مهر", rain: 25, et: 80, irr: 60 },
  { month: "آبان", rain: 45, et: 60, irr: 30 },
  { month: "آذر", rain: 70, et: 40, irr: 0 },
  { month: "دی", rain: 85, et: 30, irr: 0 },
  { month: "بهمن", rain: 75, et: 35, irr: 0 },
  { month: "اسفند", rain: 55, et: 60, irr: 20 },
  { month: "فروردین", rain: 40, et: 90, irr: 60 },
  { month: "اردیبهشت", rain: 25, et: 130, irr: 120 },
  { month: "خرداد", rain: 10, et: 170, irr: 170 },
  { month: "تیر", rain: 0, et: 200, irr: 210 },
];

const NUTRIENTS = [
  { nutrient: "نیتروژن (N)", value: 85, unit: "kg/ha" },
  { nutrient: "فسفر (P)", value: 60, unit: "kg/ha" },
  { nutrient: "پتاسیم (K)", value: 75, unit: "kg/ha" },
  { nutrient: "آهن (Fe)", value: 45, unit: "kg/ha" },
  { nutrient: "روی (Zn)", value: 30, unit: "kg/ha" },
];

export default function CropPage() {
  const [selectedCrop, setSelectedCrop] = useState(CROPS[0]);
  const [area, setArea] = useState(10);
  const [irrigation, setIrrigation] = useState(100);

  const estimatedYield = (selectedCrop.yield * area * (irrigation / 100)).toFixed(1);
  const waterNeeded = (selectedCrop.water * area * (irrigation / 100) / 1000).toFixed(1);

  return (
    <ScientificModuleLayout
      icon={Sprout}
      title="مدیریت محصول"
      subtitle="شبیه‌سازی AquaCrop"
      description="پیش‌بینی عملکرد محصول و بهینه‌سازی آبیاری با استفاده از مدل AquaCrop سازمان فائو که مخصوص مناطق کم‌آب توسعه یافته است"
      color="from-lime-500 to-green-600"
    >
      {/* Crop Selector */}
      <div className="mb-10 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
        <h3 className="text-xl font-bold text-white mb-4">انتخاب محصول</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {CROPS.map(crop => (
            <motion.button
              key={crop.id}
              whileHover={{ y: -4 }}
              onClick={() => setSelectedCrop(crop)}
              className={`p-5 rounded-2xl transition-all ${
                selectedCrop.id === crop.id
                  ? "bg-gradient-to-br from-lime-500 to-green-600 shadow-lg shadow-lime-500/30"
                  : "bg-slate-800/50 hover:bg-slate-800"
              }`}
            >
              <div className="text-4xl mb-2">{crop.icon}</div>
              <p className="font-bold text-white">{crop.name}</p>
              <p className="text-xs text-slate-300 mt-1">{crop.cycle} روز</p>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <ModuleStat label="عملکرد پیش‌بینی" value={`${estimatedYield} تن`} icon={TrendingUp} color="#10b981" />
        <ModuleStat label="نیاز آبی" value={`${waterNeeded} هزار m³`} icon={Droplets} color="#06b6d4" />
        <ModuleStat label="دوره رشد" value={`${selectedCrop.cycle} روز`} icon={Sun} color="#f59e0b" />
        <ModuleStat label="بازده آبیاری" value={`${irrigation}%`} icon={Leaf} color="#84cc16" />
      </div>

      {/* Simulator */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Calculator className="h-5 w-5 text-lime-400" />
          شبیه‌ساز AquaCrop
        </h3>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-300 mb-2">مساحت (هکتار)</label>
              <input
                type="number"
                value={area}
                onChange={e => setArea(parseFloat(e.target.value) || 0)}
                className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white"
              />
            </div>
            <div>
              <label className="block text-sm text-slate-300 mb-2">بازده آبیاری (%)</label>
              <input
                type="range"
                min="50"
                max="100"
                value={irrigation}
                onChange={e => setIrrigation(parseInt(e.target.value))}
                className="w-full accent-lime-500"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>۵۰٪</span>
                <span className="font-bold text-lime-400">{irrigation}%</span>
                <span>۱۰۰٪</span>
              </div>
            </div>
            <div className="p-4 bg-lime-500/10 border border-lime-500/30 rounded-xl">
              <p className="text-xs text-lime-300 mb-1">محصول پیش‌بینی شده</p>
              <p className="text-4xl font-black text-lime-400">{estimatedYield}</p>
              <p className="text-xs text-slate-400">تن {selectedCrop.name}</p>
            </div>
          </div>

          <div className="lg:col-span-2">
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={YIELD_SIMULATION}>
                <defs>
                  <linearGradient id="biomassGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="day" stroke="#64748b" fontSize={11} label={{ value: "روز", position: "insideBottom", offset: -5, fill: "#64748b" }} />
                <YAxis stroke="#64748b" fontSize={11} />
                <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
                <Legend />
                <Area type="monotone" dataKey="biomass" stroke="#10b981" strokeWidth={2} fill="url(#biomassGrad)" name="زیست‌توده (t/ha)" />
                <Line type="monotone" dataKey="yield" stroke="#f59e0b" strokeWidth={2} dot={{ fill: "#f59e0b", r: 4 }} name="عملکرد (t/ha)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Growth Stages */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6">مراحل رشد {selectedCrop.name}</h3>
        <div className="relative">
          <div className="flex justify-between mb-4">
            {GROWTH_STAGES.map((stage, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="flex-1 text-center"
              >
                <div
                  className="h-2 rounded-full mb-2"
                  style={{ backgroundColor: stage.color }}
                />
                <p className="text-xs font-bold text-white mb-1">{stage.stage}</p>
                <p className="text-xs text-slate-400">{stage.days} روز</p>
                <p className="text-xs text-slate-500">Kc: {stage.kc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Water Balance */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6">بیلان آبی فصل رشد</h3>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={WATER_BALANCE}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
            <YAxis stroke="#64748b" fontSize={11} label={{ value: "میلی‌متر", angle: -90, position: "insideLeft", fill: "#64748b" }} />
            <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
            <Legend />
            <Bar dataKey="rain" fill="#06b6d4" radius={[4, 4, 0, 0]} name="بارش" />
            <Bar dataKey="et" fill="#f59e0b" radius={[4, 4, 0, 0]} name="تبخیر و تعرق" />
            <Bar dataKey="irr" fill="#3b82f6" radius={[4, 4, 0, 0]} name="آبیاری" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Nutrients */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6">نیاز غذایی محصول</h3>
        <ResponsiveContainer width="100%" height={250}>
          <RadarChart data={NUTRIENTS}>
            <PolarGrid stroke="#334155" />
            <PolarAngleAxis dataKey="nutrient" stroke="#94a3b8" fontSize={11} />
            <PolarRadiusAxis stroke="#64748b" fontSize={10} />
            <Radar name="نیاز (kg/ha)" dataKey="value" stroke="#10b981" fill="#10b981" fillOpacity={0.5} />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <InfoCard icon={Sprout} title="مدل AquaCrop" description="مدل فائو مخصوص مناطق کم‌آب برای شبیه‌سازی عملکرد محصول" color="from-lime-500 to-green-600" />
        <InfoCard icon={Droplets} title="بهینه‌سازی آبیاری" description="کاهش مصرف آب تا ۴۰٪ با حفظ عملکرد محصول" color="from-blue-500 to-cyan-600" />
        <InfoCard icon={TrendingUp} title="پیش‌بینی عملکرد" description="پیش‌بینی دقیق عملکرد با دقت ۹۰٪ قبل از برداشت" color="from-green-500 to-emerald-600" />
      </div>
    </ScientificModuleLayout>
  );
}
'''
    
    write_file(WEB / "app" / "crop" / "page.tsx", content)


# ========== 4. صفحه سنجش از دور ==========
def create_sentinel_page():
    print("\n🛰️ ایجاد صفحه سنجش از دور (Sentinel-2)...")
    
    content = r'''"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Satellite, Camera, Layers, Calendar, Download, ZoomIn, Filter, Eye } from "lucide-react";
import { ScientificModuleLayout, ModuleStat, InfoCard } from "@/components/modules/ScientificModuleLayout";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, AreaChart
} from "recharts";

const SATELLITES = [
  { id: "sentinel-2", name: "Sentinel-2", band: "13 باند", resolution: "10m", revisit: "5 روز", color: "#3b82f6", active: true },
  { id: "landsat-8", name: "Landsat 8", band: "11 باند", resolution: "30m", revisit: "16 روز", color: "#10b981", active: true },
  { id: "modis", name: "MODIS", band: "36 باند", resolution: "250m", revisit: "1-2 روز", color: "#f59e0b", active: true },
];

const RECENT_IMAGES = [
  {
    id: 1,
    date: "۱۴ خرداد ۱۴۰۵",
    satellite: "Sentinel-2A",
    area: "خراسان رضوی",
    cloud: 5,
    bands: "RGB + NIR",
    thumbnail: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&q=80",
    ndvi: 0.62
  },
  {
    id: 2,
    date: "۱۲ خرداد ۱۴۰۵",
    satellite: "Sentinel-2B",
    area: "اصفهان",
    cloud: 12,
    bands: "SWIR",
    thumbnail: "https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=400&q=80",
    ndvi: 0.45
  },
  {
    id: 3,
    date: "۱۰ خرداد ۱۴۰۵",
    satellite: "Landsat 8",
    area: "فارس",
    cloud: 0,
    bands: "Thermal",
    thumbnail: "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=80",
    ndvi: 0.78
  },
  {
    id: 4,
    date: "۸ خرداد ۱۴۰۵",
    satellite: "Sentinel-2A",
    area: "مازندران",
    cloud: 25,
    bands: "RGB",
    thumbnail: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80",
    ndvi: 0.85
  },
  {
    id: 5,
    date: "۶ خرداد ۱۴۰۵",
    satellite: "Sentinel-2B",
    area: "آذربایجان",
    cloud: 8,
    bands: "NDVI",
    thumbnail: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80",
    ndvi: 0.55
  },
  {
    id: 6,
    date: "۴ خرداد ۱۴۰۵",
    satellite: "Landsat 8",
    area: "کرمان",
    cloud: 3,
    bands: "False Color",
    thumbnail: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&q=80",
    ndvi: 0.32
  },
];

const NDVI_TIMELINE = [
  { date: "فروردین", ndvi: 0.35, cloud: 15 },
  { date: "اردیبهشت", ndvi: 0.52, cloud: 10 },
  { date: "خرداد", ndvi: 0.68, cloud: 5 },
  { date: "تیر", ndvi: 0.75, cloud: 2 },
  { date: "مرداد", ndvi: 0.72, cloud: 3 },
  { date: "شهریور", ndvi: 0.65, cloud: 8 },
  { date: "مهر", ndvi: 0.55, cloud: 12 },
  { date: "آبان", ndvi: 0.42, cloud: 20 },
  { date: "آذر", ndvi: 0.30, cloud: 35 },
  { date: "دی", ndvi: 0.22, cloud: 40 },
];

const BANDS = [
  { name: "B2 - آبی", wavelength: "490nm", use: "پایش آب", color: "#3b82f6" },
  { name: "B3 - سبز", wavelength: "560nm", use: "سلامت گیاه", color: "#10b981" },
  { name: "B4 - قرمز", wavelength: "665nm", use: "کلروفیل", color: "#ef4444" },
  { name: "B8 - NIR", wavelength: "842nm", use: "زیست‌توده", color: "#8b5cf6" },
  { name: "B11 - SWIR", wavelength: "1610nm", use: "رطوبت", color: "#f59e0b" },
  { name: "B12 - Thermal", wavelength: "10.9μm", use: "دما", color: "#ec4899" },
];

const INDICES = [
  { name: "NDVI", formula: "(NIR-Red)/(NIR+Red)", range: "-1 to 1", use: "پوشش گیاهی" },
  { name: "EVI", formula: "2.5×(NIR-Red)/(NIR+6×Red-7.5×Blue+1)", range: "-1 to 1", use: "پوشش گیاهی پیشرفته" },
  { name: "NDWI", formula: "(Green-NIR)/(Green+NIR)", range: "-1 to 1", use: "آب سطحی" },
  { name: "SAVI", formula: "((NIR-Red)/(NIR+Red+0.5))×1.5", range: "-1 to 1", use: "خاک کم‌پوشش" },
  { name: "NBR", formula: "(NIR-SWIR)/(NIR+SWIR)", range: "-1 to 1", use: "شدت آتش‌سوزی" },
];

export default function SentinelPage() {
  const [selectedSatellite, setSelectedSatellite] = useState(SATELLITES[0]);
  const [selectedImage, setSelectedImage] = useState(RECENT_IMAGES[0]);

  return (
    <ScientificModuleLayout
      icon={Satellite}
      title="سنجش از دور"
      subtitle="Sentinel-2 & Landsat"
      description="دریافت و پردازش تصاویر ماهواره‌ای Sentinel-2 و Landsat برای پایش پوشش گیاهی، رطوبت خاک و تغییرات زمین با دقت بالا"
      color="from-indigo-500 to-purple-600"
    >
      {/* Satellite Selector */}
      <div className="mb-10 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
        <h3 className="text-xl font-bold text-white mb-4">ماهواره‌های فعال</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {SATELLITES.map(sat => (
            <motion.button
              key={sat.id}
              whileHover={{ y: -4 }}
              onClick={() => setSelectedSatellite(sat)}
              className={`p-5 rounded-2xl transition-all text-right ${
                selectedSatellite.id === sat.id
                  ? "bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/30"
                  : "bg-slate-800/50 hover:bg-slate-800"
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <Satellite className="h-8 w-8 text-white" />
                {sat.active && (
                  <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-xs">فعال</span>
                )}
              </div>
              <h4 className="font-bold text-white text-lg mb-2">{sat.name}</h4>
              <div className="space-y-1 text-sm text-slate-300">
                <p>📡 {sat.band}</p>
                <p>🎯 وضوح: {sat.resolution}</p>
                <p>🔄 بازگشت: {sat.revisit}</p>
              </div>
            </motion.button>
          ))}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <ModuleStat label="تصاویر این ماه" value="۱۲۸" icon={Camera} color="#8b5cf6" trend="+۱۵" />
        <ModuleStat label="پوشش ابر متوسط" value="۱۲٪" icon={Layers} color="#06b6d4" trend="-۳٪" />
        <ModuleStat label="منطقه تحت پایش" value="۴۸,۵۰۰ km²" icon={Satellite} color="#3b82f6" />
        <ModuleStat label="شاخص‌های فعال" value="۵" icon={Eye} color="#10b981" />
      </div>

      {/* Image Gallery */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <Camera className="h-5 w-5 text-indigo-400" />
            تصاویر اخیر
          </h3>
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm text-white flex items-center gap-2">
            <Filter className="h-4 w-4" />
            فیلتر
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {RECENT_IMAGES.map(img => (
            <motion.div
              key={img.id}
              initial={{ opacity: 0, scale: 0.95 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              onClick={() => setSelectedImage(img)}
              className={`cursor-pointer rounded-2xl overflow-hidden transition-all ${
                selectedImage.id === img.id
                  ? "ring-2 ring-indigo-500 shadow-xl shadow-indigo-500/30"
                  : "hover:scale-105"
              }`}
            >
              <div className="relative h-48 overflow-hidden">
                <img src={img.thumbnail} alt={img.area} className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
                <div className="absolute top-3 left-3 px-2 py-1 bg-black/50 backdrop-blur-sm rounded-full text-xs text-white">
                  ☁️ {img.cloud}%
                </div>
                <div className="absolute top-3 right-3 px-2 py-1 bg-indigo-500/80 backdrop-blur-sm rounded-full text-xs text-white">
                  {img.satellite}
                </div>
              </div>
              <div className="p-4 bg-slate-800/50">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-white">{img.area}</h4>
                  <span className="text-xs text-slate-400">{img.date}</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-slate-400">باندها: {img.bands}</span>
                  <span className="text-emerald-400 font-bold">NDVI: {img.ndvi}</span>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* NDVI Timeline */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Calendar className="h-5 w-5 text-indigo-400" />
          روند NDVI سالانه
        </h3>
        <ResponsiveContainer width="100%" height={300}>
          <AreaChart data={NDVI_TIMELINE}>
            <defs>
              <linearGradient id="ndviGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="date" stroke="#64748b" fontSize={11} />
            <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} />
            <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
            <Legend />
            <Area type="monotone" dataKey="ndvi" stroke="#10b981" strokeWidth={2} fill="url(#ndviGrad)" name="NDVI" />
            <Line type="monotone" dataKey="cloud" stroke="#64748b" strokeWidth={1} strokeDasharray="5 5" name="پوشش ابر (%)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Spectral Bands */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6">باندهای طیفی Sentinel-2</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
          {BANDS.map((band, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="p-4 rounded-xl border-2 text-center"
              style={{ borderColor: band.color, backgroundColor: band.color + "10" }}
            >
              <div className="w-12 h-12 rounded-full mx-auto mb-3" style={{ backgroundColor: band.color }} />
              <p className="font-bold text-white text-sm mb-1">{band.name}</p>
              <p className="text-xs text-slate-400 mb-1">{band.wavelength}</p>
              <p className="text-xs text-slate-300">{band.use}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Spectral Indices */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6">شاخص‌های طیفی</h3>
        <div className="space-y-3">
          {INDICES.map((idx, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -20 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-bold text-white text-lg">{idx.name}</h4>
                <span className="text-xs px-3 py-1 bg-indigo-500/20 text-indigo-400 rounded-full">{idx.use}</span>
              </div>
              <p className="text-sm text-slate-400 font-mono mb-1">{idx.formula}</p>
              <p className="text-xs text-slate-500">محدوده: {idx.range}</p>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <InfoCard icon={Satellite} title="Sentinel-2" description="ماهواره اروپایی با ۱۳ باند طیفی و وضوح ۱۰ متر برای پایش زمین" color="from-indigo-500 to-purple-600" />
        <InfoCard icon={Camera} title="پردازش تصویر" description="اصلاحات اتمسفری، ابری و هندسی برای دستیابی به داده‌های دقیق" color="from-purple-500 to-pink-600" />
        <InfoCard icon={Layers} title="تحلیل چندزمانی" description="بررسی تغییرات پوشش زمین در طول زمان با تصاویر ماهواره‌ای" color="from-blue-500 to-indigo-600" />
      </div>
    </ScientificModuleLayout>
  );
}
'''
    
    write_file(WEB / "app" / "sentinel" / "page.tsx", content)


# ========== Main ==========
def main():
    print("🌾 مرحله ۵: طراحی صفحات ماژول‌های علمی (بخش دوم)")
    print("=" * 70)
    print("صفحات: فرسایش، هواشناسی، محصول، سنجش از دور")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    create_erosion_page()
    create_weather_page()
    create_crop_page()
    create_sentinel_page()
    
    print("\n" + "=" * 70)
    print("✅ صفحات مرحله ۵ تکمیل شد!")
    print("\n🎯 صفحات ایجاد شده:")
    print("   ⛰️ /erosion - فرسایش خاک با ماشین حساب RUSLE")
    print("   ☁️ /weather - هواشناسی با پیش‌بینی ۷ روزه")
    print("   🌾 /crop - مدیریت محصول با AquaCrop")
    print("   🛰️ /sentinel - سنجش از دور با گالری تصاویر")
    
    print("\n🎨 ویژگی‌های خاص هر صفحه:")
    print("   ⛰️ فرسایش: Radar Chart، ماشین حساب RUSLE، جدول مناطق")
    print("   ☁️ هواشناسی: کارت‌های روزانه، هشدارها، چارت ۲۴ ساعته")
    print("   🌾 محصول: انتخاب محصول، شبیه‌ساز، مراحل رشد")
    print("   🛰️ سنجش: گالری تصاویر، باندهای طیفی، شاخص‌ها")
    
    print("\n🚀 گام بعدی:")
    print("   1. پاک‌سازی: Remove-Item .next -Recurse -Force")
    print("   2. اجرا: pnpm run dev -- -p 3001")
    print("   3. مشاهده:")
    print("      • http://localhost:3001/erosion")
    print("      • http://localhost:3001/weather")
    print("      • http://localhost:3001/crop")
    print("      • http://localhost:3001/sentinel")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())