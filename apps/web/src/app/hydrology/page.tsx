"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Droplets, TrendingUp, CloudRain, Mountain, Activity, Download } from "lucide-react";
import { ScientificModuleLayout, ModuleStat, InfoCard } from "@/components/modules/ScientificModuleLayout";
import { hydrologyService } from "@/lib/api";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, Area, AreaChart
} from "recharts";

// Sample data
const MONTHLY_FLOW = [
  { month: "فروردین", flow: 45, rain: 80, evap: 30 },
  { month: "اردیبهشت", flow: 62, rain: 95, evap: 45 },
  { month: "خرداد", flow: 38, rain: 40, evap: 70 },
  { month: "تیر", flow: 18, rain: 10, evap: 95 },
  { month: "مرداد", flow: 12, rain: 5, evap: 110 },
  { month: "شهریور", flow: 15, rain: 8, evap: 90 },
  { month: "مهر", flow: 28, rain: 35, evap: 60 },
  { month: "آبان", flow: 52, rain: 75, evap: 40 },
  { month: "آذر", flow: 68, rain: 110, evap: 25 },
  { month: "دی", flow: 72, rain: 120, evap: 20 },
  { month: "بهمن", flow: 65, rain: 105, evap: 22 },
  { month: "اسفند", flow: 55, rain: 85, evap: 35 },
];

const BASINS = [
  { id: 1, name: "کشف‌رود", area: "۵,۲۰۰ km²", flow: "۴۵ m³/s", status: "active" },
  { id: 2, name: "زاینده‌رود", area: "۴۱,۵۰۰ km²", flow: "۱۲ m³/s", status: "critical" },
  { id: 3, name: "کارون", area: "۶۶,۵۰۰ km²", flow: "۵۸۰ m³/s", status: "active" },
  { id: 4, name: "هیرمند", area: "۱۴۰,۰۰۰ km²", flow: "۸۵ m³/s", status: "warning" },
];

export default function HydrologyPage() {
  const [selectedBasin, setSelectedBasin] = useState(1);

  return (
    <ScientificModuleLayout
      icon={Droplets}
      title="هیدرولوژی"
      subtitle="شبیه‌سازی رواناب"
      description="تحلیل جریان آب، بارش و تبخیر در حوضه‌های آبریز خشک و نیمه‌خشک با استفاده از مدل‌های پیشرفته هیدرولوژیکی"
      color="from-blue-500 to-cyan-600"
      citizenModuleType="hydrology"
    >
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <ModuleStat label="حوضه فعال" value="۱۲" icon={Droplets} color="#3b82f6" trend="+۲" />
        <ModuleStat label="دبی متوسط" value="۷۳۲ m³/s" icon={Activity} color="#06b6d4" />
        <ModuleStat label="بارش سالانه" value="۲۸۰ mm" icon={CloudRain} color="#0ea5e9" trend="-۱۲٪" />
        <ModuleStat label="تبخیر سالانه" value="۱,۸۵۰ mm" icon={TrendingUp} color="#8b5cf6" />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-10">
        {/* Flow Chart */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">روند جریان ماهانه</h3>
            <button onClick={() => console.log("Button clicked")}  className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
              <Download className="h-4 w-4 text-slate-300" />
            </button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={MONTHLY_FLOW}>
              <defs>
                <linearGradient id="flowGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8}/>
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "#0f172a", 
                  border: "1px solid #334155",
                  borderRadius: "8px"
                }}
              />
              <Area 
                type="monotone" 
                dataKey="flow" 
                stroke="#3b82f6" 
                strokeWidth={2}
                fill="url(#flowGradient)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Rain vs Evaporation */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold text-white">بارش در برابر تبخیر</h3>
            <button onClick={() => console.log("Button clicked")}  className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
              <Download className="h-4 w-4 text-slate-300" />
            </button>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={MONTHLY_FLOW}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: "#0f172a", 
                  border: "1px solid #334155",
                  borderRadius: "8px"
                }}
              />
              <Legend />
              <Bar dataKey="rain" fill="#06b6d4" radius={[4, 4, 0, 0]} name="بارش (mm)" />
              <Bar dataKey="evap" fill="#f59e0b" radius={[4, 4, 0, 0]} name="تبخیر (mm)" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Basins Table */}
      <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-10">
        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
          <Mountain className="h-5 w-5 text-blue-400" />
          حوضه‌های آبریز اصلی
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">نام حوضه</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">مساحت</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">دبی متوسط</th>
                <th className="text-right py-3 px-4 text-sm font-semibold text-slate-300">وضعیت</th>
              </tr>
            </thead>
            <tbody>
              {BASINS.map(basin => (
                <tr key={basin.id} className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors">
                  <td className="py-4 px-4 text-white font-medium">{basin.name}</td>
                  <td className="py-4 px-4 text-slate-300">{basin.area}</td>
                  <td className="py-4 px-4 text-slate-300">{basin.flow}</td>
                  <td className="py-4 px-4">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                      basin.status === "active" ? "bg-emerald-500/10 text-emerald-400" :
                      basin.status === "warning" ? "bg-amber-500/10 text-amber-400" :
                      "bg-red-500/10 text-red-400"
                    }`}>
                      {basin.status === "active" ? "فعال" : 
                       basin.status === "warning" ? "هشدار" : "بحرانی"}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <InfoCard
          icon={Droplets}
          title="مدل HEC-HMS"
          description="شبیه‌سازی رواناب و جریان آب با استفاده از مدل‌های هیدرولوژیکی استاندارد جهانی"
          color="from-blue-500 to-cyan-600"
      citizenModuleType="hydrology"
        />
        <InfoCard
          icon={CloudRain}
          title="تحلیل بارش"
          description="پردازش داده‌های بارش از ایستگاه‌های هواشناسی و تصاویر ماهواره‌ای"
          color="from-sky-500 to-blue-600"
        />
        <InfoCard
          icon={TrendingUp}
          title="پیش‌بینی جریان"
          description="پیش‌بینی دبی رودخانه‌ها با استفاده از مدل‌های آماری و هوش مصنوعی"
          color="from-cyan-500 to-teal-600"
        />
      </div>
    </ScientificModuleLayout>
  );
}