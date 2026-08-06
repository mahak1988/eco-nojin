import React, { useEffect, useState } from 'react';
import { Plus, Search, Loader2, MapPin, Trash2, Edit2, RefreshCw } from 'lucide-react';

interface Farm {
  id: number;
  name: string;
  region?: string;
  area_ha?: number;
  latitude?: number;
  longitude?: number;
  is_active: boolean;
  created_at?: string;
}

interface FarmListResponse {
  data: Farm[];
  meta: { total: number; page: number; size: number; pages: number };
}

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

const FarmsPage: React.FC = () => {
  const [farms, setFarms] = useState<Farm[]>([]);
  const [meta, setMeta] = useState({ total: 0, page: 1, size: 20, pages: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [form, setForm] = useState({ name: '', region: '', area_ha: '', latitude: '', longitude: '' });

  const fetchFarms = async (page = 1, q = search) => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ page: String(page), size: '20' });
      if (q) params.set('search', q);
      const r = await fetch(`${BASE}/farms?${params}`, { credentials: 'include' });
      if (!r.ok) throw new Error(`خطای سرور: ${r.status}`);
      const body: FarmListResponse = await r.json();
      setFarms(body.data);
      setMeta(body.meta);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : 'خطا در بارگذاری مزارع');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchFarms(); }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchFarms(1, search);
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      const body = {
        name: form.name,
        region: form.region || undefined,
        area_ha: form.area_ha ? parseFloat(form.area_ha) : undefined,
        latitude: form.latitude ? parseFloat(form.latitude) : undefined,
        longitude: form.longitude ? parseFloat(form.longitude) : undefined,
      };
      const r = await fetch(`${BASE}/farms`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body),
      });
      if (!r.ok) throw new Error(`خطا: ${r.status}`);
      setShowForm(false);
      setForm({ name: '', region: '', area_ha: '', latitude: '', longitude: '' });
      fetchFarms();
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'خطا در ایجاد مزرعه');
    } finally {
      setSubmitting(false);
    }
  };

  const handleSeedDemo = async () => {
    try {
      await fetch(`${BASE}/farms/seed-demo`, { method: 'POST', credentials: 'include' });
      fetchFarms();
    } catch {
      alert('خطا در بارگذاری داده نمونه');
    }
  };

  return (
    <div className="space-y-5 p-1" dir="rtl">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-xl font-bold">مزارع</h1>
          <p className="text-sm text-muted-foreground">{meta.total} مزرعه ثبت‌شده</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={handleSeedDemo}
            className="px-3 py-1.5 text-xs rounded-lg border hover:bg-muted transition-colors"
          >
            داده نمونه
          </button>
          <button
            onClick={() => fetchFarms()}
            className="px-3 py-1.5 text-xs rounded-lg border hover:bg-muted transition-colors flex items-center gap-1"
          >
            <RefreshCw className="w-3.5 h-3.5" /> بارگذاری مجدد
          </button>
          <button
            onClick={() => setShowForm((v) => !v)}
            className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 transition-opacity"
          >
            <Plus className="w-4 h-4" /> افزودن مزرعه
          </button>
        </div>
      </div>

      {/* Create Form */}
      {showForm && (
        <form onSubmit={handleCreate} className="rounded-xl border bg-card p-4 space-y-3">
          <h2 className="text-sm font-semibold">مزرعه جدید</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">نام مزرعه *</label>
              <input
                required
                value={form.name}
                onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
                className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="مثال: مزرعه اصفهان"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">استان/منطقه</label>
              <input
                value={form.region}
                onChange={(e) => setForm((f) => ({ ...f, region: e.target.value }))}
                className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="مثال: اصفهان"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">مساحت (هکتار)</label>
              <input
                type="number" step="0.01" min="0"
                value={form.area_ha}
                onChange={(e) => setForm((f) => ({ ...f, area_ha: e.target.value }))}
                className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                placeholder="مثال: 12.5"
              />
            </div>
            <div className="flex gap-2">
              <div className="flex-1">
                <label className="text-xs text-muted-foreground block mb-1">عرض جغرافیایی</label>
                <input
                  type="number" step="0.0001"
                  value={form.latitude}
                  onChange={(e) => setForm((f) => ({ ...f, latitude: e.target.value }))}
                  className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="32.65"
                />
              </div>
              <div className="flex-1">
                <label className="text-xs text-muted-foreground block mb-1">طول جغرافیایی</label>
                <input
                  type="number" step="0.0001"
                  value={form.longitude}
                  onChange={(e) => setForm((f) => ({ ...f, longitude: e.target.value }))}
                  className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                  placeholder="51.67"
                />
              </div>
            </div>
          </div>
          <div className="flex gap-2 justify-end">
            <button
              type="button"
              onClick={() => setShowForm(false)}
              className="px-4 py-1.5 rounded-lg border text-sm hover:bg-muted transition-colors"
            >
              انصراف
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 disabled:opacity-50"
            >
              {submitting && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
              ذخیره
            </button>
          </div>
        </form>
      )}

      {/* Search */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="جستجوی مزرعه..."
            className="w-full rounded-lg border bg-background pr-9 pl-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <button type="submit" className="px-4 py-2 rounded-lg border text-sm hover:bg-muted transition-colors">
          جستجو
        </button>
      </form>

      {/* List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
        </div>
      ) : error ? (
        <div className="rounded-xl border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">{error}</div>
      ) : farms.length === 0 ? (
        <div className="rounded-xl border bg-card p-8 text-center text-muted-foreground text-sm">
          هیچ مزرعه‌ای یافت نشد. برای شروع، داده نمونه بارگذاری کنید.
        </div>
      ) : (
        <div className="rounded-xl border bg-card overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="text-right px-4 py-3 font-medium text-muted-foreground">نام</th>
                <th className="text-right px-4 py-3 font-medium text-muted-foreground hidden sm:table-cell">منطقه</th>
                <th className="text-right px-4 py-3 font-medium text-muted-foreground hidden md:table-cell">مساحت (هکتار)</th>
                <th className="text-right px-4 py-3 font-medium text-muted-foreground hidden lg:table-cell">مختصات</th>
                <th className="text-right px-4 py-3 font-medium text-muted-foreground">وضعیت</th>
              </tr>
            </thead>
            <tbody>
              {farms.map((farm, i) => (
                <tr key={farm.id} className={`border-b last:border-0 hover:bg-muted/30 transition-colors ${i % 2 === 0 ? '' : 'bg-muted/10'}`}>
                  <td className="px-4 py-3 font-medium">{farm.name}</td>
                  <td className="px-4 py-3 text-muted-foreground hidden sm:table-cell">{farm.region ?? '—'}</td>
                  <td className="px-4 py-3 hidden md:table-cell">
                    {farm.area_ha != null ? farm.area_ha.toLocaleString('fa-IR') : '—'}
                  </td>
                  <td className="px-4 py-3 hidden lg:table-cell">
                    {farm.latitude != null && farm.longitude != null ? (
                      <span className="flex items-center gap-1 text-xs text-muted-foreground">
                        <MapPin className="w-3 h-3" />
                        {farm.latitude.toFixed(4)}, {farm.longitude.toFixed(4)}
                      </span>
                    ) : '—'}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${farm.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'}`}>
                      {farm.is_active ? 'فعال' : 'غیرفعال'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {meta.pages > 1 && (
        <div className="flex items-center justify-center gap-2 text-sm">
          <button
            disabled={meta.page <= 1}
            onClick={() => fetchFarms(meta.page - 1)}
            className="px-3 py-1.5 rounded-lg border hover:bg-muted disabled:opacity-40 transition-colors"
          >
            قبلی
          </button>
          <span className="text-muted-foreground">
            صفحه {meta.page} از {meta.pages}
          </span>
          <button
            disabled={meta.page >= meta.pages}
            onClick={() => fetchFarms(meta.page + 1)}
            className="px-3 py-1.5 rounded-lg border hover:bg-muted disabled:opacity-40 transition-colors"
          >
            بعدی
          </button>
        </div>
      )}
    </div>
  );
};

export default FarmsPage;
