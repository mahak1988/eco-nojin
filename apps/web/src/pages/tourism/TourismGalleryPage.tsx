import { useState } from 'react';
import { X, ChevronLeft, ChevronRight, ZoomIn } from 'lucide-react';

const GALLERY_ITEMS = [
  { id: '1', src: '', title: 'دره الموت', category: 'کوهستان', desc: 'چشم‌انداز قلعه حسن صباح' },
  { id: '2', src: '', title: 'جنگل‌های ماسال', category: 'جنگل', desc: 'مه‌گرفتگی ییلاقات' },
  { id: '3', src: '', title: 'کلوت‌های شهداد', category: 'کویر', desc: 'سازه‌های طبیعی کویر لوت' },
  { id: '4', src: '', title: 'جزیره قشم', category: 'دریا', desc: 'دره ستارگان' },
  { id: '5', src: '', title: 'کندوان', category: 'روستایی', desc: 'خانه‌های صخره‌ای' },
  { id: '6', src: '', title: 'سواحل چابهار', category: 'دریا', desc: 'کوه‌های مریخی' },
  { id: '7', src: '', title: 'دماوند', category: 'کوهستان', desc: 'بام ایران' },
  { id: '8', src: '', title: 'تالاب انزلی', category: 'تالاب', desc: 'نیلوفرهای آبی' },
  { id: '9', src: '', title: 'باغ شازده ماهان', category: 'تاریخی', desc: 'بهشت کویر کرمان' },
];

const CATEGORIES = ['همه', 'کوهستان', 'جنگل', 'کویر', 'دریا', 'تالاب', 'روستایی', 'تاریخی'];

export default function TourismGalleryPage() {
  const [activeCategory, setActiveCategory] = useState('همه');
  const [lightbox, setLightbox] = useState<number | null>(null);

  const filtered = activeCategory === 'همه'
    ? GALLERY_ITEMS
    : GALLERY_ITEMS.filter(i => i.category === activeCategory);

  return (
    <div className="min-h-screen bg-gradient-to-b from-stone-50 to-emerald-50">
      <div className="bg-gradient-to-br from-emerald-800 via-teal-700 to-emerald-600 py-16 px-4">
        <div className="max-w-6xl mx-auto text-center">
          <h1 className="text-4xl md:text-5xl font-display font-bold text-white mb-4">گالری تصاویر</h1>
          <p className="text-emerald-100 text-lg">زیبایی‌های طبیعی ایران را در قاب تصویر ببینید</p>
        </div>
      </div>

      <div className="max-w-6xl mx-auto px-4 -mt-6 pb-16">
        <div className="flex flex-wrap gap-2 justify-center mb-8">
          {CATEGORIES.map(cat => (
            <button key={cat} onClick={() => setActiveCategory(cat)}
              className={'px-4 py-2 rounded-full text-sm font-medium transition-all ' + (activeCategory === cat ? 'bg-emerald-600 text-white shadow-lg' : 'bg-white text-stone-600 hover:bg-emerald-50')}>
              {cat}
            </button>
          ))}
        </div>

        <div className="columns-1 md:columns-2 lg:columns-3 gap-4">
          {filtered.map((item, idx) => (
            <div key={item.id} onClick={() => setLightbox(idx)} className="break-inside-avoid mb-4 cursor-pointer group">
              <div className="bg-white rounded-2xl overflow-hidden shadow-md hover:shadow-xl transition-all">
                <div className="h-64 bg-gradient-to-br from-emerald-300 via-teal-400 to-cyan-500 relative">
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/10 transition-colors flex items-center justify-center">
                    <ZoomIn className="w-10 h-10 text-white opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
                <div className="p-4">
                  <h3 className="font-bold text-stone-800">{item.title}</h3>
                  <p className="text-sm text-stone-500">{item.desc}</p>
                  <span className="text-xs text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-full mt-2 inline-block">{item.category}</span>
                </div>
              </div>
            </div>
          ))}
        </div>

        {lightbox !== null && (
          <div className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center" onClick={() => setLightbox(null)}>
            <button className="absolute top-4 right-4 text-white/80 hover:text-white"><X className="w-8 h-8" /></button>
            <button onClick={e => { e.stopPropagation(); setLightbox(l => Math.max(0, (l || 1) - 1)); }}
              className="absolute left-4 text-white/80 hover:text-white"><ChevronLeft className="w-10 h-10" /></button>
            <button onClick={e => { e.stopPropagation(); setLightbox(l => Math.min(filtered.length - 1, (l || 0) + 1)); }}
              className="absolute right-4 text-white/80 hover:text-white"><ChevronRight className="w-10 h-10" /></button>
            <div className="max-w-4xl max-h-[80vh] p-4">
              <div className="w-full h-[60vh] bg-gradient-to-br from-emerald-300 via-teal-400 to-cyan-500 rounded-2xl" />
              <p className="text-white text-center mt-4 text-lg">{filtered[lightbox]?.title} - {filtered[lightbox]?.desc}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
