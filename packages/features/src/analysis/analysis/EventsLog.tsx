'use client';

import { Radio, CheckCircle2, AlertCircle, Loader2 } from 'lucide-react';
import { useAnalysisStore } from '@/store/analysis';
import { cn } from '@/lib/utils';

export function EventsLog() {
  const events = useAnalysisStore((state) => state.events);
  const isLoading = useAnalysisStore((state) => state.isLoading);

  if (events.length === 0 && !isLoading) return null;

  const recentEvents = events.slice(-6).reverse();

  return (
    <div
      className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-5 border border-slate-700 shadow-xl"
      dir="rtl"
    >
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-amber-500/20 flex items-center justify-center">
            <Radio className="w-5 h-5 text-amber-400" />
          </div>
          <h4 className="font-bold text-white">رویدادهای بلادرنگ</h4>
        </div>
        {isLoading && (
          <span className="flex items-center gap-1.5 text-xs text-sky-400 bg-sky-500/10 px-2.5 py-1 rounded-full">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-sky-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-sky-500"></span>
            </span>
            در حال پردازش
          </span>
        )}
      </div>

      <div className="space-y-2 max-h-[240px] overflow-y-auto custom-scrollbar">
        {recentEvents.length === 0 ? (
          <div className="text-center py-6 text-slate-500 text-sm">
            <Loader2 className="w-5 h-5 animate-spin mx-auto mb-2" />
            در انتظار شروع تحلیل...
          </div>
        ) : (
          recentEvents.map((event, idx) => {
            const config = {
              start: {
                icon: <Radio className="w-4 h-4" />,
                style: 'border-sky-500 bg-sky-900/20 text-sky-200',
              },
              processing: {
                icon: <Loader2 className="w-4 h-4 animate-spin" />,
                style: 'border-amber-500 bg-amber-900/20 text-amber-200',
              },
              final: {
                icon: <CheckCircle2 className="w-4 h-4" />,
                style: 'border-emerald-500 bg-emerald-900/20 text-emerald-200',
              },
              error: {
                icon: <AlertCircle className="w-4 h-4" />,
                style: 'border-red-500 bg-red-900/20 text-red-200',
              },
            };

            const { icon, style } =
              config[event.event_type as keyof typeof config] || config.start;

            return (
              <div
                key={`${event.timestamp}-${idx}`}
                className={cn(
                  'border-r-4 px-3 py-2.5 rounded-lg text-sm flex items-start gap-2',
                  'transition-all animate-in fade-in slide-in-from-right-2 duration-300',
                  style
                )}
              >
                <span className="mt-0.5 flex-shrink-0">{icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium">{event.message}</div>
                  <div className="text-xs opacity-70 mt-0.5">
                    {new Date(event.timestamp * 1000).toLocaleTimeString('fa-IR')}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}