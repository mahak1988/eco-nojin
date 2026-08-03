import { useState, useMemo } from 'react';
import { Package, ArrowDown, ArrowUp, Search, Filter, Download, AlertTriangle, TrendingUp, Warehouse, Box } from 'lucide-react';
import { InventoryTable } from '../../components/inventory/InventoryTable';
import { StockCard } from '../../components/inventory/StockCard';

interface StockItem {
  id: string; name: string; nameFa: string; category: string; categoryFa: string;
  quantity: number; unit: string; minStock: number; location: string;
  lastUpdated: string; status: 'normal' | 'low' | 'critical';
}

const ITEMS: StockItem[] = [
  { id: 'i1', name: 'Urea Fertilizer', nameFa: 'کود اوره', category: 'fertilizer', categoryFa: 'کود', quantity: 250, unit: 'کیلوگرم', minStock: 100, location: 'انبار A', lastUpdated: '۱۴۰۵/۰۵/۰۱', status: 'normal' },
  { id: 'i2', name: 'Phosphate Fertilizer', nameFa: 'کود فسفات', category: 'fertilizer', categoryFa: 'کود', quantity: 80, unit: 'کیلوگرم', minStock: 100, location: 'انبار A', lastUpdated: '۱۴۰۵/۰۴/۲۸', status: 'low' },
  { id: 'i3', name: 'Wheat Seeds', nameFa: 'بذر گندم', category: 'seed', categoryFa: 'بذر', quantity: 500, unit: 'کیلوگرم', minStock: 200, location: 'انبار B', lastUpdated: '۱۴۰۵/۰۵/۰۲', status: 'normal' },
  { id: 'i4', name: 'Pesticide Spray', nameFa: 'سم‌پاش', category: 'equipment', categoryFa: 'تجهیزات', quantity: 3, unit: 'دستگاه', minStock: 5, location: 'انبار C', lastUpdated: '۱۴۰۵/۰۴/۱۵', status: 'low' },
  { id: 'i5', name: 'Drip Irrigation Kit', nameFa: 'کیت آبیاری قطره‌ای', category: 'equipment', categoryFa: 'تجهیزات', quantity: 15, unit: 'دستگاه', minStock: 10, location: 'انبار B', lastUpdated: '۱۴۰۵/۰۴/۳۰', status: 'normal' },
  { id: 'i6', name: 'Barley Seeds', nameFa: 'بذر جو', category: 'seed', categoryFa: 'بذر', quantity: 120, unit: 'کیلوگرم', minStock: 150, location: 'انبار A', lastUpdated: '۱۴۰۵/۰۴/۲۶', status: 'low' },
  { id: 'i7', name: 'Organic Compost', nameFa: 'کمپوست ارگانیک', category: 'fertilizer', categoryFa: 'کود', quantity: 800, unit: 'کیلوگرم', minStock: 300, location: 'انبار C', lastUpdated: '۱۴۰۵/۰۵/۰۳', status: 'normal' },
  { id: 'i8', name: 'Tractor Oil', nameFa: 'روغن تراکتور', category: 'consumable', categoryFa: 'مصرفی', quantity: 5, unit: 'لیتر', minStock: 20, location: 'انبار C', lastUpdated: '۱۴۰۵/۰۳/۲۰', status: 'critical' },
  { id: 'i9', name: 'Safety Gloves', nameFa: 'دستکش ایمنی', category: 'consumable', categoryFa: 'مصرفی', quantity: 45, unit: 'جفت', minStock: 30, location: 'انبار A', lastUpdated: '۱۴۰۵/۰۵/۰۱', status: 'normal' },
  { id: 'i10', name: 'Tomato Seeds', nameFa: 'بذر گوجه', category: 'seed', categoryFa: 'بذر', quantity: 1000, unit: 'عدد', minStock: 500, location: 'انبار B', lastUpdated: '۱۴۰۵/۰۵/۰۲', status: 'normal' },
];

const CATEGORIES = [...new Set(ITEMS.map(i => i.category))];

export default function StockReportPage() {
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [statusFilter, setStatusFilter] = useState('all');

  const filtered = useMemo(() => ITEMS.filter(i => {
    return (i.nameFa.includes(search) || i.name.includes(search))
      && (categoryFilter === 'all' || i.category === categoryFilter)
      && (statusFilter === 'all' || i.status === statusFilter);
  }), [search, categoryFilter, statusFilter]);

  const stats = { total: ITEMS.length, normal: ITEMS.filter(i => i.status === 'normal').length, low: ITEMS.filter(i => i.status === 'low').length, critical: ITEMS.filter(i => i.status === 'critical').length };

  return (
    <div className="space-y-6 p-4">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-xl p-4 shadow-sm border border-stone-100">
          <div className="flex items-center gap-2 mb-1"><Box className="w-5 h-5 text-blue-500" /><span className="text-xs text-stone-500">کل اقلام</span></div>
          <p className="text-2xl font-bold text-stone-800">{stats.total}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-stone-100">
          <div className="flex items-center gap-2 mb-1"><TrendingUp className="w-5 h-5 text-emerald-500" /><span className="text-xs text-stone-500">موجودی نرمال</span></div>
          <p className="text-2xl font-bold text-emerald-600">{stats.normal}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-stone-100">
          <div className="flex items-center gap-2 mb-1"><AlertTriangle className="w-5 h-5 text-amber-500" /><span className="text-xs text-stone-500">هشدار کمبود</span></div>
          <p className="text-2xl font-bold text-amber-600">{stats.low}</p>
        </div>
        <div className="bg-white rounded-xl p-4 shadow-sm border border-stone-100">
          <div className="flex items-center gap-2 mb-1"><Package className="w-5 h-5 text-red-500" /><span className="text-xs text-stone-500">بحرانی</span></div>
          <p className="text-2xl font-bold text-red-600">{stats.critical}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-3 items-center bg-white rounded-xl p-4 shadow-sm">
        <div className="flex-1 min-w-[200px] relative">
          <Search className="absolute right-3 top-2.5 w-5 h-5 text-stone-400" />
          <input type="text" placeholder="جستجوی کالا..." value={search} onChange={e => setSearch(e.target.value)}
            className="w-full pr-10 pl-4 py-2 rounded-lg border border-stone-200 text-right" />
        </div>
        <select value={categoryFilter} onChange={e => setCategoryFilter(e.target.value)} className="px-3 py-2 rounded-lg border border-stone-200 bg-white text-right">
          <option value="all">همه دسته‌ها</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{ITEMS.find(i => i.category === c)?.categoryFa || c}</option>)}
        </select>
        <select value={statusFilter} onChange={e => setStatusFilter(e.target.value)} className="px-3 py-2 rounded-lg border border-stone-200 bg-white text-right">
          <option value="all">همه وضعیت‌ها</option>
          <option value="normal">عادی</option><option value="low">کمبود</option><option value="critical">بحرانی</option>
        </select>
        <button className="flex items-center gap-1 px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700">
          <Download className="w-4 h-4" /> خروجی Excel
        </button>
      </div>

      {/* Table */}
      <InventoryTable items={filtered} />
    </div>
  );
}
