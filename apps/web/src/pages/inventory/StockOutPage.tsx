import { useState, useMemo } from 'react';
import { Search, ArrowDown } from 'lucide-react';
import { InventoryTable } from '../../components/inventory/InventoryTable';

interface StockItem { id: string; name: string; nameFa: string; category: string; categoryFa: string; quantity: number; unit: string; minStock: number; location: string; lastUpdated: string; status: 'normal' | 'low' | 'critical'; }

const ITEMS: StockItem[] = [
  { id: 'i1', name: 'Urea Fertilizer', nameFa: 'کود اوره', category: 'fertilizer', categoryFa: 'کود', quantity: 250, unit: 'کیلوگرم', minStock: 100, location: 'انبار A', lastUpdated: '۱۴۰۵/۰۵/۰۱', status: 'normal' },
  { id: 'i2', name: 'Phosphate Fertilizer', nameFa: 'کود فسفات', category: 'fertilizer', categoryFa: 'کود', quantity: 80, unit: 'کیلوگرم', minStock: 100, location: 'انبار A', lastUpdated: '۱۴۰۵/۰۴/۲۸', status: 'low' },
  { id: 'i3', name: 'Wheat Seeds', nameFa: 'بذر گندم', category: 'seed', categoryFa: 'بذر', quantity: 500, unit: 'کیلوگرم', minStock: 200, location: 'انبار B', lastUpdated: '۱۴۰۵/۰۵/۰۲', status: 'normal' },
  { id: 'i4', name: 'Pesticide Spray', nameFa: 'سم‌پاش', category: 'equipment', categoryFa: 'تجهیزات', quantity: 3, unit: 'دستگاه', minStock: 5, location: 'انبار C', lastUpdated: '۱۴۰۵/۰۴/۱۵', status: 'low' },
  { id: 'i5', name: 'Drip Irrigation', nameFa: 'کیت آبیاری', category: 'equipment', categoryFa: 'تجهیزات', quantity: 15, unit: 'دستگاه', minStock: 10, location: 'انبار B', lastUpdated: '۱۴۰۵/۰۴/۳۰', status: 'normal' },
  { id: 'i6', name: 'Barley Seeds', nameFa: 'بذر جو', category: 'seed', categoryFa: 'بذر', quantity: 120, unit: 'کیلوگرم', minStock: 150, location: 'انبار A', lastUpdated: '۱۴۰۵/۰۴/۲۶', status: 'low' },
  { id: 'i7', name: 'Organic Compost', nameFa: 'کمپوست ارگانیک', category: 'fertilizer', categoryFa: 'کود', quantity: 800, unit: 'کیلوگرم', minStock: 300, location: 'انبار C', lastUpdated: '۱۴۰۵/۰۵/۰۳', status: 'normal' },
  { id: 'i8', name: 'Tractor Oil', nameFa: 'روغن تراکتور', category: 'consumable', categoryFa: 'مصرفی', quantity: 5, unit: 'لیتر', minStock: 20, location: 'انبار C', lastUpdated: '۱۴۰۵/۰۳/۲۰', status: 'critical' },
];

const CATEGORIES = ['fertilizer', 'seed', 'equipment', 'consumable'];

export default function StockOutPage() {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [form, setForm] = useState({ itemId: '', quantity: 0, receiver: '', reason: '', date: new Date().toISOString().split('T')[0] });
  const [submitted, setSubmitted] = useState(false);

  const filtered = useMemo(() => ITEMS.filter(i =>
    (i.nameFa.includes(search) || i.name.includes(search)) &&
    (categoryFilter === 'all' || i.category === categoryFilter)
  ), [search, categoryFilter]);

  const handleSubmit = () => { if (form.itemId && form.quantity > 0) setSubmitted(true); };

  if (submitted) {
    const item = ITEMS.find(i => i.id === form.itemId);
    return (
      <div className="max-w-lg mx-auto p-4">
        <div className="bg-white rounded-2xl shadow-lg p-8 text-center">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <ArrowDown className="w-8 h-8 text-red-500" />
          </div>
          <h2 className="text-xl font-bold text-stone-800 mb-2">خروج کالا ثبت شد</h2>
          <p className="text-stone-600 mb-4">{item?.nameFa} - {form.quantity} {item?.unit} به {form.receiver} تحویل شد</p>
          <button onClick={() => { setSubmitted(false); setForm({ itemId: '', quantity: 0, receiver: '', reason: '', date: new Date().toISOString().split('T')[0] }); }}
            className="px-6 py-2 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-700">ثبت خروج جدید</button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-4 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold text-stone-800">خروج کالا از انبار</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-stone-100">
            <h3 className="font-bold text-stone-700 mb-4">اطلاعات خروج</h3>
            <div className="space-y-3">
              <div><label className="block text-sm text-stone-500 mb-1">تاریخ</label>
                <input type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))}
                  className="w-full px-3 py-2 rounded-lg border border-stone-200 text-right" /></div>
              <div><label className="block text-sm text-stone-500 mb-1">گیرنده</label>
                <input type="text" value={form.receiver} onChange={e => setForm(f => ({ ...f, receiver: e.target.value }))}
                  placeholder="نام گیرنده" className="w-full px-3 py-2 rounded-lg border border-stone-200 text-right" /></div>
              <div><label className="block text-sm text-stone-500 mb-1">مقدار</label>
                <input type="number" min={1} value={form.quantity || ''} onChange={e => setForm(f => ({ ...f, quantity: parseInt(e.target.value) || 0 }))}
                  className="w-full px-3 py-2 rounded-lg border border-stone-200 text-right" /></div>
              <div><label className="block text-sm text-stone-500 mb-1">علت خروج</label>
                <textarea value={form.reason} onChange={e => setForm(f => ({ ...f, reason: e.target.value }))}
                  rows={2} placeholder="توضیحات..." className="w-full px-3 py-2 rounded-lg border border-stone-200 text-right" /></div>
            </div>
          </div>
        </div>

        <div>
          <div className="bg-white rounded-xl p-6 shadow-sm border border-stone-100">
            <h3 className="font-bold text-stone-700 mb-4">انتخاب کالا</h3>
            <div className="flex flex-wrap gap-2 mb-4">
              <button onClick={() => setCategoryFilter('all')} className={'px-3 py-1 rounded-full text-xs font-medium ' + (categoryFilter === 'all' ? 'bg-emerald-600 text-white' : 'bg-stone-100 text-stone-600')}>همه</button>
              {CATEGORIES.map(c => <button key={c} onClick={() => setCategoryFilter(c)} className={'px-3 py-1 rounded-full text-xs font-medium ' + (categoryFilter === c ? 'bg-emerald-600 text-white' : 'bg-stone-100 text-stone-600')}>{ITEMS.find(i => i.category === c)?.categoryFa}</button>)}
            </div>
            <div className="relative mb-3">
              <Search className="absolute right-3 top-2 w-4 h-4 text-stone-400" />
              <input type="text" placeholder="جستجو..." value={search} onChange={e => setSearch(e.target.value)}
                className="w-full pr-9 pl-3 py-2 rounded-lg border border-stone-200 text-right text-sm" />
            </div>
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {filtered.map(item => (
                <div key={item.id} onClick={() => setForm(f => ({ ...f, itemId: item.id }))}
                  className={'p-3 rounded-lg cursor-pointer transition-all border ' + (form.itemId === item.id ? 'border-emerald-500 bg-emerald-50' : 'border-stone-100 hover:border-stone-300')}>
                  <div className="flex justify-between items-center">
                    <span className="font-medium text-sm">{item.nameFa}</span>
                    <span className="text-xs text-stone-500">موجودی: {item.quantity} {item.unit}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <button onClick={handleSubmit} disabled={!form.itemId || form.quantity <= 0}
        className="w-full py-3 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 disabled:bg-stone-300 disabled:cursor-not-allowed flex items-center justify-center gap-2">
        <ArrowDown className="w-5 h-5" /> ثبت خروج کالا
      </button>
    </div>
  );
}
