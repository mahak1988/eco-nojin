"use client";

import Link from 'next/link';
import BackButton from '@/components/BackButton';

const models = [
    { name: 'SWAT', fullName: 'Soil & Water Assessment Tool', org: 'USDA', year: 1998, icon: '💧', href: '/simulation/swat', description: 'مدل‌سازی حوضه آبریز و کیفیت آب' },
    { name: 'HEC-HMS', fullName: 'Hydrologic Modeling System', org: 'USACE', year: 2000, icon: '🌊', href: '/simulation/hechms', description: 'شبیه‌سازی هیدرولوژی و سیلاب' },
    { name: 'HBV', fullName: 'Hydrologiska Byråns Vattenbalansavdelning', org: 'SMHI', year: 1972, icon: '❄️', href: '/simulation/hbv', description: 'مدل هیدرولوژی مناطق سردسیر' },
    { name: 'MIKE SHE', fullName: 'Integrated Hydrological Modeling', org: 'DHI', year: 1990, icon: '🌊', href: '/simulation/mike-she', description: 'مدل‌سازی یکپارچه هیدرولوژی' },
    { name: 'VIC', fullName: 'Variable Infiltration Capacity', org: 'UW', year: 1994, icon: '🌍', href: '/simulation/vic', description: 'مدل هیدرولوژی مقیاس بزرگ' },
    { name: 'TOPMODEL', fullName: 'Topography-based Model', org: 'Lancaster', year: 1979, icon: '⛰️', href: '/simulation/topmodel', description: 'مدل مبتنی بر توپوگرافی' },
    { name: 'Sacramento', fullName: 'Sacramento Soil Moisture Accounting', org: 'NWS', year: 1973, icon: '🏛️', href: '/simulation/sacramento', description: 'مدل حسابداری رطوبت خاک' },
    { name: 'HSPF', fullName: 'Hydrological Simulation Program', org: 'EPA', year: 1981, icon: '🧪', href: '/simulation/hspf', description: 'شبیه‌سازی هیدرولوژی و کیفیت آب' },
    { name: 'MODFLOW', fullName: 'Modular 3D Groundwater Flow', org: 'USGS', year: 1984, icon: '💧', href: '/simulation/modflow', description: 'مدل جریان آب زیرزمینی سه‌بعدی' },
    { name: 'WEAP', fullName: 'Water Evaluation And Planning', org: 'SEI', year: 2001, icon: '⚖️', href: '/simulation/weap', description: 'برنامه‌ریزی منابع آب' },
    { name: 'HEC-RAS', fullName: 'River Analysis System', org: 'USACE', year: 1995, icon: '🌊', href: '/simulation/hecras', description: 'تحلیل هیدرولیک رودخانه' },
    { name: 'QUAL2K', fullName: 'Water Quality Analysis', org: 'EPA', year: 2005, icon: '🧪', href: '/simulation/qual2k', description: 'تحلیل کیفیت آب رودخانه' },
    { name: 'WASP', fullName: 'Water Quality Analysis Simulation', org: 'EPA', year: 1983, icon: '🧪', href: '/simulation/wasp', description: 'شبیه‌سازی کیفیت آب پیشرفته' }
];

export default function CategoryPage() {
  return (
    <>
      <main className="min-h-screen bg-gradient-to-br from-gray-950 via-gray-900 to-black pt-20">
        <div className="container mx-auto px-4 py-8">
          <div className="mb-8">
            <BackButton fallbackHref="/models" label="بازگشت به مدل‌ها" />
            <h1 className="text-4xl font-black text-white mb-2 mt-2">💧 مدل‌های هیدرولوژی</h1>
            <p className="text-gray-400">۱۳ مدل علمی برای شبیه‌سازی جریان آب و حوضه آبریز</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {models.map((model, i) => (
              <Link key={i} href={model.href} className="group">
                <div className="glass rounded-2xl p-6 border border-blue-500/20 hover:border-blue-500/40 transition-all h-full">
                  <div className="flex items-start justify-between mb-4">
                    <div className="text-5xl group-hover:scale-110 transition-transform">{model.icon}</div>
                    <span className="px-3 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs">{model.year}</span>
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
