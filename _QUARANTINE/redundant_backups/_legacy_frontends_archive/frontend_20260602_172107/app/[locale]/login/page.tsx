'use client';
import React from 'react';

import { useParams } from 'next/navigation';
import { LogIn } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function Page() {
  const params = useParams();
  const locale = (params.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa' || locale === 'ar' || locale === 'ur';

  // Safe i18n access with fallback
  const title = dict?.auth?.title || (isPersian ? 'ورود' : 'Login');
  const subtitle = dict?.auth?.subtitle || (isPersian ? 'این صفحه در حال توسعه است' : 'This page is under development');

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-white dark:from-gray-900 dark:to-gray-800 pt-24">
      <div className="max-w-5xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <LogIn className="w-16 h-16 text-green-600 mx-auto mb-4" />
          <h1 className="text-4xl font-bold mb-4">{title}</h1>
          <p className="text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">{subtitle}</p>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 shadow-lg">
          <div className="prose dark:prose-invert max-w-none">
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
              {isPersian
                ? 'اکونوژین یک پلتفرم علمی برای محاسبه و تأیید تأثیرات زیست‌محیطی است. ما از مدل‌های علمی RothC، AquaCrop و تصاویر ماهواره‌ای Sentinel-2 استفاده می‌کنیم.'
                : 'Econojin is a scientific platform for calculating and verifying environmental impacts. We use RothC, AquaCrop scientific models and Sentinel-2 satellite imagery.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
