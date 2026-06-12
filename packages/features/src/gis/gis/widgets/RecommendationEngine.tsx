"use client";

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Lightbulb, CheckCircle, AlertTriangle, Droplet, Sprout, Bug } from 'lucide-react';

export function RecommendationEngine() {
  const recommendations = [
    {
      title: 'آبیاری بهینه',
      description: 'افزایش 20% راندمان آبیاری با سیستم قطره‌ای',
      priority: 'high',
      icon: Droplet,
      color: 'text-blue-400',
      impact: 'افزایش 15% محصول'
    },
    {
      title: 'کوددهی نیتروژن',
      description: 'استفاده از کود اوره در هفته آینده',
      priority: 'medium',
      icon: Sprout,
      color: 'text-emerald-400',
      impact: 'بهبود NDVI تا 0.15'
    },
    {
      title: 'پایش آفات',
      description: 'بررسی منظم برای پیشگیری از آفت کرم ساقه‌خوار',
      priority: 'high',
      icon: Bug,
      color: 'text-orange-400',
      impact: 'کاهش 30% خسارت'
    },
    {
      title: 'برداشت بهینه',
      description: 'زمان مناسب برداشت: 10 روز آینده',
      priority: 'low',
      icon: CheckCircle,
      color: 'text-yellow-400',
      impact: 'بالاترین کیفیت محصول'
    }
  ];

  return (
    <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
      <div className="p-4">
        <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
          <Lightbulb className="w-4 h-4 text-yellow-400" />
          توصیه‌های هوشمند
        </h3>
        <div className="space-y-3">
          {recommendations.map((rec, idx) => {
            const Icon = rec.icon;
            return (
              <div key={idx} className="p-3 bg-slate-800/50 rounded-lg">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <Icon className={`w-5 h-5 ${rec.color}`} />
                    <div>
                      <div className="font-medium text-white text-sm">{rec.title}</div>
                      <Badge 
                        variant={rec.priority === 'high' ? 'destructive' : rec.priority === 'medium' ? 'default' : 'secondary'}
                        className="mt-1"
                      >
                        {rec.priority === 'high' ? 'فوری' : rec.priority === 'medium' ? 'مهم' : 'عادی'}
                      </Badge>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-400 mb-2">{rec.description}</p>
                <div className="text-xs text-emerald-400 mb-2">
                  💡 {rec.impact}
                </div>
                <Button size="sm" variant="outline" className="w-full text-xs">
                  اعمال توصیه
                </Button>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
}
