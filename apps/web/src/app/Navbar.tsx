'use client';

import { useState } from 'react';
import { useParams, usePathname, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  Menu, X, Leaf, Droplets, FlaskConical, Sprout, 
  BarChart3, BookOpen, MessageSquare, Users, Bot, 
  Video, Wallet, Settings, User, LogOut, ChevronDown,
  Mountain, CloudRain, Wind, Sun, TreePine, Zap
} from 'lucide-react';
import { getDictionary, type Locale } from '@/lib/i18n';
import { useAuth } from './providers/AuthProvider';

const ECONOJIN_MODULES = [
  { id: 'dashboard', name: { fa: 'داشبورد', en: 'Dashboard' }, path: '/dashboard', icon: BarChart3, color: 'green' },
  { id: 'hydrology', name: { fa: 'هیدرولوژی', en: 'Hydrology' }, path: '/hydrology', icon: Droplets, color: 'blue' },
  { id: 'soil-water', name: { fa: 'آب در خاک', en: 'Soil Water' }, path: '/soil-water', icon: CloudRain, color: 'cyan' },
  { id: 'crop', name: { fa: 'رشد محصول', en: 'Crop Growth' }, path: '/crop', icon: Sprout, color: 'emerald' },
  { id: 'carbon', name: { fa: 'کربن خاک', en: 'Soil Carbon' }, path: '/carbon', icon: Leaf, color: 'lime' },
  { id: 'erosion', name: { fa: 'فرسایش', en: 'Erosion' }, path: '/erosion', icon: Mountain, color: 'orange' },
  { id: 'library', name: { fa: 'کتابخانه', en: 'Library' }, path: '/library', icon: BookOpen, color: 'purple' },
];

const USER_MODULES = [
  { id: 'halls', name: { fa: 'تالارها', en: 'Halls' }, path: '/halls', icon: MessageSquare },
  { id: 'advisors', name: { fa: 'مشاوران', en: 'Advisors' }, path: '/advisors', icon: Bot },
  { id: 'webinars', name: { fa: 'وبینارها', en: 'Webinars' }, path: '/webinars', icon: Video },
  { id: 'wallet', name: { fa: 'کیف پول', en: 'Wallet' }, path: '/wallet', icon: Wallet },
];

export default function Navbar({ locale }: { locale: Locale }) {
  const [isOpen, setIsOpen] = useState(false);
  const [showModules, setShowModules] = useState(false);
  const [showUserMenu, setShowUserMenu] = useState(false);
  
  const pathname = usePathname();
  const router = useRouter();
  const dict = getDictionary(locale);
  const isRTL = ['fa', 'ar', 'ur'].includes(locale);
  const { user, logout } = useAuth();

  const isActive = (path: string) => pathname?.startsWith(path);

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 dark:bg-gray-900/90 backdrop-blur-md border-b border-gray-200 dark:border-gray-800">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          
          {/* Logo */}
          <Link href={`/${locale}`} className="flex items-center gap-2">
            <Leaf className="w-8 h-8 text-green-600" />
            <span className="text-xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              Econojin
            </span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center gap-1">
            <div className="relative">
              <button
                onClick={() => setShowModules(!showModules)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                  isActive('/dashboard') || isActive('/hydrology') || isActive('/crop')
                    ? 'bg-green-100 text-green-700'
                    : 'hover:bg-gray-100'
                }`}
              >
                <FlaskConical className="w-4 h-4" />
                <span className="text-sm font-medium">{dict?.common?.modules || 'ماژول‌ها'}</span>
                <ChevronDown className={`w-4 h-4 transition ${showModules ? 'rotate-180' : ''}`} />
              </button>
              
              {showModules && (
                <div className="absolute right-0 top-full mt-2 w-72 bg-white rounded-xl shadow-xl border overflow-hidden">
                  <div className="p-3 grid grid-cols-2 gap-2">
                    {ECONOJIN_MODULES.map((module) => {
                      const Icon = module.icon;
                      return (
                        <Link
                          key={module.id}
                          href={`/${locale}${module.path}`}
                          onClick={() => setShowModules(false)}
                          className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-50"
                        >
                          <div className={`w-10 h-10 rounded-lg bg-${module.color}-100 flex items-center justify-center`}>
                            <Icon className={`w-5 h-5 text-${module.color}-600`} />
                          </div>
                          <div className="text-right">
                            <div className="font-medium text-sm">{module.name[isRTL ? 'fa' : 'en']}</div>
                          </div>
                        </Link>
                      );
                    })}
                  </div>
                </div>
              )}
            </div>

            {USER_MODULES.map((module) => {
              const Icon = module.icon;
              return (
                <Link
                  key={module.id}
                  href={`/${locale}${module.path}`}
                  className={`flex items-center gap-2 px-4 py-2 rounded-lg transition ${
                    isActive(module.path) ? 'bg-green-100' : 'hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span className="text-sm font-medium">{module.name[isRTL ? 'fa' : 'en']}</span>
                </Link>
              );
            })}
          </div>

          {/* Right Side */}
          <div className="flex items-center gap-2">
            <select
              value={locale}
              onChange={(e) => router.push(`/${e.target.value}${pathname?.replace(`/${locale}`, '') || ''}`)}
              className="px-3 py-2 text-sm border rounded-lg bg-white"
            >
              <option value="fa">فارسی</option>
              <option value="en">English</option>
              <option value="ar">العربية</option>
            </select>

            {user ? (
              <button onClick={logout} className="px-4 py-2 text-sm font-medium text-red-600 hover:bg-red-50 rounded-lg">
                خروج
              </button>
            ) : (
              <div className="flex items-center gap-2">
                <Link href={`/${locale}/login`} className="px-4 py-2 text-sm hover:bg-gray-100 rounded-lg">ورود</Link>
                <Link href={`/${locale}/register`} className="px-4 py-2 text-sm bg-green-600 text-white rounded-lg">ثبت‌نام</Link>
              </div>
            )}

            <button onClick={() => setIsOpen(!isOpen)} className="md:hidden p-2">
              {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isOpen && (
          <div className="md:hidden py-4 border-t">
            <div className="space-y-2">
              {ECONOJIN_MODULES.map((module) => (
                <Link
                  key={module.id}
                  href={`/${locale}${module.path}`}
                  onClick={() => setIsOpen(false)}
                  className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100"
                >
                  <module.icon className="w-5 h-5" />
                  <span>{module.name[isRTL ? 'fa' : 'en']}</span>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </nav>
  );
}
