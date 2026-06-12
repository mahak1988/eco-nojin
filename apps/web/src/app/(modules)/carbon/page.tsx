"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { TreePine, Leaf, TrendingUp, Calculator, Download, BarChart3 } from "lucide-react";
import { ScientificModuleLayout, ModuleStat, InfoCard } from "@/components/modules/ScientificModuleLayout";
import { carbonService } from "@/lib/api";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, AreaChart
} from "recharts";

const CARBON_TREND = [
  { year: "۱۳۹۵", soc: 2.1, litter: 0.8, total: 2.9 },
  { year: "۱۳۹۶", soc: 2.3, litter: 0.9, total: 3.2 },
  { year: "۱۳۹۷", soc: 2.5, litter: 1.0, total: 3.5 },
  { year: "۱۳۹۸", soc: 2.8, litter: 1.1, total: 3.9 },
  { year: "۱۳۹۹", soc: 3.1, litter: 1.2, total: 4.3 },
  { year: "۱۴۰۰", soc: 3.4, litter: 1.3, total: 4.7 },
  { year: "۱۴۰۱", soc: 3.7, litter: 1.4, total: 5.1 },
  { year: "۱۴۰۲", soc: 4.0, litter: 1.5, total: 5.5 },
  { year: "۱۴۰۳", soc: 4.3, litter: 1.6, total: 5.9 },
  { year: "۱۴۰۴", soc: 4.6, litter: 1.7, total: 6.3 },
];

const LAND_USE = [
  { type: "جنگل", carbon: 150, area: "۲,۵۰۰ ha", color: "#059669" },
  { type: "مرتع", carbon: 45, area: "۵,۸۰۰ ha", color: "#10b981" },
  { type: "کشاورزی", carbon: 28, area: "۳,۲۰۰ ha", color: "#84cc16" },
  { type: "بایر", carbon: 12, area: "۹۵۰ ha", color: "#f59e0b" },
];

export default function CarbonPage() {
  return (
    <ScientificModuleLayout
      icon={TreePine}
      title="کربن خاک"
      subtitle="مدل RothC"
      description="پیش‌بینی دینامیک کربن آلی خاک و ارزیابی پتانسیل جذب کربن با استفاده از مدل RothC که توسط Rothamsted Research توسعه یافته است"
      color="from-emerald-500 to-green-600"
      citizenModuleType="carbon"
    >
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <ModuleStat label="کربن جذب‌شده" value="۲,۴۵۰ tCO₂" icon={Leaf} color="#10b981" trend="+۱۸٪" />
        <ModuleStat label="SOC متوسط" value="۴.۶٪" icon={TreePine} color="#059669" trend="+۰.۳" />
        <ModuleStat label="سطح زیر کشت" value="۱۲,۴۵۰ ha" icon={BarChart3} color="#84cc16" />
        <ModuleStat label="پروژه فعال" value="۲۴" icon={TrendingUp} color="#22c55e" trend="+۵" />
      </div>

      {/* Main Chart */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-bold text-white flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-emerald-400" />
            روند جذب کربن (۱۰ سال اخیر)
          </h3>
          <button onClick={() => console.log("Button clicked")}  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm text-white flex items-center gap-2">
            <Download className="h-4 w-4" />
            دانلود گزارش
          </button>
        </div>
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart data={CARBON_TREND}>
            <defs>
              <linearGradient id="socGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="litterGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#84cc16" stopOpacity={0.6}/>
                <stop offset="95%" stopColor="#84cc16" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
            <XAxis dataKey="year" stroke="#64748b" fontSize={12} />
            <YAxis stroke="#64748b" fontSize={12} label={{ value: "تن در هکتار", angle: -90, position: "insideLeft", fill: "#64748b" }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: "#0f172a", 
                border: "1px solid #334155",
                borderRadius: "8px"
              }}
            />
            <Legend />
            <Area type="monotone" dataKey="soc" stackId="1" stroke="#10b981" strokeWidth={2} fill="url(#socGrad)" name="کربن آلی خاک" />
            <Area type="monotone" dataKey="litter" stackId="1" stroke="#84cc16" strokeWidth={2} fill="url(#litterGrad)" name="لایه آشغال" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Land Use Comparison */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-6">کربن بر اساس کاربری اراضی</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={LAND_USE} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis type="number" stroke="#64748b" fontSize={11} />
              <YAxis dataKey="type" type="category" stroke="#64748b" fontSize={12} width={80} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "#0f172a", 
                  border: "1px solid #334155",
                  borderRadius: "8px"
                }}
              />
              <Bar dataKey="carbon" radius={[0, 8, 8, 0]}>
                {LAND_USE.map((entry, index) => (
                  <rect key={index} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Calculator */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Calculator className="h-5 w-5 text-emerald-400" />
            ماشین حساب کربن
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-slate-400 mb-2">نوع کاربری اراضی</label>
              <select className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white">
                <option>جنگل</option>
                <option>مرتع</option>
                <option>کشاورزی</option>
                <option>بایر</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-2">مساحت (هکتار)</label>
              <input type="number" defaultValue="100" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
            </div>
            <div>
              <label className="block text-sm text-slate-400 mb-2">مدت زمان (سال)</label>
              <input type="number" defaultValue="10" className="w-full px-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white" />
            </div>
            <button onClick={() => console.log("Button clicked")}  className="w-full py-3 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-emerald-500/30 transition-all">
              محاسبه کربن جذب‌شده
            </button>
            <div className="p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl text-center">
              <p className="text-sm text-emerald-300 mb-1">کربن جذب‌شده پیش‌بینی شده</p>
              <p className="text-3xl font-black text-emerald-400">۱۵۰ tCO₂</p>
            </div>
          </div>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <InfoCard
          icon={TreePine}
          title="مدل RothC"
          description="مدل معتبر جهانی برای شبیه‌سازی دینامیک کربن آلی خاک در شرایط مختلف اقلیمی"
          color="from-emerald-500 to-green-600"
        />
        <InfoCard
          icon={Leaf}
          title="اعتبار کربن"
          description="صدور گواهی‌نامه جذب کربن بر اساس استانداردهای بین‌المللی Verra و Gold Standard"
          color="from-green-500 to-teal-600"
        />
        <InfoCard
          icon={TrendingUp}
          title="پایش مستمر"
          description="رصد تغییرات کربن خاک با استفاده از تصاویر ماهواره‌ای و نمونه‌برداری میدانی"
          color="from-teal-500 to-cyan-600"
        />
      </div>
    </ScientificModuleLayout>
  );
}