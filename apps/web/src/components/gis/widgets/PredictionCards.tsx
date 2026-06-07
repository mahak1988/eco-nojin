"use client";

import { Card } from '@/components/ui/card';
import { TrendingUp, TrendingDown, Minus, Sprout, Droplet, AlertTriangle } from 'lucide-react';

export function PredictionCards() {
  const predictions = [
    {
      title: 'پیش‌بینی محصول',
      value: '4.2',
      unit: 'تن/هکتار',
      change: '+12%',
      trend: 'up',
      color: 'text-emerald-400',
      icon: Sprout,
      confidence: 87
    },
    {
      title: 'شاخص خشکسالی',
      value: '0.35',
      unit: 'SPEI',
      change: '-0.05',
      trend: 'down',
      color: 'text-blue-400',
      icon: Droplet,
      confidence: 92
    },
    {
      title: 'نیاز آبیاری',
      value: '4500',
      unit: 'm³/هکتار',
      change: '0',
      trend: 'stable',
      color: 'text-yellow-400',
      icon: Droplet,
      confidence: 78
    },
    {
      title: 'خطر آفت',
      value: 'متوسط',
      unit: '',
      change: '+15%',
      trend: 'up',
      color: 'text-orange-400',
      icon: AlertTriangle,
      confidence: 65
    }
  ];

  return (
    <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
      <div className="p-4">
        <h3 className="font-semibold text-white mb-4">پیش‌بینی‌های هوشمند</h3>
        <div className="space-y-3">
          {predictions.map((pred, idx) => {
            const Icon = pred.icon;
            return (
              <div key={idx} className="p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon className={`w-5 h-5 ${pred.color}`} />
                    <div>
                      <div className="text-xs text-slate-400">{pred.title}</div>
                      <div className="text-lg font-bold text-white">
                        {pred.value} {pred.unit}
                      </div>
                    </div>
                  </div>
                  <div className={`flex items-center gap-1 ${pred.color}`}>
                    {pred.trend === 'up' && <TrendingUp className="w-4 h-4" />}
                    {pred.trend === 'down' && <TrendingDown className="w-4 h-4" />}
                    {pred.trend === 'stable' && <Minus className="w-4 h-4" />}
                    <span className="text-sm">{pred.change}</span>
                  </div>
                </div>
                
                <div className="mt-2">
                  <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
                    <span>اطمینان</span>
                    <span>{pred.confidence}%</span>
                  </div>
                  <div className="w-full bg-slate-700 rounded-full h-1.5">
                    <div 
                      className={`h-1.5 rounded-full ${pred.color.replace('text', 'bg')}`}
                      style={{ width: `${pred.confidence}%` }}
                    ></div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
