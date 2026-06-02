'use client';

import { useParams } from 'next/navigation';
import Link from 'next/link';
import { ArrowLeft, Loader2 } from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function Page() {
  const params = useParams();
  const locale = (params?.locale as Locale) || 'fa';
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);
  
  const moduleNames: Record<string, {fa: string, en: string}> = {
    'hydrology': { fa: 'هیدرولوژی', en: 'Hydrology' },
    'soil-water': { fa: 'آب در خاک', en: 'Soil Water' },
    'crop': { fa: 'رشد محصول', en: 'Crop Growth' },
    'carbon': { fa: 'کربن خاک', en: 'Soil Carbon' },
    'erosion': { fa: 'فرسایش', en: 'Erosion' },
    'halls': { fa: 'تالارها', en: 'Halls' },
    'advisors': { fa: 'مشاوران', en: 'Advisors' },
    'webinars': { fa: 'وبینارها', en: 'Webinars' },
    'wallet': { fa: 'کیف پول', en: 'Wallet' },
  };
  
  const moduleName = moduleNames['carbon'] || { fa: 'در حال توسعه', en: 'Under Development' };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white pt-24">
      <div className="max-w-4xl mx-auto px-4 py-12 text-center">
        <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-green-400 to-emerald-600 mb-6">
          <Loader2 className="w-10 h-10 text-white animate-spin" />
        </div>
        
        <h1 className="text-4xl font-bold mb-4">{moduleName[isRTL ? 'fa' : 'en']}</h1>
        <p className="text-lg text-gray-600 mb-8">
          {isRTL ? 'این ماژول در حال توسعه است.' : 'This module is under development.'}
        </p>
        
        <Link href={`/${locale}`} className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 text-white rounded-xl">
          <ArrowLeft className="w-4 h-4" />
          {isRTL ? 'بازگشت به خانه' : 'Back to Home'}
        </Link>
      </div>
    </div>
  );
}
