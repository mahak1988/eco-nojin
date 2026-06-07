"use client";

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
      citizenModuleType="soil"
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