"use client";

import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Satellite, Mountain, Map, Layers, Globe } from 'lucide-react';
import { useGisStore } from '@/store/gis/useGisStore';

export function SatelliteLayers() {
  const { selectedLayer, setSelectedLayer } = useGisStore();

  const layers = [
    {
      id: 'Sentinel-2 TMS',
      name: 'Sentinel-2 (TMS)',
      icon: Satellite,
      description: '10m | 5 روز تکرار | EOX',
      color: 'text-emerald-400'
    },
    {
      id: 'Sentinel-2',
      name: 'Sentinel-2 (WMS)',
      icon: Satellite,
      description: 'کیفیت بالا | WMS',
      color: 'text-emerald-300'
    },
    {
      id: 'Landsat',
      name: 'Landsat 8/9',
      icon: Satellite,
      description: '30m | 16 روز تکرار | USGS',
      color: 'text-blue-400'
    },
    {
      id: 'Esri Satellite',
      name: 'Esri World Imagery',
      icon: Layers,
      description: 'رزولوشن بالا | Esri',
      color: 'text-purple-400'
    },
    {
      id: 'Topographic',
      name: 'توپوگرافی',
      icon: Mountain,
      description: 'ارتفاع و عوارض زمین',
      color: 'text-orange-400'
    },
    {
      id: 'OSM',
      name: 'OpenStreetMap',
      icon: Map,
      description: 'نقشه خیابانی',
      color: 'text-slate-400'
    }
  ];

  return (
    <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
      <div className="p-4 border-b border-slate-800">
        <h3 className="font-semibold text-white flex items-center gap-2">
          <Globe className="w-4 h-4" />
          لایه‌های ماهواره‌ای و نقشه
        </h3>
      </div>
      <div className="p-4 space-y-2">
        {layers.map((layer) => {
          const Icon = layer.icon;
          const isActive = selectedLayer === layer.id;
          
          return (
            <Button
              key={layer.id}
              variant={isActive ? 'default' : 'outline'}
              className={`w-full justify-start gap-2 ${
                isActive 
                  ? 'bg-emerald-600 hover:bg-emerald-700' 
                  : 'border-slate-700 hover:bg-slate-800'
              }`}
              onClick={() => setSelectedLayer(layer.id)}
            >
              <Icon className={`w-4 h-4 ${layer.color}`} />
              <div className="flex-1 text-right">
                <div className="text-sm font-medium">{layer.name}</div>
                <div className="text-xs text-slate-400">{layer.description}</div>
              </div>
              {isActive && <Badge className="bg-white text-emerald-600">فعال</Badge>}
            </Button>
          );
        })}
      </div>
    </Card>
  );
}
