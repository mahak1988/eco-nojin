import React, { useState } from 'react';
import { AlertTriangle, Loader2, ShieldAlert, CheckCircle } from 'lucide-react';

interface RiskReport {
  [key: string]: unknown;
}

const BASE = import.meta.env.VITE_API_BASE_URL ?? '/api/v1';

const severityColor = (value: unknown): string => {
  const v = typeof value === 'number' ? value : parseFloat(String(value));
  if (isNaN(v)) return 'text-muted-foreground';
  if (v >= 0.7) return 'text-red-600 font-bold';
  if (v >= 0.4) return 'text-amber-600 font-semibold';
  return 'text-green-600';
};

const RisksPage: React.FC = () => {
  const [demoResult, setDemoResult] = useState<RiskReport | null>(null);
  const [predResult, setPredResult] = useState<RiskReport | null>(null);
  const [demoLoading, setDemoLoading] = useState(false);
  const [predLoading, setPredLoading] = useState(false);
  const [form, setForm] = useState({
    latitude: '32.65',
    longitude: '51.67',
    crop_type: 'wheat',
    area_ha: '10',
    soil_type: 'clay_loam',
    irrigation_method: 'drip',
    season: 'spring',
  });

  const runDemo = async () => {
    setDemoLoading(true);
    try {
      const r = await fetch(`${BASE}/risks/predict/demo`, { credentials: 'include' });
      if (!r.ok) throw new Error(`خطا: ${r.status}`);
      setDemoResult(await r.json());
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'خطا در دریافت نمونه');
    } finally {
      setDemoLoading(false);
    }
  };

  const runPredict = async (e: React.FormEvent) => {
    e.preventDefault();
    setPredLoading(true);
    try {
      const payload = {
        latitude: parseFloat(form.latitude),
        longitude: parseFloat(form.longitude),
        crop_type: form.crop_type,
        area_ha: parseFloat(form.area_ha),
        soil_type: form.soil_type,
        irrigation_method: form.irrigation_method,
        season: form.season,
      };
      const r = await fetch(`${BASE}/risks/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      });
      if (!r.ok) throw new Error(`خطا: ${r.status}`);
      setPredResult(await r.json());
    } catch (e: unknown) {
      alert(e instanceof Error ? e.message : 'خطا در پیش‌بینی ریسک');
    } finally {
      setPredLoading(false);
    }
  };

  const RiskResultCard: React.FC<{ result: RiskReport; title: string }> = ({ result, title }) => (
    <div className="rounded-xl border bg-card p-4 mt-4">
      <h3 className="text-sm font-semibold mb-3 flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 text-red-500" /> {title}
      </h3>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
        {Object.entries(result).map(([k, v]) => (
          <div key={k} className="p-2 rounded-lg bg-muted/30 text-xs">
            <span className="text-muted-foreground block mb-0.5">{k}</span>
            <span className={severityColor(v)}>{String(v)}</span>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="space-y-6 p-1" dir="rtl">
      <div>
        <h1 className="text-xl font-bold">ارزیابی ریسک</h1>
        <p className="text-sm text-muted-foreground">پیش‌بینی ریسک‌های کشاورزی</p>
      </div>

      {/* Demo */}
      <div className="rounded-xl border bg-card p-5">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-sm font-semibold flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-500" /> نمونه آزمایشی
          </h2>
          <button
            onClick={runDemo}
            disabled={demoLoading}
            className="flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 disabled:opacity-50"
          >
            {demoLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            اجرای نمونه
          </button>
        </div>
        <p className="text-xs text-muted-foreground">نتیجه پیش‌بینی ریسک برای یک سناریوی نمونه پیش‌فرض.</p>
        {demoResult && <RiskResultCard result={demoResult} title="نتیجه نمونه" />}
      </div>

      {/* Custom Prediction */}
      <div className="rounded-xl border bg-card p-5">
        <h2 className="text-sm font-semibold mb-4 flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-amber-500" /> پیش‌بینی سفارشی
        </h2>
        <form onSubmit={runPredict} className="space-y-4">
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            {[
              { key: 'latitude', label: 'عرض جغرافیایی', type: 'number', step: '0.01' },
              { key: 'longitude', label: 'طول جغرافیایی', type: 'number', step: '0.01' },
              { key: 'area_ha', label: 'مساحت (هکتار)', type: 'number', step: '0.1' },
            ].map(({ key, label, type, step }) => (
              <div key={key}>
                <label className="text-xs text-muted-foreground block mb-1">{label}</label>
                <input
                  type={type} step={step}
                  value={form[key as keyof typeof form]}
                  onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                  className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>
            ))}
            {[
              { key: 'crop_type', label: 'نوع محصول', options: ['wheat', 'rice', 'corn', 'barley', 'cotton', 'sugarbeet'] },
              { key: 'soil_type', label: 'نوع خاک', options: ['clay', 'clay_loam', 'loam', 'sandy_loam', 'sand', 'silt'] },
              { key: 'irrigation_method', label: 'روش آبیاری', options: ['drip', 'sprinkler', 'flood', 'furrow', 'none'] },
              { key: 'season', label: 'فصل', options: ['spring', 'summer', 'autumn', 'winter'] },
            ].map(({ key, label, options }) => (
              <div key={key}>
                <label className="text-xs text-muted-foreground block mb-1">{label}</label>
                <select
                  value={form[key as keyof typeof form]}
                  onChange={(e) => setForm((f) => ({ ...f, [key]: e.target.value }))}
                  className="w-full rounded-lg border bg-background px-3 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                >
                  {options.map((o) => <option key={o} value={o}>{o}</option>)}
                </select>
              </div>
            ))}
          </div>
          <button
            type="submit"
            disabled={predLoading}
            className="flex items-center gap-1.5 px-5 py-2 rounded-lg bg-primary text-primary-foreground text-sm hover:opacity-90 disabled:opacity-50"
          >
            {predLoading && <Loader2 className="w-3.5 h-3.5 animate-spin" />}
            پیش‌بینی ریسک
          </button>
        </form>
        {predResult && <RiskResultCard result={predResult} title="نتیجه پیش‌بینی" />}
      </div>
    </div>
  );
};

export default RisksPage;
