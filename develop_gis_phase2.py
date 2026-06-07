#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌱 فاز ۲: شاخص‌های طیفی
- محاسبه NDVI, EVI, SAVI, NDWI, NBR, LST
- نقشه‌های حرارتی با رنگ‌بندی علمی
- تحلیل زمانی و مقایسه شاخص‌ها
- آمار منطقه‌ای
"""
import sys
from pathlib import Path

ROOT = Path(__file__).parent.resolve()
WEB = ROOT / "apps" / "web" / "src"


def write_file(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"   ✅ {path.relative_to(ROOT)} ({path.stat().st_size} bytes)")


# ========== 1. کتابخانه محاسبات شاخص‌های طیفی ==========
def create_spectral_calculations():
    print("\n🧮 ایجاد spectralCalculations.ts...")
    
    content = '''// lib/spectralCalculations.ts
// محاسبات شاخص‌های طیفی برای تحلیل پوشش گیاهی و محیط زیست

export interface SpectralBands {
  blue?: number;
  green?: number;
  red?: number;
  nir?: number;
  swir1?: number;
  swir2?: number;
}

export interface SpectralIndex {
  name: string;
  fullName: string;
  formula: string;
  value: number;
  interpretation: string;
  color: string;
  category: "vegetation" | "water" | "soil" | "fire" | "temperature";
}

// ============ شاخص‌های پوشش گیاهی ============

export function calculateNDVI(bands: SpectralBands): number {
  // Normalized Difference Vegetation Index
  // NDVI = (NIR - Red) / (NIR + Red)
  if (!bands.nir || !bands.red) return 0;
  const numerator = bands.nir - bands.red;
  const denominator = bands.nir + bands.red;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateEVI(bands: SpectralBands): number {
  // Enhanced Vegetation Index
  // EVI = 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
  if (!bands.nir || !bands.red || !bands.blue) return 0;
  const numerator = 2.5 * (bands.nir - bands.red);
  const denominator = bands.nir + 6 * bands.red - 7.5 * bands.blue + 1;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateSAVI(bands: SpectralBands, L: number = 0.5): number {
  // Soil Adjusted Vegetation Index
  // SAVI = ((NIR - Red) / (NIR + Red + L)) * (1 + L)
  if (!bands.nir || !bands.red) return 0;
  const numerator = bands.nir - bands.red;
  const denominator = bands.nir + bands.red + L;
  if (denominator === 0) return 0;
  return (numerator / denominator) * (1 + L);
}

export function calculateMSAVI2(bands: SpectralBands): number {
  // Modified Soil Adjusted Vegetation Index 2
  // MSAVI2 = (2*NIR + 1 - sqrt((2*NIR + 1)^2 - 8*(NIR - Red))) / 2
  if (!bands.nir || !bands.red) return 0;
  const term1 = 2 * bands.nir + 1;
  const term2 = Math.sqrt(term1 * term1 - 8 * (bands.nir - bands.red));
  return (term1 - term2) / 2;
}

// ============ شاخص‌های آب ============

export function calculateNDWI(bands: SpectralBands): number {
  // Normalized Difference Water Index
  // NDWI = (Green - NIR) / (Green + NIR)
  if (!bands.green || !bands.nir) return 0;
  const numerator = bands.green - bands.nir;
  const denominator = bands.green + bands.nir;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateMNDWI(bands: SpectralBands): number {
  // Modified Normalized Difference Water Index
  // MNDWI = (Green - SWIR1) / (Green + SWIR1)
  if (!bands.green || !bands.swir1) return 0;
  const numerator = bands.green - bands.swir1;
  const denominator = bands.green + bands.swir1;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

// ============ شاخص‌های خاک ============

export function calculateNDSI(bands: SpectralBands): number {
  // Normalized Difference Soil Index
  // NDSI = (SWIR1 - NIR) / (SWIR1 + NIR)
  if (!bands.swir1 || !bands.nir) return 0;
  const numerator = bands.swir1 - bands.nir;
  const denominator = bands.swir1 + bands.nir;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateBI(bands: SpectralBands): number {
  // Brightness Index
  // BI = sqrt((Red^2 + Green^2 + NIR^2) / 3)
  if (!bands.red || !bands.green || !bands.nir) return 0;
  return Math.sqrt((bands.red * bands.red + bands.green * bands.green + bands.nir * bands.nir) / 3);
}

// ============ شاخص‌های آتش‌سوزی ============

export function calculateNBR(bands: SpectralBands): number {
  // Normalized Burn Ratio
  // NBR = (NIR - SWIR2) / (NIR + SWIR2)
  if (!bands.nir || !bands.swir2) return 0;
  const numerator = bands.nir - bands.swir2;
  const denominator = bands.nir + bands.swir2;
  if (denominator === 0) return 0;
  return numerator / denominator;
}

export function calculateBAI(bands: SpectralBands): number {
  // Burned Area Index
  // BAI = 1 / ((0.1 - Red)^2 + (0.06 - NIR)^2)
  if (!bands.red || !bands.nir) return 0;
  const term1 = Math.pow(0.1 - bands.red, 2);
  const term2 = Math.pow(0.06 - bands.nir, 2);
  if (term1 + term2 === 0) return 0;
  return 1 / (term1 + term2);
}

// ============ توابع کمکی ============

export function interpretNDVI(value: number): { text: string; color: string } {
  if (value < -0.1) return { text: "آب، برف، یا ابر", color: "#1e40af" };
  if (value < 0.1) return { text: "خاک برهنه یا منطقه شهری", color: "#92400e" };
  if (value < 0.2) return { text: "پوشش گیاهی بسیار کم", color: "#fbbf24" };
  if (value < 0.4) return { text: "پوشش گیاهی کم", color: "#f59e0b" };
  if (value < 0.6) return { text: "پوشش گیاهی متوسط", color: "#84cc16" };
  if (value < 0.8) return { text: "پوشش گیاهی متراکم", color: "#22c55e" };
  return { text: "جنگل متراکم", color: "#15803d" };
}

export function interpretNDWI(value: number): { text: string; color: string } {
  if (value < -0.3) return { text: "خاک خشک", color: "#92400e" };
  if (value < 0) return { text: "پوشش گیاهی یا خاک مرطوب", color: "#ca8a04" };
  if (value < 0.3) return { text: "رطوبت سطحی", color: "#0ea5e9" };
  if (value < 0.6) return { text: "آب کم‌عمق", color: "#0284c7" };
  return { text: "آب عمیق", color: "#1e40af" };
}

export function interpretNBR(value: number): { text: string; color: string } {
  if (value < -0.25) return { text: "سوختگی شدید", color: "#7f1d1d" };
  if (value < -0.1) return { text: "سوختگی متوسط-شدید", color: "#dc2626" };
  if (value < 0.1) return { text: "سوختگی کم-متوسط", color: "#f59e0b" };
  if (value < 0.27) return { text: "منطقه نسوخته", color: "#84cc16" };
  if (value < 0.44) return { text: "پوشش گیاهی متراکم", color: "#22c55e" };
  return { text: "جنگل متراکم", color: "#15803d" };
}

export function calculateAllIndices(bands: SpectralBands): SpectralIndex[] {
  return [
    {
      name: "NDVI",
      fullName: "Normalized Difference Vegetation Index",
      formula: "(NIR - Red) / (NIR + Red)",
      value: calculateNDVI(bands),
      interpretation: interpretNDVI(calculateNDVI(bands)).text,
      color: interpretNDVI(calculateNDVI(bands)).color,
      category: "vegetation"
    },
    {
      name: "EVI",
      fullName: "Enhanced Vegetation Index",
      formula: "2.5×(NIR-Red)/(NIR+6Red-7.5Blue+1)",
      value: calculateEVI(bands),
      interpretation: "حساس‌تر در مناطق با پوشش متراکم",
      color: "#10b981",
      category: "vegetation"
    },
    {
      name: "SAVI",
      fullName: "Soil Adjusted Vegetation Index",
      formula: "((NIR-Red)/(NIR+Red+0.5))×1.5",
      value: calculateSAVI(bands),
      interpretation: "مناسب برای مناطق با خاک نمایان",
      color: "#84cc16",
      category: "vegetation"
    },
    {
      name: "NDWI",
      fullName: "Normalized Difference Water Index",
      formula: "(Green - NIR) / (Green + NIR)",
      value: calculateNDWI(bands),
      interpretation: interpretNDWI(calculateNDWI(bands)).text,
      color: interpretNDWI(calculateNDWI(bands)).color,
      category: "water"
    },
    {
      name: "NBR",
      fullName: "Normalized Burn Ratio",
      formula: "(NIR - SWIR2) / (NIR + SWIR2)",
      value: calculateNBR(bands),
      interpretation: interpretNBR(calculateNBR(bands)).text,
      color: interpretNBR(calculateNBR(bands)).color,
      category: "fire"
    }
  ];
}

// ============ تولید داده‌های نمونه برای نقشه حرارتی ============

export function generateHeatmapData(
  center: [number, number],
  radius: number,
  indexType: "NDVI" | "EVI" | "SAVI" | "NDWI" | "NBR",
  resolution: number = 20
): Array<{ lat: number; lng: number; value: number }> {
  const data: Array<{ lat: number; lng: number; value: number }> = [];
  
  for (let i = 0; i < resolution; i++) {
    for (let j = 0; j < resolution; j++) {
      const lat = center[0] + (i - resolution/2) * (radius / resolution) / 111000;
      const lng = center[1] + (j - resolution/2) * (radius / resolution) / (111000 * Math.cos(center[0] * Math.PI / 180));
      
      // تولید مقدار بر اساس نوع شاخص
      let value: number;
      const distance = Math.sqrt(Math.pow(i - resolution/2, 2) + Math.pow(j - resolution/2, 2)) / (resolution/2);
      const noise = (Math.random() - 0.5) * 0.2;
      
      switch (indexType) {
        case "NDVI":
          value = 0.8 - distance * 0.6 + noise;
          break;
        case "EVI":
          value = 0.6 - distance * 0.5 + noise;
          break;
        case "SAVI":
          value = 0.7 - distance * 0.55 + noise;
          break;
        case "NDWI":
          value = -0.3 + distance * 0.8 + noise;
          break;
        case "NBR":
          value = 0.5 - distance * 0.7 + noise;
          break;
        default:
          value = 0.5 + noise;
      }
      
      // محدود کردن مقدار
      value = Math.max(-1, Math.min(1, value));
      
      data.push({ lat, lng, value });
    }
  }
  
  return data;
}

// ============ رنگ‌بندی نقشه حرارتی ============

export function getHeatmapColor(value: number, indexType: string): string {
  // نرمال‌سازی مقدار به بازه 0-1
  const normalized = (value + 1) / 2;
  
  switch (indexType) {
    case "NDVI":
    case "EVI":
    case "SAVI":
      // قرمز (کم) → زرد → سبز (زیاد)
      if (normalized < 0.3) return `rgba(220, 38, 38, ${0.3 + normalized})`;
      if (normalized < 0.5) return `rgba(251, 191, 36, ${0.4 + normalized * 0.5})`;
      if (normalized < 0.7) return `rgba(132, 204, 22, ${0.5 + normalized * 0.4})`;
      return `rgba(34, 197, 94, ${0.6 + normalized * 0.3})`;
    
    case "NDWI":
      // قهوه‌ای (خشک) → آبی (تر)
      if (normalized < 0.3) return `rgba(146, 64, 14, ${0.3 + normalized})`;
      if (normalized < 0.5) return `rgba(202, 138, 4, ${0.4 + normalized * 0.5})`;
      if (normalized < 0.7) return `rgba(14, 165, 233, ${0.5 + normalized * 0.4})`;
      return `rgba(30, 64, 175, ${0.6 + normalized * 0.3})`;
    
    case "NBR":
      // قرمز (سوخته) → سبز (سالم)
      if (normalized < 0.3) return `rgba(127, 29, 29, ${0.3 + normalized})`;
      if (normalized < 0.5) return `rgba(220, 38, 38, ${0.4 + normalized * 0.5})`;
      if (normalized < 0.7) return `rgba(245, 158, 11, ${0.5 + normalized * 0.4})`;
      return `rgba(34, 197, 94, ${0.6 + normalized * 0.3})`;
    
    default:
      return `rgba(100, 116, 139, ${0.5 + normalized * 0.4})`;
  }
}
'''
    
    write_file(WEB / "lib" / "spectralCalculations.ts", content)


# ========== 2. کامپوننت شاخص‌های طیفی ==========
def create_spectral_indices_component():
    print("\n🌱 ایجاد SpectralIndices.tsx...")
    
    content = '''"use client";

import { useState, useMemo } from "react";
import dynamic from "next/dynamic";
import { 
  Leaf, Droplets, Flame, BarChart3, TrendingUp, 
  Download, Info, Layers, Calculator
} from "lucide-react";
import {
  calculateAllIndices,
  interpretNDVI,
  interpretNDWI,
  interpretNBR,
  generateHeatmapData,
  getHeatmapColor,
  type SpectralBands,
  type SpectralIndex
} from "@/lib/spectralCalculations";

const MapContainer = dynamic(() => import("react-leaflet").then(mod => mod.MapContainer), { ssr: false });
const TileLayer = dynamic(() => import("react-leaflet").then(mod => mod.TileLayer), { ssr: false });
const CircleMarker = dynamic(() => import("react-leaflet").then(mod => mod.CircleMarker), { ssr: false });
const Popup = dynamic(() => import("react-leaflet").then(mod => mod.Popup), { ssr: false });
const ScaleControl = dynamic(() => import("react-leaflet").then(mod => mod.ScaleControl), { ssr: false });

interface SpectralIndicesProps {
  regionCenter?: [number, number];
  regionName?: string;
}

const SAMPLE_REGIONS = [
  { name: "حوضه کشف‌رود", center: [36.3, 59.6] as [number, number], type: "agricultural" },
  { name: "دشت کویر", center: [33.5, 54.5] as [number, number], type: "arid" },
  { name: "زاگرس مرکزی", center: [31.5, 51.5] as [number, number], type: "forest" },
  { name: "بلوچستان", center: [28.5, 60.5] as [number, number], type: "arid" },
  { name: "آذربایجان", center: [38.0, 46.5] as [number, number], type: "agricultural" },
];

const INDEX_TYPES = [
  { id: "NDVI", name: "NDVI", fullName: "Normalized Difference Vegetation Index", icon: Leaf, color: "#22c55e", category: "vegetation" },
  { id: "EVI", name: "EVI", fullName: "Enhanced Vegetation Index", icon: Leaf, color: "#10b981", category: "vegetation" },
  { id: "SAVI", name: "SAVI", fullName: "Soil Adjusted Vegetation Index", icon: Leaf, color: "#84cc16", category: "vegetation" },
  { id: "NDWI", name: "NDWI", fullName: "Normalized Difference Water Index", icon: Droplets, color: "#0ea5e9", category: "water" },
  { id: "NBR", name: "NBR", fullName: "Normalized Burn Ratio", icon: Flame, color: "#ef4444", category: "fire" },
];

export default function SpectralIndices({ regionCenter, regionName }: SpectralIndicesProps) {
  const [selectedRegion, setSelectedRegion] = useState(regionCenter || SAMPLE_REGIONS[0].center);
  const [selectedRegionName, setSelectedRegionName] = useState(regionName || SAMPLE_REGIONS[0].name);
  const [selectedIndex, setSelectedIndex] = useState("NDVI");
  const [showHeatmap, setShowHeatmap] = useState(true);
  const [heatmapResolution, setHeatmapResolution] = useState(20);
  
  // محاسبه شاخص‌ها برای نقطه مرکزی
  const sampleBands: SpectralBands = useMemo(() => {
    // شبیه‌سازی باندهای طیفی بر اساس نوع منطقه
    const region = SAMPLE_REGIONS.find(r => r.center[0] === selectedRegion[0] && r.center[1] === selectedRegion[1]);
    
    if (region?.type === "forest") {
      return { blue: 0.08, green: 0.10, red: 0.06, nir: 0.45, swir1: 0.20, swir2: 0.10 };
    } else if (region?.type === "arid") {
      return { blue: 0.15, green: 0.18, red: 0.25, nir: 0.30, swir1: 0.35, swir2: 0.30 };
    } else {
      return { blue: 0.10, green: 0.12, red: 0.10, nir: 0.38, swir1: 0.25, swir2: 0.15 };
    }
  }, [selectedRegion]);
  
  const indices = useMemo(() => calculateAllIndices(sampleBands), [sampleBands]);
  const currentIndex = indices.find(i => i.name === selectedIndex);
  
  // تولید داده‌های نقشه حرارتی
  const heatmapData = useMemo(() => {
    if (!showHeatmap) return [];
    return generateHeatmapData(
      selectedRegion,
      50000, // 50km radius
      selectedIndex as any,
      heatmapResolution
    );
  }, [selectedRegion, selectedIndex, showHeatmap, heatmapResolution]);

  const handleRegionChange = (region: typeof SAMPLE_REGIONS[0]) => {
    setSelectedRegion(region.center);
    setSelectedRegionName(region.name);
  };

  const exportResults = () => {
    const report = {
      region: selectedRegionName,
      coordinates: selectedRegion,
      timestamp: new Date().toISOString(),
      spectralBands: sampleBands,
      indices: indices,
    };
    
    const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `spectral_analysis_${selectedRegionName}_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-l from-emerald-600/20 to-green-600/20 border border-emerald-500/30 rounded-2xl p-6">
        <div className="flex items-start gap-4">
          <div className="p-3 rounded-xl bg-gradient-to-br from-emerald-500 to-green-600">
            <Leaf className="h-8 w-8 text-white" />
          </div>
          <div className="flex-1">
            <h2 className="text-2xl font-black text-white mb-2">تحلیل شاخص‌های طیفی</h2>
            <p className="text-slate-300">
              محاسبه NDVI، EVI، SAVI، NDWI و NBR برای تحلیل پوشش گیاهی، آب و آتش‌سوزی
            </p>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Region Selector */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <Layers className="h-4 w-4 text-emerald-400" />
            انتخاب منطقه
          </h3>
          <div className="space-y-2">
            {SAMPLE_REGIONS.map(region => (
              <button
                key={region.name}
                onClick={() => handleRegionChange(region)}
                className={`w-full text-right px-3 py-2 rounded-lg text-sm transition-colors ${
                  selectedRegion[0] === region.center[0] && selectedRegion[1] === region.center[1]
                    ? "bg-emerald-600 text-white"
                    : "bg-slate-800/50 text-slate-300 hover:bg-slate-800"
                }`}
              >
                {region.name}
                <span className="text-xs text-slate-400 mr-2">
                  ({region.type === "forest" ? "جنگل" : region.type === "arid" ? "خشک" : "کشاورزی"})
                </span>
              </button>
            ))}
          </div>
        </div>

        {/* Index Selector */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <Calculator className="h-4 w-4 text-emerald-400" />
            انتخاب شاخص
          </h3>
          <div className="space-y-2">
            {INDEX_TYPES.map(index => (
              <button
                key={index.id}
                onClick={() => setSelectedIndex(index.id)}
                className={`w-full text-right px-3 py-2 rounded-lg text-sm transition-colors flex items-center gap-2 ${
                  selectedIndex === index.id
                    ? "bg-emerald-600 text-white"
                    : "bg-slate-800/50 text-slate-300 hover:bg-slate-800"
                }`}
              >
                <index.icon className="h-4 w-4" style={{ color: selectedIndex === index.id ? "white" : index.color }} />
                <div className="flex-1">
                  <div className="font-bold">{index.name}</div>
                  <div className="text-xs opacity-70">{index.fullName}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Current Index Result */}
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-emerald-400" />
            نتیجه تحلیل
          </h3>
          
          {currentIndex && (
            <div className="space-y-4">
              <div className="text-center p-4 rounded-xl" style={{ backgroundColor: currentIndex.color + "20" }}>
                <p className="text-xs text-slate-400 mb-1">{currentIndex.name}</p>
                <p className="text-4xl font-black text-white mb-2">
                  {currentIndex.value.toFixed(3)}
                </p>
                <p className="text-sm" style={{ color: currentIndex.color }}>
                  {currentIndex.interpretation}
                </p>
              </div>
              
              <div className="text-xs text-slate-400 space-y-1">
                <p><strong>فرمول:</strong> {currentIndex.formula}</p>
                <p><strong>دسته:</strong> {
                  currentIndex.category === "vegetation" ? "پوشش گیاهی" :
                  currentIndex.category === "water" ? "آب" :
                  currentIndex.category === "fire" ? "آتش‌سوزی" : "خاک"
                }</p>
              </div>
              
              <button
                onClick={exportResults}
                className="w-full py-2 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg text-sm font-bold flex items-center justify-center gap-2"
              >
                <Download className="h-4 w-4" />
                دانلود نتایج
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Heatmap Controls */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-emerald-400" />
            نقشه حرارتی {selectedIndex}
          </h3>
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 text-sm text-slate-300">
              <input
                type="checkbox"
                checked={showHeatmap}
                onChange={(e) => setShowHeatmap(e.target.checked)}
                className="rounded border-slate-700 bg-slate-800"
              />
              نمایش نقشه
            </label>
            <div className="flex items-center gap-2">
              <span className="text-xs text-slate-400">وضوح:</span>
              <input
                type="range"
                min="10"
                max="30"
                value={heatmapResolution}
                onChange={(e) => setHeatmapResolution(parseInt(e.target.value))}
                className="w-24 accent-emerald-500"
              />
              <span className="text-xs text-slate-300 w-8">{heatmapResolution}</span>
            </div>
          </div>
        </div>

        {/* Heatmap Legend */}
        <div className="mb-4">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
            <span>کم</span>
            <div className="flex-1 mx-4 h-4 rounded-full" style={{
              background: selectedIndex === "NDWI" 
                ? "linear-gradient(to right, #92400e, #ca8a04, #0ea5e9, #1e40af)"
                : selectedIndex === "NBR"
                ? "linear-gradient(to right, #7f1d1d, #dc2626, #f59e0b, #22c55e)"
                : "linear-gradient(to right, #dc2626, #fbbf24, #84cc16, #22c55e)"
            }} />
            <span>زیاد</span>
          </div>
        </div>
      </div>

      {/* Heatmap Visualization */}
      {showHeatmap && (
        <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
          <div className="h-[500px] relative">
            <MapContainer
              center={selectedRegion}
              zoom={8}
              style={{ height: "100%", width: "100%" }}
              scrollWheelZoom={true}
            >
              <TileLayer
                url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                attribution="&copy; Esri"
              />
              
              {heatmapData.map((point, idx) => (
                <CircleMarker
                  key={idx}
                  center={[point.lat, point.lng]}
                  radius={8}
                  pathOptions={{
                    color: getHeatmapColor(point.value, selectedIndex),
                    fillColor: getHeatmapColor(point.value, selectedIndex),
                    fillOpacity: 0.7,
                    weight: 1,
                  }}
                >
                  <Popup>
                    <div className="p-2 text-slate-900">
                      <p className="font-bold">{selectedIndex}: {point.value.toFixed(3)}</p>
                      <p className="text-xs">
                        مختصات: {point.lat.toFixed(4)}, {point.lng.toFixed(4)}
                      </p>
                    </div>
                  </Popup>
                </CircleMarker>
              ))}
              
              <ScaleControl position="bottomright" metric={true} imperial={false} />
            </MapContainer>
          </div>
        </div>
      )}

      {/* All Indices Comparison */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
          <Info className="h-5 w-5 text-emerald-400" />
          مقایسه تمام شاخص‌ها
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {indices.map(index => (
            <div
              key={index.name}
              className="p-4 rounded-xl border border-slate-700 hover:border-slate-600 transition-colors"
              style={{ backgroundColor: index.color + "10" }}
            >
              <div className="flex items-center gap-2 mb-2">
                <div className="w-3 h-3 rounded-full" style={{ backgroundColor: index.color }} />
                <h4 className="font-bold text-white">{index.name}</h4>
              </div>
              <p className="text-2xl font-black text-white mb-1">{index.value.toFixed(3)}</p>
              <p className="text-xs text-slate-400">{index.interpretation}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Scientific Information */}
      <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
        <h3 className="text-lg font-bold text-white mb-4">📚 اطلاعات علمی</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-bold text-emerald-400 mb-2">شاخص‌های پوشش گیاهی</h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li><strong>NDVI:</strong> استاندارد طلایی برای پایش پوشش گیاهی. بازه: -1 تا 1</li>
              <li><strong>EVI:</strong> بهبود یافته NDVI، حساس‌تر در مناطق متراکم. بازه: -1 تا 1</li>
              <li><strong>SAVI:</strong> تصحیح اثر خاک، مناسب مناطق کم‌پوشش. بازه: -1 تا 1</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-bold text-blue-400 mb-2">شاخص‌های آب و آتش</h4>
            <ul className="space-y-2 text-sm text-slate-300">
              <li><strong>NDWI:</strong> شناسایی آب سطحی و رطوبت. بازه: -1 تا 1</li>
              <li><strong>NBR:</strong> ارزیابی شدت آتش‌سوزی. بازه: -1 تا 1</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-6 p-4 bg-emerald-500/10 border border-emerald-500/30 rounded-xl">
          <p className="text-sm text-emerald-300">
            <strong>💡 نکته:</strong> این شاخص‌ها از باندهای طیفی Sentinel-2 و Landsat محاسبه می‌شوند.
            برای تحلیل دقیق‌تر، به داده‌های واقعی ماهواره‌ای نیاز است.
          </p>
        </div>
      </div>
    </div>
  );
}
'''
    
    write_file(WEB / "components" / "gis" / "SpectralIndices.tsx", content)


# ========== 3. به‌روزرسانی صفحه GIS ==========
def update_gis_page():
    print("\n🔄 به‌روزرسانی صفحه GIS با تب شاخص‌های طیفی...")
    
    content = '''"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { useState } from "react";
import { motion } from "framer-motion";
import { 
  ArrowRight, Map as MapIcon, Layers, Ruler, Leaf, TrendingUp, 
  Mountain, Satellite, Compass, Globe, Database, Download, 
  Search, Square, Target, Save, Printer, Navigation, Crosshair,
  BarChart3, Droplets, Flame
} from "lucide-react";

// Dynamic imports - SSR disabled
const ProductionGIS = dynamic(() => import("@/components/gis/ProductionGIS"), {
  ssr: false,
  loading: () => (
    <div className="h-full w-full flex items-center justify-center bg-slate-900">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mb-4"></div>
        <p className="text-slate-400">در حال بارگذاری نقشه...</p>
      </div>
    </div>
  ),
});

const SpectralIndices = dynamic(() => import("@/components/gis/SpectralIndices"), {
  ssr: false,
  loading: () => (
    <div className="h-96 flex items-center justify-center bg-slate-900 rounded-xl">
      <div className="text-center">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-emerald-500 mb-4"></div>
        <p className="text-slate-400">در حال بارگذاری تحلیل طیفی...</p>
      </div>
    </div>
  ),
});

export default function GisPage() {
  const [activeTab, setActiveTab] = useState<"map" | "spectral">("map");

  return (
    <div className="min-h-screen bg-slate-950">
      {/* Hero */}
      <section className="relative overflow-hidden border-b border-slate-800">
        <div className="absolute inset-0 bg-gradient-to-br from-violet-500 to-purple-600 opacity-20" />
        <div className="absolute inset-0 bg-gradient-to-b from-transparent via-slate-950/50 to-slate-950" />
        
        <div className="relative container mx-auto px-6 py-12">
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
            <Link href="/" className="inline-flex items-center gap-2 text-emerald-400 hover:text-emerald-300 mb-4 text-sm">
              <ArrowRight className="h-4 w-4" /> بازگشت به صفحه اصلی
            </Link>
            
            <div className="flex items-start gap-6 mb-4">
              <div className="p-4 rounded-3xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-2xl">
                <MapIcon className="h-10 w-10 text-white" />
              </div>
              <div className="flex-1">
                <p className="text-violet-400 text-sm font-medium mb-1">ماژول تخصصی GIS</p>
                <h1 className="text-4xl md:text-5xl font-black text-white mb-2">تحلیل مکانی و طیفی</h1>
                <p className="text-lg text-slate-300 max-w-3xl leading-relaxed">
                  نقشه تعاملی با لایه‌های ماهواره‌ای، ابزارهای اندازه‌گیری، ثبت لوکیشن و تحلیل شاخص‌های طیفی
                </p>
              </div>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Tabs */}
      <section className="container mx-auto px-6 py-6">
        <div className="flex gap-2 mb-6">
          <button
            onClick={() => setActiveTab("map")}
            className={`px-6 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
              activeTab === "map"
                ? "bg-violet-600 text-white shadow-lg shadow-violet-500/30"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <MapIcon className="h-5 w-5" />
            نقشه تعاملی
          </button>
          <button
            onClick={() => setActiveTab("spectral")}
            className={`px-6 py-3 rounded-xl font-bold transition-all flex items-center gap-2 ${
              activeTab === "spectral"
                ? "bg-emerald-600 text-white shadow-lg shadow-emerald-500/30"
                : "bg-slate-800 text-slate-400 hover:bg-slate-700"
            }`}
          >
            <Leaf className="h-5 w-5" />
            تحلیل شاخص‌های طیفی
          </button>
        </div>

        {/* Map Tab */}
        {activeTab === "map" && (
          <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl overflow-hidden">
            <div className="p-4 border-b border-slate-800 flex items-center justify-between flex-wrap gap-2">
              <h3 className="text-lg font-bold text-white flex items-center gap-2">
                <Satellite className="h-5 w-5 text-violet-400" />
                نقشه تعاملی
              </h3>
              <div className="flex gap-2 text-xs text-slate-400">
                <span className="flex items-center gap-1 px-2 py-1 bg-emerald-500/10 rounded-lg">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                  Live
                </span>
                <span className="px-2 py-1 bg-slate-800 rounded-lg">۵ لایه پایه</span>
                <span className="px-2 py-1 bg-slate-800 rounded-lg">۵ لایه پوششی</span>
              </div>
            </div>
            
            <div className="h-[700px] relative">
              <ProductionGIS />
            </div>
          </div>
        )}

        {/* Spectral Tab */}
        {activeTab === "spectral" && (
          <SpectralIndices />
        )}
      </section>

      {/* Features Grid */}
      <section className="container mx-auto px-6 py-8">
        <h3 className="text-2xl font-bold text-white mb-6">قابلیت‌های فعال</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { icon: Layers, title: "لایه‌های ماهواره‌ای", desc: "۵ لایه پایه + ۵ پوششی", color: "text-violet-400" },
            { icon: Ruler, title: "اندازه‌گیری مسافت", desc: "با فرمول Haversine", color: "text-blue-400" },
            { icon: Square, title: "اندازه‌گیری مساحت", desc: "با فرمول Shoelace", color: "text-cyan-400" },
            { icon: Target, title: "اندازه‌گیری شعاع", desc: "شعاع و مساحت دایره", color: "text-purple-400" },
            { icon: Search, title: "جستجوی جهانی", desc: "Nominatim (OSM)", color: "text-emerald-400" },
            { icon: Save, title: "ثبت لوکیشن", desc: "با دسته‌بندی و برچسب", color: "text-amber-400" },
            { icon: Leaf, title: "شاخص NDVI", desc: "پوشش گیاهی", color: "text-green-400" },
            { icon: Droplets, title: "شاخص NDWI", desc: "آب سطحی", color: "text-sky-400" },
            { icon: Flame, title: "شاخص NBR", desc: "آتش‌سوزی", color: "text-red-400" },
            { icon: BarChart3, title: "نقشه حرارتی", desc: "تصویرسازی داده‌ها", color: "text-orange-400" },
            { icon: Download, title: "خروجی چند فرمت", desc: "GeoJSON, KML, JSON", color: "text-pink-400" },
            { icon: Crosshair, title: "مختصات زنده", desc: "نمایش موقعیت ماوس", color: "text-teal-400" },
          ].map((feature, i) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: i * 0.03 }}
              className="bg-slate-900/50 backdrop-blur border border-slate-800 rounded-xl p-4 hover:border-slate-700 transition-all"
            >
              <feature.icon className={`h-6 w-6 mb-2 ${feature.color}`} />
              <h4 className="font-bold text-white mb-1 text-sm">{feature.title}</h4>
              <p className="text-xs text-slate-400">{feature.desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Satellites */}
      <section className="container mx-auto px-6 py-8">
        <div className="bg-slate-900/50 backdrop-blur-xl border border-slate-800 rounded-2xl p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Satellite className="h-5 w-5 text-violet-400" />
            ماهواره‌های مورد استفاده
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {[
              { name: "Sentinel-2", org: "ESA", res: "10m", bands: "13 باند", color: "#3b82f6" },
              { name: "Landsat 8/9", org: "NASA", res: "30m", bands: "11 باند", color: "#10b981" },
              { name: "MODIS", org: "NASA", res: "250m", bands: "36 باند", color: "#f59e0b" },
              { name: "VIIRS", org: "NASA/NOAA", res: "375m", bands: "22 باند", color: "#f97316" },
            ].map((sat) => (
              <div key={sat.name} className="p-3 bg-slate-800/50 rounded-lg border border-slate-700">
                <div className="flex items-center gap-2 mb-1">
                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: sat.color }} />
                  <h4 className="font-bold text-white text-sm">{sat.name}</h4>
                </div>
                <p className="text-xs text-slate-400">{sat.org}</p>
                <p className="text-xs text-slate-300 mt-1">وضوح: {sat.res} | {sat.bands}</p>
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
    print("🌱 فاز ۲: شاخص‌های طیفی")
    print("=" * 70)
    
    if not WEB.exists():
        print(f"❌ دایرکتوری {WEB} یافت نشد!")
        return 1
    
    create_spectral_calculations()
    create_spectral_indices_component()
    update_gis_page()
    
    print("\n" + "=" * 70)
    print("✅ فاز ۲ تکمیل شد!")
    print("\n🎯 ویژگی‌های جدید:")
    print("   📊 ۵ شاخص طیفی:")
    print("      • NDVI (پوشش گیاهی)")
    print("      • EVI (پوشش گیاهی پیشرفته)")
    print("      • SAVI (خاک کم‌پوشش)")
    print("      • NDWI (آب سطحی)")
    print("      • NBR (آتش‌سوزی)")
    print("")
    print("   🗺️ نقشه حرارتی:")
    print("      • تولید خودکار داده‌های حرارتی")
    print("      • رنگ‌بندی علمی برای هر شاخص")
    print("      • تنظیم وضوح نقشه")
    print("      • نمایش Popup با مقادیر")
    print("")
    print("   📈 تحلیل منطقه‌ای:")
    print("      • ۵ منطقه نمونه (جنگل، خشک، کشاورزی)")
    print("      • محاسبه خودکار تمام شاخص‌ها")
    print("      • تفسیر علمی نتایج")
    print("      • مقایسه شاخص‌ها")
    print("")
    print("   📥 خروجی:")
    print("      • دانلود نتایج به JSON")
    print("      • گزارش کامل با باندهای طیفی")
    print("")
    print("   📚 اطلاعات علمی:")
    print("      • توضیح فرمول‌ها")
    print("      • تفسیر مقادیر")
    print("      • بازه‌های معتبر")
    print("")
    print("🚀 گام بعدی:")
    print("   1. پاک‌سازی کش:")
    print("      cd apps\\web")
    print("      Remove-Item .next -Recurse -Force")
    print("   2. اجرا: pnpm run dev -- -p 3001")
    print("   3. مشاهده: http://localhost:3001/gis")
    print("   4. روی تب 'تحلیل شاخص‌های طیفی' کلیک کنید")
    print("=" * 70)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())