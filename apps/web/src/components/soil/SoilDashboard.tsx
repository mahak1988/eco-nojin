"use client";

import { Card } from '@/components/ui/card';
import { useSoilProperties } from '@/hooks/soil/useSoil';
import { Mountain, Droplets, Leaf } from 'lucide-react';

export function SoilDashboard() {
  const { data: soil, isLoading } = useSoilProperties(35.6892, 51.3890);

  if (isLoading) {
    return <div className="text-center py-8 text-slate-400">در حال بارگذاری...</div>;
  }

  return (
    <Card className="bg-slate-900/50 border-slate-800 p-6">
      <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
        <Mountain className="w-5 h-5 text-orange-400" />
        تحلیل خاک
      </h3>
      
      {soil && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {soil.properties?.slice(0, 6).map((prop: any, idx: number) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-4">
                <div className="text-xs text-slate-400 mb-1">{prop.name_fa}</div>
                <div className="text-lg font-bold text-white">{prop.value?.toFixed(1)}</div>
                <div className="text-xs text-slate-400">{prop.unit} ({prop.depth})</div>
              </div>
            ))}
          </div>
          
          {soil.soil_class && (
            <div className="bg-emerald-900/30 border border-emerald-800 rounded-lg p-4">
              <div className="text-sm text-emerald-400">طبقه‌بندی خاک</div>
              <div className="text-lg font-bold text-white">{soil.soil_class}</div>
            </div>
          )}
        </div>
      )}
    </Card>
  );
}
