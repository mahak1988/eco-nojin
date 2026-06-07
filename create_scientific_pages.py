#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗺️ مرحله ۴: طراحی صفحات ماژول‌های علمی
الگو: NASA Earth Observatory + Climate Trace
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"✅ {path.relative_to(WEB)}")


# ========== 1. کامپوننت پایه ماژول علمی ==========
def create_module_layout():
    print("\n🧩 ایجاد ScientificModuleLayout...")
    
    content = '''"use client";

import { ReactNode } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, LucideIcon } from "lucide-react";

interface ScientificModuleLayoutProps {
  icon: LucideIcon;
  title: string;
  subtitle: string;
  description: string;
  color: string;
  children: ReactNode;
  backHref?: string;
}

export function ScientificModuleLayout({
  icon: Icon,
  title,
  subtitle,
  description,
  color,
  children,
  backHref = "/"
}: ScientificModuleLayoutProps) {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero Section مخصوص ماژول */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className={`absolute inset-0 bg-gradient-to-br ${color} opacity-20`} />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <Link href={backHref} className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" />
              بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className={`p-5 rounded-3xl bg-gradient-to-br ${color} shadow-2xl`}>
                <Icon className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-emerald-400 text-sm font-medium mb-2">{subtitle}</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">{title}</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">{description}</p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Content */}
      <section className="container mx-auto px-6 py-12">
        {children}
      </section>
    </div>
  );
}

// کامپوننت آمار ماژول
interface ModuleStatProps {
  label: string;
  value: string | number;
  icon: LucideIcon;
  color: string;
  trend?: string;
}

export function ModuleStat({ label, value, icon: Icon, color, trend }: ModuleStatProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
    >
      <div className="flex items-center justify-between mb-4">
        <Icon className="h-8 w-8" style={{ color }} />
        {trend && (
          <span className="text-xs px-2 py-1 bg-emerald-500/10 text-emerald-400 rounded-full">
            {trend}
          </span>
        )}
      </div>
      <p className="text-3xl font-black text-white mb-1">{value}</p>
      <p className="text-sm text-slate-400">{label}</p>
    </motion.div>
  );
}

// کامپوننت کارت اطلاعات
interface InfoCardProps {
  title: string;
  description: string;
  icon: LucideIcon;
  color: string;
}

export function InfoCard({ title, description, icon: Icon, color }: InfoCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
    >
      <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${color} mb-4`}>
        <Icon className="h-6 w-6 text-white" />
      </div>
      <h3 className="text-xl font-bold text-white mb-2">{title}</h3>
      <p className="text-slate-400 leading-relaxed">{description}</p>
    </motion.div>
  );
}
'''
    
    write_file(WEB / "components" / "modules" / "ScientificModuleLayout.tsx", content)


# ========== 2. صفحه GIS با نقشه Leaflet ==========
def create_gis_page():
    print("\n🗺️ ایجاد صفحه GIS با نقشه تعاملی...")
    
    content = '''"use client";

import { useEffect, useState } from "react";
import dynamic from "next/dynamic";
import { motion } from "framer-motion";
import { Map as MapIcon, Layers, Ruler, Leaf, TrendingUp, Download, Filter, Search } from "lucide-react";
import { ScientificModuleLayout, ModuleStat, InfoCard } from "@/components/modules/ScientificModuleLayout";
import { gisService } from "@/lib/api";

// Import Leaflet dynamically to avoid SSR issues
const MapContainer = dynamic(() => import("react-leaflet").then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then(mod => mod.TileLayer), { ssr: false });
const Circle = dynamic(() => import("react-leaflet").then(mod => mod.Circle), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then(mod => mod.Popup), { ssr: false });

// Sample data - در نسخه واقعی از API می‌آید
const SAMPLE_REGIONS = [
  { id: 1, name: "حوضه کشف‌رود", center: [36.3, 59.6], radius: 30000, ndvi: 0.62, area: "۱,۲۵۰ ha", color: "#10b981" },
  { id: 2, name: "دشت کویر", center: [33.5, 54.5], radius: 45000, ndvi: 0.28, area: "۲,۱۰۰ ha", color: "#f59e0b" },
  { id: 3, name: "زاگرس مرکزی", center: [31.5, 51.5], radius: 35000, ndvi: 0.75, area: "۸۹۰ ha", color: "#059669" },
  { id: 4, name: "بلوچستان", center: [28.5, 60.5], radius: 40000, ndvi: 0.18, area: "۶۵۰ ha", color: "#ef4444" },
  { id: 5, name: "آذربایجان", center: [38.0, 46.5], radius: 28000, ndvi: 0.68, area: "۱,۱۰۰ ha", color: "#3b82f6" },
];

export default function GisPage() {
  const [selectedLayer, setSelectedLayer] = useState("ndvi");
  const [searchQuery, setSearchQuery] = useState("");
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const loadStats = async () => {
      try {
        const data = await gisService.getNdvi("iran");
        setStats(data);
      } catch (e) {
        console.log("Using sample data");
      }
    };
    loadStats();
  }, []);

  const filteredRegions = SAMPLE_REGIONS.filter(r => 
    r.name.includes(searchQuery)
  );

  return (
    <ScientificModuleLayout
      icon={MapIcon}
      title="GIS و تحلیل مکانی"
      subtitle="ماژول تخصصی"
      description="تحلیل پوشش گیاهی، نقشه‌های tematique، محاسبه مساحت و تحلیل‌های فضایی پیشرفته با استفاده از تصاویر ماهواره‌ای و داده‌های مکانی"
      color="from-violet-500 to-purple-600"
    >
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
        <ModuleStat label="لایه‌های فعال" value="۱۲۰" icon={Layers} color="#8b5cf6" trend="+۵" />
        <ModuleStat label="منطقه تحت پایش" value="۴۸" icon={MapIcon} color="#a855f7" />
        <ModuleStat label="میانگین NDVI" value="۰.۵۴" icon={Leaf} color="#10b981" trend="+۰.۰۳" />
        <ModuleStat label="مساحت کل" value="۱۲,۴۵۰ ha" icon={Ruler} color="#3b82f6" />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-10">
        {/* Map */}
        <div className="lg:col-span-2 bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <MapIcon className="h-5 w-5 text-violet-400" />
              نقشه تعاملی ایران
            </h3>
            <div className="flex gap-2">
              <select 
                value={selectedLayer} 
                onChange={e => setSelectedLayer(e.target.value)}
                className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white"
              >
                <option value="ndvi">پوشش گیاهی (NDVI)</option>
                <option value="erosion">فرسایش خاک</option>
                <option value="moisture">رطوبت خاک</option>
                <option value="temperature">دمای سطح</option>
              </select>
              <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
                <Download className="h-4 w-4 text-slate-300" />
              </button>
            </div>
          </div>
          
          <div className="h-[500px] relative">
            <MapContainer 
              center={[32.5, 54.5]} 
              zoom={5} 
              style={{ height: "100%", width: "100%" }}
              scrollWheelZoom={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              
              {filteredRegions.map(region => (
                <Circle
                  key={region.id}
                  center={region.center as [number, number]}
                  radius={region.radius}
                  pathOptions={{
                    color: region.color,
                    fillColor: region.color,
                    fillOpacity: 0.3,
                    weight: 2
                  }}
                >
                  <Popup>
                    <div className="p-2">
                      <h4 className="font-bold text-slate-900">{region.name}</h4>
                      <p className="text-sm">مساحت: {region.area}</p>
                      <p className="text-sm">NDVI: {region.ndvi}</p>
                    </div>
                  </Popup>
                </Circle>
              ))}
            </MapContainer>
          </div>
        </div>

        {/* Sidebar */}
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-5">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Filter className="h-5 w-5 text-violet-400" />
            مناطق تحت پایش
          </h3>
          
          <div className="relative mb-4">
            <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-500" />
            <input
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              placeholder="جستجوی منطقه..."
              className="w-full pr-10 pl-4 py-2 bg-slate-800 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-violet-500"
            />
          </div>

          <div className="space-y-2 max-h-[400px] overflow-y-auto">
            {filteredRegions.map(region => (
              <motion.div
                key={region.id}
                whileHover={{ x: -4 }}
                className="p-3 bg-slate-800/50 hover:bg-slate-800 rounded-xl cursor-pointer transition-colors"
              >
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-bold text-white">{region.name}</h4>
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: region.color }} />
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400">
                  <span>مساحت: {region.area}</span>
                  <span>NDVI: {region.ndvi}</span>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>

      {/* Info Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <InfoCard
          icon={Leaf}
          title="تحلیل NDVI"
          description="محاسبه شاخص پوشش گیاهی از تصاویر ماهواره‌ای Sentinel-2 با دقت ۱۰ متر"
          color="from-emerald-500 to-green-600"
        />
        <InfoCard
          icon={Ruler}
          title="محاسبه مساحت"
          description="محاسبه دقیق مساحت مناطق با استفاده از الگوریتم‌های پیشرفته GIS"
          color="from-blue-500 to-cyan-600"
        />
        <InfoCard
          icon={TrendingUp}
          title="تحلیل روند"
          description="بررسی تغییرات زمانی پوشش گیاهی و شناسایی مناطق در معرض خطر"
          color="from-violet-500 to-purple-600"
        />
      </div>
    </ScientificModuleLayout>
  );
}
'''
    
    write_file(WEB / "app" / "gis" / "page.tsx", content)


# ========== 3. صفحه هیدرولوژی ==========
def create_hydrology_page():
    print("\n💧 ایجاد صفحه هیدرولوژی...")
    
    content = '''"use client";

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
            <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
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
            <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
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
'''
    
    write_file(WEB / "app" / "hydrology" / "page.tsx", content)


# ========== 4. صفحه کربن خاک ==========
def create_carbon_page():
    print("\n🌳 ایجاد صفحه کربن خاک...")
    
    content = '''"use client";

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
          <button className="px-4 py-2 bg-slate-800 hover:bg-slate-700 rounded-lg text-sm text-white flex items-center gap-2">
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
            <button className="w-full py-3 bg-gradient-to-l from-emerald-500 to-green-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-emerald-500/30 transition-all">
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
'''
    
    write_file(WEB / "app" / "carbon" / "page.tsx", content)


# ========== 5. نصب Leaflet CSS ==========
def add_leaflet_css():
    print("\n🗺️ افزودن Leaflet CSS...")
    
    css_path = WEB / "styles" / "globals.css"
    if css_path.exists():
        content = css_path.read_text(encoding="utf-8")
        if "unpkg.com/leaflet" not in content:
            content = '@import "leaflet/dist/leaflet.css";\n' + content
            css_path.write_text(content, encoding="utf-8")
            print("   ✅ Leaflet CSS اضافه شد")
    else:
        print("   ⚠️ globals.css یافت نشد")


# ========== Main ==========
def main():
    print("🗺️ مرحله ۴: طراحی صفحات ماژول‌های علمی")
    print("=" * 70)
    print("الگو: NASA Earth Observatory + Climate Trace")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    create_module_layout()
    create_gis_page()
    create_hydrology_page()
    create_carbon_page()
    add_leaflet_css()
    
    print("\n" + "=" * 70)
    print("✅ صفحات ماژول‌های علمی تکمیل شد!")
    print("\n🎯 صفحات ایجاد شده:")
    print("   🗺️ /gis - نقشه تعاملی با Leaflet")
    print("   💧 /hydrology - چارت‌های جریان و بارش")
    print("   🌳 /carbon - مدل RothC و ماشین حساب")
    
    print("\n🧩 کامپوننت‌های ایجاد شده:")
    print("   • ScientificModuleLayout")
    print("   • ModuleStat")
    print("   • InfoCard")
    
    print("\n📦 نصب Leaflet (اگر نصب نیست):")
    print("   pnpm add leaflet react-leaflet @types/leaflet")
    
    print("\n🚀 گام بعدی:")
    print("   1. نصب: pnpm add leaflet react-leaflet @types/leaflet")
    print("   2. پاک‌سازی: Remove-Item .next -Recurse -Force")
    print("   3. اجرا: pnpm run dev -- -p 3001")
    print("   4. مشاهده:")
    print("      • http://localhost:3001/gis")
    print("      • http://localhost:3001/hydrology")
    print("      • http://localhost:3001/carbon")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())