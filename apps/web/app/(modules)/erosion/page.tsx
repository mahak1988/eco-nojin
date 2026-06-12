"use client";

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
      citizenModuleType="erosion"
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
            <button onClick={() => console.log("Button clicked")}  className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
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