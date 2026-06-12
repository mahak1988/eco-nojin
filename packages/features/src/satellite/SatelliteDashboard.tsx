"use client";

import { Card } from '@/components/ui/card';
import { useSentinelImages, useSpectralIndex } from '@/hooks/satellite/useSatellite';
import { Satellite, TrendingUp } from 'lucide-react';

export function SatelliteDashboard() {
  const bbox: [number, number, number, number] = [51.2, 35.6, 51.5, 35.8];
  const startDate = '2024-01-01';
  const endDate = '2024-12-31';
  
  const { data: images } = useSentinelImages(bbox, startDate, endDate);
  const { data: ndvi } = useSpectralIndex(35.6892, 51.3890, 'NDVI');

  return (
    <div className="space-y-4">
      <Card className="bg-slate-900/50 border-slate-800 p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Satellite className="w-5 h-5 text-emerald-400" />
          تصاویر Sentinel-2
        </h3>
        
        {images && images.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {images.slice(0, 4).map((img: any, idx: number) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-sm text-slate-400">{img.date?.slice(0, 10)}</div>
                <div className="text-lg font-bold text-white">Cloud: {img.cloud_cover?.toFixed(1)}%</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-slate-400">تصویری یافت نشد</div>
        )}
      </Card>

      {ndvi && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-400" />
            شاخص NDVI
          </h3>
          <div className="text-4xl font-bold text-emerald-400 mb-2">{ndvi.value?.toFixed(3)}</div>
          <div className="text-slate-400">{ndvi.description}</div>
          <div className="mt-4 p-3 rounded-lg" style={{backgroundColor: ndvi.color || '#16a34a'}}>
            <div className="text-white font-bold">{ndvi.status}</div>
          </div>
        </Card>
      )}
    </div>
  );
}
