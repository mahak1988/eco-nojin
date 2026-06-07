"use client";

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useCurrentWeather, useWeatherForecast } from '@/hooks/weather/useWeather';
import { Thermometer, Droplets, Wind, Sun, CloudRain } from 'lucide-react';

export function WeatherDashboard() {
  const { data: current, isLoading } = useCurrentWeather(35.6892, 51.3890);
  const { data: forecast } = useWeatherForecast(35.6892, 51.3890, 7);

  if (isLoading) {
    return <div className="text-center py-8 text-slate-400">در حال بارگذاری...</div>;
  }

  return (
    <div className="space-y-4">
      <Card className="bg-slate-900/50 border-slate-800 p-6">
        <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
          <Sun className="w-5 h-5 text-yellow-400" />
          هوای فعلی
        </h3>
        
        {current && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-4">
              <Thermometer className="w-6 h-6 text-orange-400 mb-2" />
              <div className="text-2xl font-bold text-white">{current.temperature?.toFixed(1)}°C</div>
              <div className="text-xs text-slate-400">دما</div>
            </div>
            
            <div className="bg-slate-800/50 rounded-lg p-4">
              <Droplets className="w-6 h-6 text-blue-400 mb-2" />
              <div className="text-2xl font-bold text-white">{current.humidity}%</div>
              <div className="text-xs text-slate-400">رطوبت</div>
            </div>
            
            <div className="bg-slate-800/50 rounded-lg p-4">
              <Wind className="w-6 h-6 text-teal-400 mb-2" />
              <div className="text-2xl font-bold text-white">{current.wind_speed?.toFixed(1)}</div>
              <div className="text-xs text-slate-400">باد (km/h)</div>
            </div>
            
            <div className="bg-slate-800/50 rounded-lg p-4">
              <CloudRain className="w-6 h-6 text-indigo-400 mb-2" />
              <div className="text-2xl font-bold text-white">{current.precipitation?.toFixed(1)}</div>
              <div className="text-xs text-slate-400">بارش (mm)</div>
            </div>
          </div>
        )}
      </Card>

      {forecast && forecast.length > 0 && (
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4">پیش‌بینی ۷ روزه</h3>
          <div className="grid grid-cols-7 gap-2">
            {forecast.slice(0, 7).map((day: any, idx: number) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-3 text-center">
                <div className="text-xs text-slate-400 mb-1">{day.date?.slice(5)}</div>
                <div className="text-lg font-bold text-white">{day.temp_max?.toFixed(0)}°</div>
                <div className="text-xs text-slate-400">{day.temp_min?.toFixed(0)}°</div>
                <div className="text-xs text-blue-400 mt-1">{day.precipitation_sum?.toFixed(1)}mm</div>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
}
