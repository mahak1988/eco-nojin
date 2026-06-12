"use client";

import { useTranslation } from '@/hooks/useTranslation';

import { DroughtDashboard } from "@/components/drought/DroughtDashboard";
import { Card } from '@/components/ui/card';
import { useDroughtRisk, useSPEIAnalysis } from '@/hooks/drought/useDrought';
import { AlertTriangle, Droplets, TrendingUp } from 'lucide-react';

export default function DroughtPage() {
  const { t } = useTranslation();
  const { data: risk } = useDroughtRisk(35.6892, 51.3890);
  const { data: spei } = useSPEIAnalysis(35.6892, 51.3890);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pt-20">
      <div className="container mx-auto px-4 py-8">
        <DroughtDashboard />
        <h1 className="text-3xl font-bold text-white mb-6">{t('drought.title')}</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {risk && (
            <Card className="bg-slate-900/50 border-slate-800 p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <AlertTriangle className="w-5 h-5" style={{color: risk.color}} />
                وضعیت خشکسالی
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-400">سطح:</span>
                  <span className="text-white font-bold">{risk.description}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">امتیاز:</span>
                  <span className="text-white font-bold">{risk.score}/100</span>
                </div>
                <div className="p-3 bg-slate-800/50 rounded-lg">
                  <div className="text-sm text-slate-400 mb-1">توصیه:</div>
                  <div className="text-white">{risk.recommendation}</div>
                </div>
              </div>
            </Card>
          )}
          
          {spei && (
            <Card className="bg-slate-900/50 border-slate-800 p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <Droplets className="w-5 h-5 text-blue-400" />
                شاخص SPEI
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-400">مقدار فعلی:</span>
                  <span className="text-white font-bold">{spei.current_spei}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">دسته:</span>
                  <span className="text-white font-bold">{spei.drought_severity}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">مدت (ماه):</span>
                  <span className="text-white font-bold">{spei.duration_months}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">{t('drought.trend')}</span>
                  <span className="text-white font-bold">
                    {spei.trend === 'improving' ? '📈 بهبود' : 
                     spei.trend === 'worsening' ? '📉 وخامت' : '➡️ پایدار'}
                  </span>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}