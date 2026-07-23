'use client';

import { useMemo } from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  Cell,
} from 'recharts';
import { TrendingUp, DollarSign } from 'lucide-react';
import { useAnalysisStore } from '@/store/analysis';
import type { ProfitDataPoint } from '@/lib/types/analysis';
import { cn, formatNumber } from '@/lib/utils';

import { CHART, GIS, UI } from '@econojin/ui/lib/chart-colors';

export function ChartsPanel() {
  const ndviData = useAnalysisStore((state) => state.ndviData);
  const results = useAnalysisStore((state) => state.results);

  const profitData: ProfitDataPoint[] = useMemo(() => {
    const { area, yieldPerHa, pricePerTon, waterCost, laborCost } = results;
    const revenue = area * yieldPerHa * pricePerTon;
    const operationalCost = area * 800000;
    const totalCost = waterCost + laborCost + operationalCost;
    const netProfit = revenue - totalCost;

    return [
      { item: 'درآمد', value: revenue, color: CHART.emerald },
      { item: 'هزینه آب', value: waterCost, color: CHART.blue },
      { item: 'هزینه کارگر', value: laborCost, color: CHART.amber },
      { item: 'سود خالص', value: netProfit, color: netProfit > 0 ? CHART.emerald : CHART.red },
    ];
  }, [results]);

  if (ndviData.length === 0) {
    return (
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-8 h-[400px] flex flex-col items-center justify-center text-slate-400 border border-slate-700 shadow-xl">
        <div className="w-16 h-16 rounded-full bg-slate-700/50 flex items-center justify-center mb-3">
          <TrendingUp className="w-8 h-8 text-slate-500" />
        </div>
        <p className="text-center">
          پس از اجرای اولین تحلیل، نمودارها اینجا نمایش داده می‌شوند.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6" dir="rtl">
      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-5 border border-slate-700 shadow-xl">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-9 h-9 rounded-lg bg-sky-500/20 flex items-center justify-center">
            <TrendingUp className="w-5 h-5 text-sky-400" />
          </div>
          <h4 className="font-bold text-white">روند شاخص NDVI</h4>
        </div>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={ndviData}>
            <defs>
              <linearGradient id="ndviGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={CHART.sky} stopOpacity={0.3} />
                <stop offset="95%" stopColor={CHART.sky} stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
            <XAxis dataKey="date" stroke={UI.textMuted} fontSize={12} />
            <YAxis domain={[0, 1]} stroke={UI.textMuted} fontSize={12} />
            <Tooltip
              contentStyle={{
                backgroundColor: GIS.background,
                border: '1px solid #334155',
                borderRadius: '8px',
                color: CHART.white,
              }}
              labelStyle={{ color: CHART.sky }}
            />
            <Line
              type="monotone"
              dataKey="ndvi"
              stroke={CHART.sky}
              strokeWidth={3}
              dot={{ r: 4, fill: CHART.sky, stroke: GIS.background, strokeWidth: 2 }}
              activeDot={{ r: 6, fill: CHART.sky }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-5 border border-slate-700 shadow-xl">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-9 h-9 rounded-lg bg-emerald-500/20 flex items-center justify-center">
            <DollarSign className="w-5 h-5 text-emerald-400" />
          </div>
          <h4 className="font-bold text-white">تحلیل اقتصادی (تومان)</h4>
        </div>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={profitData} layout="vertical" margin={{ left: 20, right: 30 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
            <XAxis
              type="number"
              stroke={UI.textMuted}
              tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`}
              fontSize={12}
            />
            <YAxis
              dataKey="item"
              type="category"
              stroke={UI.textMuted}
              width={90}
              fontSize={12}
            />
            <Tooltip
              formatter={(value: number) => `${formatNumber(value)} تومان`}
              contentStyle={{
                backgroundColor: GIS.background,
                border: '1px solid #334155',
                borderRadius: '8px',
                color: CHART.white,
              }}
            />
            <Bar dataKey="value" radius={[0, 6, 6, 0]} barSize={22}>
              {profitData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}