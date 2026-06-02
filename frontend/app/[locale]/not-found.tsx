'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { type Locale } from '@/lib/i18n';

export default function NotFound() {
  const params = useParams();
  const locale = (params.locale as Locale) || 'fa';

  return (
    <div className="min-h-[60vh] flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300 dark:text-gray-700 mb-4">404</h1>
        <p className="text-xl text-gray-600 dark:text-gray-400 mb-6">Page not found</p>
        <Link href={`/${locale}`} className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition">
          Go Home
        </Link>
      </div>
    </div>
  );
}
