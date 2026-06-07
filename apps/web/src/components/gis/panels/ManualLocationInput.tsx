"use client";

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { MapPin, Save, Trash2, Upload, Download } from 'lucide-react';
import { useGisStore } from '@/store/gis/useGisStore';

export function ManualLocationInput() {
  const { addFeature, drawnFeatures, setMapCenter, setMapZoom } = useGisStore();
  const [formData, setFormData] = useState({
    name: '',
    latitude: '',
    longitude: '',
    area: '',
    cropType: '',
    notes: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const lat = parseFloat(formData.latitude);
    const lng = parseFloat(formData.longitude);
    const area = parseFloat(formData.area) || 0;
    
    if (isNaN(lat) || isNaN(lng)) {
      alert('لطفاً مختصات معتبر وارد کنید');
      return;
    }
    
    // Create a circular farm polygon based on area (if provided)
    let polygon;
    if (area > 0) {
      // Create approximate circle based on area (in hectares)
      const radius = Math.sqrt(area * 10000 / Math.PI); // radius in meters
      const numPoints = 32;
      const coordinates: [number, number][] = [];
      
      for (let i = 0; i <= numPoints; i++) {
        const angle = (2 * Math.PI * i) / numPoints;
        const dLat = (radius / 111320) * Math.cos(angle);
        const dLng = (radius / (111320 * Math.cos(lat * Math.PI / 180))) * Math.sin(angle);
        coordinates.push([lat + dLat, lng + dLng]);
      }
      
      polygon = {
        type: 'Feature' as const,
        geometry: {
          type: 'Polygon' as const,
          coordinates: [coordinates]
        },
        properties: {
          type: 'farm',
          name: formData.name || `مزرعه ${drawnFeatures.length + 1}`,
          area: area * 10000, // convert to m²
          area_hectares: area,
          perimeter: 2 * Math.PI * radius,
          center: [lng, lat],
          crop_type: formData.cropType,
          notes: formData.notes,
          created_at: new Date().toISOString(),
          source: 'manual'
        }
      };
    } else {
      // Just create a point marker
      polygon = {
        type: 'Feature' as const,
        geometry: {
          type: 'Point' as const,
          coordinates: [lng, lat]
        },
        properties: {
          type: 'location',
          name: formData.name || `موقعیت ${drawnFeatures.length + 1}`,
          crop_type: formData.cropType,
          notes: formData.notes,
          created_at: new Date().toISOString(),
          source: 'manual'
        }
      };
    }
    
    addFeature(polygon);
    setMapCenter({ lat, lng });
    setMapZoom(16);
    
    // Reset form
    setFormData({
      name: '',
      latitude: '',
      longitude: '',
      area: '',
      cropType: '',
      notes: ''
    });
  };

  const handleExport = () => {
    const data = drawnFeatures.map(f => ({
      name: f.properties?.name,
      latitude: f.geometry.type === 'Point' ? f.geometry.coordinates[1] : f.properties?.center?.[1],
      longitude: f.geometry.type === 'Point' ? f.geometry.coordinates[0] : f.properties?.center?.[0],
      area_hectares: f.properties?.area_hectares,
      crop_type: f.properties?.crop_type,
      created_at: f.properties?.created_at
    }));
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'locations.json';
    a.click();
  };

  const handleImport = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      try {
        const data = JSON.parse(event.target?.result as string);
        data.forEach((item: any) => {
          const feature = {
            type: 'Feature' as const,
            geometry: {
              type: 'Point' as const,
              coordinates: [item.longitude, item.latitude]
            },
            properties: {
              type: 'location',
              name: item.name,
              area_hectares: item.area_hectares,
              crop_type: item.crop_type,
              created_at: item.created_at || new Date().toISOString(),
              source: 'imported'
            }
          };
          addFeature(feature);
        });
        alert(`${data.length} موقعیت با موفقیت وارد شد`);
      } catch (err) {
        alert('خطا در خواندن فایل');
      }
    };
    reader.readAsText(file);
  };

  return (
    <Card className="bg-slate-900/50 border-slate-800 backdrop-blur">
      <div className="p-4 border-b border-slate-800">
        <div className="flex items-center justify-between">
          <h3 className="font-semibold text-white flex items-center gap-2">
            <MapPin className="w-4 h-4 text-emerald-400" />
            ورود دستی مختصات
          </h3>
          <div className="flex gap-1">
            <Button size="sm" variant="outline" onClick={handleExport}>
              <Download className="w-3 h-3" />
            </Button>
            <label>
              <Button size="sm" variant="outline" asChild>
                <span>
                  <Upload className="w-3 h-3" />
                </span>
              </Button>
              <input type="file" accept=".json" onChange={handleImport} className="hidden" />
            </label>
          </div>
        </div>
      </div>
      
      <form onSubmit={handleSubmit} className="p-4 space-y-3">
        <div>
          <Label htmlFor="name" className="text-slate-300 text-xs">نام مزرعه/منطقه</Label>
          <Input
            id="name"
            value={formData.name}
            onChange={(e) => setFormData({...formData, name: e.target.value})}
            placeholder="مزرعه شماره 1"
            className="bg-slate-800 border-slate-700 text-white text-sm"
          />
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          <div>
            <Label htmlFor="lat" className="text-slate-300 text-xs">عرض جغرافیایی</Label>
            <Input
              id="lat"
              type="number"
              step="0.000001"
              value={formData.latitude}
              onChange={(e) => setFormData({...formData, latitude: e.target.value})}
              placeholder="35.6892"
              className="bg-slate-800 border-slate-700 text-white text-sm font-mono"
              required
            />
          </div>
          <div>
            <Label htmlFor="lng" className="text-slate-300 text-xs">طول جغرافیایی</Label>
            <Input
              id="lng"
              type="number"
              step="0.000001"
              value={formData.longitude}
              onChange={(e) => setFormData({...formData, longitude: e.target.value})}
              placeholder="51.3890"
              className="bg-slate-800 border-slate-700 text-white text-sm font-mono"
              required
            />
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-2">
          <div>
            <Label htmlFor="area" className="text-slate-300 text-xs">مساحت (هکتار)</Label>
            <Input
              id="area"
              type="number"
              step="0.01"
              value={formData.area}
              onChange={(e) => setFormData({...formData, area: e.target.value})}
              placeholder="5.5"
              className="bg-slate-800 border-slate-700 text-white text-sm"
            />
          </div>
          <div>
            <Label htmlFor="cropType" className="text-slate-300 text-xs">نوع محصول</Label>
            <Input
              id="cropType"
              value={formData.cropType}
              onChange={(e) => setFormData({...formData, cropType: e.target.value})}
              placeholder="گندم"
              className="bg-slate-800 border-slate-700 text-white text-sm"
            />
          </div>
        </div>
        
        <div>
          <Label htmlFor="notes" className="text-slate-300 text-xs">توضیحات</Label>
          <Input
            id="notes"
            value={formData.notes}
            onChange={(e) => setFormData({...formData, notes: e.target.value})}
            placeholder="یادداشت..."
            className="bg-slate-800 border-slate-700 text-white text-sm"
          />
        </div>
        
        <Button type="submit" className="w-full bg-emerald-600 hover:bg-emerald-700 gap-2">
          <Save className="w-4 h-4" />
          ثبت موقعیت روی نقشه
        </Button>
      </form>
      
      {/* Quick Stats */}
      <div className="px-4 pb-4">
        <div className="bg-slate-800/50 rounded-lg p-3">
          <div className="text-xs text-slate-400 mb-2">موقعیت‌های ثبت‌شده</div>
          <div className="space-y-1 max-h-32 overflow-y-auto">
            {drawnFeatures.length === 0 ? (
              <div className="text-xs text-slate-500 text-center py-2">هنوز موقعیتی ثبت نشده</div>
            ) : (
              drawnFeatures.map((f: any, idx: number) => (
                <div key={idx} className="flex items-center justify-between text-xs p-2 bg-slate-900/50 rounded">
                  <span className="text-white truncate">{f.properties?.name || `موقعیت ${idx + 1}`}</span>
                  <Badge variant="secondary" className="text-xs">
                    {f.properties?.area_hectares ? `${f.properties.area_hectares.toFixed(1)} هکتار` : 'نقطه‌ای'}
                  </Badge>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </Card>
  );
}
