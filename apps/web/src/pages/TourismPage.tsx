import { useMemo } from 'react';
import { Link } from 'react-router-dom';
import { Mountain, Building2, Waves, Trees, Compass, Palmtree, Tent, Landmark, Map, Heart, ArrowRight, Star } from 'lucide-react';

const TOURISM_SECTIONS = [
  { id: 'destinations', title: 'مقاصد گردشگری', desc: 'کشف زیبایی‌های طبیعی، تاریخی و فرهنگی ایران', icon: Compass, path: '/tourism/destinations', color: 'from-emerald-500 to-teal-600', bg: 'bg-emerald-50', count: '۲۵+', countLabel: 'مقصد' },
  { id: 'lodges', title: 'اقامتگاه‌های بوم‌گردی', desc: 'اقامت در دل طبیعت با حفظ محیط زیست', icon: Tent, path: '/tourism/eco-lodges', color: 'from-teal-500 to-cyan-600', bg: 'bg-teal-50', count: '۵۰+', countLabel: 'اقامتگاه' },
  { id: 'booking', title: 'رزرو تور', desc: 'برنامه‌ریزی سفر با راهنمایان محلی', icon: Map, path: '/tourism/booking', color: 'from-cyan-500 to-blue-600', bg: 'bg-cyan-50', count: '۱۵+', countLabel: 'تور فعال' },
  { id: 'gallery', title: 'گالری تصاویر', desc: 'تماشای زیبایی‌های ایران در قاب تصویر', icon: Heart, path: '/tourism/gallery', color: 'from-rose-500 to-pink-600', bg: 'bg-rose-50', count: '۲۰۰+', countLabel: 'تصویر' },
];

const HIGHLIGHTS = [
  { icon: Mountain, text: 'کوهستان و طبیعت‌گردی' },
  { icon: Waves, text: 'دریا و سواحل' },
  { icon: Trees, text: 'جنگل و منابع طبیعی' },
  { icon: Palmtree, text: 'کویر و نجوم' },
  { icon: Building2, text: 'بناهای تاریخی' },
  { icon: Landmark, text: 'میراث فرهنگی' },
];

export default function TourismPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-stone-50 to-emerald-50">
      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-emerald-800 via-teal-700 to-emerald-600 overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-20 left-10 w-72 h-72 bg-emerald-300 rounded-full blur-3xl" />
          <div className="absolute bottom-10 right-20 w-96 h-96 bg-teal-300 rounded-full blur-3xl" />
        </div>
        <div className="relative max-w-6xl mx-auto px-4 py-24 text-center">
          <h1 className="text-5xl md:text-7xl font-display font-bold text-white mb-6 animate-fade-in-down">
            اکوتوریسم ایران
          </h1>
          <p className="text-xl text-emerald-100 max-w-3xl mx-auto mb-8">
            سفر به قلب طبیعت ایران | گردشگری پایدار با احترام به محیط زیست و فرهنگ‌های محلی
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Link to="/tourism/destinations" className="px-8 py-4 bg-white text-emerald-700 rounded-2xl font-bold text-lg hover:bg-emerald-50 transition-all shadow-lg hover:shadow-xl flex items-center gap-2">
              مقاصد گردشگری <ArrowRight className="w-5 h-5" />
            </Link>
            <Link to="/tourism/booking" className="px-8 py-4 bg-emerald-900/30 text-white border-2 border-white/30 rounded-2xl font-bold text-lg hover:bg-emerald-900/50 transition-all flex items-center gap-2 backdrop-blur-sm">
              رزرو تور <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </div>

      {/* Highlights */}
      <div className="max-w-6xl mx-auto px-4 -mt-10 pb-4">
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {HIGHLIGHTS.map((h, i) => {
            const Icon = h.icon;
            return (
              <div key={i} className="bg-white rounded-2xl shadow-lg p-4 text-center hover:shadow-xl transition-all hover:-translate-y-1">
                <Icon className="w-8 h-8 mx-auto mb-2 text-emerald-600" />
                <p className="text-xs font-medium text-stone-600">{h.text}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Sections */}
      <div className="max-w-6xl mx-auto px-4 py-16">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-stone-800 mb-3">خدمات گردشگری ما</h2>
          <p className="text-stone-500 max-w-2xl mx-auto">از برنامه‌ریزی سفر تا اقامت، همه چیز برای یک تجربه بی‌نظیر اکوتوریسم</p>
        </div>
        <div className="grid md:grid-cols-2 gap-8">
          {TOURISM_SECTIONS.map(section => {
            const Icon = section.icon;
            return (
              <Link key={section.id} to={section.path} className="group block">
                <div className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-stone-100">
                  <div className={'bg-gradient-to-r ' + section.color + ' p-8 flex items-center justify-between'}>
                    <Icon className="w-14 h-14 text-white/90" />
                    <div className="text-right">
                      <span className="text-3xl font-bold text-white">{section.count}</span>
                      <p className="text-white/70 text-sm">{section.countLabel}</p>
                    </div>
                  </div>
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-stone-800 mb-2 group-hover:text-emerald-600 transition-colors">{section.title}</h3>
                    <p className="text-stone-500 text-sm mb-4">{section.desc}</p>
                    <span className="inline-flex items-center gap-1 text-emerald-600 font-medium text-sm group-hover:gap-2 transition-all">
                      مشاهده <ArrowRight className="w-4 h-4" />
                    </span>
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Features */}
      <div className="bg-white py-16">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-stone-800 mb-3">چرا اکوتوریسم با Econojin؟</h2>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="text-center p-6">
              <div className="w-14 h-14 bg-emerald-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Star className="w-7 h-7 text-emerald-600" />
              </div>
              <h3 className="font-bold text-stone-800 mb-2">گردشگری پایدار</h3>
              <p className="text-sm text-stone-500">حفظ محیط زیست و حمایت از جوامع محلی</p>
            </div>
            <div className="text-center p-6">
              <div className="w-14 h-14 bg-teal-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Compass className="w-7 h-7 text-teal-600" />
              </div>
              <h3 className="font-bold text-stone-800 mb-2">راهنمایان محلی</h3>
              <p className="text-sm text-stone-500">تجربه اصیل با راهنمایان بومی و متخصص</p>
            </div>
            <div className="text-center p-6">
              <div className="w-14 h-14 bg-cyan-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                <Heart className="w-7 h-7 text-cyan-600" />
              </div>
              <h3 className="font-bold text-stone-800 mb-2">تجربه‌های منحصربه‌فرد</h3>
              <p className="text-sm text-stone-500">از کویر تا جنگل، از دریا تا کوهستان</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
