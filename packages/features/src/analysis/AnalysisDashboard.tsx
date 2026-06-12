'use client';

import { useEffect } from 'react';
import dynamic from 'next/dynamic';
import { useAnalysisStore } from '@/store/analysis';
import { useAnalysisWebSocket } from '@/hooks/analysis';
import { AnalysisForm } from './AnalysisForm';
import { ChartsPanel } from './ChartsPanel';
import { EventsLog } from './EventsLog';

const MapPanel = dynamic(() => import('./MapPanel').then((mod) => mod.MapPanel), {
  ssr: false,
  loading: () => (
    <div className="bg-slate-800/50 rounded-2xl p-8 h-[400px] flex items-center justify-center text-slate-400 border border-slate-700">
      <p>در حال بارگذاری نقشه...</p>
    </div>
  ),
});

export function AnalysisDashboard() {
  const fetchRegions = useAnalysisStore((state) => state.fetchRegions);
  const fetchAnalyses = useAnalysisStore((state) => state.fetchAnalyses);

  useAnalysisWebSocket();

  useEffect(() => {
    fetchRegions();
    fetchAnalyses();
  }, [fetchRegions, fetchAnalyses]);

  return (
    <div className="w-full" dir="rtl">
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-4 space-y-6">
          <AnalysisForm />
          <EventsLog />
        </div>
        <div className="lg:col-span-8 space-y-6">
          <ChartsPanel />
          <MapPanel />
        </div>
      </div>
    </div>
  );
}