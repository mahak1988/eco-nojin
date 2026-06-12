'use client';

import { useMemo } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import { Map as MapIcon } from 'lucide-react';
import { useAnalysisStore } from '@/store/analysis';
import { formatNumber } from '@/lib/utils';

interface MapPoint {
  region: string;
  lat: number;
  lon: number;
  ndvi: number;
  crop: string;
  profit: number;
}

export function MapPanel() {
  const analyses = useAnalysisStore((state) => state.analyses);
  const regions = useAnalysisStore((state) => state.regions);

  // ترکیب داده‌های تحلیل با مختصات جغرافیایی
  const mapPoints = useMemo<MapPoint[]>(() => {
    return analyses
      .map((analysis) => {
        const region = regions.find((r) => r.name === analysis.region);
        if (!region) return null;
        return {
          region: analysis.region,
          lat: region.lat,
          lon: region.lon,
          ndvi: analysis.ndvi,
          crop: analysis.crop,
          profit: analysis.profit,
        };
      })
      .filter((p): p is MapPoint => p !== null);
  }, [analyses, regions]);

  const getMarkerColor = (ndvi: number): string => {
    if (ndvi >= 0.6) return '#10b981';
    if (ndvi >= 0.4) return '#84cc16';
    if (ndvi >= 0.2) return '#f59e0b';
    return '#ef4444';
  };

  const getMarkerRadius = (ndvi: number): number => 8 + ndvi * 10;

  if (mapPoints.length === 0) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 h-[400px] flex flex-col items-center justify-center text-slate-400 border border-slate-700 shadow-xl">
        <div className="w-16 h-16 rounded-full bg-slate-700/50 flex items-center justify-center mb-3">
          <MapIcon className="w-8 h-8 text-slate-500" />
        </div>
        <p className="text-center">
          پس از اجرای تحلیل، نقاط روی نقشه نمایش داده می‌شوند.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-5 border border-slate-700 shadow-xl" dir="rtl">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/20 flex items-center justify-center">
            <MapIcon className="w-5 h-5 text-emerald-400" />
          </div>
          <h4 className="font-bold text-white">نقشه پراکندگی مناطق</h4>
        </div>
        <div className="flex items-center gap-3 text-xs flex-wrap">
          <Legend color="#10b981" label="عالی (≥0.6)" />
          <Legend color="#84cc16" label="خوب (≥0.4)" />
          <Legend color="#f59e0b" label="متوسط (≥0.2)" />
          <Legend color="#ef4444" label="ضعیف (<0.2)" />
        </div>
      </div>

      <div className="rounded-xl overflow-hidden border border-slate-700">
        <MapContainer
          center={[32.4279, 53.688]}
          zoom={5}
          scrollWheelZoom={true}
          style={{ height: '400px', width: '100%' }}
          className="z-0"
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />

          {mapPoints.map((point, idx) => (
            <CircleMarker
              key={`${point.region}-${idx}`}
              center={[point.lat, point.lon]}
              radius={getMarkerRadius(point.ndvi)}
              pathOptions={{
                color: getMarkerColor(point.ndvi),
                fillColor: getMarkerColor(point.ndvi),
                fillOpacity: 0.7,
                weight: 2,
              }}
            >
              <Tooltip direction="top" offset={[0, -10]} opacity={0.9}>
                <span className="font-bold">{point.region}</span>
                <br />
                NDVI: {point.ndvi.toFixed(3)}
              </Tooltip>
              <Popup>
                <div className="text-right text-sm p-1 min-w-[180px]" dir="rtl">
                  <h5 className="font-bold text-base text-slate-800 mb-2 border-b border-slate-300 pb-1">
                    {point.region}
                  </h5>
                  <div className="space-y-1 text-slate-700">
                    <p>
                      <span className="font-semibold">🌾 محصول:</span> {point.crop}
                    </p>
                    <p>
                      <span className="font-semibold">📊 NDVI:</span>{' '}
                      <span style={{ color: getMarkerColor(point.ndvi) }}>
                        {point.ndvi.toFixed(3)}
                      </span>
                    </p>
                    <p>
                      <span className="font-semibold">💰 سود:</span>{' '}
                      {formatNumber(point.profit)} تومان
                    </p>
                  </div>
                </div>
              </Popup>
            </CircleMarker>
          ))}
        </MapContainer>
      </div>
    </div>
  );
}

function Legend({ color, label }: { color: string; label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span
        className="inline-block w-3 h-3 rounded-full shadow-sm"
        style={{ backgroundColor: color }}
      ></span>
      <span className="text-slate-300">{label}</span>
    </div>
  );
}