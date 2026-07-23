"use client";

import { useState, useMemo } from "react";
import dynamic from "next/dynamic";
import { 
  Leaf, Droplets, Flame, BarChart3, TrendingUp, 
  Download, Info, Layers, Calculator
} from "lucide-react";
import {
import { CHART, GIS } from '@econojin/ui/lib/chart-colors';

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
  { id: "NDVI", name: "NDVI", fullName: "Normalized Difference Vegetation Index", icon: Leaf, color: GIS.vegetation, category: "vegetation" },
  { id: "EVI", name: "EVI", fullName: "Enhanced Vegetation Index", icon: Leaf, color: CHART.emerald, category: "vegetation" },
  { id: "SAVI", name: "SAVI", fullName: "Soil Adjusted Vegetation Index", icon: Leaf, color: CHART.lime, category: "vegetation" },
  { id: "NDWI", name: "NDWI", fullName: "Normalized Difference Water Index", icon: Droplets, color: GIS.water, category: "water" },
  { id: "NBR", name: "NBR", fullName: "Normalized Burn Ratio", icon: Flame, color: CHART.red, category: "fire" },
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
