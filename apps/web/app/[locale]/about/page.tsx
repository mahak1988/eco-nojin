'use client';
import React from 'react';

import { useParams } from 'next/navigation';
import { Leaf, Target, Eye, Users, Heart, Award, Sparkles, Globe, Shield, Zap, TrendingUp, TreePine } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function AboutPage() {
  const params = useParams();
  const locale = (params.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa' || locale === 'ar' || locale === 'ur';

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 pt-20">
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <Leaf className="w-20 h-20 text-green-600 mx-auto mb-6" />
          <h1 className="text-5xl font-bold mb-6 bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
            {dict?.pages?.about?.title || (isPersian ? 'درباره اکونوژین' : 'About Econojin')}
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            {isPersian ? 'ما به قدرت علم و فناوری برای مبارزه با تغییرات اقلیمی باور داریم' : 'We believe in science and technology to fight climate change'}
          </p>
        </div>
      </section>

      <section className="py-12 px-4 bg-white dark:bg-gray-800">
        <div className="max-w-6xl mx-auto grid grid-cols-2 md:grid-cols-4 gap-6">
          {[
            { icon: TreePine, value: '1M+', label: isPersian ? 'درخت' : 'Trees' },
            { icon: Globe, value: '20', label: isPersian ? 'زبان' : 'Languages' },
            { icon: Users, value: '50K+', label: isPersian ? 'کاربر' : 'Users' },
            { icon: TrendingUp, value: '203t', label: 'CO₂' },
          ].map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div key={i} className="text-center p-6 bg-gray-50 dark:bg-gray-900 rounded-2xl">
                <Icon className="w-10 h-10 mx-auto mb-3 text-green-500" />
                <div className="text-3xl font-bold">{stat.value}</div>
                <div className="text-sm text-gray-600 dark:text-gray-400">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto grid md:grid-cols-2 gap-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
            <Target className="w-14 h-14 text-green-600 mb-6" />
            <h2 className="text-3xl font-bold mb-4">{dict?.pages?.about?.mission || (isPersian ? 'ماموریت ما' : 'Our Mission')}</h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              {isPersian ? 'تبدیل فعالیت‌های اکولوژیکی به دارایی‌های دیجیتال با RothC، AquaCrop و Sentinel-2' : 'Transform ecological activities into digital assets with RothC, AquaCrop & Sentinel-2'}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
            <Eye className="w-14 h-14 text-blue-600 mb-6" />
            <h2 className="text-3xl font-bold mb-4">{dict?.pages?.about?.vision || (isPersian ? 'چشم‌انداز' : 'Our Vision')}</h2>
            <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
              {isPersian ? 'ایجاد اکوسیستم جهانی برای تبدیل تأثیر مثبت به ارزش اقتصادی' : 'Global ecosystem for turning positive impact into economic value'}
            </p>
          </div>
        </div>
      </section>

      <section className="py-16 px-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl font-bold mb-12 text-center">{isPersian ? 'ارزش‌های ما' : 'Our Values'}</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Heart, title: isPersian ? 'پایداری' : 'Sustainability' },
              { icon: Award, title: isPersian ? 'شفافیت' : 'Transparency' },
              { icon: Users, title: isPersian ? 'همکاری' : 'Collaboration' },
            ].map((v, i) => {
              const Icon = v.icon;
              return (
                <div key={i} className="text-center p-6 bg-white/10 backdrop-blur rounded-2xl">
                  <Icon className="w-14 h-14 mx-auto mb-4" />
                  <h3 className="text-2xl font-bold">{v.title}</h3>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-xl">
          <Sparkles className="w-8 h-8 text-yellow-500 mb-6" />
          <h2 className="text-3xl font-bold mb-6">{dict?.pages?.about?.story || (isPersian ? 'داستان ما' : 'Our Story')}</h2>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
            {isPersian ? 'اکونوژین در ۲۰۲۴ برای ایجاد پلی میان علم و بلاکچین تأسیس شد.' : 'Econojin was founded in 2024 to bridge science and blockchain.'}
          </p>
          <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
            {isPersian ? 'با Sentinel-2 از ESA، فعالیت‌ها را از فضا تأیید می‌کنیم.' : 'With Sentinel-2 from ESA, we verify activities from space.'}
          </p>
        </div>
      </section>
    </div>
  );
}
