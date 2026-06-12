"use client";

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Satellite, Download, MapPin, TrendingUp, AlertTriangle,
  Wind, Droplet, Sun, Thermometer, Activity, Database,
  Mountain, Leaf, Layers, Ruler
} from 'lucide-react';
import { useGisStore } from '@/store/gis/useGisStore';
import { PredictionCards } from '@/components/gis/widgets/PredictionCards';
import { RecommendationEngine } from '@/components/gis/widgets/RecommendationEngine';
import { SatelliteLayers } from '@/components/gis/layers/SatelliteLayers';
import { MeasurementTools } from '@/components/gis/tools/MeasurementTools';
import { SpectralAnalysis } from '@/components/gis/widgets/SpectralAnalysis';
import { TopographicAnalysis } from '@/components/gis/widgets/TopographicAnalysis';
import { ManualLocationInput } from '@/components/gis/panels/ManualLocationInput';
import { SatelliteSources } from '@/components/gis/panels/SatelliteSources';

const InteractiveMap = dynamic(
  () => import('@/components/gis/InteractiveMap').then(mod => mod.InteractiveMap),
  { 
    loading: () => (
      <div className="flex items-center justify-center h-full bg-black/40 backdrop-blur-xl">
        <div className="text-center">
          <div className="relative inline-block mb-4">
            <div className="absolute inset-0 bg-emerald-500 rounded-full blur-2xl opacity-50 animate-pulse" />
            <Satellite className="relative w-12 h-12 text-emerald-400 animate-pulse" />
          </div>
          <p className="text-emerald-400 font-medium">در حال بارگذاری موتور ماهواره‌ای...</p>
        </div>
      </div>
    ),
    ssr: false 
  }
);

export default function GisPage() {
  const [activeTab, setActiveTab] = useState('map');
  const [weatherData, setWeatherData] = useState<any>(null);
  
  const { 
    measurements, 
    drawnFeatures, 
    selectedLayer,
    mapCenter,
    mapZoom,
    setMapCenter,
    setMapZoom,
    clearAll,
    exportData
  } = useGisStore();

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const res = await fetch(
          `https://api.open-meteo.com/v1/forecast?latitude=${mapCenter.lat}&longitude=${mapCenter.lng}&current=temperature_2m,relative_humidity_2m,wind_speed_10m,sunshine_duration&timezone=Asia/Tehran`
        );
        const data = await res.json();
        setWeatherData(data.current);
      } catch (err) {
        console.error('Weather fetch failed:', err);
      }
    };
    
    fetchWeather();
    const interval = setInterval(fetchWeather, 600000);
    return () => clearInterval(interval);
  }, [mapCenter.lat, mapCenter.lng]);

  const handleExport = async (format: 'geojson' | 'kml') => {
    try {
      const data = await exportData(format);
      const blob = new Blob([data], { 
        type: format === 'kml' ? 'application/vnd.google-earth.kml+xml' : 'application/json' 
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `econojin-gis-${Date.now()}.${format === 'kml' ? 'kml' : 'geojson'}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error('Export failed:', err);
    }
  };

  const tabs = [
    { id: 'map', label: 'نقشه', icon: MapPin, color: '#10b981' },
    { id: 'spectral', label: 'تحلیل طیفی', icon: Leaf, color: '#84cc16' },
    { id: 'topographic', label: 'توپوگرافی', icon: Mountain, color: '#8b5cf6' },
    { id: 'predictions', label: 'پیش‌بینی', icon: TrendingUp, color: '#3b82f6' },
    { id: 'manual', label: 'ورود دستی', icon: Database, color: '#f59e0b' },
    { id: 'sources', label: 'منابع ماهواره', icon: Satellite, color: '#06b6d4' }
  ];

  return (
    <div className="min-h-screen relative overflow-hidden">
      {/* Ambient Background - Nature Distilled */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        <div 
          className="absolute inset-0 opacity-50"
          style={{
            backgroundImage: `
              radial-gradient(at 10% 10%, rgba(16, 185, 129, 0.2) 0px, transparent 50%),
              radial-gradient(at 90% 20%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
              radial-gradient(at 50% 90%, rgba(6, 182, 212, 0.12) 0px, transparent 50%)
            `
          }}
        />
        {/* Noise texture */}
        <div 
          className="absolute inset-0 opacity-[0.02] mix-blend-overlay"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
          }}
        />
      </div>

      {/* Header - Glassmorphism */}
      <header className="sticky top-0 z-50 bg-black/40 backdrop-blur-2xl border-b border-white/10 shadow-[0_8px_32px_rgba(0,0,0,0.4)]">
        {/* Mesh gradient در هدر */}
        <div 
          className="absolute inset-0 opacity-30 pointer-events-none"
          style={{
            backgroundImage: `
              radial-gradient(at 20% 0%, rgba(16, 185, 129, 0.2) 0px, transparent 50%),
              radial-gradient(at 80% 0%, rgba(6, 182, 212, 0.15) 0px, transparent 50%)
            `
          }}
        />

        <div className="container mx-auto px-6 py-4 relative">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-4"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-emerald-500 rounded-2xl blur-xl opacity-50" />
                <div className="relative p-3 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-2xl">
                  <Satellite className="w-6 h-6 text-white" />
                </div>
              </div>
              <div>
                <h1 className="text-2xl font-black text-white tracking-tight">سیستم GIS پیشرفته</h1>
                <p className="text-xs text-zinc-400 font-medium tracking-wide">Sentinel-2 • Landsat • NASA • ESA</p>
              </div>
            </motion.div>
            
            <motion.div 
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center gap-3 flex-wrap"
            >
              <Button 
                variant="outline" 
                size="sm" 
                className="gap-2 bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20 rounded-xl backdrop-blur-xl"
                onClick={() => handleExport('geojson')}
              >
                <Download className="w-4 h-4" />
                GeoJSON
              </Button>
              <Button 
                variant="outline" 
                size="sm" 
                className="gap-2 bg-white/5 border-white/10 hover:bg-white/10 hover:border-white/20 rounded-xl backdrop-blur-xl"
                onClick={() => handleExport('kml')}
              >
                <Download className="w-4 h-4" />
                KML
              </Button>
              <Button 
                variant="destructive" 
                size="sm" 
                className="rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 hover:bg-red-500/20"
                onClick={clearAll}
              >
                پاک‌سازی
              </Button>
            </motion.div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-6 py-8">
        <div className="grid grid-cols-12 gap-6">
          {/* Sidebar */}
          <motion.div 
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.1 }}
            className="col-span-12 lg:col-span-3 space-y-4"
          >
            {/* Satellite Layers */}
            <SatelliteLayers />
            
            {/* Measurement Tools */}
            <MeasurementTools />
            
            {/* Manual Location Input */}
            <ManualLocationInput />

            {/* Quick Stats - Glassmorphism */}
            <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 shadow-2xl overflow-hidden">
              <div className="p-5 border-b border-white/10">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-emerald-500/20">
                    <Activity className="w-4 h-4 text-emerald-400" />
                  </div>
                  آمار سریع
                </h3>
              </div>
              <div className="p-5 space-y-4">
                {[
                  { label: 'مزارع ثبت‌شده', value: drawnFeatures.filter(f => f.properties?.type === 'farm').length, color: '#10b981' },
                  { label: 'اندازه‌گیری‌ها', value: measurements.length, color: '#3b82f6' },
                  { label: 'لایه فعال', value: selectedLayer || 'Esri Satellite', color: '#06b6d4' }
                ].map((stat, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.2 + idx * 0.1 }}
                    className="flex items-center justify-between p-3 bg-black/20 rounded-xl border border-white/5"
                  >
                    <span className="text-sm text-zinc-400">{stat.label}</span>
                    <Badge 
                      className="font-bold tabular-nums"
                      style={{ 
                        backgroundColor: `${stat.color}20`,
                        color: stat.color,
                        border: `1px solid ${stat.color}30`
                      }}
                    >
                      {stat.value}
                    </Badge>
                  </motion.div>
                ))}
              </div>
            </Card>

            {/* Weather Card - Glassmorphism with animations */}
            <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 shadow-2xl overflow-hidden">
              <div className="p-5 border-b border-white/10">
                <h3 className="font-bold text-white flex items-center gap-2">
                  <div className="p-1.5 rounded-lg bg-blue-500/20">
                    <Wind className="w-4 h-4 text-blue-400" />
                  </div>
                  وضعیت جوی لحظه‌ای
                  <Badge className="bg-emerald-500/20 text-emerald-400 border-emerald-500/30 text-xs mr-auto">
                    <span className="relative flex h-2 w-2 mr-1.5">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    LIVE
                  </Badge>
                </h3>
              </div>
              <div className="p-5">
                {weatherData ? (
                  <div className="grid grid-cols-2 gap-3">
                    {[
                      { icon: Thermometer, label: 'دما', value: `${weatherData.temperature_2m?.toFixed(1) || '--'}°C`, color: '#f97316', gradient: 'from-orange-500/10' },
                      { icon: Droplet, label: 'رطوبت', value: `${weatherData.relative_humidity_2m || '--'}%`, color: '#3b82f6', gradient: 'from-blue-500/10' },
                      { icon: Sun, label: 'ساعت آفتابی', value: `${((weatherData.sunshine_duration || 0) / 3600).toFixed(1)}`, color: '#eab308', gradient: 'from-yellow-500/10' },
                      { icon: Wind, label: 'باد (km/h)', value: weatherData.wind_speed_10m?.toFixed(1) || '--', color: '#14b8a6', gradient: 'from-teal-500/10' }
                    ].map((item, idx) => {
                      const Icon = item.icon;
                      return (
                        <motion.div
                          key={idx}
                          initial={{ opacity: 0, scale: 0.9 }}
                          animate={{ opacity: 1, scale: 1 }}
                          transition={{ delay: 0.3 + idx * 0.1 }}
                          className={`relative bg-gradient-to-br ${item.gradient} to-transparent border border-white/5 rounded-2xl p-4 overflow-hidden group hover:border-white/10 transition-all`}
                        >
                          <div 
                            className="absolute top-0 right-0 w-16 h-16 rounded-full blur-2xl opacity-30 group-hover:opacity-50 transition-opacity"
                            style={{ backgroundColor: item.color }}
                          />
                          <div className="relative">
                            <Icon className="w-5 h-5 mb-2" style={{ color: item.color }} />
                            <div className="text-xl font-black text-white tabular-nums">
                              {item.value}
                            </div>
                            <div className="text-xs text-zinc-400 mt-1">{item.label}</div>
                          </div>
                        </motion.div>
                      );
                    })}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="inline-flex items-center gap-2 text-zinc-400">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
                      در حال بارگذاری...
                    </div>
                  </div>
                )}
              </div>
            </Card>
          </motion.div>

          {/* Main Content */}
          <motion.div 
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="col-span-12 lg:col-span-9 space-y-4"
          >
            {/* Map Container - Glassmorphism */}
            <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 shadow-2xl h-[700px] relative overflow-hidden">
              <InteractiveMap
                center={mapCenter}
                zoom={mapZoom}
                onCenterChange={setMapCenter}
                onZoomChange={setMapZoom}
              />

              {/* Coordinates Overlay - Glassmorphism */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
                className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl px-4 py-3 z-[1000] shadow-2xl"
              >
                <div className="text-xs text-zinc-400 mb-1 font-medium">WGS84</div>
                <div className="text-sm font-mono text-white tabular-nums">
                  {mapCenter.lat.toFixed(6)}°, {mapCenter.lng.toFixed(6)}°
                </div>
                <div className="text-xs text-zinc-400 mt-2 font-medium">UTM Zone 39N</div>
                <div className="text-xs font-mono text-emerald-400 tabular-nums">
                  E: {Math.round(500000 + (mapCenter.lng - 51) * 111320 * Math.cos(mapCenter.lat * Math.PI / 180))} m
                </div>
              </motion.div>

              {/* Scale Overlay - Glassmorphism */}
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="absolute bottom-4 right-4 bg-black/60 backdrop-blur-2xl border border-white/10 rounded-2xl px-4 py-3 z-[1000] shadow-2xl"
              >
                <div className="text-xs text-zinc-400 mb-2 font-medium">مقیاس</div>
                <div className="w-32 h-2 bg-gradient-to-r from-emerald-500 to-emerald-300 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]" />
                <div className="text-xs text-center text-white mt-2 font-mono tabular-nums">
                  {Math.round(156543.03392 * Math.cos(mapCenter.lat * Math.PI / 180) / Math.pow(2, mapZoom))} m
                </div>
              </motion.div>
            </Card>

            {/* Tabs - Modern Design */}
            <div className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 rounded-2xl p-2 shadow-2xl">
              <div className="grid grid-cols-3 md:grid-cols-6 gap-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  const isActive = activeTab === tab.id;
                  return (
                    <motion.button
                      key={tab.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`relative flex items-center justify-center gap-2 px-3 py-3 rounded-xl text-xs font-medium transition-all ${
                        isActive 
                          ? 'text-white shadow-lg' 
                          : 'text-zinc-400 hover:text-white hover:bg-white/5'
                      }`}
                      onClick={() => setActiveTab(tab.id)}
                      style={isActive ? {
                        backgroundColor: `${tab.color}20`,
                        border: `1px solid ${tab.color}40`,
                        boxShadow: `0 0 20px ${tab.color}30`
                      } : {}}
                    >
                      <Icon className="w-4 h-4" style={{ color: isActive ? tab.color : undefined }} />
                      <span className="hidden md:inline">{tab.label}</span>
                    </motion.button>
                  );
                })}
              </div>
            </div>

            {/* Tab Content */}
            <AnimatePresence mode="wait">
              {activeTab === 'map' && (
                <motion.div
                  key="map"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className="grid grid-cols-1 md:grid-cols-3 gap-4"
                >
                  <PredictionCards />
                  <RecommendationEngine />
                  
                  {/* Alerts Card - Glassmorphism */}
                  <Card className="bg-white/[0.03] backdrop-blur-2xl border border-white/10 shadow-2xl">
                    <div className="p-5">
                      <h3 className="font-bold text-white mb-4 flex items-center gap-2">
                        <div className="p-1.5 rounded-lg bg-yellow-500/20">
                          <AlertTriangle className="w-4 h-4 text-yellow-400" />
                        </div>
                        هشدارهای فعال
                      </h3>
                      <div className="space-y-3">
                        {[
                          { text: 'کمبود رطوبت خاک', color: '#eab308' },
                          { text: 'نیاز به کوددهی', color: '#f97316' },
                          { text: 'خطر آفت', color: '#ef4444' }
                        ].map((alert, idx) => (
                          <motion.div
                            key={idx}
                            initial={{ opacity: 0, x: -10 }}
                            animate={{ opacity: 1, x: 0 }}
                            transition={{ delay: idx * 0.1 }}
                            className="flex items-center gap-3 p-3 bg-black/20 rounded-xl border border-white/5"
                          >
                            <AlertTriangle className="w-4 h-4 flex-shrink-0" style={{ color: alert.color }} />
                            <span className="text-sm text-white">{alert.text}</span>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  </Card>
                </motion.div>
              )}
              
              {activeTab === 'spectral' && (
                <motion.div
                  key="spectral"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <SpectralAnalysis />
                </motion.div>
              )}
              
              {activeTab === 'topographic' && (
                <motion.div
                  key="topographic"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <TopographicAnalysis />
                </motion.div>
              )}
              
              {activeTab === 'predictions' && (
                <motion.div
                  key="predictions"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-4"
                >
                  <PredictionCards />
                  <RecommendationEngine />
                </motion.div>
              )}
              
              {activeTab === 'manual' && (
                <motion.div
                  key="manual"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <ManualLocationInput />
                </motion.div>
              )}
              
              {activeTab === 'sources' && (
                <motion.div
                  key="sources"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <SatelliteSources />
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        </div>
      </div>
    </div>
  );
}