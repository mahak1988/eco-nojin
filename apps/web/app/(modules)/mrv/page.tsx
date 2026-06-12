"use client";

import { ForestDashboard } from "@/components/forest/ForestDashboard";
import { Card } from '@/components/ui/card';
import { useForestMetrics, useCarbonSequestration } from '@/hooks/forest/useForest';
import { TreePine, Leaf, Coins } from 'lucide-react';

export default function MRVPage() {
  const { t } = useTranslation();
  const { data: forest } = useForestMetrics(35.6892, 51.3890);
  const { data: carbon } = useCarbonSequestration(35.6892, 51.3890, 10);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pt-20">
      <div className="container mx-auto px-4 py-8">
        <ForestDashboard />
        <h1 className="text-3xl font-bold text-white mb-6">{t('mrv.title')}</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {forest && (
            <Card className="bg-slate-900/50 border-slate-800 p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <TreePine className="w-5 h-5 text-emerald-400" />
                معیارهای جنگل
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-400">{t('mrv.canopy_height')}:</span>
                  <span className="text-white font-bold">{forest.mean_canopy_height} m</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">{t('mrv.canopy_cover')}:</span>
                  <span className="text-white font-bold">{forest.canopy_cover}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">{t('mrv.biomass')}:</span>
                  <span className="text-white font-bold">{forest.estimated_biomass} t/ha</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">{t('mrv.forest_type')}:</span>
                  <span className="text-white font-bold">{forest.forest_type}</span>
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
              <div className="space-y-3">
                <div className="flex justify-between">
                  <span className="text-slate-400">کربن جذب شده:</span>
                  <span className="text-white font-bold">{carbon.carbon_sequestered_tons} t</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">معادل CO2:</span>
                  <span className="text-white font-bold">{carbon.co2_equivalent_tons} t</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">ارزش اقتصادی:</span>
                  <span className="text-emerald-400 font-bold">${carbon.economic_value_usd}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">در هکتار:</span>
                  <span className="text-white font-bold">{carbon.per_hectare} t/ha</span>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}