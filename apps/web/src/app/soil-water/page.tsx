"use client";

import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useSoilProperties } from '@/hooks/soil/useSoil';
import { 
  Mountain, Droplets, Leaf, MapPin, Search, 
  BarChart3, TestTube, TrendingUp
} from 'lucide-react';

export default function SoilWaterPage() {
  const { t } = useTranslation();
  const [lat, setLat] = useState(35.6892);
  const [lng, setLng] = useState(51.3890);
  
  const { data: soil, isLoading } = useSoilProperties(lat, lng);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">{t('soil_water.title')}</h1>
          <p className="text-slate-400">{t('soil_water.subtitle')}</p>
        </div>

        {/* Location Search */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <MapPin className="w-5 h-5 text-emerald-400" />
            موقعیت نمونه‌برداری
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
              <Button className="w-full bg-emerald-600 hover:bg-emerald-700">
                <Search className="w-4 h-4 ml-2" />
                تحلیل خاک
              </Button>
            </div>
          </div>
        </Card>

        {/* Soil Properties */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <TestTube className="w-5 h-5 text-orange-400" />
            خواص فیزیکی و شیمیایی خاک
          </h3>
          
          {isLoading ? (
            <div className="text-center py-8 text-slate-400">در حال تحلیل...</div>
          ) : soil && soil.properties ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {soil.properties.map((prop: any, idx: number) => (
                <div key={idx} className="bg-slate-800/50 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-white">{prop.name_fa}</span>
                    <span className="text-xs text-slate-400">{prop.depth}</span>
                  </div>
                  <div className="text-2xl font-bold text-white mb-1">
                    {prop.value?.toFixed(1) || 'N/A'}
                  </div>
                  <div className="text-xs text-slate-400">{prop.unit}</div>
                  {prop.uncertainty && (
                    <div className="text-xs text-slate-500 mt-1">
                      ±{prop.uncertainty.toFixed(1)}
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">داده‌ای در دسترس نیست</div>
          )}
        </Card>

        {/* Soil Classification */}
        {soil?.soil_class && (
          <Card className="bg-gradient-to-br from-emerald-900/30 to-emerald-800/10 border-emerald-800 p-6 mb-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Mountain className="w-5 h-5 text-emerald-400" />
              طبقه‌بندی خاک
            </h3>
            <div className="text-3xl font-bold text-emerald-400">{soil.soil_class}</div>
            <p className="text-sm text-slate-400 mt-2">بر اساس سیستم طبقه‌بندی FAO</p>
          </Card>
        )}

        {/* Water Management */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Droplets className="w-5 h-5 text-blue-400" />
            مدیریت آب خاک
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-2">ظرفیت نگهداری آب</div>
              <div className="text-3xl font-bold text-white">
                {soil?.water_holding_capacity?.toFixed(1) || 'N/A'} mm/m
              </div>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="text-sm text-slate-400 mb-2">نفوذپذیری</div>
              <div className="text-3xl font-bold text-white">
                {soil?.infiltration_rate?.toFixed(1) || 'N/A'} mm/h
              </div>
            </div>
          </div>
        </Card>

        {/* Recommendations */}
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-green-400" />
            توصیه‌های مدیریتی
          </h3>
          <div className="space-y-3">
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="font-medium text-white mb-1">آبیاری</div>
              <p className="text-sm text-slate-400">
                بر اساس بافت خاک، آبیاری قطره‌ای با فواصل ۲-۳ روزه توصیه می‌شود
              </p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="font-medium text-white mb-1">کوددهی</div>
              <p className="text-sm text-slate-400">
                افزودن مواد آلی برای بهبود ساختار خاک و افزایش ظرفیت نگهداری آب
              </p>
            </div>
            <div className="bg-slate-800/50 rounded-lg p-4">
              <div className="font-medium text-white mb-1">حفاظت خاک</div>
              <p className="text-sm text-slate-400">
                استفاده از پوشش گیاهی برای جلوگیری از فرسایش و حفظ رطوبت
              </p>
            </div>
          </div>
        </Card>

        {/* Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">{t('weather.data_source')}</h4>
            <p className="text-sm text-slate-400">SoilGrids v2.0 - رزولوشن ۲۵۰ متر</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">۱۴ خاصیت خاک</h4>
            <p className="text-sm text-slate-400">pH، کربن، نیتروژن، بافت و...</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">۶ عمق</h4>
            <p className="text-sm text-slate-400">از سطح تا ۲ متر عمق</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
