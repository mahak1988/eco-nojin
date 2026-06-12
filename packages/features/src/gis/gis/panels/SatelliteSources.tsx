"use client";

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ExternalLink, Satellite, Globe, Radar, Mountain } from 'lucide-react';

export function SatelliteSources() {
  const satellites = [
    {
      name: 'Sentinel-2',
      provider: 'ESA/Copernicus',
      resolution: '10m',
      revisit: '5 روز',
      status: 'active',
      url: 'https://sentinel.esa.int/web/sentinel/missions/sentinel-2',
      icon: Satellite,
      color: 'text-emerald-400',
      description: 'تصاویر چندطیفی با رزولوشن بالا'
    },
    {
      name: 'Landsat 8/9',
      provider: 'NASA/USGS',
      resolution: '30m',
      revisit: '16 روز',
      status: 'active',
      url: 'https://landsat.gsfc.nasa.gov/',
      icon: Satellite,
      color: 'text-blue-400',
      description: 'قدیمی‌ترین برنامه مشاهده زمین'
    },
    {
      name: 'Sentinel-1',
      provider: 'ESA/Copernicus',
      resolution: '5x20m',
      revisit: '6 روز',
      status: 'active',
      url: 'https://sentinel.esa.int/web/sentinel/missions/sentinel-1',
      icon: Radar,
      color: 'text-purple-400',
      description: 'رادار SAR - تمام‌weather'
    },
    {
      name: 'MODIS',
      provider: 'NASA',
      resolution: '250m-1km',
      revisit: 'روزانه',
      status: 'active',
      url: 'https://modis.gsfc.nasa.gov/',
      icon: Globe,
      color: 'text-orange-400',
      description: 'پایش روزانه جهانی'
    },
    {
      name: 'VIIRS',
      provider: 'NASA/NOAA',
      resolution: '375m',
      revisit: 'روزانه',
      status: 'active',
      url: 'https://viirsland.gsfc.nasa.gov/',
      icon: Globe,
      color: 'text-cyan-400',
      description: 'جانشین MODIS'
    },
    {
      name: 'SRTM',
      provider: 'NASA',
      resolution: '30m',
      revisit: 'یک‌بار',
      status: 'active',
      url: 'https://www2.jpl.nasa.gov/srtm/',
      icon: Mountain,
      color: 'text-yellow-400',
      description: 'مدل ارتفاعی دیجیتال'
    },
    {
      name: 'GEDI',
      provider: 'NASA',
      resolution: '25m',
      revisit: 'متغیر',
      status: 'active',
      url: 'https://gedi.umd.edu/',
      icon: Mountain,
      color: 'text-green-400',
      description: 'اندازه‌گیری ارتفاع جنگل'
    },
    {
      name: 'Planet NICFI',
      provider: 'Planet/NOAA',
      resolution: '4.77m',
      revisit: 'ماهانه',
      status: 'active',
      url: 'https://www.planet.com/nicfi/',
      icon: Satellite,
      color: 'text-pink-400',
      description: 'رایگان برای مناطق استوایی'
    }
  ];

  return (
    <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
      <div className="p-4 border-b border-slate-800">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Satellite className="w-4 h-4 text-emerald-400" />
          منابع داده ماهواره‌ای
        </h3>
      </div>
      <div className="p-4 space-y-2 max-h-[400px] overflow-y-auto">
        {satellites.map((sat, idx) => {
          const Icon = sat.icon;
          return (
            <div key={idx} className="p-3 bg-slate-800/30 rounded-lg hover:bg-slate-800/50 transition-colors">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <Icon className={`w-4 h-4 ${sat.color}`} />
                  <div className="font-medium text-white text-sm">{sat.name}</div>
                </div>
                <Badge className={sat.status === 'active' ? 'bg-green-600' : 'bg-red-600'}>
                  {sat.status === 'active' ? 'فعال' : 'غیرفعال'}
                </Badge>
              </div>
              
              <div className="text-xs text-slate-400 mb-2">{sat.description}</div>
              
              <div className="grid grid-cols-3 gap-2 text-xs mb-2">
                <div className="bg-slate-900/50 rounded p-1 text-center">
                  <div className="text-slate-500">رزولوشن</div>
                  <div className="text-white font-medium">{sat.resolution}</div>
                </div>
                <div className="bg-slate-900/50 rounded p-1 text-center">
                  <div className="text-slate-500">تکرار</div>
                  <div className="text-white font-medium">{sat.revisit}</div>
                </div>
                <div className="bg-slate-900/50 rounded p-1 text-center">
                  <div className="text-slate-500">ارائه‌دهنده</div>
                  <div className="text-white font-medium truncate">{sat.provider}</div>
                </div>
              </div>
              
              <Button 
                size="sm" 
                variant="ghost" 
                className="w-full text-xs gap-1 text-slate-400 hover:text-white"
                onClick={() => window.open(sat.url, '_blank')}
              >
                <ExternalLink className="w-3 h-3" />
                مشاهده اطلاعات بیشتر
              </Button>
            </div>
          );
        })}
      </div>
    </Card>
  );
}
