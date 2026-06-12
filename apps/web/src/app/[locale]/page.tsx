import type { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: 'Econojin - پلتفرم تصمیم‌یار کشاورزی',
  description: 'پلتفرم پیشرفته تصمیم‌یار کشاورزی و پایش محیط‌زیست',
};

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900">
      {/* Header */}
      <header className="border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold bg-gradient-to-l from-sky-400 to-emerald-400 bg-clip-text text-transparent flex items-center gap-2">
                <span>🛰️</span> Econojin Advanced
              </h1>
              <p className="text-sm text-slate-400 mt-1">
                پلتفرم پیشرفته تصمیم‌یار کشاورزی و پایش محیط‌زیست
              </p>
            </div>
            <nav className="hidden md:flex items-center gap-6">
              <Link href="/fa/analysis" className="text-slate-300 hover:text-sky-400 transition-colors">
                داشبورد تحلیل
              </Link>
              <Link href="/fa/about" className="text-slate-300 hover:text-sky-400 transition-colors">
                درباره ما
              </Link>
              <Link href="/fa/contact" className="text-slate-300 hover:text-sky-400 transition-colors">
                تماس
              </Link>
            </nav>
            <div className="hidden md:flex items-center gap-2 text-xs text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              سیستم آنلاین
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="text-center max-w-4xl mx-auto">
          <h2 className="text-5xl font-bold text-white mb-6 leading-tight">
            تصمیم‌یار هوشمند برای{' '}
            <span className="bg-gradient-to-l from-sky-400 to-emerald-400 bg-clip-text text-transparent">
              کشاورزی پایدار
            </span>
          </h2>
          <p className="text-xl text-slate-300 mb-8 leading-relaxed">
            با استفاده از هوش مصنوعی و تحلیل داده‌های ماهواره‌ای، بهترین تصمیمات را برای مزارع خود بگیرید
          </p>
          
          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Link 
              href="/fa/analysis"
              className="px-8 py-4 bg-gradient-to-l from-sky-600 to-sky-500 hover:from-sky-500 hover:to-sky-400 text-white font-bold rounded-xl shadow-lg hover:shadow-sky-500/30 transition-all transform hover:scale-105"
            >
              🚀 شروع تحلیل
            </Link>
            <Link 
              href="/fa/about"
              className="px-8 py-4 bg-slate-700/50 hover:bg-slate-700 text-white font-bold rounded-xl border border-slate-600 transition-all"
            >
              📖 بیشتر بدانید
            </Link>
          </div>

          {/* Features Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-16">
            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700 shadow-xl">
              <div className="w-12 h-12 rounded-lg bg-sky-500/20 flex items-center justify-center mb-4 mx-auto">
                <span className="text-2xl">📊</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">تحلیل NDVI</h3>
              <p className="text-slate-400 text-sm">
                پایش سلامت vegetation با شاخص‌های پیشرفته ماهواره‌ای
              </p>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700 shadow-xl">
              <div className="w-12 h-12 rounded-lg bg-emerald-500/20 flex items-center justify-center mb-4 mx-auto">
                <span className="text-2xl">💰</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">تحلیل اقتصادی</h3>
              <p className="text-slate-400 text-sm">
                محاسبه سود و هزینه‌های کشاورزی با دقت بالا
              </p>
            </div>

            <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl p-6 border border-slate-700 shadow-xl">
              <div className="w-12 h-12 rounded-lg bg-amber-500/20 flex items-center justify-center mb-4 mx-auto">
                <span className="text-2xl">🗺️</span>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">نقشه تعاملی</h3>
              <p className="text-slate-400 text-sm">
                مشاهده مناطق تحلیل‌شده روی نقشه با جزئیات کامل
              </p>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 py-8 border-t border-slate-700/50 bg-slate-900/30">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
            <div>
              <h4 className="text-white font-bold mb-3 flex items-center gap-2">
                <span>🛰️</span> Econojin
              </h4>
              <p className="text-slate-400 text-sm">
                پلتفرم پیشرفته تصمیم‌یار کشاورزی و پایش محیط‌زیست
              </p>
            </div>
            <div>
              <h4 className="text-white font-bold mb-3">دسترسی سریع</h4>
              <ul className="space-y-2 text-sm">
                <li>
                  <Link href="/fa/analysis" className="text-slate-400 hover:text-sky-400 transition-colors">
                    داشبورد تحلیل
                  </Link>
                </li>
                <li>
                  <Link href="/fa/about" className="text-slate-400 hover:text-sky-400 transition-colors">
                    درباره ما
                  </Link>
                </li>
                <li>
                  <Link href="/fa/contact" className="text-slate-400 hover:text-sky-400 transition-colors">
                    تماس با ما
                  </Link>
                </li>
              </ul>
            </div>
            <div>
              <h4 className="text-white font-bold mb-3">تماس</h4>
              <ul className="space-y-2 text-sm text-slate-400">
                <li>📧 info@econojin.com</li>
                <li>📞 021-12345678</li>
                <li>📍 تهران، ایران</li>
              </ul>
            </div>
          </div>
          <div className="pt-6 border-t border-slate-700/50 text-center text-sm text-slate-500">
            <p>🌾 Econojin © {new Date().getFullYear()} | HydroMa NojiN . NarvaN Agro-Industrial Company</p>
          </div>
        </div>
      </footer>
    </div>
  );
}