"use client";

import { Badge } from '@/components/ui/badge';
import { Search } from 'lucide-react';

import { useState } from 'react';
import { useTranslation } from '@/hooks/useTranslation';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useSentinelImages, useSpectralIndex } from '@/hooks/satellite/useSatellite';
import { 
  Satellite, Map, Calendar, Cloud, TrendingUp, 
  Leaf, BarChart3, Image as ImageIcon
} from 'lucide-react';

export default function SentinelPage() {
  const { t } = useTranslation();
  const [startDate, setStartDate] = useState('2024-01-01');
  const [endDate, setEndDate] = useState('2024-12-31');
  const [cloudCover, setCloudCover] = useState(20);
  
  const bbox: [number, number, number, number] = [51.2, 35.6, 51.5, 35.8];
  
  const { data: images, isLoading } = useSentinelImages(bbox, startDate, endDate, cloudCover);
  const { data: ndvi } = useSpectralIndex(35.6892, 51.3890, 'NDVI');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pt-20">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-white mb-2">{t('sentinel.title')}</h1>
          <p className="text-slate-400">{t('sentinel.subtitle')}</p>
        </div>

        {/* Search Filters */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <Search className="w-5 h-5 text-emerald-400" />
            فیلترهای جستجو
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="text-sm text-slate-400 mb-1 block">{t('sentinel.start_date')}</label>
              <Input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 mb-1 block">{t('sentinel.end_date')}</label>
              <Input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            <div>
              <label className="text-sm text-slate-400 mb-1 block">{t('sentinel.cloud_cover_max')}</label>
              <Input
                type="number"
                min="0"
                max="100"
                value={cloudCover}
                onChange={(e) => setCloudCover(parseInt(e.target.value))}
                className="bg-slate-800 border-slate-700 text-white"
              />
            </div>
            <div className="flex items-end">
              <Button className="w-full bg-emerald-600 hover:bg-emerald-700">
                <Search className="w-4 h-4 ml-2" />
                جستجو
              </Button>
            </div>
          </div>
        </Card>

        {/* NDVI Analysis */}
        {ndvi && (
          <Card className="bg-gradient-to-br from-green-900/30 to-green-800/10 border-green-800 p-6 mb-6">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Leaf className="w-5 h-5 text-green-400" />
              شاخص NDVI
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">مقدار</div>
                <div className="text-4xl font-bold text-green-400">{ndvi.value?.toFixed(3)}</div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">{t('iot.status')}</div>
                <div className="text-2xl font-bold text-white">{ndvi.status}</div>
              </div>
              <div className="bg-slate-900/50 rounded-lg p-4">
                <div className="text-sm text-slate-400 mb-1">توضیحات</div>
                <div className="text-sm text-white">{ndvi.description}</div>
              </div>
            </div>
          </Card>
        )}

        {/* Satellite Images */}
        <Card className="bg-slate-900/50 border-slate-800 p-6 mb-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <ImageIcon className="w-5 h-5 text-blue-400" />
            تصاویر Sentinel-2
          </h3>
          
          {isLoading ? (
            <div className="text-center py-8 text-slate-400">{t('common.loading')}</div>
          ) : images && images.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {images.map((img: any, idx: number) => (
                <div key={idx} className="bg-slate-800/50 rounded-lg p-4 hover:bg-slate-800 transition-colors cursor-pointer">
                  <div className="aspect-video bg-slate-900 rounded mb-3 flex items-center justify-center">
                    <Satellite className="w-12 h-12 text-slate-600" />
                  </div>
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-white">
                        {img.date?.slice(0, 10)}
                      </span>
                      <Badge className={img.cloud_cover < 10 ? 'bg-green-600' : 'bg-yellow-600'}>
                        <Cloud className="w-3 h-3 ml-1" />
                        {img.cloud_cover?.toFixed(1)}%
                      </Badge>
                    </div>
                    <div className="text-xs text-slate-400">
                      رزولوشن: 10m | باند: RGB
                    </div>
                    <Button size="sm" variant="outline" className="w-full">
                      مشاهده تصویر
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-slate-400">
              <Satellite className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>تصویری یافت نشد</p>
              <p className="text-sm mt-2">فیلترها را تغییر دهید</p>
            </div>
          )}
        </Card>

        {/* Spectral Indices */}
        <Card className="bg-slate-900/50 border-slate-800 p-6">
          <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
            <BarChart3 className="w-5 h-5 text-purple-400" />
            شاخص‌های طیفی
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { name: 'NDVI', desc: 'پوشش گیاهی', color: 'text-green-400' },
              { name: 'EVI', desc: 'شاخص بهبودیافته', color: 'text-emerald-400' },
              { name: 'NDWI', desc: 'رطوبت', color: 'text-blue-400' },
              { name: 'SAVI', desc: 'تنظیم‌شده خاک', color: 'text-teal-400' },
            ].map((index, idx) => (
              <div key={idx} className="bg-slate-800/50 rounded-lg p-4">
                <div className={`text-lg font-bold ${index.color} mb-1`}>{index.name}</div>
                <div className="text-sm text-slate-400">{index.desc}</div>
                <Button size="sm" variant="outline" className="w-full mt-3">
                  محاسبه
                </Button>
              </div>
            ))}
          </div>
        </Card>

        {/* Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">Sentinel-2</h4>
            <p className="text-sm text-slate-400">رزولوشن ۱۰ متر، تکرار ۵ روزه</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">۱۳ باند طیفی</h4>
            <p className="text-sm text-slate-400">از مرئی تا مادون قرمز حرارتی</p>
          </Card>
          <Card className="bg-slate-900/50 border-slate-800 p-4">
            <h4 className="font-bold text-white mb-2">رایگان</h4>
            <p className="text-sm text-slate-400">داده‌های Copernicus ESA</p>
          </Card>
        </div>
      </div>
    </div>
  );
}
