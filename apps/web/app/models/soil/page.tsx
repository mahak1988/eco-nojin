"use client";

import Link from 'next/link';
import BackButton from '@/components/BackButton';

const models = [
    { name: 'RUSLE2', fullName: 'Revised Universal Soil Loss Equation', org: 'USDA-ARS', year: 1997, icon: '🏔️', href: '/simulation/rusle2', description: 'پیش‌بینی فرسایش خاک بلندمدت' },
    { name: 'WEPP', fullName: 'Water Erosion Prediction Project', org: 'USDA-ARS', year: 1995, icon: '🌊', href: '/simulation/wepp', description: 'پیش‌بینی فرسایش آب روزانه' },
    { name: 'HYDRUS', fullName: 'Soil Water Movement Model', org: 'US Salinity Lab', year: 1990, icon: '💧', href: '/simulation/hydrus', description: 'حرکت آب و املاح در خاک' }
];

export default function CategoryPage() {
  return (
    <>
      <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black pt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <BackButton fallbackHref="/models" label="بازگشت به مدل‌ها" />
            <h1 className="text-4xl font-black text-white mb-2 mt-2">🏔️ مدل‌های خاک</h1>
            <p className="text-gray-400">۳ مدل علمی برای شبیه‌سازی فرسایش خاک و حرکت آب</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {models.map((model, i) => (
              <Link key={i} href={model.href} className="group">
                <div className="glass rounded-2xl p-6 border border-amber-500/20 hover:border-amber-500/40 transition-all h-full">
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-5xl group-hover:scale-110 transition-transform">{model.icon}</div>
                    <span className="px-3 py-1 bg-amber-500/20 text-amber-400 rounded-full text-xs">{model.year}</span>
                  </div>
                  <h3 className="text-xl font-bold text-white mb-1">{model.name}</h3>
                  <p className="text-xs text-gray-500 mb-2">{model.fullName}</p>
                  <p className="text-sm text-gray-300 mb-3">{model.description}</p>
                  <div className="text-xs text-gray-400 mb-3">🏛️ {model.org}</div>
                  <div className="flex items-center gap-2 text-sm text-emerald-400 group-hover:gap-3 transition-all">
                    <span>اجرای شبیه‌سازی</span>
                    <span>→</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </main>
    </>
  );
}
