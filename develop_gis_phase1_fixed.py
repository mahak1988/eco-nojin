#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🗺️ فاز ۱: توسعه هسته GIS پیشرفته (نسخه اصلاح‌شده)
- بدون نصب خودکار کتابخانه‌ها
- فقط ایجاد فایل‌ها
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ========== 1. کامپوننت نقشه پیشرفته ==========
def create_advanced_map():
    print("\n🗺️ ایجاد AdvancedGISMap.tsx...")
    
    content = '''"use client";

import { useState, useRef } from "react";
import dynamic from "next/dynamic";
import { 
  MapPin, Ruler, Square, Layers, Search, ZoomIn, ZoomOut, 
  Maximize2, Download, Eye, EyeOff
} from "lucide-react";

const MapContainer = dynamic(() => import("react-leaflet").then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then(mod => mod.TileLayer), { ssr: false });
const Circle = dynamic(() => import("react-leaflet").then(mod => mod.Circle), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then(mod => mod.Popup), { ssr: false });
const Polyline = dynamic(() => import("react-leaflet").then(mod => mod.Polyline), { ssr: false });
const Polygon = dynamic(() => import("react-leaflet").then(mod => mod.Polygon), { ssr: false });
const ScaleControl = dynamic(() => import("react-leaflet").then(mod => mod.ScaleControl), { ssr: false });

const BASE_LAYERS = {
  osm: {
    name: "OpenStreetMap",
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    attribution: '&copy; OpenStreetMap',
    maxZoom: 19
  },
  satellite: {
    name: "تصویر ماهواره‌ای (Esri)",
    url: "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    attribution: '&copy; Esri',
    maxZoom: 19
  },
  terrain: {
    name: "توپوگرافی",
    url: "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
    attribution: '&copy; OpenTopoMap',
    maxZoom: 17
  },
  dark: {
    name: "حالت تاریک",
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution: '&copy; CARTO',
    maxZoom: 19
  }
};

const OVERLAY_LAYERS = {
  ndvi: { name: "NDVI (پوشش گیاهی)", opacity: 0.6, color: "#10b981" },
  drought: { name: "شاخص خشکسالی", opacity: 0.5, color: "#f59e0b" },
  elevation: { name: "مدل ارتفاعی", opacity: 0.4, color: "#8b5cf6" },
  hydrology: { name: "شبکه آبراهه‌ها", opacity: 0.7, color: "#3b82f6" }
};

interface Region {
  id: number;
  name: string;
  center: [number, number];
  radius: number;
  ndvi: number;
  area: string;
  color: string;
  status: string;
}

const SAMPLE_REGIONS: Region[] = [
  { id: 1, name: "حوضه کشف‌رود", center: [36.3, 59.6], radius: 30000, ndvi: 0.62, area: "۱,۲۵۰ ha", color: "#10b981", status: "سالم" },
  { id: 2, name: "دشت کویر", center: [33.5, 54.5], radius: 45000, ndvi: 0.28, area: "۲,۱۰۰ ha", color: "#f59e0b", status: "هشدار" },
  { id: 3, name: "زاگرس مرکزی", center: [31.5, 51.5], radius: 35000, ndvi: 0.75, area: "۸۹۰ ha", color: "#059669", status: "عالی" },
  { id: 4, name: "بلوچستان", center: [28.5, 60.5], radius: 40000, ndvi: 0.18, area: "۶۵۰ ha", color: "#ef4444", status: "بحرانی" },
  { id: 5, name: "آذربایجان", center: [38.0, 46.5], radius: 28000, ndvi: 0.68, area: "۱,۱۰۰ ha", color: "#3b82f6", status: "خوب" },
  { id: 6, name: "فارس", center: [29.6, 52.5], radius: 32000, ndvi: 0.45, area: "۱,۴۵۰ ha", color: "#8b5cf6", status: "متوسط" },
];

export default function AdvancedGISMap() {
  const [baseLayer, setBaseLayer] = useState<keyof typeof BASE_LAYERS>("satellite");
  const [overlays, setOverlays] = useState<Record<string, boolean>>({
    ndvi: false, drought: false, elevation: false, hydrology: false
  });
  const [measureMode, setMeasureMode] = useState<"none" | "distance" | "area">("none");
  const [measurePoints, setMeasurePoints] = useState<[number, number][]>([]);
  const [measureResult, setMeasureResult] = useState("");
  const [selectedRegion, setSelectedRegion] = useState<Region | null>(null);
  const [showLayerPanel, setShowLayerPanel] = useState(false);

  const calculateDistance = (points: [number, number][]) => {
    if (points.length < 2) return 0;
    let total = 0;
    for (let i = 1; i < points.length; i++) {
      const [lat1, lng1] = points[i - 1];
      const [lat2, lng2] = points[i];
      const R = 6371000;
      const dLat = (lat2 - lat1) * Math.PI / 180;
      const dLng = (lng2 - lng1) * Math.PI / 180;
      const a = Math.sin(dLat/2)**2 + Math.cos(lat1*Math.PI/180)*Math.cos(lat2*Math.PI/180)*Math.sin(dLng/2)**2;
      total += R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
    }
    return total;
  };

  const calculateArea = (points: [number, number][]) => {
    if (points.length < 3) return 0;
    let area = 0;
    const n = points.length;
    for (let i = 0; i < n; i++) {
      const [lat1, lng1] = points[i];
      const [lat2, lng2] = points[(i + 1) % n];
      area += (lng2 - lng1) * (2 + Math.sin(lat1*Math.PI/180) + Math.sin(lat2*Math.PI/180));
    }
    return Math.abs(area * 6371000 * 6371000 / 2);
  };

  const handleMapClick = (e: any) => {
    if (measureMode === "none") return;
    const { lat, lng } = e.latlng;
    const newPoints = [...measurePoints, [lat, lng] as [number, number]];
    setMeasurePoints(newPoints);

    if (measureMode === "distance" && newPoints.length >= 2) {
      const distance = calculateDistance(newPoints);
      setMeasureResult(distance > 1000 ? `${(distance/1000).toFixed(2)} km` : `${distance.toFixed(0)} m`);
    } else if (measureMode === "area" && newPoints.length >= 3) {
      const area = calculateArea(newPoints);
      setMeasureResult(area > 1000000 ? `${(area/1000000).toFixed(2)} km²` : `${(area/10000).toFixed(2)} ha`);
    }
  };

  const resetMeasure = () => {
    setMeasurePoints([]);
    setMeasureResult("");
  };

  const toggleOverlay = (key: string) => {
    setOverlays(prev => ({ ...prev, [key]: !prev[key] }));
  };

  return (
    <div className="relative h-full">
      <MapContainer
        center={[32.5, 54.5]}
        zoom={6}
        style={{ height: "100%", width: "100%" }}
        scrollWheelZoom={true}
        onClick={handleMapClick}
      >
        <TileLayer
          key={baseLayer}
          url={BASE_LAYERS[baseLayer].url}
          attribution={BASE_LAYERS[baseLayer].attribution}
          maxZoom={BASE_LAYERS[baseLayer].maxZoom}
        />

        {SAMPLE_REGIONS.map(region => (
          <Circle
            key={region.id}
            center={region.center}
            radius={region.radius}
            pathOptions={{
              color: region.color,
              fillColor: region.color,
              fillOpacity: 0.3,
              weight: 2
            }}
            eventHandlers={{ click: () => setSelectedRegion(region) }}
          >
            <Popup>
              <div className="p-2 text-slate-900">
                <h4 className="font-bold">{region.name}</h4>
                <p>مساحت: {region.area}</p>
                <p>NDVI: {region.ndvi}</p>
                <p>وضعیت: {region.status}</p>
              </div>
            </Popup>
          </Circle>
        ))}

        {measurePoints.map((point, idx) => (
          <Circle
            key={idx}
            center={point}
            radius={100}
            pathOptions={{ color: "#f59e0b", fillColor: "#f59e0b", fillOpacity: 0.8 }}
          />
        ))}

        {measureMode === "distance" && measurePoints.length >= 2 && (
          <Polyline
            positions={measurePoints}
            pathOptions={{ color: "#f59e0b", weight: 3, dashArray: "10, 10" }}
          />
        )}
        {measureMode === "area" && measurePoints.length >= 3 && (
          <Polygon
            positions={measurePoints}
            pathOptions={{ color: "#f59e0b", weight: 3, fillColor: "#f59e0b", fillOpacity: 0.3 }}
          />
        )}

        <ScaleControl position="bottomright" metric={true} imperial={false} />
      </MapContainer>

      {/* Toolbar */}
      <div className="absolute top-4 left-4 z-[1000] flex flex-col gap-2">
        <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-2 flex items-center gap-2 w-64">
          <Search className="h-4 w-4 text-slate-400" />
          <input
            type="text"
            placeholder="جستجوی مکان..."
            className="flex-1 bg-transparent text-white text-sm focus:outline-none"
          />
        </div>

        <div className="bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-2 flex gap-2">
          <button
            onClick={() => { setMeasureMode("none"); resetMeasure(); }}
            className={`p-2 rounded-lg transition-colors ${measureMode === "none" ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"}`}
            title="حالت عادی"
          >
            <MapPin className="h-4 w-4" />
          </button>
          <button
            onClick={() => { setMeasureMode("distance"); resetMeasure(); }}
            className={`p-2 rounded-lg transition-colors ${measureMode === "distance" ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"}`}
            title="اندازه‌گیری مسافت"
          >
            <Ruler className="h-4 w-4" />
          </button>
          <button
            onClick={() => { setMeasureMode("area"); resetMeasure(); }}
            className={`p-2 rounded-lg transition-colors ${measureMode === "area" ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"}`}
            title="اندازه‌گیری مساحت"
          >
            <Square className="h-4 w-4" />
          </button>
          <button
            onClick={() => setShowLayerPanel(!showLayerPanel)}
            className={`p-2 rounded-lg transition-colors ${showLayerPanel ? "bg-emerald-600 text-white" : "text-slate-400 hover:bg-slate-800"}`}
            title="لایه‌ها"
          >
            <Layers className="h-4 w-4" />
          </button>
        </div>

        {measureResult && (
          <div className="bg-amber-500/95 backdrop-blur border border-amber-400 rounded-xl p-3 text-white">
            <p className="text-xs text-amber-100">
              {measureMode === "distance" ? "مسافت:" : "مساحت:"}
            </p>
            <p className="text-xl font-bold">{measureResult}</p>
            <button onClick={resetMeasure} className="text-xs text-amber-100 hover:text-white mt-1">
              پاک کردن
            </button>
          </div>
        )}
      </div>

      {/* Layer Panel */}
      {showLayerPanel && (
        <div className="absolute top-4 right-4 z-[1000] bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-4 w-72">
          <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
            <Layers className="h-5 w-5 text-emerald-400" />
            لایه‌های نقشه
          </h3>

          <div className="mb-4">
            <p className="text-xs text-slate-400 mb-2 uppercase">لایه پایه</p>
            <div className="space-y-1">
              {Object.entries(BASE_LAYERS).map(([key, layer]) => (
                <button
                  key={key}
                  onClick={() => setBaseLayer(key as keyof typeof BASE_LAYERS)}
                  className={`w-full text-right px-3 py-2 rounded-lg text-sm transition-colors ${
                    baseLayer === key ? "bg-emerald-600 text-white" : "text-slate-300 hover:bg-slate-800"
                  }`}
                >
                  {layer.name}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="text-xs text-slate-400 mb-2 uppercase">لایه‌های پوششی</p>
            <div className="space-y-1">
              {Object.entries(OVERLAY_LAYERS).map(([key, layer]) => (
                <button
                  key={key}
                  onClick={() => toggleOverlay(key)}
                  className={`w-full text-right px-3 py-2 rounded-lg text-sm transition-colors flex items-center justify-between ${
                    overlays[key] ? "bg-slate-800 text-white" : "text-slate-400 hover:bg-slate-800"
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: layer.color }} />
                    {layer.name}
                  </span>
                  {overlays[key] ? <Eye className="h-4 w-4" /> : <EyeOff className="h-4 w-4" />}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Region Info */}
      {selectedRegion && (
        <div className="absolute bottom-4 right-4 z-[1000] bg-slate-900/95 backdrop-blur border border-slate-700 rounded-xl p-4 w-80">
          <div className="flex items-start justify-between mb-3">
            <div>
              <h3 className="text-lg font-bold text-white">{selectedRegion.name}</h3>
              <p className="text-sm text-slate-400">{selectedRegion.area}</p>
            </div>
            <button onClick={() => setSelectedRegion(null)} className="text-slate-400 hover:text-white">✕</button>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">NDVI:</span>
              <span className="text-white font-bold">{selectedRegion.ndvi}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-slate-400">وضعیت:</span>
              <span className="px-2 py-0.5 rounded-full text-xs" style={{ backgroundColor: selectedRegion.color + "20", color: selectedRegion.color }}>
                {selectedRegion.status}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Instructions */}
      {measureMode !== "none" && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 z-[1000] bg-amber-500/95 backdrop-blur border border-amber-400 rounded-xl p-4 text-white pointer-events-none">
          <p className="font-bold mb-1">
            {measureMode === "distance" ? "📏 اندازه‌گیری مسافت" : "📐 اندازه‌گیری مساحت"}
          </p>
          <p className="text-sm">روی نقشه کلیک کنید • نقاط: {measurePoints.length}</p>
        </div>
      )}
    </div>
  );
}
'''
    
    write_file(WEB / "components" / "gis" / "AdvancedGISMap.tsx", content)


# ========== 2. به‌روزرسانی صفحه GIS ==========
def update_gis_page():
    print("\n🔄 به‌روزرسانی صفحه GIS...")
    
    content = '''"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { 
  ArrowRight, Map as MapIcon, Layers, Ruler, Leaf, TrendingUp, 
  Mountain, Satellite, Compass, Globe
} from "lucide-react";
import AdvancedGISMap from "@/components/gis/AdvancedGISMap";

export default function GisPage() {
  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-500 to-purple-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-16">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-6 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-6">
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

      {/* Interactive Map */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden">
          <div className="p-5 border-b border-slate-800 flex items-center justify-between">
            <h3 className="text-xl font-bold text-white flex items-center gap-2">
              <Satellite className="h-5 w-5 text-violet-400" />
              نقشه تعاملی پیشرفته
            </h3>
            <div className="flex gap-2 text-sm text-slate-400">
              <span className="flex items-center gap-1">
                <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                Live
              </span>
            </div>
          </div>
          
          <div className="h-[700px] relative">
            <AdvancedGISMap />
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="container mx-auto px-6 py-8">
        <h3 className="text-2xl font-bold text-white mb-6">قابلیت‌های GIS</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { icon: Layers, title: "لایه‌های ماهواره‌ای", description: "دسترسی به تصاویر Sentinel-2، Landsat، MODIS", color: "from-violet-500 to-purple-600" },
            { icon: Ruler, title: "ابزارهای اندازه‌گیری", description: "محاسبه دقیق مسافت، مساحت و محیط", color: "from-blue-500 to-cyan-600" },
            { icon: TrendingUp, title: "شاخص‌های طیفی", description: "NDVI، EVI، SAVI، NDWI و سایر شاخص‌ها", color: "from-emerald-500 to-green-600" },
            { icon: Mountain, title: "تحلیل توپوگرافی", description: "شیب، جهت، TWI و مدل‌های ارتفاعی", color: "from-amber-500 to-orange-600" },
            { icon: Compass, title: "تحلیل حوضه آبریز", description: "delineation حوضه، جهت جریان، تجمع جریان", color: "from-sky-500 to-blue-600" },
            { icon: Globe, title: "خروجی‌های استاندارد", description: "GeoJSON، Shapefile، KML و گزارش PDF", color: "from-rose-500 to-pink-600" },
          ].map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.05 }}
              className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6 hover:border-slate-700 transition-all"
            >
              <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.color} mb-4`}>
                <feature.icon className="h-6 w-6 text-white" />
              </div>
              <h4 className="text-xl font-bold text-white mb-2">{feature.title}</h4>
              <p className="text-slate-400 leading-relaxed">{feature.description}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Satellites */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <Satellite className="h-5 w-5 text-violet-400" />
            ماهواره‌های در دسترس
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { name: "Sentinel-2", org: "ESA", res: "10m", revisit: "5 روز", color: "#3b82f6" },
              { name: "Landsat 8/9", org: "NASA", res: "30m", revisit: "16 روز", color: "#10b981" },
              { name: "MODIS", org: "NASA", res: "250m", revisit: "روزانه", color: "#f59e0b" },
              { name: "SRTM", org: "NASA", res: "30m", revisit: "DEM", color: "#8b5cf6" },
            ].map((sat) => (
              <div key={sat.name} className="p-4 bg-slate-800/50 rounded-xl border border-slate-700">
                <div className="flex items-center gap-2 mb-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: sat.color }} />
                  <h4 className="font-bold text-white">{sat.name}</h4>
                </div>
                <p className="text-xs text-slate-400 mb-1">{sat.org}</p>
                <div className="flex justify-between text-xs text-slate-300">
                  <span>وضوح: {sat.res}</span>
                  <span>بازگشت: {sat.revisit}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}
'''
    
    write_file(WEB / "app" / "gis" / "page.tsx", content)


# ========== Main ==========
def main():
    print("🗺️ فاز ۱: توسعه هسته GIS پیشرفته")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    create_advanced_map()
    update_gis_page()
    
    print("\n" + "=" * 70)
    print("✅ فایل‌ها ایجاد شدند!")
    print("\n📦 نصب کتابخانه‌ها (دستی):")
    print("   cd apps\\web")
    print("   pnpm add leaflet react-leaflet @types/leaflet")
    print("")
    print("🚀 گام بعدی:")
    print("   1. نصب کتابخانه‌ها (دستور بالا)")
    print("   2. پاک‌سازی کش:")
    print("      Remove-Item .next -Recurse -Force")
    print("   3. اجرا: pnpm run dev -- -p 3001")
    print("   4. مشاهده: http://localhost:3001/gis")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())