'use client';

import { useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import { 
  Calculator, Globe, Award, TreePine, ArrowRight, 
  Shield, Zap, Leaf, Satellite, Cpu, CheckCircle, 
  Star, TrendingUp, Users, Sparkles, BookOpen,
  MessageSquare, FlaskConical, Bot, Video, Wallet,
  Droplets, CloudRain, Sprout, Mountain, BarChart3
} from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

const SCIENTIFIC_MODULES = [
  { id: 'hydrology', icon: Droplets, title: { fa: 'هیدرولوژی', en: 'Hydrology' }, desc: { fa: 'شبیه‌سازی رواناب', en: 'Runoff simulation' }, href: '/hydrology', color: 'blue' },
  { id: 'soil-water', icon: CloudRain, title: { fa: 'آب در خاک', en: 'Soil Water' }, desc: { fa: 'مدل‌سازی رطوبت', en: 'Moisture modeling' }, href: '/soil-water', color: 'cyan' },
  { id: 'crop', icon: Sprout, title: { fa: 'رشد محصول', en: 'Crop Growth' }, desc: { fa: 'شبیه‌سازی عملکرد', en: 'Yield simulation' }, href: '/crop', color: 'emerald' },
  { id: 'carbon', icon: Leaf, title: { fa: 'کربن خاک', en: 'Soil Carbon' }, desc: { fa: 'ترسیب کربن', en: 'Carbon sequestration' }, href: '/carbon', color: 'lime' },
  { id: 'erosion', icon: Mountain, title: { fa: 'فرسایش', en: 'Erosion' }, desc: { fa: 'برآورد فرسایش', en: 'Erosion estimation' }, href: '/erosion', color: 'orange' },
  { id: 'dashboard', icon: BarChart3, title: { fa: 'داشبورد', en: 'Dashboard' }, desc: { fa: 'نظارت لحظه‌ای', en: 'Real-time monitoring' }, href: '/dashboard', color: 'purple' },
];

export default function HomePage() {
  const params = useParams();
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div className="min-h-screen bg-gradient-to-b from-green-50 via-white to-blue-50">
      
      {/* Hero */}
      <section className="pt-28 pb-16 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 bg-green-100 px-4 py-2 rounded-full mb-6">
            <Shield className="w-4 h-4" />
            <span className="text-sm">CVE-2025-66478 Patched • Next.js 15.0.5</span>
          </div>

          <h1 className="text-5xl md:text-7xl font-bold mb-6 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
            {dict?.common?.appName || (isRTL ? 'اکونوژین' : 'Econojin')}
          </h1>

          <p className="text-2xl text-gray-700 mb-4">
            {dict?.common?.tagline || (isRTL ? 'پلتفرم علمی کربن' : 'Scientific Carbon Platform')}
          </p>

          <div className="relative max-w-2xl mx-auto mb-8">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder={isRTL ? 'جستجو...' : 'Search...'}
              className="w-full px-6 py-4 text-lg rounded-xl border-2 focus:border-green-500 focus:outline-none bg-white"
            />
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href={`/${locale}/calculate`} className="inline-flex items-center gap-2 bg-gradient-to-r from-green-600 to-emerald-600 text-white px-8 py-4 rounded-xl font-semibold">
              <Calculator className="w-5 h-5" />
              {dict?.common?.calculator || (isRTL ? 'محاسبه' : 'Calculate')}
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link href={`/${locale}/dashboard`} className="inline-flex items-center gap-2 bg-white px-8 py-4 rounded-xl font-semibold border-2">
              {dict?.common?.dashboard || (isRTL ? 'داشبورد' : 'Dashboard')}
            </Link>
          </div>

          <div className="flex flex-wrap justify-center gap-4 mt-8 text-sm text-gray-500">
            <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> IPCC Compliant</div>
            <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Sentinel-2</div>
            <div className="flex items-center gap-2"><CheckCircle className="w-4 h-4 text-green-600" /> Polygon</div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-12 px-4 bg-white">
        <div className="max-w-7xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: TreePine, value: '1M+', label: isRTL ? 'درخت' : 'Trees' },
            { icon: Leaf, value: '203t', label: 'CO₂' },
            { icon: Award, value: '20K+', label: 'SEED' },
            { icon: Globe, value: '20', label: isRTL ? 'زبان' : 'Languages' },
          ].map((stat, i) => (
            <div key={i} className="text-center p-6 rounded-2xl bg-gray-50">
              <stat.icon className="w-10 h-10 mx-auto mb-3 text-green-500" />
              <div className="text-3xl font-bold">{stat.value}</div>
              <div className="text-sm text-gray-600">{stat.label}</div>
            </div>
          ))}
        </div>
      </section>

      {/* Modules */}
      <section className="py-16 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">{isRTL ? 'ماژول‌های علمی' : 'Scientific Modules'}</h2>
            <p className="text-gray-600">{isRTL ? 'همه متن‌باز و رایگان' : 'All open-source and free'}</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {SCIENTIFIC_MODULES.map((module, i) => {
              const Icon = module.icon;
              return (
                <Link key={module.id} href={`/${locale}${module.href}`} className="group bg-white rounded-2xl p-6 shadow hover:shadow-xl transition">
                  <div className={`w-14 h-14 rounded-xl bg-${module.color}-100 flex items-center justify-center mb-4`}>
                    <Icon className={`w-7 h-7 text-${module.color}-600`} />
                  </div>
                  <h3 className="text-xl font-bold mb-2">{module.title[isRTL ? 'fa' : 'en']}</h3>
                  <p className="text-gray-600 text-sm">{module.desc[isRTL ? 'fa' : 'en']}</p>
                </Link>
              );
            })}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="py-16 px-4 bg-gradient-to-r from-green-600 to-emerald-700 text-white">
        <div className="max-w-4xl mx-auto text-center">
          <Sparkles className="w-16 h-16 mx-auto mb-6" />
          <h2 className="text-4xl font-bold mb-4">{isRTL ? 'شروع کنید' : 'Get Started'}</h2>
          <Link href={`/${locale}/register`} className="inline-flex items-center gap-2 bg-white text-green-700 px-8 py-4 rounded-xl font-bold">
            {isRTL ? 'ثبت‌نام رایگان' : 'Sign Up Free'}
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  );
}
