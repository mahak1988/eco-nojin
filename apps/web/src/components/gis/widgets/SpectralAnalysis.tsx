"use client";

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, Leaf, Droplet, Sun } from 'lucide-react';

export function SpectralAnalysis() {
  const indices = [
    {
      name: 'NDVI',
      fullName: 'Normalized Difference Vegetation Index',
      value: 0.72,
      status: 'healthy',
      color: 'text-emerald-400',
      bgColor: 'bg-emerald-500/20',
      description: 'شاخص پوشش گیاهی'
    },
    {
      name: 'EVI',
      fullName: 'Enhanced Vegetation Index',
      value: 0.58,
      status: 'good',
      color: 'text-green-400',
      bgColor: 'bg-green-500/20',
      description: 'شاخص بهبودیافته گیاهی'
    },
    {
      name: 'NDWI',
      fullName: 'Normalized Difference Water Index',
      value: 0.35,
      status: 'moderate',
      color: 'text-blue-400',
      bgColor: 'bg-blue-500/20',
      description: 'شاخص رطوبت'
    },
    {
      name: 'SAVI',
      fullName: 'Soil Adjusted Vegetation Index',
      value: 0.65,
      status: 'good',
      color: 'text-teal-400',
      bgColor: 'bg-teal-500/20',
      description: 'شاخص گیاهی تنظیم‌شده با خاک'
    },
    {
      name: 'NBR',
      fullName: 'Normalized Burn Ratio',
      value: 0.12,
      status: 'low',
      color: 'text-yellow-400',
      bgColor: 'bg-yellow-500/20',
      description: 'شاخص سوختگی'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      {indices.map((index, idx) => (
        <Card key={idx} className="bg-slate-900/50 border-slate-800 backdrop-blur">
          <div className="p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Leaf className={`w-5 h-5 ${index.color}`} />
                <h3 className="font-semibold text-white">{index.name}</h3>
              </div>
              <Badge className={index.bgColor + ' ' + index.color}>
                {index.status}
              </Badge>
            </div>
            
            <div className="text-3xl font-bold text-white mb-2">
              {index.value.toFixed(2)}
            </div>
            
            <div className="text-xs text-slate-400 mb-3">
              {index.description}
            </div>
            
            <div className="w-full bg-slate-800 rounded-full h-2 mb-2">
              <div 
                className={`h-2 rounded-full ${index.bgColor.replace('/20', '')}`}
                style={{ width: `${Math.abs(index.value) * 100}%` }}
              ></div>
            </div>
            
            <div className="flex items-center justify-between text-xs text-slate-400">
              <span>Min: -1.0</span>
              <span>Max: 1.0</span>
            </div>
          </div>
        </Card>
      ))}
      
      <Card className="bg-slate-900/50 border-slate-800 backdrop-blur md:col-span-2 lg:col-span-3">
        <div className="p-4">
          <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
            <TrendingUp className="w-4 h-4" />
            تحلیل زمانی شاخص‌ها
          </h3>
          <div className="grid grid-cols-7 gap-2">
            {['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر'].map((month, idx) => (
              <div key={idx} className="text-center">
                <div className="text-xs text-slate-400 mb-1">{month}</div>
                <div className="bg-emerald-500/20 rounded p-2">
                  <div className="text-lg font-bold text-emerald-400">
                    {(0.5 + Math.random() * 0.3).toFixed(2)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    </div>
  );
}
