import type { Metadata } from 'next';
import { AnalysisDashboard } from '@/components/analysis';

export const metadata: Metadata = {
  title: 'داشبورد تحلیل کشاورزی | Econojin',
  description: 'پلتفرم پیشرفته تصمیم‌یار کشاورزی و پایش محیط‌زیست',
};

export default function AnalysisPage() {
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
            <div className="hidden md:flex items-center gap-2 text-xs text-slate-400">
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
              سیستم آنلاین
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <AnalysisDashboard />
      </main>

      {/* Footer */}
      <footer className="mt-12 py-6 border-t border-slate-700/50 text-center text-sm text-slate-500">
        <div className="container mx-auto px-4">
          <p>🌾 Econojin © {new Date().getFullYear()} | HydroMa NojiN . NarvaN Agro-Industrial Company</p>
        </div>
      </footer>
    </div>
  );
}