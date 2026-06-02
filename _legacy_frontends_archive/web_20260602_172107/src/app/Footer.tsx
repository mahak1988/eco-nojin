import Link from 'next/link';
import Logo from './Logo';
import { getDictionary, type Locale } from '@/lib/i18n';

export default function Footer({ locale }: { locale: Locale }) {
  const dict = getDictionary(locale);
  const isPersian = locale === 'fa';

  return (
    <footer className="bg-gray-900 dark:bg-black text-white mt-16">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <Logo locale={locale} size="md" />
            <p className="text-gray-400 text-sm mt-4">
              {dict?.common?.tagline || (isPersian ? 'پلتفرم علمی کربن' : 'Scientific Carbon Platform')}
            </p>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Platform</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href={`/${locale}/calculate`} className="hover:text-green-500 transition">{dict?.common?.calculator || 'Calculator'}</Link></li>
              <li><Link href={`/${locale}/dashboard`} className="hover:text-green-500 transition">{dict?.common?.dashboard || 'Dashboard'}</Link></li>
              <li><Link href={`/${locale}/map`} className="hover:text-green-500 transition">{dict?.common?.map || 'Map'}</Link></li>
              <li><Link href={`/${locale}/shop`} className="hover:text-green-500 transition">{dict?.common?.shop || 'Shop'}</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Resources</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href={`/${locale}/library`} className="hover:text-green-500 transition">{dict?.common?.library || 'Library'}</Link></li>
              <li><Link href={`/${locale}/about`} className="hover:text-green-500 transition">{dict?.common?.about || 'About'}</Link></li>
              <li><Link href={`/${locale}/contact`} className="hover:text-green-500 transition">{dict?.common?.contact || 'Contact'}</Link></li>
            </ul>
          </div>

          <div>
            <h3 className="font-semibold mb-4">Legal</h3>
            <ul className="space-y-2 text-sm text-gray-400">
              <li><Link href={`/${locale}/privacy`} className="hover:text-green-500 transition">{dict?.common?.privacy || 'Privacy'}</Link></li>
              <li><Link href={`/${locale}/terms`} className="hover:text-green-500 transition">{dict?.common?.terms || 'Terms'}</Link></li>
              <li><Link href={`/${locale}/policy`} className="hover:text-green-500 transition">{dict?.common?.policy || 'Policy'}</Link></li>
            </ul>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-sm text-gray-400">
          © {new Date().getFullYear()} Econojin. All rights reserved.
        </div>
      </div>
    </footer>
  );
}
