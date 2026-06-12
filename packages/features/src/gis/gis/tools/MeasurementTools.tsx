"use client";

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Ruler, MapPin, Trash2 } from 'lucide-react';
import { useGisStore } from '@/store/gis/useGisStore';

export function MeasurementTools() {
  const { measurements, drawnFeatures, clearAll } = useGisStore();

  const totalArea = drawnFeatures.reduce((sum, f) => sum + (f.properties?.area || 0), 0);
  const totalDistance = measurements.reduce((sum, m) => sum + (m.distance || 0), 0);

  return (
    <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
      <div className="p-4 border-b border-slate-800 flex items-center justify-between">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Ruler className="w-4 h-4" />
          ابزارهای اندازه‌گیری
        </h3>
        <Button size="sm" variant="destructive" onClick={clearAll}>
          <Trash2 className="w-3 h-3" />
        </Button>
      </div>
      <div className="p-4 space-y-3">
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">مساحت کل</span>
            <Badge className="bg-emerald-600">{drawnFeatures.length}</Badge>
          </div>
          <div className="text-2xl font-bold text-white">{(totalArea / 10000).toFixed(2)}</div>
          <div className="text-xs text-slate-400">هکتار</div>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm text-slate-400">مسافت کل</span>
            <Badge className="bg-blue-600">{measurements.length}</Badge>
          </div>
          <div className="text-2xl font-bold text-white">{(totalDistance / 1000).toFixed(2)}</div>
          <div className="text-xs text-slate-400">کیلومتر</div>
        </div>
        
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="text-sm text-slate-400 mb-2">آخرین اندازه‌گیری</div>
          {measurements.length > 0 ? (
            <div className="text-sm text-white">
              {measurements[measurements.length - 1].type === 'line' 
                ? `${(measurements[measurements.length - 1].distance || 0).toFixed(0)} متر`
                : `${((measurements[measurements.length - 1].area || 0) / 10000).toFixed(2)} هکتار`
              }
            </div>
          ) : (
            <div className="text-sm text-slate-500">اندازه‌گیری نشده</div>
          )}
        </div>
      </div>
    </Card>
  );
}
