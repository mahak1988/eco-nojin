import { Star, MapPin, Wifi, Coffee, Car, Waves, Trees } from 'lucide-react';

interface EcoLodge {
  id: string; name: string; nameFa: string; location: string; locationFa: string;
  rating: number; reviews: number; price: string; image: string;
  type: string; amenities: string[]; description: string; capacity: number;
}

const LODGES: EcoLodge[] = [
  { id: 'l1', name: 'Gileboom Eco Lodge', nameFa: 'اقامتگاه بوم‌گردی گیله بوم', location: 'Rasht', locationFa: 'رشت', rating: 4.8, reviews: 156, price: '۸۵۰,۰۰۰', image: '', type: 'سنتی', amenities: ['wifi', 'parking', 'food'], description: 'خانه سنتی گیلکی با حیاط مرکزی و غذای محلی', capacity: 12 },
  { id: 'l2', name: 'Matin Abad Desert Camp', nameFa: 'کمپ کویری متین‌آباد', location: 'Isfahan', locationFa: 'اصفهان', rating: 4.6, reviews: 98, price: '۱,۲۰۰,۰۰۰', image: '', type: 'کویری', amenities: ['wifi', 'coffee'], description: 'اقامت در قلب کویر با آسمان پرستاره', capacity: 20 },
  { id: 'l3', name: 'Kandovan Rock Hotel', nameFa: 'هتل صخره‌ای کندوان', location: 'Tabriz', locationFa: 'تبریز', rating: 4.7, reviews: 203, price: '۲,۱۰۰,۰۰۰', image: '', type: 'صخره‌ای', amenities: ['wifi', 'parking', 'food', 'coffee'], description: 'اقامت در دل صخره‌های ۷۰۰ ساله کندوان', capacity: 8 },
  { id: 'l4', name: 'Qeshm Ecolodge', nameFa: 'اقامتگاه بوم‌گردی قشم', location: 'Qeshm', locationFa: 'قشم', rating: 4.5, reviews: 134, price: '۹۵۰,۰۰۰', image: '', type: 'ساحلی', amenities: ['wifi', 'food'], description: 'کلبه‌های حصیری کنار ساحل خلیج فارس', capacity: 15 },
  { id: 'l5', name: 'Masal Yeylagh Hut', nameFa: 'کلبه ییلاقی ماسال', location: 'Masal', locationFa: 'ماسال', rating: 4.9, reviews: 87, price: '۶۵۰,۰۰۰', image: '', type: 'جنگلی', amenities: ['parking', 'food'], description: 'کلبه چوبی در دل جنگل‌های مه‌آلود ماسال', capacity: 6 },
];

const AMENITY_ICONS: Record<string, any> = { wifi: Wifi, parking: Car, food: Coffee, coffee: Coffee };

export default function EcoLodgesPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-stone-50 to-emerald-50">
      <div className="bg-gradient-to-br from-emerald-800 via-teal-700 to-emerald-600 py-20 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-4">اقامتگاه‌های بوم‌گردی</h1>
          <p className="text-emerald-100 text-lg max-w-2xl mx-auto">اقامت در دل طبیعت با حفظ محیط زیست و فرهنگ محلی</p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 -mt-8 pb-16">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {LODGES.map(lodge => (
            <div key={lodge.id} className="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-stone-100">
              <div className="h-48 bg-gradient-to-br from-teal-400 to-emerald-700 relative">
                <div className="absolute inset-0 bg-black/10" />
                <div className="absolute top-3 left-3 bg-white/90 rounded-full px-3 py-1 text-xs font-bold text-emerald-700">{lodge.type}</div>
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-4">
                  <span className="text-white/80 text-sm flex items-center gap-1"><MapPin className="w-3 h-3" />{lodge.locationFa}</span>
                </div>
              </div>
              <div className="p-5">
                <div className="flex items-start justify-between mb-2">
                  <h3 className="text-lg font-bold text-stone-800">{lodge.nameFa}</h3>
                  <div className="flex items-center gap-1"><Star className="w-4 h-4 text-amber-400 fill-amber-400" /><span className="text-sm font-medium">{lodge.rating}</span></div>
                </div>
                <p className="text-sm text-stone-600 mb-3">{lodge.description}</p>
                <div className="flex gap-2 mb-3">
                  {lodge.amenities.map(a => { const Icon = AMENITY_ICONS[a]; return <span key={a} className="p-1.5 bg-stone-100 rounded-lg" title={a}><Icon className="w-4 h-4 text-stone-500" /></span>; })}
                </div>
                <div className="flex items-center justify-between pt-3 border-t border-stone-100">
                  <div><span className="text-emerald-700 font-bold">{lodge.price}</span><span className="text-xs text-stone-400 mr-1">تومان / شب</span></div>
                  <span className="text-xs text-stone-400">ظرفیت {lodge.capacity} نفر</span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
