"use client";

import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { useCurrentWeather, useWeatherForecast } from '@/hooks/weather/useWeather';
import { 
  Thermometer, Droplets, Wind, Sun, CloudRain, Cloud, 
  MapPin, Search, TrendingUp, TrendingDown, Calendar
} from 'lucide-react';

export default function WeatherPage() {
  const { t } = useTranslation();
  const [lat, setLat] = useState(35.6892);
  const [lng, setLng] = useState(51.3890);
  const [location, setLocation] = useState('تهران');
  
  const { data: current, isLoading: currentLoading } = useCurrentWeather(lat, lng);
  const { data: forecast, isLoading: forecastLoading } = useWeatherForecast(lat, lng, 7);

  const handleSearch = () => {
    // In real app, use geocoding API
    setLocation(`موقعیت ${lat.toFixed(2)}, ${lng.toFixed(2)}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">{t('weather.title')}</h1>
          <p className="text-slate-400">{t('weather.subtitle')}</p>
        </div>

        {/* Location Search */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-emerald-400" />
            جستجوی موقعیت
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-sm text-slate-400 mb-1 block">{t('weather.latitude')}</label>
              <Input
                type="number"
                step="0.0001"
                value={lat}
                onChange={(e) => setLat(parseFloat(e.target.value))}
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 mb-1 block">{t('weather.longitude')}</label>
              <Input
                type="number"
                step="0.0001"
                value={lng}
                onChange={(e) => setLng(parseFloat(e.target.value))}
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            <div className="flex items-end">
              <Button onClick={handleSearch} className="w-full bg-emerald-600 hover:bg-emerald-700">
                <Search className="w-4 h-4 ml-2" />
                جستجو
              </Button>
            </div>
          </div>
          <div className="mt-3 text-sm text-slate-400">
            موقعیت فعلی: <span className="text-white">{location}</span>
          </div>
        </Card>

        {/* Current Weather */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Sun className="w-5 h-5 text-yellow-400" />
            هوای فعلی
          </h3>
          
          {currentLoading ? (
            <div className="text-center py-8 text-slate-400">{t('common.loading')}</div>
          ) : current ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-slate-800/50 rounded-lg p-4">
                <Thermometer className="w-6 h-6 text-orange-400 mb-2" />
                <div className="text-3xl font-bold text-white">{current.temperature?.toFixed(1)}°C</div>
                <div className="text-xs text-slate-400">{t('weather.temperature')}</div>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg p-4">
                <Droplets className="w-6 h-6 text-blue-400 mb-2" />
                <div className="text-3xl font-bold text-white">{current.humidity}%</div>
                <div className="text-xs text-slate-400">{t('weather.humidity')}</div>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg p-4">
                <Wind className="w-6 h-6 text-teal-400 mb-2" />
                <div className="text-3xl font-bold text-white">{current.wind_speed?.toFixed(1)}</div>
                <div className="text-xs text-slate-400">{t('weather.wind_speed')}</div>
              </div>
              
              <div className="bg-slate-800/50 rounded-lg p-4">
                <CloudRain className="w-6 h-6 text-indigo-400 mb-2" />
                <div className="text-3xl font-bold text-white">{current.precipitation?.toFixed(1)}</div>
                <div className="text-xs text-slate-400">{t('weather.precipitation')}</div>
              </div>

              <div className="bg-slate-800/50 rounded-lg p-4">
                <Cloud className="w-6 h-6 text-slate-400 mb-2" />
                <div className="text-3xl font-bold text-white">{current.cloud_cover}%</div>
                <div className="text-xs text-slate-400">{t('weather.cloud_cover')}</div>
              </div>

              <div className="bg-slate-800/50 rounded-lg p-4">
                <TrendingUp className="w-6 h-6 text-purple-400 mb-2" />
                <div className="text-3xl font-bold text-white">{current.pressure?.toFixed(0)}</div>
                <div className="text-xs text-slate-400">{t('weather.pressure')}</div>
              </div>

              <div className="bg-slate-800/50 rounded-lg p-4 col-span-2">
                <div className="text-sm text-slate-400 mb-1">وضعیت هوا</div>
                <div className="text-xl font-bold text-white">{current.weather_description || 'نامشخص'}</div>
                <div className="text-xs text-slate-400 mt-1">آخرین به‌روزرسانی: {current.timestamp}</div>
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">داده‌ای در دسترس نیست</div>
          )}
        </Card>

        {/* 7-Day Forecast */}
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Calendar className="w-5 h-5 text-blue-400" />
            پیش‌بینی ۷ روزه
          </h3>
          
          {forecastLoading ? (
            <div className="text-center py-8 text-slate-400">{t('common.loading')}</div>
          ) : forecast && forecast.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-7 gap-3">
              {forecast.map((day: any, idx: number) => (
                <div key={idx} className="bg-slate-800/50 rounded-lg p-4 text-center">
                  <div className="text-sm text-slate-400 mb-2">{day.date?.slice(5)}</div>
                  <div className="text-2xl font-bold text-white mb-1">{day.temp_max?.toFixed(0)}°</div>
                  <div className="text-sm text-slate-400">{day.temp_min?.toFixed(0)}°</div>
                  <div className="mt-3 pt-3 border-t border-slate-700">
                    <div className="text-xs text-blue-400">{day.precipitation_sum?.toFixed(1)} mm</div>
                    <div className="text-xs text-slate-400">{day.precipitation_probability}%</div>
                  </div>
                  <div className="mt-2 text-xs text-slate-400">
                    باد: {day.wind_speed_max?.toFixed(0)} km/h
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">پیش‌بینی در دسترس نیست</div>
          )}
        </Card>

        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">{t('weather.data_source')}</h4>
            <p className="text-sm text-slate-400">Open-Meteo API - رایگان و بدون نیاز به API Key</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">{t('weather.accuracy')}</h4>
            <p className="text-sm text-slate-400">مدل‌های ECMWF, GFS, JMA با دقت ۱۱ کیلومتر</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">{t('weather.update_frequency')}</h4>
            <p className="text-sm text-slate-400">داده‌های فعلی هر ۱۰ دقیقه، پیش‌بینی هر ۳۰ دقیقه</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
