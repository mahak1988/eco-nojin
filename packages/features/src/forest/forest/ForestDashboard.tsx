"use client";

import { Card } from '@/components/ui/card';
import { useForestMetrics, useCarbonSequestration, useVegetationTimeseries } from '@/hooks/forest/useForest';
import { TreePine, Leaf, Coins } from 'lucide-react';

export function ForestDashboard() {
  const { data: forest } = useForestMetrics(35.6892, 51.3890);
  const { data: carbon } = useCarbonSequestration(35.6892, 51.3890, 10);
  const { data: vegetation } = useVegetationTimeseries(35.6892, 51.3890, '2024-01-01', '2024-12-31');

  return (
    <div className="space-y-4">
      {forest && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <TreePine className="w-5 h-5 text-emerald-400" />
            معیارهای جنگل
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-slate-400 text-sm">ارتفاع تاج</div>
              <div className="text-xl font-bold text-white">{forest.mean_canopy_height} m</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-slate-400 text-sm">پوشش تاج</div>
              <div className="text-xl font-bold text-white">{forest.canopy_cover}%</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-slate-400 text-sm">زیست‌توده</div>
              <div className="text-xl font-bold text-white">{forest.estimated_biomass} t/ha</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-slate-400 text-sm">نوع جنگل</div>
              <div className="text-xl font-bold text-white text-sm">{forest.forest_type}</div>
            </div>
          </div>
        </Card>
      )}

      {carbon && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Coins className="w-5 h-5 text-yellow-400" />
            جذب کربن
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-emerald-900/30 border border-emerald-800 rounded-lg p-3">
              <div className="text-emerald-400 text-sm">کربن جذب شده</div>
              <div className="text-2xl font-bold text-white">{carbon.carbon_sequestered_tons} t</div>
            </div>
            <div className="bg-emerald-900/30 border border-emerald-800 rounded-lg p-3">
              <div className="text-emerald-400 text-sm">ارزش اقتصادی</div>
              <div className="text-2xl font-bold text-white">${carbon.economic_value_usd}</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
