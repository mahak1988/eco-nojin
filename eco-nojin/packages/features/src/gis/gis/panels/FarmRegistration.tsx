"use client";

import { useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { X, Save, MapPin } from 'lucide-react';
import { useGisStore } from '@/store/gis/useGisStore';

interface FarmRegistrationProps {
  onClose: () => void;
}

export function FarmRegistration({ onClose }: FarmRegistrationProps) {
  const { drawnFeatures, addFeature } = useGisStore();
  const [farmName, setFarmName] = useState('');
  const [cropType, setCropType] = useState('');
  const [area, setArea] = useState('0');

  const lastFeature = drawnFeatures[drawnFeatures.length - 1];

  const handleSave = () => {
    if (lastFeature) {
      // Update last feature with farm details
      const updatedFeature = {
        ...lastFeature,
        properties: {
          ...lastFeature.properties,
          name: farmName,
          crop_type: cropType
        }
      };
      
      // Remove last and add updated
      // Note: In real implementation, you'd update the store properly
      console.log('Saving farm:', updatedFeature);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-[2000] flex items-center justify-center">
      <Card className="bg-slate-900 border-slate-800 w-full max-w-md mx-4">
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-bold text-white flex items-center gap-2">
              <MapPin className="w-5 h-5 text-emerald-400" />
              ثبت مزرعه جدید
            </h2>
            <Button size="icon" variant="ghost" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="farmName" className="text-slate-300">نام مزرعه</Label>
              <Input
                id="farmName"
                value={farmName}
                onChange={(e) => setFarmName(e.target.value)}
                placeholder="مزرعه شماره 1"
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            
            <div>
              <Label htmlFor="cropType" className="text-slate-300">نوع محصول</Label>
              <Input
                id="cropType"
                value={cropType}
                onChange={(e) => setCropType(e.target.value)}
                placeholder="گندم، جو، ذرت..."
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            
            {lastFeature && (
              <div className="bg-slate-800/50 rounded-lg p-3">
                <div className="text-sm text-slate-400 mb-2">اطلاعات مکانی</div>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <span className="text-slate-400">مساحت:</span>
                    <span className="text-white font-medium">
                      {lastFeature.properties?.area_hectares?.toFixed(2) || 0} هکتار
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">محیط:</span>
                    <span className="text-white font-medium">
                      {lastFeature.properties?.perimeter?.toFixed(0) || 0} متر
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">مختصات مرکز:</span>
                    <span className="text-white font-mono text-xs">
                      {lastFeature.properties?.center?.[0]?.toFixed(4) || 0}, 
                      {lastFeature.properties?.center?.[1]?.toFixed(4) || 0}
                    </span>
                  </div>
                </div>
              </div>
            )}
            
            <div className="flex gap-2">
              <Button 
                variant="outline" 
                className="flex-1"
                onClick={onClose}
              >
                انصراف
              </Button>
              <Button 
                className="flex-1 bg-emerald-600 hover:bg-emerald-700"
                onClick={handleSave}
              >
                <Save className="w-4 h-4 mr-2" />
                ذخیره مزرعه
              </Button>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
}
