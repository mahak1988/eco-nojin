"use client";

import { Card } from '@/components/ui/card';
import { useDroughtRisk, useSPEIAnalysis, useRainfallData } from '@/hooks/drought/useDrought';
import { AlertTriangle, Droplets, CloudRain } from 'lucide-react';

export function DroughtDashboard() {
  const { data: risk } = useDroughtRisk(35.6892, 51.3890);
  const { data: spei } = useSPEIAnalysis(35.6892, 51.3890);
  const { data: rainfall } = useRainfallData(35.6892, 51.3890, '2024-01-01', '2024-12-31');

  return (
    <div className="space-y-4">
      {risk && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" style={{color: risk.color}} />
            ریسک خشکسالی
          </h3>
          <div className="text-3xl font-bold mb-2" style={{color: risk.color}}>{risk.score}/100</div>
          <div className="text-white mb-2">{risk.description}</div>
          <div className="bg-slate-800/50 rounded-lg p-3 text-slate-300">{risk.recommendation}</div>
        </Card>
      )}

      {spei && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Droplets className="w-5 h-5 text-blue-400" />
            شاخص SPEI
          </h3>
          <div className="text-3xl font-bold text-white mb-2">{spei.current_spei}</div>
          <div className="text-white">{spei.drought_severity} - {spei.duration_months} ماه</div>
        </Card>
      )}

      {rainfall && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <CloudRain className="w-5 h-5 text-indigo-400" />
            آمار بارش
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-slate-400 text-sm">مجموع</div>
              <div className="text-xl font-bold text-white">{rainfall.total_rainfall?.toFixed(1)} mm</div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-3">
              <div className="text-slate-400 text-sm">روزهای بارانی</div>
              <div className="text-xl font-bold text-white">{rainfall.rainy_days}</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}
