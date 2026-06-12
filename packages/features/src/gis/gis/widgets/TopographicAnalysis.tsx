"use client";

import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Mountain, TrendingUp, Compass, Droplet } from 'lucide-react';

export function TopographicAnalysis() {
  const topographicData = {
    elevation: {
      min: 1200,
      max: 1850,
      avg: 1525,
      unit: 'm'
    },
    slope: {
      min: 2,
      max: 35,
      avg: 12,
      unit: '°'
    },
    aspect: {
      dominant: 'North-West',
      degrees: 315
    },
    curvature: {
      type: 'Concave',
      value: -0.15
    }
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
        <div className="p-4">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Mountain className="w-4 h-4 text-orange-400" />
            ارتفاع از سطح دریا
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">حداقل</span>
              <Badge className="bg-blue-600">{topographicData.elevation.min} m</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">میانگین</span>
              <Badge className="bg-emerald-600">{topographicData.elevation.avg} m</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">حداکثر</span>
              <Badge className="bg-red-600">{topographicData.elevation.max} m</Badge>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="text-xs text-slate-400 mb-2">پروفایل ارتفاعی</div>
            <div className="h-20 bg-gradient-to-r from-blue-500 via-emerald-500 to-red-500 rounded"></div>
          </div>
        </div>
      </Card>
      
      <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
        <div className="p-4">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-yellow-400" />
            شیب زمین
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">حداقل</span>
              <Badge className="bg-green-600">{topographicData.slope.min}°</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">میانگین</span>
              <Badge className="bg-yellow-600">{topographicData.slope.avg}°</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">حداکثر</span>
              <Badge className="bg-orange-600">{topographicData.slope.max}°</Badge>
            </div>
          </div>
          
          <div className="mt-4">
            <div className="text-xs text-slate-400 mb-2">نقشه شیب</div>
            <div className="h-20 bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded"></div>
          </div>
        </div>
      </Card>
      
      <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
        <div className="p-4">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Compass className="w-4 h-4 text-purple-400" />
            جهت شیب (Aspect)
          </h3>
          <div className="flex items-center justify-center">
            <div className="relative w-32 h-32">
              <div className="absolute inset-0 border-4 border-slate-700 rounded-full"></div>
              <div 
                className="absolute top-1/2 left-1/2 w-1 h-16 bg-purple-500 origin-bottom"
                style={{ 
                  transform: `translate(-50%, -100%) rotate(${topographicData.aspect.degrees}deg)` 
                }}
              ></div>
              <div className="absolute top-0 left-1/2 transform -translate-x-1/2 text-xs text-slate-400">N</div>
              <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 text-xs text-slate-400">S</div>
              <div className="absolute left-0 top-1/2 transform -translate-y-1/2 text-xs text-slate-400">W</div>
              <div className="absolute right-0 top-1/2 transform -translate-y-1/2 text-xs text-slate-400">E</div>
            </div>
          </div>
          <div className="text-center mt-4">
            <div className="text-2xl font-bold text-white">{topographicData.aspect.degrees}°</div>
            <div className="text-sm text-slate-400">{topographicData.aspect.dominant}</div>
          </div>
        </div>
      </Card>
      
      <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
        <div className="p-4">
          <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
            <Droplet className="w-4 h-4 text-blue-400" />
            انحنای زمین
          </h3>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">نوع</span>
              <Badge className="bg-blue-600">{topographicData.curvature.type}</Badge>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-400">مقدار</span>
              <Badge className="bg-slate-600">{topographicData.curvature.value}</Badge>
            </div>
          </div>
          
          <div className="mt-4 p-3 bg-slate-800/50 rounded-lg">
            <div className="text-xs text-slate-400 mb-2">تأثیر بر آبیاری</div>
            <div className="text-sm text-white">
              زمین مقعر باعث تجمع آب در مرکز مزرعه می‌شود
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
