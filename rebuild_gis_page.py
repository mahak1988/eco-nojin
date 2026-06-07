from pathlib import Path

print("=" * 80)
print("🔧 REBUILDING GIS PAGE WITH CORRECT IMPORTS")
print("=" * 80)

frontend_path = Path('apps/web/src')
gis_page = frontend_path / 'app/gis/page.tsx'

content = '''"use client";

import { useState, useEffect } from 'react';
import dynamic from 'next/dynamic';
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
      <div className="flex items-center justify-center h-full bg-slate-900">
        <div className="text-emerald-400 animate-pulse">Loading Satellite Engine...</div>
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
    { id: 'map', label: 'نقشه', icon: MapPin },
    { id: 'spectral', label: 'تحلیل طیفی', icon: Leaf },
    { id: 'topographic', label: 'توپوگرافی', icon: Mountain },
    { id: 'predictions', label: 'پیش‌بینی', icon: TrendingUp },
    { id: 'manual', label: 'ورود دستی', icon: Database },
    { id: 'sources', label: 'منابع ماهواره', icon: Satellite }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-xl sticky top-0 z-50">
        <div className="container mx-auto px-4 py-3">
          <div className="flex items-center justify-between flex-wrap gap-3">
            <div className="flex items-center gap-3">
              <Satellite className="w-6 h-6 text-emerald-400" />
              <div>
                <h1 className="text-xl font-bold text-white">سیستم GIS پیشرفته Econojin</h1>
                <p className="text-xs text-slate-400">Sentinel-2 | Landsat | NASA | ESA</p>
              </div>
            </div>
            
            <div className="flex items-center gap-2 flex-wrap">
              <Button variant="outline" size="sm" className="gap-2" onClick={() => handleExport('geojson')}>
                <Download className="w-4 h-4" />
                GeoJSON
              </Button>
              <Button variant="outline" size="sm" className="gap-2" onClick={() => handleExport('kml')}>
                <Download className="w-4 h-4" />
                KML
              </Button>
              <Button variant="destructive" size="sm" onClick={clearAll}>
                پاک‌سازی
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-12 gap-6">
          <div className="col-span-12 lg:col-span-3 space-y-4">
            <SatelliteLayers />
            <MeasurementTools />
            <ManualLocationInput />

            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
              <div className="p-4 border-b border-slate-800">
                <h3 className="font-semibold text-white flex items-center gap-2">
                  <Activity className="w-4 h-4" />
                  آمار سریع
                </h3>
              </div>
              <div className="p-4 space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">مزارع ثبت‌شده</span>
                  <Badge variant="secondary">
                    {drawnFeatures.filter(f => f.properties?.type === 'farm').length}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">اندازه‌گیری‌ها</span>
                  <Badge variant="secondary">{measurements.length}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-slate-400">لایه فعال</span>
                  <Badge className="bg-emerald-600">{selectedLayer || 'Esri Satellite'}</Badge>
                </div>
              </div>
            </Card>

            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
              <div className="p-4">
                <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                  <Wind className="w-4 h-4" />
                  وضعیت جوی لحظه‌ای
                  <Badge className="bg-green-600 text-xs mr-auto">LIVE</Badge>
                </h3>
                {weatherData ? (
                  <div className="grid grid-cols-2 gap-3">
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <Thermometer className="w-5 h-5 text-orange-400 mb-2" />
                      <div className="text-2xl font-bold text-white">
                        {weatherData.temperature_2m?.toFixed(1) || '--'}°C
                      </div>
                      <div className="text-xs text-slate-400">دما</div>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <Droplet className="w-5 h-5 text-blue-400 mb-2" />
                      <div className="text-2xl font-bold text-white">
                        {weatherData.relative_humidity_2m || '--'}%
                      </div>
                      <div className="text-xs text-slate-400">رطوبت</div>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <Sun className="w-5 h-5 text-yellow-400 mb-2" />
                      <div className="text-2xl font-bold text-white">
                        {((weatherData.sunshine_duration || 0) / 3600).toFixed(1)}
                      </div>
                      <div className="text-xs text-slate-400">ساعت آفتابی</div>
                    </div>
                    <div className="bg-slate-800/50 rounded-lg p-3">
                      <Wind className="w-5 h-5 text-teal-400 mb-2" />
                      <div className="text-2xl font-bold text-white">
                        {weatherData.wind_speed_10m?.toFixed(1) || '--'}
                      </div>
                      <div className="text-xs text-slate-400">باد (km/h)</div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center text-slate-400 py-4">در حال بارگذاری...</div>
                )}
              </div>
            </Card>
          </div>

          <div className="col-span-12 lg:col-span-9 space-y-4">
            <Card className="bg-slate-900/50 border-slate-800 backdrop-blur h-[700px] relative overflow-hidden">
              <InteractiveMap
                center={mapCenter}
                zoom={mapZoom}
                onCenterChange={setMapCenter}
                onZoomChange={setMapZoom}
              />

              <div className="absolute bottom-4 left-4 bg-slate-900/90 border border-slate-700 rounded-lg px-3 py-2 z-[1000]">
                <div className="text-xs text-slate-400">WGS84</div>
                <div className="text-sm font-mono text-white">
                  {mapCenter.lat.toFixed(6)}°, {mapCenter.lng.toFixed(6)}°
                </div>
                <div className="text-xs text-slate-400 mt-1">UTM Zone 39N</div>
                <div className="text-xs font-mono text-emerald-400">
                  E: {Math.round(500000 + (mapCenter.lng - 51) * 111320 * Math.cos(mapCenter.lat * Math.PI / 180))} m
                </div>
              </div>

              <div className="absolute bottom-4 right-4 bg-slate-900/90 border border-slate-700 rounded-lg px-3 py-2 z-[1000]">
                <div className="text-xs text-slate-400 mb-1">مقیاس</div>
                <div className="w-32 h-2 bg-gradient-to-r from-emerald-500 to-emerald-300 rounded"></div>
                <div className="text-xs text-center text-white mt-1">
                  {Math.round(156543.03392 * Math.cos(mapCenter.lat * Math.PI / 180) / Math.pow(2, mapZoom))} m
                </div>
              </div>
            </Card>

            <div className="grid grid-cols-3 md:grid-cols-6 gap-2 bg-slate-900/50 border border-slate-800 rounded-lg p-2">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <Button
                    key={tab.id}
                    size="sm"
                    variant={isActive ? 'default' : 'ghost'}
                    className={`gap-1 text-xs ${isActive ? 'bg-emerald-600 hover:bg-emerald-700' : 'hover:bg-slate-800'}`}
                    onClick={() => setActiveTab(tab.id)}
                  >
                    <Icon className="w-3 h-3" />
                    <span className="hidden md:inline">{tab.label}</span>
                  </Button>
                );
              })}
            </div>

            {activeTab === 'map' && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <PredictionCards />
                <RecommendationEngine />
                
                <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
                  <div className="p-4">
                    <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-yellow-400" />
                      هشدارهای فعال
                    </h3>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2 text-sm text-yellow-400">
                        <AlertTriangle className="w-4 h-4" />
                        <span>کمبود رطوبت خاک</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-orange-400">
                        <AlertTriangle className="w-4 h-4" />
                        <span>نیاز به کوددهی</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-red-400">
                        <AlertTriangle className="w-4 h-4" />
                        <span>خطر آفت</span>
                      </div>
                    </div>
                  </div>
                </Card>
              </div>
            )}
            
            {activeTab === 'spectral' && <SpectralAnalysis />}
            {activeTab === 'topographic' && <TopographicAnalysis />}
            {activeTab === 'predictions' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <PredictionCards />
                <RecommendationEngine />
              </div>
            )}
            {activeTab === 'manual' && <ManualLocationInput />}
            {activeTab === 'sources' && <SatelliteSources />}
          </div>
        </div>
      </div>
    </div>
  );
}
'''

gis_page.write_text(content, encoding='utf-8')
print("✅ Rebuilt app/gis/page.tsx with correct imports")
print("   - Added: Mountain, Leaf, Layers, Ruler")
print("   - Fixed all tab icons")
print("\n🚀 Restart server:")
print("   npx next dev -p 3001")
print("\n🌐 Visit: http://localhost:3001/gis")