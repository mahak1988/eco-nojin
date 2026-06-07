#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎨 توسعه کامل تمام صفحات اکو نوژین
- GIS با نقشه Leaflet کامل
- Library (کتابخانه دیجیتال)
- Education (پلتفرم آموزشی)
- Community (انجمن)
- Shop (فروشگاه)
- Psychology (سلامت روان)
- Ecomining (کیف پول)
- Desktop (میزکار)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)}")


# ========== 1. GIS کامل با Leaflet ==========
def create_gis_complete():
    print("\n🗺️ ایجاد صفحه GIS کامل با نقشه Leaflet...")
    
    content = '''"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, Map as MapIcon, Layers, Ruler, Leaf, TrendingUp, 
  Download, Filter, Search, ZoomIn, ZoomOut, Maximize2, 
  Satellite, Cloud, Droplets, Thermometer
} from "lucide-react";
import {
  ResponsiveContainer, LineChart, Line, AreaChart, Area,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar
} from "recharts";

const MapContainer = dynamic(() => import("react-leaflet").then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then(mod => mod.TileLayer), { ssr: false });
const Circle = dynamic(() => import("react-leaflet").then(mod => mod.Circle), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then(mod => mod.Popup), { ssr: false });
const Marker = dynamic(() => import("react-leaflet").then(mod => mod.Marker), { ssr: false });

const REGIONS = [
  { id: 1, name: "حوضه کشف‌رود", center: [36.3, 59.6], radius: 30000, ndvi: 0.62, area: "۱,۲۵۰ ha", color: "#10b981", status: "سالم" },
  { id: 2, name: "دشت کویر", center: [33.5, 54.5], radius: 45000, ndvi: 0.28, area: "۲,۱۰۰ ha", color: "#f59e0b", status: "هشدار" },
  { id: 3, name: "زاگرس مرکزی", center: [31.5, 51.5], radius: 35000, ndvi: 0.75, area: "۸۹۰ ha", color: "#059669", status: "عالی" },
  { id: 4, name: "بلوچستان", center: [28.5, 60.5], radius: 40000, ndvi: 0.18, area: "۶۵۰ ha", color: "#ef4444", status: "بحرانی" },
  { id: 5, name: "آذربایجان", center: [38.0, 46.5], radius: 28000, ndvi: 0.68, area: "۱,۱۰۰ ha", color: "#3b82f6", status: "خوب" },
  { id: 6, name: "فارس", center: [29.6, 52.5], radius: 32000, ndvi: 0.45, area: "۱,۴۵۰ ha", color: "#8b5cf6", status: "متوسط" },
];

const NDVI_TIMELINE = [
  { month: "فروردین", ndvi: 0.35, rain: 45 },
  { month: "اردیبهشت", ndvi: 0.52, rain: 60 },
  { month: "خرداد", ndvi: 0.68, rain: 25 },
  { month: "تیر", ndvi: 0.75, rain: 10 },
  { month: "مرداد", ndvi: 0.72, rain: 5 },
  { month: "شهریور", ndvi: 0.65, rain: 15 },
  { month: "مهر", ndvi: 0.55, rain: 35 },
  { month: "آبان", ndvi: 0.42, rain: 55 },
];

const LAYERS = [
  { id: "ndvi", name: "پوشش گیاهی (NDVI)", icon: Leaf, color: "#10b981" },
  { id: "erosion", name: "فرسایش خاک", icon: TrendingUp, color: "#f59e0b" },
  { id: "moisture", name: "رطوبت خاک", icon: Droplets, color: "#3b82f6" },
  { id: "temperature", name: "دمای سطح", icon: Thermometer, color: "#ef4444" },
];

export default function GisPage() {
  const [selectedLayer, setSelectedLayer] = useState("ndvi");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedRegion, setSelectedRegion] = useState(REGIONS[0]);
  const [zoom, setZoom] = useState(5);

  const filteredRegions = REGIONS.filter(r => 
    r.name.includes(searchQuery)
  );

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-500 to-purple-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-2xl">
                <MapIcon className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-violet-400 text-sm font-medium mb-2">ماژول تخصصی</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">GIS و تحلیل مکانی</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  تحلیل پوشش گیاهی، نقشه‌های tematique، محاسبه مساحت و تحلیل‌های فضایی پیشرفته با استفاده از تصاویر ماهواره‌ای
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "لایه‌های فعال", value: "۱۲۰", icon: Layers, color: "#8b5cf6" },
            { label: "منطقه تحت پایش", value: "۴۸", icon: MapIcon, color: "#a855f7" },
            { label: "میانگین NDVI", value: "۰.۵۴", icon: Leaf, color: "#10b981" },
            { label: "مساحت کل", value: "۱۲,۴۵۰ ha", icon: Ruler, color: "#3b82f6" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Map Section */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
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
                  {LAYERS.map(layer => (
                    <option key={layer.id} value={layer.id}>{layer.name}</option>
                  ))}
                </select>
                <button className="p-2 bg-slate-800 hover:bg-slate-700 rounded-lg">
                  <Download className="h-4 w-4 text-slate-300" />
                </button>
              </div>
            </div>
            
            <div className="h-[600px] relative">
              <MapContainer 
                center={[32.5, 54.5]} 
                zoom={zoom} 
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
                    eventHandlers={{
                      click: () => setSelectedRegion(region),
                    }}
                  >
                    <Popup>
                      <div className="p-2">
                        <h4 className="font-bold text-slate-900">{region.name}</h4>
                        <p className="text-sm">مساحت: {region.area}</p>
                        <p className="text-sm">NDVI: {region.ndvi}</p>
                        <p className="text-sm">وضعیت: {region.status}</p>
                      </div>
                    </Popup>
                  </Circle>
                ))}
              </MapContainer>

              {/* Map Controls */}
              <div className="absolute top-4 right-4 flex flex-col gap-2">
                <button 
                  onClick={() => setZoom(z => Math.min(z + 1, 18))}
                  className="p-2 bg-slate-900/90 hover:bg-slate-800 rounded-lg border border-slate-700"
                >
                  <ZoomIn className="h-5 w-5 text-white" />
                </button>
                <button 
                  onClick={() => setZoom(z => Math.max(z - 1, 3))}
                  className="p-2 bg-slate-900/90 hover:bg-slate-800 rounded-lg border border-slate-700"
                >
                  <ZoomOut className="h-5 w-5 text-white" />
                </button>
                <button className="p-2 bg-slate-900/90 hover:bg-slate-800 rounded-lg border border-slate-700">
                  <Maximize2 className="h-5 w-5 text-white" />
                </button>
              </div>
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

            <div className="space-y-2 max-h-[500px] overflow-y-auto">
              {filteredRegions.map(region => (
                <motion.div
                  key={region.id}
                  whileHover={{ x: -4 }}
                  onClick={() => setSelectedRegion(region)}
                  className={`p-3 rounded-xl cursor-pointer transition-all ${
                    selectedRegion.id === region.id
                      ? "bg-violet-500/20 border-2 border-violet-500"
                      : "bg-slate-800/50 hover:bg-slate-800 border-2 border-transparent"
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-bold text-white">{region.name}</h4>
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: region.color }} />
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-400">
                    <span>مساحت: {region.area}</span>
                    <span>NDVI: {region.ndvi}</span>
                  </div>
                  <div className="mt-2">
                    <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: region.color + "20", color: region.color }}>
                      {region.status}
                    </span>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* NDVI Timeline */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <TrendingUp className="h-5 w-5 text-violet-400" />
            روند NDVI ماهانه
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
              <XAxis dataKey="month" stroke="#64748b" fontSize={11} />
              <YAxis stroke="#64748b" fontSize={11} domain={[0, 1]} />
              <Tooltip contentStyle={{ backgroundColor: "#0f172a", border: "1px solid #334155", borderRadius: "8px" }} />
              <Legend />
              <Area type="monotone" dataKey="ndvi" stroke="#10b981" strokeWidth={2} fill="url(#ndviGrad)" name="NDVI" />
              <Line type="monotone" dataKey="rain" stroke="#3b82f6" strokeWidth={2} name="بارش (mm)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "gis" / "page.tsx", content)


# ========== 2. Library (کتابخانه دیجیتال) ==========
def create_library():
    print("\n📚 ایجاد صفحه کتابخانه دیجیتال...")
    
    content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, BookOpen, Search, Filter, Download, Eye, 
  Star, Calendar, User, Tag, TrendingUp
} from "lucide-react";

const RESOURCES = [
  {
    id: 1,
    title: "مدیریت پایدار آب در مناطق خشک",
    author: "دکتر احمد محمدی",
    category: "مقاله علمی",
    date: "۱۴۰۴/۱۲/۱۵",
    views: 1250,
    rating: 4.8,
    tags: ["آب", "خشکسالی", "مدیریت"],
    image: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&q=80",
    description: "راهکارهای نوین برای مدیریت منابع آب در شرایط کم‌آبی و تغییر اقلیم"
  },
  {
    id: 2,
    title: "مدل RothC برای شبیه‌سازی کربن خاک",
    author: "دکتر مریم حسینی",
    category: "کتاب",
    date: "۱۴۰۴/۱۰/۲۰",
    views: 890,
    rating: 4.9,
    tags: ["کربن", "خاک", "مدل‌سازی"],
    image: "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=80",
    description: "راهنمای کامل استفاده از مدل RothC برای پیش‌بینی دینامیک کربن آلی خاک"
  },
  {
    id: 3,
    title: "کاربرد تصاویر Sentinel-2 در کشاورزی",
    author: "مهندس رضا کریمی",
    category: "ویدئو آموزشی",
    date: "۱۴۰۴/۰۸/۰۵",
    views: 2340,
    rating: 4.7,
    tags: ["سنجش از دور", "Sentinel", "کشاورزی"],
    image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80",
    description: "آموزش گام به گام پردازش تصاویر ماهواره‌ای برای پایش محصولات کشاورزی"
  },
  {
    id: 4,
    title: "فرسایش خاک و راهکارهای حفاظتی",
    author: "دکتر زهرا احمدی",
    category: "مقاله علمی",
    date: "۱۴۰۴/۰۶/۱۲",
    views: 1560,
    rating: 4.6,
    tags: ["فرسایش", "حفاظت", "خاک"],
    image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80",
    description: "بررسی عوامل فرسایش خاک و معرفی روش‌های مؤثر حفاظتی"
  },
  {
    id: 5,
    title: "کشاورزی حفاظتی در اقلیم خشک",
    author: "دکتر علی رضایی",
    category: "کتاب",
    date: "۱۴۰۴/۰۴/۱۸",
    views: 980,
    rating: 4.8,
    tags: ["کشاورزی", "حفاظتی", "خشک"],
    image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&q=80",
    description: "اصول و روش‌های کشاورزی حفاظتی مناسب برای مناطق خشک و نیمه‌خشک"
  },
  {
    id: 6,
    title: "تحلیل NDVI با Google Earth Engine",
    author: "مهندس سارا محمدی",
    category: "ویدئو آموزشی",
    date: "۱۴۰۴/۰۲/۲۵",
    views: 3120,
    rating: 4.9,
    tags: ["NDVI", "GEE", "تحلیل"],
    image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80",
    description: "آموزش محاسبه و تحلیل شاخص NDVI با استفاده از پلتفرم Google Earth Engine"
  },
];

const CATEGORIES = ["همه", "مقاله علمی", "کتاب", "ویدئو آموزشی", "پایان‌نامه", "گزارش فنی"];

export default function LibraryPage() {
  const [selectedCategory, setSelectedCategory] = useState("همه");
  const [searchQuery, setSearchQuery] = useState("");
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");

  const filteredResources = RESOURCES.filter(r => 
    (selectedCategory === "همه" || r.category === selectedCategory) &&
    (r.title.includes(searchQuery) || r.author.includes(searchQuery) || r.tags.some(t => t.includes(searchQuery)))
  );

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-rose-500 to-pink-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-rose-500 to-pink-600 shadow-2xl">
                <BookOpen className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-rose-400 text-sm font-medium mb-2">منابع علمی</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">کتابخانه دیجیتال</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  دسترسی به هزاران مقاله، کتاب، ویدئو آموزشی و منابع علمی در حوزه احیای زمین و کشاورزی پایدار
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "مقالات علمی", value: "۵۲۰", icon: BookOpen, color: "#f43f5e" },
            { label: "کتاب‌ها", value: "۱۸۰", icon: BookOpen, color: "#ec4899" },
            { label: "ویدئو آموزشی", value: "۳۴۰", icon: BookOpen, color: "#d946ef" },
            { label: "دانلود این ماه", value: "۱۲,۴۵۰", icon: Download, color: "#a855f7" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Filters */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="جستجو در عنوان، نویسنده یا برچسب..."
                className="w-full pr-10 pl-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-rose-500"
              />
            </div>
            <div className="flex gap-2 overflow-x-auto">
              {CATEGORIES.map(cat => (
                <button
                  key={cat}
                  onClick={() => setSelectedCategory(cat)}
                  className={`px-4 py-2 rounded-xl whitespace-nowrap transition-all ${
                    selectedCategory === cat
                      ? "bg-rose-600 text-white"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Resources Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredResources.map((resource, i) => (
            <motion.div
              key={resource.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all group"
            >
              <div className="relative h-48 overflow-hidden">
                <img src={resource.image} alt={resource.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
                <div className="absolute top-3 right-3 px-3 py-1 bg-rose-500/90 backdrop-blur-sm rounded-full text-xs text-white font-medium">
                  {resource.category}
                </div>
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-rose-300 transition-colors line-clamp-2">
                  {resource.title}
                </h3>
                <p className="text-sm text-slate-400 mb-4 line-clamp-2">{resource.description}</p>
                
                <div className="flex items-center gap-4 text-xs text-slate-500 mb-4">
                  <span className="flex items-center gap-1">
                    <User className="h-3 w-3" /> {resource.author}
                  </span>
                  <span className="flex items-center gap-1">
                    <Calendar className="h-3 w-3" /> {resource.date}
                  </span>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  {resource.tags.map(tag => (
                    <span key={tag} className="px-2 py-1 bg-slate-800 text-slate-400 rounded text-xs">
                      #{tag}
                    </span>
                  ))}
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <div className="flex items-center gap-3 text-sm text-slate-400">
                    <span className="flex items-center gap-1">
                      <Eye className="h-4 w-4" /> {resource.views}
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-amber-400 text-amber-400" /> {resource.rating}
                    </span>
                  </div>
                  <button className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg text-sm font-medium transition-colors">
                    مشاهده
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "library" / "page.tsx", content)


# ========== 3. Education (پلتفرم آموزشی) ==========
def create_education():
    print("\n🎓 ایجاد پلتفرم آموزشی...")
    
    content = '''"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, GraduationCap, Play, Clock, Users, Star, 
  Award, TrendingUp, Filter, Search, BookOpen
} from "lucide-react";

const COURSES = [
  {
    id: 1,
    title: "مبانی هیدرولوژی کاربردی",
    instructor: "دکتر احمد محمدی",
    duration: "۲۴ ساعت",
    students: 1250,
    rating: 4.9,
    level: "مقدماتی",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=400&q=80",
    progress: 0,
    lessons: 32
  },
  {
    id: 2,
    title: "مدل‌سازی کربن خاک با RothC",
    instructor: "دکتر مریم حسینی",
    duration: "۱۸ ساعت",
    students: 890,
    rating: 4.8,
    level: "پیشرفته",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1448375240586-882707db888b?w=400&q=80",
    progress: 65,
    lessons: 24
  },
  {
    id: 3,
    title: "پردازش تصاویر ماهواره‌ای",
    instructor: "مهندس رضا کریمی",
    duration: "۳۰ ساعت",
    students: 2340,
    rating: 4.9,
    level: "متوسط",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=400&q=80",
    progress: 30,
    lessons: 40
  },
  {
    id: 4,
    title: "کشاورزی پایدار در اقلیم خشک",
    instructor: "دکتر علی رضایی",
    duration: "۲۰ ساعت",
    students: 1560,
    rating: 4.7,
    level: "مقدماتی",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1625246333195-78d9c38ad449?w=400&q=80",
    progress: 0,
    lessons: 28
  },
  {
    id: 5,
    title: "مدیریت فرسایش خاک",
    instructor: "دکتر زهرا احمدی",
    duration: "۱۵ ساعت",
    students: 980,
    rating: 4.8,
    level: "متوسط",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=400&q=80",
    progress: 100,
    lessons: 20
  },
  {
    id: 6,
    title: "تحلیل NDVI با Google Earth Engine",
    instructor: "مهندس سارا محمدی",
    duration: "۱۲ ساعت",
    students: 3120,
    rating: 4.9,
    level: "پیشرفته",
    price: "رایگان",
    image: "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=400&q=80",
    progress: 45,
    lessons: 16
  },
];

const LEVELS = ["همه", "مقدماتی", "متوسط", "پیشرفته"];

export default function EducationPage() {
  const [selectedLevel, setSelectedLevel] = useState("همه");
  const [searchQuery, setSearchQuery] = useState("");

  const filteredCourses = COURSES.filter(c => 
    (selectedLevel === "همه" || c.level === selectedLevel) &&
    c.title.includes(searchQuery)
  );

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-yellow-500 to-amber-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-20">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-8 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-8">
              <div className="p-5 rounded-3xl bg-gradient-to-br from-yellow-500 to-amber-600 shadow-2xl">
                <GraduationCap className="h-12 w-12 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-yellow-400 text-sm font-medium mb-2">آموزش رایگان</p>
                <h1 className="text-5xl md:text-6xl font-black text-white mb-4">آکادمی اکو نوژین</h1>
                <p className="text-xl text-slate-300 max-w-3xl leading-relaxed">
                  دوره‌های تخصصی رایگان در حوزه هیدرولوژی، کربن خاک، سنجش از دور و کشاورزی پایدار با گواهی‌نامه معتبر
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Stats */}
      <section className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "دوره‌های فعال", value: "۴۸", icon: BookOpen, color: "#f59e0b" },
            { label: "دانشجویان", value: "۱۲,۴۵۰", icon: Users, color: "#eab308" },
            { label: "ساعات آموزش", value: "۸۵۰", icon: Clock, color: "#ca8a04" },
            { label: "گواهی‌نامه صادر شده", value: "۳,۲۸۰", icon: Award, color: "#a16207" },
          ].map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6"
            >
              <stat.icon className="h-8 w-8 mb-3" style={{ color: stat.color }} />
              <p className="text-3xl font-black text-white mb-1">{stat.value}</p>
              <p className="text-sm text-slate-400">{stat.label}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Filters */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="relative flex-1">
              <Search className="absolute right-3 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-500" />
              <input
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                placeholder="جستجو در دوره‌ها..."
                className="w-full pr-10 pl-4 py-3 bg-slate-800 border border-slate-700 rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-yellow-500"
              />
            </div>
            <div className="flex gap-2">
              {LEVELS.map(level => (
                <button
                  key={level}
                  onClick={() => setSelectedLevel(level)}
                  className={`px-4 py-2 rounded-xl transition-all ${
                    selectedLevel === level
                      ? "bg-yellow-600 text-white"
                      : "bg-slate-800 text-slate-400 hover:bg-slate-700"
                  }`}
                >
                  {level}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Courses Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredCourses.map((course, i) => (
            <motion.div
              key={course.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.05 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden hover:border-slate-700 transition-all group"
            >
              <div className="relative h-48 overflow-hidden">
                <img src={course.image} alt={course.title} className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                <div className="absolute inset-0 bg-gradient-to-t from-slate-950 via-transparent to-transparent" />
                <div className="absolute top-3 right-3 px-3 py-1 bg-yellow-500/90 backdrop-blur-sm rounded-full text-xs text-white font-medium">
                  {course.level}
                </div>
                {course.progress > 0 && (
                  <div className="absolute bottom-0 left-0 right-0 h-1 bg-slate-800">
                    <div className="h-full bg-gradient-to-l from-yellow-500 to-amber-600" style={{ width: `${course.progress}%` }} />
                  </div>
                )}
              </div>
              
              <div className="p-6">
                <h3 className="text-xl font-bold text-white mb-2 group-hover:text-yellow-300 transition-colors line-clamp-2">
                  {course.title}
                </h3>
                
                <div className="flex items-center gap-4 text-xs text-slate-500 mb-4">
                  <span className="flex items-center gap-1">
                    <Users className="h-3 w-3" /> {course.instructor}
                  </span>
                </div>

                <div className="flex items-center justify-between text-sm text-slate-400 mb-4">
                  <span className="flex items-center gap-1">
                    <Clock className="h-4 w-4" /> {course.duration}
                  </span>
                  <span className="flex items-center gap-1">
                    <BookOpen className="h-4 w-4" /> {course.lessons} درس
                  </span>
                </div>

                {course.progress > 0 && (
                  <div className="mb-4">
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                      <span>پیشرفت</span>
                      <span>{course.progress}%</span>
                    </div>
                    <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                      <div className="h-full bg-gradient-to-l from-yellow-500 to-amber-600" style={{ width: `${course.progress}%` }} />
                    </div>
                  </div>
                )}

                <div className="flex items-center justify-between pt-4 border-t border-slate-800">
                  <div className="flex items-center gap-3 text-sm text-slate-400">
                    <span className="flex items-center gap-1">
                      <Users className="h-4 w-4" /> {course.students}
                    </span>
                    <span className="flex items-center gap-1">
                      <Star className="h-4 w-4 fill-amber-400 text-amber-400" /> {course.rating}
                    </span>
                  </div>
                  <button className="px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
                    {course.progress > 0 ? "ادامه" : "شروع"}
                    <Play className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "education" / "page.tsx", content)


# ========== Main ==========
def main():
    print("🎨 توسعه کامل صفحات اکو نوژین - بخش ۱")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    create_gis_complete()
    create_library()
    create_education()
    
    print("\n" + "=" * 70)
    print("✅ بخش ۱ تکمیل شد!")
    print("\n🎯 صفحات ایجاد شده:")
    print("   🗺️ GIS کامل با نقشه Leaflet")
    print("   📚 کتابخانه دیجیتال")
    print("   🎓 پلتفرم آموزشی")
    
    print("\n🚀 گام بعدی:")
    print("   1. پاک‌سازی: Remove-Item .next -Recurse -Force")
    print("   2. اجرا: pnpm run dev -- -p 3001")
    print("   3. مشاهده:")
    print("      • http://localhost:3001/gis")
    print("      • http://localhost:3001/library")
    print("      • http://localhost:3001/education")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())